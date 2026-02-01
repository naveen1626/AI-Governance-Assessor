"""
Script: fetch_ai4eda_abstracts.py

Usage:
  1) git clone https://github.com/Thinklab-SJTU/awesome-ai4eda.git
  2) cd awesome-ai4eda
  3) Place this script at repo root (same level as data/*.bib)
  4) python fetch_ai4eda_abstracts.py
  5) Output: ai4eda_abstracts.csv
"""

import os
import csv
import re
from pathlib import Path

try:
    import bibtexparser
except ImportError:
    raise SystemExit("pip install bibtexparser")

RE_TRAILING_COMMA = re.compile(r',\s*}$')

def load_bib_entries(bib_path: Path):
    """Load entries from a .bib file, doing light cleanup if needed."""
    text = bib_path.read_text(encoding="utf-8")

    # Very mild cleanup for some malformed abstract/URL endings (defensive).
    text = RE_TRAILING_COMMA.sub('}', text)

    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
    db = bibtexparser.loads(text, parser=parser)
    return db.entries

def main():
    repo_root = Path(__file__).resolve().parent
    data_dir = repo_root / "data"

    if not data_dir.is_dir():
        raise SystemExit("Could not find data/ directory. "
                         "Run this from the awesome-ai4eda repo root.")

    out_csv = repo_root / "ai4eda_abstracts.csv"

    rows = []
    for bib_path in sorted(data_dir.glob("*.bib")):
        print(f"Parsing {bib_path}...")
        entries = load_bib_entries(bib_path)

        for e in entries:
            title = e.get("title", "").strip()
            authors = e.get("author", "").strip()
            year = e.get("year", "").strip()
            venue = e.get("venue", "").strip()
            url = e.get("url", "").strip()
            abstract = e.get("abstract", "").strip()

            # Normalize whitespace a bit
            title = " ".join(title.split())
            authors = " ".join(authors.split())
            venue = " ".join(venue.split())
            abstract = " ".join(abstract.split())

            rows.append({
                "key": e.get("ID", ""),
                "title": title,
                "authors": authors,
                "year": year,
                "venue": venue,
                "url": url,
                "abstract": abstract,
                "source_bib": bib_path.name,
            })

    # Write CSV
    fieldnames = [
        "key", "title", "authors", "year",
        "venue", "url", "abstract", "source_bib"
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} entries to {out_csv}")

if __name__ == "__main__":
    main()
