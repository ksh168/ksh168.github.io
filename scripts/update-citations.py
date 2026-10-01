"""
update-citations.py

Fetches citation counts from Google Scholar using the `scholarly` library
and updates src/data/data.json.

Includes a strict multiprocessing timeout to prevent hangs when executed
in environments where Google Scholar blocks datacenter IPs (like GitHub Actions).
"""

import json
import multiprocessing
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHOLAR_TIMEOUT_SECONDS = 25
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


def _fetch_scholar_worker(author_id: str, return_dict):
    """
    Worker function executed in a separate process to enforce a strict timeout.
    """
    try:
        from scholarly import scholarly

        print(f"Connecting to Google Scholar for author ID: {author_id}...")
        author = scholarly.search_author_id(author_id)
        author = scholarly.fill(author, sections=["publications"])
        for p in author.get("publications", []):
            pub_id = p.get("author_pub_id")
            num_citations = p.get("num_citations", 0)
            title = p.get("bib", {}).get("title", "Unknown")
            if pub_id:
                return_dict[pub_id] = num_citations
            print(f"  Scholar found: {pub_id} | {title} | {num_citations} citations")
    except Exception as e:
        print(f"  Error in scholarly worker: {e}")


def fetch_scholar_publications_with_timeout(author_id: str) -> dict[str, int]:
    """
    Spawns a child process with a hard timeout to fetch Scholar citations.
    Terminates cleanly if Google Scholar blocks or throttles the connection.
    """
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    p = multiprocessing.Process(
        target=_fetch_scholar_worker, args=(author_id, return_dict)
    )
    p.start()
    p.join(timeout=SCHOLAR_TIMEOUT_SECONDS)

    if p.is_alive():
        print(
            f"  ⚠️ Google Scholar timed out after {SCHOLAR_TIMEOUT_SECONDS}s "
            "(likely blocked by Google bot detection/CAPTCHA on datacenter IP)."
        )
        p.terminate()
        p.join(timeout=2)
        if p.is_alive():
            p.kill()
        print("  Worker process safely terminated.")
        return {}

    return dict(return_dict)


def main():
    if not DATA_PATH.exists():
        print(f"Error: {DATA_PATH} not found.")
        sys.exit(1)

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    publications = data.get("publications", [])

    if not publications:
        print("No publications found in data.json.")
        return

    # Collect author IDs from URLs
    author_ids = set()
    for pub in publications:
        url = pub.get("publisherUrl", "")
        uid, _ = extract_author_and_citation_ids(url)
        if uid:
            author_ids.add(uid)

    all_pubs_map = {}
    for uid in author_ids:
        pubs = fetch_scholar_publications_with_timeout(uid)
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
            print(
                f"  ℹ️ Keeping current citation value: {pub.get('citations', 'none')}"
            )

    DATA_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"\n✅ Completed citation update check ({updated}/{len(publications)} refreshed)."
    )


if __name__ == "__main__":
    main()
