"""Compare the model's ratings with the human (lev_) ratings.

Usage:
  python scripts/analyze.py --workbook data/crypto_argument_pilot_core.xlsx --ratings results/ratings_claude-opus-5-5.csv
"""
import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["centrality", "strength", "correctness", "clarity"]
HUMAN = [f"lev_{d}" for d in DIMS]
MODEL = [f"claude_{d}" for d in DIMS]


def md_table(df):
    """Render a DataFrame as a Markdown table (no extra dependency needed)."""
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = [f"{v:.2f}" if isinstance(v, float) else str(v) for v in r]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def agreement(h, m):
    d = m - h
    rho = spearmanr(h, m).statistic if h.nunique() > 1 and m.nunique() > 1 else float("nan")
    return {"exact": (d == 0).mean(), "within_1": (d.abs() <= 1).mean(),
            "mean_signed (model-human)": d.mean(), "mean_abs": d.abs().mean(),
            "spearman": rho}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbook", required=True, type=Path)
    ap.add_argument("--ratings", required=True, type=Path)
    args = ap.parse_args()
    model = pd.read_csv(args.ratings, encoding="utf-8")
    model_name = model["model"].iloc[0]

    # Only the Items sheet; the Design sheet is never opened.
    human = pd.read_excel(args.workbook, sheet_name="Items", usecols=[
        "arg_id", "position_id", "layer", "position_title", "argument_text", *HUMAN, "lev_notes"])
    human = human.dropna(subset=["arg_id"])
    n_all = len(human)
    human = human.dropna(subset=HUMAN)  # the human may not have finished rating
    print(f"Human ratings: {len(human)} complete rows, {n_all - len(human)} dropped as incomplete.")

    df = human.merge(model.drop(columns=["position_id", "layer"]), on="arg_id", how="inner")
    n_joined = len(df)
    df = df.dropna(subset=MODEL)  # model rows whose JSON failed to parse
    print(f"Joined: {n_joined} rows; {n_joined - len(df)} dropped for missing model scores.")
    df[HUMAN + MODEL] = df[HUMAN + MODEL].astype(int)
    for d in DIMS:
        df[f"diff_{d}"] = df[f"claude_{d}"] - df[f"lev_{d}"]
    df["lev_total"], df["claude_total"] = df[HUMAN].sum(axis=1), df[MODEL].sum(axis=1)
    df["diff_total"] = df["claude_total"] - df["lev_total"]
    df["abs_diff_sum"] = df[[f"diff_{d}" for d in DIMS]].abs().sum(axis=1)

    # Agreement per dimension and for the 4-dimension total.
    agree = pd.DataFrame([{"dimension": d, **agreement(df[f"lev_{d}"], df[f"claude_{d}"])}
                          for d in DIMS + ["total"]])
    # Per position: which positions does the model find hardest?
    per_pos = (df.groupby("position_id")
                 .agg(n=("arg_id", "size"),
                      **{f"mad_{d}": (f"diff_{d}", lambda s: s.abs().mean()) for d in DIMS},
                      mad_total=("abs_diff_sum", lambda s: s.mean() / 4))
                 .reset_index().sort_values("mad_total", ascending=False))

    # Fluency leak: well-written but legally wrong arguments, per the human.
    fl = df[(df["lev_clarity"] >= 4) & (df["lev_correctness"] <= 2)]
    if len(fl):
        fluency = (f"{len(fl)} rows (human clarity >= 4, correctness <= 2).\n\n"
                   f"- Strength: model {fl['claude_strength'].mean():.2f} vs human {fl['lev_strength'].mean():.2f}\n"
                   f"- Correctness: model {fl['claude_correctness'].mean():.2f} vs human {fl['lev_correctness'].mean():.2f}\n\n"
                   "If the model's numbers are higher, it is rewarding fluency.")
    else:
        fluency = "No rows meet the condition (human clarity >= 4 and correctness <= 2)."
    # Settled-law leak: arguments the human judged legally wrong.
    sl = df[df["lev_correctness"] <= 2]
    if len(sl):
        hits = (sl["claude_correctness"] >= 4).sum()
        settled = (f"{hits} of {len(sl)} rows the human marked correctness <= 2 "
                   f"got model correctness >= 4 ({hits / len(sl):.0%}).")
    else:
        settled = "No rows with human correctness <= 2."

    top = df.sort_values("abs_diff_sum", ascending=False).head(8)
    div = []
    for _, r in top.iterrows():
        h = "/".join(str(r[c]) for c in HUMAN)
        m = "/".join(str(r[c]) for c in MODEL)
        notes = r["lev_notes"] if pd.notna(r["lev_notes"]) else "(none)"
        div.append(f"### {r['arg_id']} - {r['position_title']} (abs diff {r['abs_diff_sum']})\n\n"
                   f"**Argument:** {r['argument_text']}\n\n"
                   f"**Scores (centrality/strength/correctness/clarity):** human {h}, model {m}\n\n"
                   f"**Human notes:** {notes}\n\n"
                   f"**Model justification:** {r['claude_justification']}\n")

    summary = "\n\n".join([
        f"# Agreement summary: {model_name}", f"Rows compared: {len(df)}",
        "## Agreement by dimension", md_table(agree),
        "## Mean absolute difference by position (hardest first)", md_table(per_pos),
        "## Fluency leak", fluency, "## Settled-law leak", settled,
        "## Top 8 divergences", *div])

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    df.drop(columns=["abs_diff_sum"]).to_csv(out / f"comparison_{model_name}.csv",
                                             index=False, encoding="utf-8")
    (out / f"summary_{model_name}.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
