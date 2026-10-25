"""Ask a Claude model to rate each argument in the Items sheet, blind to the human ratings.

Usage:
  python scripts/rate.py --workbook data/crypto_argument_pilot_core.xlsx --model claude-opus-5-5 [--dry-run] [--limit N]
"""
import argparse
import csv
import json
import re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
RUBRIC = ROOT / "prompts" / "rubric.txt"
RESULTS = ROOT / "results"

# The only columns this script may see. They are the first eight columns of Items (A-H),
# so we read only those cells; the lev_ columns (I onward) are never touched.
NEEDED = ["item_id", "position_id", "layer", "scope", "position_title",
          "position_text", "arg_id", "argument_text"]
DIMS = ["centrality", "strength", "correctness", "clarity"]
OUT_COLS = (["arg_id", "item_id", "position_id", "layer", "scope", "model"]
            + [f"claude_{d}" for d in DIMS]
            + ["claude_justification", "input_tokens", "output_tokens", "request_id"])
RETRY_LINE = "Your previous response was not valid JSON. Respond with only the JSON object."


def load_items(workbook):
    wb = openpyxl.load_workbook(workbook, read_only=True)
    ws = wb["Items"]  # the only sheet we open
    rows = ws.iter_rows(min_col=1, max_col=len(NEEDED), values_only=True)
    header = list(next(rows))
    assert header == NEEDED, f"Items columns A-H are not as expected: {header}"
    assert not any(str(h).startswith("lev_") for h in header), "lev_ column loaded"
    items = [dict(zip(header, r)) for r in rows if r[NEEDED.index("arg_id")]]
    wb.close()
    return items


def build_prompt(template, item):
    prompt = (template.replace("{position_title}", str(item["position_title"]))
                      .replace("{position_text}", str(item["position_text"]))
                      .replace("{argument_text}", str(item["argument_text"])))
    # Blindness check: nothing from a lev_ column can be in the prompt.
    assert "lev_" not in prompt, f"prompt for {item['arg_id']} mentions lev_"
    return prompt


def parse_rating(text):
    """Return a dict of four 1-5 ints plus a justification string, or None if invalid."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    start, end = text.find("{"), text.rfind("}")
    try:
        data = json.loads(text[start:end + 1])
    except (ValueError, TypeError):
        return None
    ok = (isinstance(data, dict)
          and all(type(data.get(d)) is int and 1 <= data[d] <= 5 for d in DIMS)
          and isinstance(data.get("justification"), str))
    return data if ok else None


def call(client, args, prompt):
    params = {"model": args.model, "max_tokens": args.max_tokens,
              "messages": [{"role": "user", "content": prompt}]}
    if args.effort != "none":
        params["output_config"] = {"effort": args.effort}
    resp = client.messages.create(**params)
    text = "".join(b.text for b in resp.content if b.type == "text")
    return params, resp, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbook", required=True, type=Path)
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int)
    # Current models always think before answering, and thinking counts toward max_tokens,
    # so the brief's 300 would leave no room for the JSON answer.
    ap.add_argument("--max-tokens", type=int, default=4000)
    # Set explicitly so different models are compared at the same setting ("none" = omit).
    ap.add_argument("--effort", default="medium")
    args = ap.parse_args()

    template = RUBRIC.read_text(encoding="utf-8")
    items = load_items(args.workbook)
    prompts = {it["arg_id"]: build_prompt(template, it) for it in items}

    if args.dry_run:
        print(prompts[items[0]["arg_id"]])
        print(f"\n--- dry run: {len(items)} rows loaded; no API calls made ---")
        return

    from anthropic import Anthropic
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    client = Anthropic(max_retries=3)

    out_csv = RESULTS / f"ratings_{args.model}.csv"
    raw_dir = RESULTS / "raw" / args.model
    raw_dir.mkdir(parents=True, exist_ok=True)
    done = set()
    if out_csv.exists():  # resume: skip rows already rated
        with out_csv.open(encoding="utf-8", newline="") as f:
            done = {r["arg_id"] for r in csv.DictReader(f)}
    todo = [it for it in items if it["arg_id"] not in done][:args.limit]

    new_file = not out_csv.exists()
    rated = failures = tok_in = tok_out = 0
    with out_csv.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_COLS)
        if new_file:
            writer.writeheader()
        for it in todo:
            prompt = prompts[it["arg_id"]]
            attempts = []
            params, resp, text = call(client, args, prompt)
            attempts.append((params, resp, text))
            rating = parse_rating(text)
            if rating is None:  # one retry with a nudge
                params, resp, text = call(client, args, prompt + "\n\n" + RETRY_LINE)
                attempts.append((params, resp, text))
                rating = parse_rating(text)

            usage_in = sum(r.usage.input_tokens for _, r, _ in attempts)
            usage_out = sum(r.usage.output_tokens for _, r, _ in attempts)
            tok_in, tok_out = tok_in + usage_in, tok_out + usage_out
            # Audit trail: every attempt's request (no key is ever in params) and response.
            raw = [{"request": p, "response_text": t, "stop_reason": r.stop_reason,
                    "usage": r.usage.to_dict(), "request_id": r._request_id}
                   for p, r, t in attempts]
            (raw_dir / f"{it['arg_id']}.json").write_text(
                json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")

            row = {k: it[k] for k in ["arg_id", "item_id", "position_id", "layer", "scope"]}
            row.update(model=args.model, input_tokens=usage_in, output_tokens=usage_out,
                       request_id=resp._request_id)
            if rating:
                row.update({f"claude_{d}": rating[d] for d in DIMS},
                           claude_justification=rating["justification"])
                rated += 1
                scores = " ".join(f"{d[:4]}={rating[d]}" for d in DIMS)
                print(f"{it['arg_id']}: {scores}")
            else:
                row["claude_justification"] = text
                failures += 1
                print(f"{it['arg_id']}: FAILED to parse (stop_reason={resp.stop_reason})")
            writer.writerow(row)
            f.flush()  # so an interrupted run can resume

    print(f"\nDone: {rated} rated, {failures} failures, "
          f"{tok_in} input + {tok_out} output tokens. Output: {out_csv}")


if __name__ == "__main__":
    main()
