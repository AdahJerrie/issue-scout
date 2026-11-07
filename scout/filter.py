from datetime import datetime, timedelta

REPO_PREFIX = "https://api.github.com/repos/"


def _parse_time(value):
    """Turn GitHub's '2026-11-05T10:00:00Z' into a datetime."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _clean_body(text, max_chars):
    """Collapse all whitespace to single spaces, then cut to max_chars."""
    return " ".join(text.split())[:max_chars]


def filter_issues(items, now, max_age_days=90, min_body_chars=50,
                  max_comments=10, max_body_chars=800, max_candidates=15):
    """Keep only issues worth sending to the AI; return small clean dicts."""
    cutoff = now - timedelta(days=max_age_days)
    seen_ids = set()
    kept = []

    for item in items:
        # Rule 1: pull requests are not issues
        if "pull_request" in item:
            continue
        # Rule 2: already assigned
        if item.get("assignee") is not None or item.get("assignees"):
            continue
        # Rule 6: duplicates
        if item["id"] in seen_ids:
            continue
        # Rule 3: stale
        if _parse_time(item["updated_at"]) < cutoff:
            continue
        # Rule 4: missing or too-short body (body can be None!)
        body = _clean_body(item.get("body") or "", max_body_chars)
        if len(body) < min_body_chars:
            continue
        # Rule 5: busy thread
        if item.get("comments", 0) > max_comments:
            continue

        seen_ids.add(item["id"])
        kept.append({
            "id": item["id"],
            "title": item["title"],
            "repo": item["repository_url"].replace(REPO_PREFIX, ""),
            "url": item["html_url"],
            "labels": [label["name"] for label in item.get("labels", [])],
            "comments": item.get("comments", 0),
            "updated_at": item["updated_at"],
            "body": body,
        })

    return kept[:max_candidates]