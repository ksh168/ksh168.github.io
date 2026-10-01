"""
update-citations.py

Fetches citation counts from Google Scholar using the `scholarly` library
and updates src/data/data.json.
"""

import json
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

try:
    from scholarly import scholarly
except Exception as e:
    print(f"ERROR: Could not import 'scholarly': {e}")
    traceback.print_exc()
    sys.exit(1)

DATA_PATH = Path(__file__).resolve().parent.parent / "src" / "data" / "data.json"


def extract_author_and_citation_ids(publisher_url: str) -> tuple[str | None, str | None]:
    """
    Extracts author user ID and citation ID from a Google Scholar URL.
    """
    user_match = re.search(r"user=([^&]+)", publisher_url)
    cite_match = re.search(r"citation_for_view=([^&]+)", publisher_url)
    user_id = user_match.group(1) if user_match else None
    cite_id = cite_match.group(1) if cite_match else None
    return user_id, cite_id


def fetch_author_publications(author_id: str) -> dict[str, int]:
    """
    Fetches the author's publications map: citation_id -> num_citations.
    """
    pub_map = {}
    try:
        print(f"Fetching Google Scholar author profile for ID: {author_id}...")
        author = scholarly.search_author_id(author_id)
        author = scholarly.fill(author, sections=["publications"])
        for p in author.get("publications", []):
            pub_id = p.get("author_pub_id")
            num_citations = p.get("num_citations", 0)
            title = p.get("bib", {}).get("title", "Unknown")
            if pub_id:
                pub_map[pub_id] = num_citations
            print(f"  Scholar entry: {pub_id} | {title} | {num_citations} citations")
    except Exception as e:
        print(f"  Error fetching author profile: {e}")
        traceback.print_exc()
    return pub_map


def main():
    if not DATA_PATH.exists():
        print(f"Error: {DATA_PATH} not found.")
        sys.exit(1)

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    publications = data.get("publications", [])

    if not publications:
        print("No publications found in data.json.")
        return

    # Collect author IDs
    author_ids = set()
    for pub in publications:
        url = pub.get("publisherUrl", "")
        uid, _ = extract_author_and_citation_ids(url)
        if uid:
            author_ids.add(uid)

    all_pubs_map = {}
    for uid in author_ids:
        pubs = fetch_author_publications(uid)
        all_pubs_map.update(pubs)

    updated = 0
    now_iso = datetime.now(timezone.utc).isoformat()

    for pub in publications:
        title = pub.get("title", "Unknown")
        url = pub.get("publisherUrl", "")
        _, cite_id = extract_author_and_citation_ids(url)

        print(f"\nProcessing: {title}")
        print(f"  Citation ID: {cite_id}")

        if cite_id and cite_id in all_pubs_map:
            count = all_pubs_map[cite_id]
            pub["citations"] = count
            pub["lastUpdated"] = now_iso
            print(f"  ✅ Updated to {count} citations.")
            updated += 1
        else:
            print(f"  ⚠️  Could not find matching citation count — keeping existing value ({pub.get('citations', 'none')}).")

    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n✅ Done! Updated {updated}/{len(publications)} publications in data.json.")


if __name__ == "__main__":
    main()
