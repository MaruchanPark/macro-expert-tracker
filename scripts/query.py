#!/usr/bin/env python3
"""Query the macro expert opinion tables (stdlib only).

Examples:
  python3 scripts/query.py last-run                 # last successful run
  python3 scripts/query.py run 3                    # all opinions from run 3
  python3 scripts/query.py expert "Luke Gromen"     # his opinions, newest first
  python3 scripts/query.py expert "Luke Gromen" --nth 2   # 2 before his latest (0 = latest)
  python3 scripts/query.py expert "Luke Gromen" --asset BTC
  python3 scripts/query.py asset UST --run 3        # one asset, one run
  python3 scripts/query.py scoreboard 3             # Bull/Bear/Neutral counts per asset for run 3
"""
import argparse, csv, os, sys
from collections import Counter, OrderedDict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

def load(name):
    with open(os.path.join(ROOT, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def items(rows):
    """Group per-asset rows back into items (one item = one link)."""
    out = OrderedDict()
    for r in rows:
        it = out.setdefault(r["link"], {**r, "stances": []})
        it["stances"].append(f'{r["asset"]} {r["stance"]}' + (" (stance change)" if r["stance_change"] == "Y" else ""))
    return list(out.values())

def show(rows):
    for it in items(rows):
        print(f'[run {it["run_no"]}] {it["published_date"]}  {it["expert"]}  — {it["title"]}')
        print(f'    {" / ".join(it["stances"])}')
        print(f'    {it["summary"]}')
        print(f'    {it["link"]}')
    if not rows:
        print("(no rows)")

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("last-run")
    r = sub.add_parser("run"); r.add_argument("n")
    e = sub.add_parser("expert"); e.add_argument("name"); e.add_argument("--nth", type=int); e.add_argument("--asset")
    a = sub.add_parser("asset"); a.add_argument("asset"); a.add_argument("--run")
    s = sub.add_parser("scoreboard"); s.add_argument("n")
    args = p.parse_args()
    ops = load("opinions.csv")

    if args.cmd == "last-run":
        ok = [x for x in load("runs.csv") if x["status"] == "success"]
        print(ok[-1] if ok else "(no successful run yet)")
    elif args.cmd == "run":
        show([x for x in ops if x["run_no"] == args.n])
    elif args.cmd == "expert":
        rows = [x for x in ops if x["expert"].lower() == args.name.lower()
                and (not args.asset or x["asset"].upper() == args.asset.upper())]
        its = sorted(items(rows), key=lambda x: x["published_date"], reverse=True)
        if args.nth is not None:
            its = its[args.nth:args.nth + 1]
        keep = {i["link"] for i in its}
        show(sorted([x for x in rows if x["link"] in keep], key=lambda x: x["published_date"], reverse=True))
    elif args.cmd == "asset":
        show([x for x in ops if x["asset"].upper() == args.asset.upper() and (not args.run or x["run_no"] == args.run)])
    elif args.cmd == "scoreboard":
        rows = [x for x in ops if x["run_no"] == args.n]
        for asset in ["BTC", "ETH", "NDX", "UST"]:
            c = Counter(x["stance"] for x in rows if x["asset"] == asset)
            ch = sorted({x["expert"] for x in rows if x["asset"] == asset and x["stance_change"] == "Y"})
            print(f'{asset}: Bull {c["Bull"]} / Bear {c["Bear"]} / Neutral {c["Neutral"]}'
                  + (f'  | stance change: {", ".join(ch)}' if ch else ""))
        roster = [x["expert"] for x in load("roster.csv")]
        seen = {x["expert"] for x in rows}
        print("No new opinion:", ", ".join(n for n in roster if n not in seen) or "-")

if __name__ == "__main__":
    sys.exit(main())
