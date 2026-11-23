
# Macro expert opinion tracker

Results accumulate in the GitHub repo `MaruchanPark/macro-expert-tracker` (branch `main`).
The owner has authorized committing tracker results directly to `main`.

## Target assets
Bitcoin (BTC), Ethereum (ETH), Nasdaq / US stocks (NDX), US Treasuries (UST)

## Repo layout
- `data/roster.csv`: experts, expected stance per asset (Bull / Bear / Mixed / -), where to look
- `data/runs.csv`: `run_no,run_date,period_start,period_end,status,items,notes` (append-only)
- `data/opinions.csv`: `run_no,expert,published_date,asset,stance,stance_change,title,summary,link` (append-only; one row per asset per item)
- `reports/run-NNN.md`: readable report per run
- `scripts/query.py`: queries (`run N`, `scoreboard N`, `expert "Name" [--nth K] [--asset A]`, `asset A [--run N]`, `last-run`)

## Weekly run procedure
1. Clone or pull the repo and check out `main`.
2. Read `data/runs.csv`. New `run_no` = last `run_no` + 1. `period_start` = `period_end` of the last row with `status=success` (if none: now minus 7 days). `period_end` = now (UTC, ISO 8601).
3. Read `data/roster.csv` for the expert list and expected stances. Read the set of `link` values already in `data/opinions.csv` (dedupe key).
4. For each expert, search the web for columns, interviews, podcasts, X posts, newsletters in the period (use the roster's where_to_look; also news coverage such as Bloomberg, FT, CNBC, Stocktwits, Benzinga, Project Syndicate, Substack). Searching several experts per query, and adding the month and year, helps surface dated items.
5. Keep only items whose publication date falls inside the period and that state a view on a target asset. Open every source to confirm date and content; never record a link you did not open. Skip links already in `opinions.csv`.
6. For each item: stance per asset (Bull / Bear / Neutral) only where the source supports it; summary in Korean, at most 5 lines, covering the core claim, reasoning and key numbers; distinguish the expert's words from the article's framing. `stance_change=Y` when the stance differs from the roster's expected stance for that asset (treat roster `Mixed` as matching `Neutral`; roster `-` means no change flag), otherwise `N`.
7. Append rows to `data/opinions.csv` with Python's `csv` module (proper quoting), append the run row to `data/runs.csv` (`status=success`, `items` = number of distinct links added, short notes), and write `reports/run-NNN.md` (three-digit number) with per-expert entries, an asset scoreboard (Bull/Bear/Neutral counts, stance changes), experts with no new opinion, and notable items just outside the period. `python3 scripts/query.py scoreboard N` produces the scoreboard numbers.
8. If the run fails partway, do not append partial opinions; append a run row with `status=failed` and the reason so the next run reuses the same `period_start`.
9. Commit (`Run N: <period_start date> to <period_end date>`) and push to `main`. If the push is rejected, pull and retry.
10. Reply in Korean with: run number and period, item count, the scoreboard, stance changes, and a link to the report on GitHub.

## Ad-hoc requests
- "N회차 의견": `python3 scripts/query.py run N` (or read `reports/run-NNN.md`).
- "Gromen의 최신에서 2번째 전 의견": `python3 scripts/query.py expert "Luke Gromen" --nth 2` (0 = latest, sorted by published_date).
- A request for a different period or subset of experts that is not the weekly run: follow steps 4 to 6 and answer in chat; only write to the repo when asked.

## Output format (Korean)
Per expert:
- **Name** — date, [title](link)
  - 스탠스: BTC Bull / UST Bear ... (⚠️ 스탠스 변화 where flagged)
  - 요약 (<=5 lines)

Then the asset scoreboard and the list of experts with no new opinion.
