# Your instructions: running the pilot (Monday)

Your time: about 2½ hours total, of which ~75 minutes is rating and the rest is setup and checking. Rating and building run in parallel — start Claude Code on the build, then rate while it works.

What you are doing, in one line: Claude Code writes a small script; the script asks Claude (the model) to rate the same 39 arguments you rate; a second script compares the two.

---

## Before Monday (10 minutes)

1. **Make a folder** on your computer, e.g. `Documents\crypto-argument-pilot`.
2. **Put three files in it:** `crypto_argument_pilot_core.xlsx`, `CLAUDE_CODE_BRIEF.md`, and this file.
3. **Get an API key.** Go to the Claude Console (console.anthropic.com), sign in, create an API key, and copy it somewhere safe. This is separate from your Claude subscription login. Expect the whole pilot to cost a few dollars at most; add $10 of credit if the account has none. Never paste the key into chat, email, or the GitHub repo — it goes only into a file called `.env` that Claude Code will create.

## Monday — setup (20–30 minutes, Windows)

**Python.** If `python --version` in a terminal doesn't print 3.10 or higher, install Python from python.org. On the installer's first screen, tick **"Add python.exe to PATH"** before clicking Install. Close and reopen the terminal afterward.

**Claude Code.** Open PowerShell (Start menu → type "PowerShell"). Your prompt will start with `PS C:\`. Paste:

```
irm https://claude.ai/install.ps1 | iex
```

It shows no progress while downloading; wait for it to finish. Then open a *new* PowerShell window and run `claude --version`. A version number means it worked. If it says `claude` isn't recognized, the install directory isn't on your PATH yet — tell me and I'll walk you through it, or see the troubleshooting link at the end.

Optional but recommended: install Git for Windows (git-scm.com/downloads/win) with default settings, so Claude Code can run commands and commit to a repo.

**Log in.** In PowerShell, `cd` into your folder and run `claude`. It opens a browser to log in. Use your Claude.ai subscription login (Claude Code needs Pro, Max, Team, Enterprise, or a Console account; the free plan doesn't include it). If it asks whether to use an `ANTHROPIC_API_KEY` from your environment, say no at this stage; the key belongs in `.env` for the scripts, not for Claude Code itself.

## Monday — kick off the build (5 minutes)

In the Claude Code session, paste this:

> Read CLAUDE_CODE_BRIEF.md in this folder and build exactly what it specifies. Create the repository layout, put the workbook in data/, write prompts/rubric.txt verbatim from section 5, then write scripts/rate.py and scripts/analyze.py. Create .env.example and ask me to paste my API key into a .env file myself. Start with the dry run and show me the formatted prompt before making any API calls.

Then go rate. Check back when it says the dry run is ready.

## Rating (about 75 minutes)

Open `crypto_argument_pilot_core.xlsx`. Read the Rubric tab once. Then on the Items tab, fill the four yellow columns for all 39 rows, 1–5, with a short note where something is worth remembering. Rules:

- **Strength is a 12(b)(6) question:** take the argument's premises as true and ask how far it goes. Whether the premises *are* true is Correctness.
- **Clarity is expression only.** A wrong argument can be a 5. Gibberish is a 1 regardless of polish.
- **Don't grade on a curve within a position.** Each argument on its own.
- **Edit any text that states the law or your view wrong.** Fix it in the cell. That's what makes it your dataset.
- **Do not open the Design tab** until all 39 are done.
- Save often. Keep the file name unchanged.

## Checkpoints with Claude Code (15 minutes total, spread out)

**1. The dry run.** It should print one complete prompt. Check two things: the prompt contains the position and the argument, and it contains *none of your ratings* (nothing from the `lev_` columns). If you see a number from your sheet in there, stop and tell it so.

**2. Your key.** It will ask you to create a `.env` file and paste `ANTHROPIC_API_KEY=sk-ant-...` into it. Do that yourself in Notepad. Don't paste the key into the chat.

**3. The limit-3 run.** Tell it to run `--limit 3`. Look at the three rows of output: four integers each and a one-sentence justification that actually refers to the argument. If the justifications are generic, say so.

**4. Full run.** Tell it to run the rest. It takes a couple of minutes. The output is `results/ratings_claude-opus-5-5.csv` with 39 rows.

**5. Analysis.** Once your ratings are complete and saved, tell it: "Run analyze.py against my completed workbook and show me the summary." Read `results/summary_claude-opus-5-5.md`. The three things to look at: the agreement table, the two "leak" checks, and the top divergences.

**6. Optional second model.** `--model claude-sonnet-5-5` gives a comparison column for the article. Not needed for the application.

## Things to write down as you go (for the application's Claude Code question)

Keep a short note in a text file. You will want:

- What you asked Claude Code to build, in one line.
- One thing it got wrong or you had to correct (there is always one).
- What you personally verified: the blindness of the prompt, the three sample rows, the row count.
- How long it took.

That is a true, specific answer to "describe your use case and workflow."

## If the setup fights you

Give it one hour. If Python or Claude Code won't install, fall back to the no-code version: open a fresh Claude chat, paste the rubric prompt from section 5 of the brief with one position and argument filled in, record the four numbers in the `claude_*` columns of the workbook by hand, and repeat. Slower, equally valid for the comparison, and still worth doing — but then the application's Claude Code answer has to describe your actual (lighter) experience, not this workflow.

## Publishing the repo (Tuesday, 15 minutes)

Once the summary exists and you've filled the README results block: in Claude Code, say "Initialize a git repository, make sure .env and results/raw are ignored, and commit." Then create an empty repository on github.com under your account (public or private), and tell Claude Code to push to it; it will ask you to authenticate with GitHub once. Check the repo page before you link it anywhere: no `.env`, no key, your README reads cleanly.

## Reference

- Claude Code setup and troubleshooting: https://code.claude.com/docs/en/setup
- Python SDK (what the script uses): https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python
