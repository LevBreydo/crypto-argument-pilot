# Build brief: argument-rating harness for a legal-classification pilot

You are building a small, reproducible research harness. Read this whole file before writing any code, then build exactly what it specifies. Ask before deviating from the data contract or the blindness rules.

## 1. Purpose

A law professor has written position texts (legal-classification claims about crypto assets) and arguments against each position, and is rating every argument by hand on four 1–5 dimensions. This harness asks Claude (the model) to rate the same arguments under the same rubric, blind to the human ratings, and then compares the two. The output is the pilot for a dataset modeled on LMCA (Cooper, Oesterheld et al., *Conceptual Reasoning Index*, Aug 2026): grade arguments, not conclusions.

The research question: does a frontier model judge contested legal arguments the way an expert does, and where does it diverge?

## 2. Repository layout (create this)

```
crypto-argument-pilot/
  README.md                 # method, how to run, headline results (template in §8)
  requirements.txt          # anthropic, openpyxl, pandas, scipy, python-dotenv
  .env.example              # ANTHROPIC_API_KEY=sk-ant-...
  .gitignore                # .env, __pycache__/, results/raw/
  data/
    crypto_argument_pilot_core.xlsx   # the human-rated workbook (provided; NEVER modified by code)
  prompts/
    rubric.txt              # the fixed rating prompt (§5)
  scripts/
    rate.py                 # §6
    analyze.py              # §7
  results/
    raw/                    # one JSON per API response (for audit)
    ratings_<model>.csv     # model ratings, one row per argument
    comparison_<model>.csv  # human + model side by side, with differences
    summary_<model>.md      # agreement table + top divergences
```

## 3. Data contract

The workbook `data/crypto_argument_pilot_core.xlsx` has these sheets: `README`, `Rubric`, `Positions`, `Items`, `Design (read after rating)`.

**Read only the `Items` sheet.** Never open or read the `Design (read after rating)` sheet in any script — it contains the author's intended quality labels and would contaminate the comparison. Never read the `Rubric` sheet either; the prompt text lives in `prompts/rubric.txt` so it is version-controlled.

`Items` columns, in order:

| column | type | used by |
| --- | --- | --- |
| item_id | int | both |
| position_id | str (P1, P2a, …) | both |
| layer | a / b / c | both |
| scope | core / extended | both |
| position_title | str | rate.py (prompt) |
| position_text | str | rate.py (prompt) |
| arg_id | str (P1-A1, …) | both; the join key |
| argument_text | str | rate.py (prompt) |
| lev_centrality, lev_strength, lev_correctness, lev_clarity | int 1–5 or blank | analyze.py ONLY |
| lev_notes | str | analyze.py ONLY (carried into comparison) |
| claude_centrality … claude_justification | blank | ignore; do not write to the workbook |

**Blindness rule (hard):** `rate.py` must not read, log, print, or include in any prompt any column beginning with `lev_`. Load only the columns it needs. Add a test or assertion that the prompt string contains no `lev_` values.

The workbook is the human's working file. Scripts read it; they never write to it. All outputs go to `results/`.

## 4. Models and cost

Default model: `claude-opus-5-5`. Make the model a `--model` argument so the same run can be repeated with `claude-sonnet-5-5` or others; output filenames carry the model name. Expected volume: 39 arguments × ~700 input tokens × ~200 output tokens — well under a few dollars per model. Use the standard Messages API via the official SDK (`pip install anthropic`; `from anthropic import Anthropic`; `client.messages.create(...)`). The key is read from `ANTHROPIC_API_KEY` (load `.env` with python-dotenv). Do not use the Batches API for the pilot; synchronous calls with `max_retries=3` are fine. Set `temperature=0`.

## 5. The rating prompt (`prompts/rubric.txt`)

One fixed prompt for every row. Fill `{position_title}`, `{position_text}`, `{argument_text}`. Use this text verbatim:

```
You are an expert in U.S. securities, commodities, and financial regulation. You will rate one argument made AGAINST a stated position. Rate the argument, not the position, and not whether you agree with the position.

POSITION ("{position_title}"):
{position_text}

ARGUMENT AGAINST THE POSITION:
{argument_text}

Rate the argument on four dimensions, each an integer from 1 to 5.

1. CENTRALITY — Does the argument address what actually decides the question, as opposed to a side point?
   1 = irrelevant to the position's basis; 3 = touches a real but secondary consideration; 5 = goes to the dispositive criterion.

2. STRENGTH — Taking the argument's factual and legal premises as true (as on a motion to dismiss), how far does it go toward defeating the position?
   1 = would not move a careful expert at all; 3 = a fair point requiring a response; 5 = substantially undermines the position.

3. CORRECTNESS — Is the law (doctrine, statute, case holding, agency action) stated accurately?
   1 = materially wrong statement of law; 3 = mostly right with a meaningful error or omission; 5 = accurate and complete for its purpose.

4. CLARITY — Is the argument clearly stated and easy to follow, independent of whether it is right? Test: could a competent reader restate its logic in one sentence?
   1 = confused or incoherent; 3 = understandable with effort; 5 = crisp and well-organized.

Rate each dimension on its own. A fluent argument can be wrong; a correct argument can be beside the point. Do not grade on a curve.

Respond with ONLY a JSON object, no prose before or after:
{"centrality": <1-5>, "strength": <1-5>, "correctness": <1-5>, "clarity": <1-5>, "justification": "<one sentence>"}
```

## 6. `scripts/rate.py`

Command: `python scripts/rate.py --workbook data/crypto_argument_pilot_core.xlsx --model claude-opus-5-5 [--dry-run] [--limit N]`

Behavior:

1. Load `Items` with openpyxl or pandas, selecting only: item_id, position_id, layer, scope, position_title, position_text, arg_id, argument_text. Assert no `lev_` column is loaded.
2. Load `prompts/rubric.txt`; for each row, format the prompt.
3. `--dry-run`: print the fully formatted prompt for the first row and the row count, make no API calls, exit. (The human will use this to confirm blindness.)
4. Otherwise call the API once per row with `temperature=0`, `max_tokens=300`. Parse the JSON from the response text (strip code fences if present). Validate: four integers in 1–5 plus a string. On parse failure, retry once with an appended line "Your previous response was not valid JSON. Respond with only the JSON object." If it still fails, record the row with blank scores and the raw text in `justification`, and continue.
5. Save every raw response as `results/raw/<model>/<arg_id>.json` (request params minus the key, response text, token usage, request id).
6. Resume safely: if `results/ratings_<model>.csv` exists, skip arg_ids already present. `--limit N` processes at most N new rows (for a first test).
7. Write `results/ratings_<model>.csv` with columns: arg_id, item_id, position_id, layer, scope, model, claude_centrality, claude_strength, claude_correctness, claude_clarity, claude_justification, input_tokens, output_tokens, request_id.
8. Print a one-line progress message per row and a final summary (rows rated, failures, total tokens).

Use `pathlib`, UTF-8 everywhere, and no OS-specific paths; this will run on Windows.

## 7. `scripts/analyze.py`

Command: `python scripts/analyze.py --workbook data/crypto_argument_pilot_core.xlsx --ratings results/ratings_claude-opus-5-5.csv`

Behavior:

1. Load the human ratings from `Items` (arg_id, position_id, layer, the four `lev_` columns, lev_notes). Drop rows where any `lev_` score is blank and report how many were dropped (the human may not have finished).
2. Join to the model ratings on `arg_id`.
3. For each dimension (centrality, strength, correctness, clarity) compute: exact agreement rate; within-1 agreement rate; mean signed difference (model minus human); mean absolute difference; Spearman rank correlation (scipy). Also compute the same for the 4-dimension total.
4. Per-position summary: mean absolute difference per position_id, so the hardest positions for the model are visible.
5. Divergences: rank rows by sum of absolute differences across the four dimensions; output the top 8 with position_title, argument_text, the human scores, the model scores, lev_notes, and the model's justification.
6. Two targeted checks the research question cares about:
   - **Fluency leak:** among rows where the human gave clarity ≥ 4 but correctness ≤ 2, report the model's mean strength and correctness versus the human's. If the model's are higher, it is rewarding fluency.
   - **Settled-law leak:** among rows the human marked correctness ≤ 2, report how often the model gave correctness ≥ 4.
7. Write `results/comparison_<model>.csv` (all joined rows with per-dimension differences) and `results/summary_<model>.md` (the agreement table, per-position table, the two leak checks, and the top divergences formatted for reading). Print the summary to the console too.

## 8. `README.md` template

Write it so a reader who opens only this file understands the project in two minutes:

- **Question** (one sentence).
- **Method** (five lines): positions drawn from the author's taxonomy article; three arguments per position written to vary in quality; expert ratings on four dimensions; model rated blind under the identical rubric; agreement and divergence analysis.
- **Data**: what is in `data/`, what the columns mean, the blindness rule.
- **Run**: `pip install -r requirements.txt`, copy `.env.example` to `.env`, the dry-run command, the rate command, the analyze command.
- **Results**: leave a clearly marked placeholder block the author fills in from `summary_<model>.md` (headline agreement per dimension; the leak checks; three divergences with one sentence each).
- **Attribution and status**: pilot built Oct 2026; positions and arguments drafted with Claude from the author's article and edited by the author; all expert ratings are the author's own; method follows LMCA. Mark it a pilot, not a benchmark.

## 9. Working style

- Start with the dry run, show the human the formatted prompt, and wait for confirmation before making API calls.
- Do a `--limit 3` run first, show the three rows of output, then run the rest.
- Keep each script under ~150 lines and readable by a non-programmer; comments explain *why*, briefly.
- Commit after each working step with a plain commit message. Do not commit `.env` or `results/raw/`.
- If anything in this brief is ambiguous, ask one question rather than guessing.
