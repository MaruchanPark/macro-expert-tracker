
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
- `data/catalog.csv`: long-form reading catalog `expert,tier,title,published_date,outlet,read,link` (tier 3 = books/papers/research reports, tier 2 = long-form 5+ min read; tier 1 short items are never added; `read` defaults to `N`)
- `scripts/catalog.py`: catalog tool (`list [--expert] [--tier] [--unread]`, `add rows.csv` with dedupe, `mark-read "text"`, `stats`)
- `briefs/YYYY-MM/YYYY-MM-DD.md`: daily bull/bear outlook brief (BTC, ETH, Nasdaq, US dollar hegemony + US macro snapshot)
- `data/briefs.csv`: `date,btc,eth,ndx,usd,headline,file` (append-only; one row per day; mood values `Bull` / `Bear` / `Mixed`)

## Weekly run procedure
1. Clone or pull the repo and check out `main`.
2. Read `data/runs.csv`. New `run_no` = last `run_no` + 1. `period_start` = `period_end` of the last row with `status=success` (if none: now minus 7 days). `period_end` = now (UTC, ISO 8601).
3. Read `data/roster.csv` for the expert list and expected stances. Read the set of `link` values already in `data/opinions.csv` (dedupe key).
4. For each expert, search the web for columns, interviews, podcasts, X posts, newsletters in the period (use the roster's where_to_look; also news coverage such as Bloomberg, FT, CNBC, Stocktwits, Benzinga, Project Syndicate, Substack). Searching several experts per query, and adding the month and year, helps surface dated items.
5. Keep only items whose publication date falls inside the period and that state a view on a target asset. Open every source to confirm date and content; never record a link you did not open. Skip links already in `opinions.csv`.
6. For each item: stance per asset (Bull / Bear / Neutral) only where the source supports it; summary in Korean, at most 5 lines, covering the core claim, reasoning and key numbers; distinguish the expert's words from the article's framing. `stance_change=Y` when the stance differs from the roster's expected stance for that asset (treat roster `Mixed` as matching `Neutral`; roster `-` means no change flag), otherwise `N`.
7. Append rows to `data/opinions.csv` with Python's `csv` module (proper quoting), append the run row to `data/runs.csv` (`status=success`, `items` = number of distinct links added, short notes), and write `reports/run-NNN.md` (three-digit number) with per-expert entries, an asset scoreboard (Bull/Bear/Neutral counts, stance changes), experts with no new opinion, and notable items just outside the period. `python3 scripts/query.py scoreboard N` produces the scoreboard numbers.
7a. Catalog: for every item collected in this run that is tier 2 (a long-form piece of roughly 1,000+ words / 5+ minutes of reading: essay, newsletter issue, research letter, long op-ed) or tier 3 (book, paper, research report), also add it to `data/catalog.csv`. Write the rows to a temp CSV with the catalog columns and run `python3 scripts/catalog.py add <file>`; it skips tier 1 and duplicates (same expert + same title, or same item link). Short items (X posts, quotes in news articles, short interviews, clips) stay out of the catalog. Also add any tier 2/3 item by a tracked expert that you came across during the run even if it states no view on a target asset. Mention the number of catalog rows added in the run notes and the reply.
8. If the run fails partway, do not append partial opinions; append a run row with `status=failed` and the reason so the next run reuses the same `period_start`.
9. Commit (`Run N: <period_start date> to <period_end date>`) and push to `main`. If the push is rejected, pull and retry.
10. Reply in Korean with: run number and period, item count, the scoreboard, stance changes, and a link to the report on GitHub.

## Monthly catalog update procedure
Runs on the 1st of each month (scheduled task, morning KST). It catches long-form items the weekly run missed.
1. Clone or pull the repo and check out `main`.
2. Window: from the 1st of the previous month (UTC) to now. Read `data/catalog.csv` for existing rows (dedupe) and `data/roster.csv` for the experts.
3. For each expert, check their long-form sources for new tier 2/3 items published in the window: books (new or announced releases), papers / working papers (NBER, SSRN, journals, central-bank or IMF series), research reports, and long-form pieces (5+ min read). Known sources: Hussman market comments (hussmanfunds.com/category/comment/), Hoisington quarterly reviews (hoisington.com/economic_overview.html), lynalden.com and her newsletter archive, GMO research library (Grantham), TIME / economicprinciples.org / LinkedIn long essays (Dalio), Capital Wars Substack (Howell; posts are mostly paid, keep only essays, not weekly data updates), ARK research and Big Ideas (Wood), Rogoff's Harvard page / NBER, yardeni.com books, Ex Uno Plures (Pozsar), Project Syndicate / Foreign Affairs long essays, plus web search per expert with the month and year.
4. Open every item to confirm date, author and length; never add a link you did not open. Tier 3 = book / paper / research report; tier 2 = 5+ min read; skip anything shorter.
5. Write new rows to a temp CSV (`expert,tier,title,published_date,outlet,read,link`, `read=N`, date as YYYY-MM-DD or as precise as known) and run `python3 scripts/catalog.py add <file>`.
6. Commit (`Catalog update: YYYY-MM`) and push to `main`; if nothing new, commit nothing. If the push is rejected, pull and retry.
7. Reply in Korean: number of rows added per expert, the new tier 3 items by name, and a link to `data/catalog.csv` on GitHub. Note any source that could not be reached.

## Daily outlook brief procedure
Runs every day in the morning KST (scheduled task). Independent of the weekly expert run.
1. Clone or pull the repo and check out `main`. Date = today's date in KST (YYYY-MM-DD). If `data/briefs.csv` already has a row for that date, stop without writing.
2. Research the last 24-48 hours (since Friday on Mondays) with web search, following the `daily-macro-outlook` skill when it is available: US macro snapshot (CPI/PCE, Fed decision and next FOMC with market odds, 2y/10y yields, latest jobs report, S&P 500 earnings and big-tech results, dollar index, key events this week), then for BTC, ETH, Nasdaq and dollar hegemony: price/24h move, 2-3 bull points, 2-3 bear points, today's key issue; then a synthesis with each asset's mood (Bull / Bear / Mixed) and the cross-asset link. Every figure from a source opened in this run, with its link; never from memory.
3. Write the brief in Korean to `briefs/YYYY-MM/YYYY-MM-DD.md` with a `## 출처` link list at the end and the line `투자 조언이 아닙니다.`
4. Append one row to `data/briefs.csv` with Python's `csv` module: date, mood per asset (`Bull`/`Bear`/`Mixed`), a one-line Korean headline, the file path.
5. Commit (`Daily brief: YYYY-MM-DD`) and push to `main`. If the push is rejected, pull and retry.
6. Reply in Korean with the full brief and the GitHub link to the file.

## Ad-hoc requests
- "안 읽은 책/논문": `python3 scripts/catalog.py list --tier 3 --unread` (add `--expert "Name"` to filter). "읽음 처리": `python3 scripts/catalog.py mark-read "title text"`, then commit and push.
- "N회차 의견": `python3 scripts/query.py run N` (or read `reports/run-NNN.md`).
- "Gromen의 최신에서 2번째 전 의견": `python3 scripts/query.py expert "Luke Gromen" --nth 2` (0 = latest, sorted by published_date).
- "N일 브리프" / "이번 주 분위기 변화": read `briefs/YYYY-MM/YYYY-MM-DD.md` or `data/briefs.csv`.
- A request for a different period or subset of experts that is not the weekly run: follow steps 4 to 6 and answer in chat; only write to the repo when asked.

## Output format (Korean)
Per expert:
- **Name** — date, [title](link)
  - 스탠스: BTC Bull / UST Bear ... (⚠️ 스탠스 변화 where flagged)
  - 요약 (<=5 lines)

Then the asset scoreboard and the list of experts with no new opinion.
