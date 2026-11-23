#!/usr/bin/env python3
"""Long-form content catalog (data/catalog.csv), stdlib only.

Tiers: 3 = books, papers, research reports; 2 = long-form pieces (5+ min read).
Short items (tier 1, under 5 min) are never added.

  python3 scripts/catalog.py list                          # all, per expert, newest first
  python3 scripts/catalog.py list --expert "Lyn Alden" --unread
  python3 scripts/catalog.py list --tier 3                 # books/papers only
  python3 scripts/catalog.py add new_rows.csv              # append rows (same columns), deduped
  python3 scripts/catalog.py mark-read "Broken Money"      # set read=Y on rows whose title or link contains the text
  python3 scripts/catalog.py stats
"""
import argparse, csv, os, re, sys
from collections import Counter
from itertools import groupby

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "catalog.csv")
COLS = ["expert", "tier", "title", "published_date", "outlet", "read", "link"]
# Pages shared by several items (a books index page etc.) are not a dedupe key.
SHARED_LINK = re.compile(r"/books/?$|/book/?$|/archives?/?$")

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

def load():
    with open(PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def save(rows):
    rows = sorted(rows, key=lambda r: r["expert"])
    out = []
    for _, g in groupby(rows, key=lambda r: r["expert"]):
        out += sorted(g, key=lambda r: r["published_date"], reverse=True)
    with open(PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(out)

def is_dup(row, rows):
    for r in rows:
        if r["expert"] == row["expert"] and norm(r["title"]) == norm(row["title"]):
            return True
        if row["link"] and r["link"] == row["link"] and not SHARED_LINK.search(row["link"]):
            return True
    return False

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list"); l.add_argument("--expert"); l.add_argument("--tier"); l.add_argument("--unread", action="store_true")
    a = sub.add_parser("add"); a.add_argument("csvfile")
    m = sub.add_parser("mark-read"); m.add_argument("text")
    sub.add_parser("stats")
    args = p.parse_args()
    rows = load()

    if args.cmd == "list":
        for r in rows:
            if args.expert and r["expert"].lower() != args.expert.lower(): continue
            if args.tier and r["tier"] != args.tier: continue
            if args.unread and r["read"] == "Y": continue
            print(f'{r["published_date"]:<10}  T{r["tier"]}  {"✓" if r["read"] == "Y" else " "}  {r["expert"]} — {r["title"]} ({r["outlet"]})  {r["link"]}')
    elif args.cmd == "add":
        with open(args.csvfile, newline="", encoding="utf-8") as f:
            new = list(csv.DictReader(f))
        added = 0
        for n in new:
            n = {c: (n.get(c) or "").strip() for c in COLS}
            n["read"] = n["read"] or "N"
            if n["tier"] not in ("2", "3"):
                print(f'skip (tier {n["tier"]!r} not 2/3): {n["title"]}'); continue
            if is_dup(n, rows):
                print(f'skip (duplicate): {n["expert"]} — {n["title"]}'); continue
            rows.append(n); added += 1
        save(rows)
        print(f"added {added}")
    elif args.cmd == "mark-read":
        t = args.text.lower(); hit = 0
        for r in rows:
            if t in r["title"].lower() or (r["link"] and t in r["link"].lower()):
                r["read"] = "Y"; hit += 1; print(f'read: {r["expert"]} — {r["title"]}')
        save(rows)
        print(f"marked {hit}")
    elif args.cmd == "stats":
        c = Counter((r["expert"], r["tier"]) for r in rows)
        for e in sorted({r["expert"] for r in rows}):
            unread = sum(1 for r in rows if r["expert"] == e and r["read"] != "Y")
            print(f'{e:<20} T3 {c[(e, "3")]:>3}  T2 {c[(e, "2")]:>3}  unread {unread:>3}')

if __name__ == "__main__":
    main()
