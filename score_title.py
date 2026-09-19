#!/usr/bin/env python3
"""Heuristic scorer for Etsy-style digital listing titles."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

# Common filler that wastes title space for digital downloads
FILLER = {"the", "a", "an", "and", "or", "for", "with", "to", "of", "in"}


def score_title(title: str) -> dict:
    raw = title.strip()
    length = len(raw)
    words = re.findall(r"[A-Za-z0-9']+", raw)
    lower_words = [w.lower() for w in words]
    filler_count = sum(1 for w in lower_words if w in FILLER)

    score = 100
    notes: list[str] = []

    # Length band ~40–140 chars often workable; Etsy allows more — keep readable
    if length < 30:
        score -= 25
        notes.append("Too short — add primary keyword + format (PDF/Notion)")
    elif length > 140:
        score -= 20
        notes.append("Very long — front-load keywords; trim fluff")
    elif 40 <= length <= 120:
        notes.append("Length looks reasonable")
    else:
        score -= 5
        notes.append("Length OK but not ideal band (aim ~40–120)")

    if words and lower_words[0] in FILLER:
        score -= 15
        notes.append("Starts with filler — lead with keyword")

    if filler_count >= 4:
        score -= 10
        notes.append("Many filler words — tighten")

    if not re.search(r"(pdf|notion|template|printable|checklist|tracker|planner)", raw, re.I):
        score -= 15
        notes.append("Consider a format/type keyword (PDF, printable, template…)")

    if raw.isupper():
        score -= 20
        notes.append("ALL CAPS hurts readability")

    if "!" in raw or "???" in raw:
        score -= 5
        notes.append("Go easy on punctuation hype")

    # Keyword density: unique words ratio
    if words:
        uniqueness = len(set(lower_words)) / len(lower_words)
        if uniqueness < 0.6:
            score -= 10
            notes.append("Repeated words — reduce duplication")

    score = max(0, min(100, score))
    return {"title": raw, "length": length, "words": len(words), "score": score, "notes": notes}


def print_result(result: dict) -> None:
    print(f"\nTitle: {result['title']}")
    print(f"Score: {result['score']}/100  |  chars={result['length']}  words={result['words']}")
    for n in result["notes"]:
        print(f"  - {n}")


def main() -> None:
    p = argparse.ArgumentParser(description="Score Etsy-style titles")
    p.add_argument("title", nargs="?", help="Title string")
    p.add_argument("--file", type=Path, help="File with one title per line")
    args = p.parse_args()
    if args.file:
        for line in args.file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                print_result(score_title(line))
    elif args.title:
        print_result(score_title(args.title))
    else:
        raise SystemExit("Provide a title or --file")


if __name__ == "__main__":
    main()
