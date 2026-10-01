"""
update-citations.py

Fetches citation counts from Google Scholar using the `scholarly` library
and updates src/data/data.json.

scholarly docs: https://scholarly.readthedocs.io/en/stable/
"""

import json
import re
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from scholarly import scholarly, ProxyGenerator
except ImportError:
    print("ERROR: 'scholarly' is not installed. Run: pip install scholarly")
    sys.exit(1)


DATA_PATH = Path(__file__).parent.parent / "src" / "data" / "data.json"
DELAY_BETWEEN_REQUESTS = 15  # seconds — be polite to avoid rate limits


def extract_citation_id(publisher_url: str) -> str | None:
    """
    Extracts the paper-level citation ID from a Google Scholar URL.

    Example URL:
      https://scholar.google.com/citations?view_op=view_citation&user=iGdBvvwAAAAJ&citation_for_view=iGdBvvwAAAAJ:u5HHmVD_uO8C
    Returns:
      "iGdBvvwAAAAJ:u5HHmVD_uO8C"
    """
    match = re.search(r"citation_for_view=([^&]+)", publisher_url)
    return match.group(1) if match else None


def fetch_citation_count(citation_id: str) -> int | None:
    """
    Uses scholarly to look up a paper by its Google Scholar citation_for_view ID
    and returns its citation count.
    """
    try:
        # scholarly.search_pubs_custom_url lets us query a specific citation page
        url = f"/citations?view_op=view_citation&citation_for_view={citation_id}"
        pub = scholarly.search_pubs_custom_url(url)
        paper = next(pub)
        bib = paper.get("bib", {})
        cited_by = paper.get("num_citations", None)
        title = bib.get("title", "Unknown")
        print(f"  Title from Scholar: {title}")
        print(f"  Citation count:     {cited_by}")
        return cited_by
    except StopIteration:
        print("  No results returned from scholarly.")
        return None
    except Exception as e:
        print(f"  Error fetching from scholarly: {e}")
        return None


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    publications = data.get("publications", [])

    if not publications:
        print("No publications found in data.json.")
        return

    updated = 0

    for pub in publications:
        title = pub.get("title", "Unknown")
        publisher_url = pub.get("publisherUrl", "")
        print(f"\nProcessing: {title}")

        citation_id = extract_citation_id(publisher_url)
        if not citation_id:
            print(f"  ⚠️  Could not extract citation_for_view ID from publisherUrl — skipping.")
            continue

        print(f"  Citation ID: {citation_id}")
        count = fetch_citation_count(citation_id)

        if count is not None:
            pub["citations"] = count
            pub["lastUpdated"] = datetime.now(timezone.utc).isoformat()
            print(f"  ✅ Updated to {count} citations.")
            updated += 1
        else:
            print(f"  ⚠️  Keeping existing value ({pub.get('citations', 'none')}).")

        if pub is not publications[-1]:
            print(f"  Waiting {DELAY_BETWEEN_REQUESTS}s before next request...")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Done! Updated {updated}/{len(publications)} publications.")


if __name__ == "__main__":
    main()
