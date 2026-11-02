
from scout.filter import filter_issues

CUTOFF = "2026-08-11"  # 90 days before 2026-11-09

def make(**over):
    base = {
        "id": 1, "title": "Add --json flag",
        "body": "Please add a --json flag to the list command so output can be piped. " * 2,
        "html_url": "https://github.com/acme/tool/issues/7",
        "repository_url": "https://api.github.com/repos/acme/tool",
        "comments": 1, "updated_at": "2026-11-05T10:00:00Z",
        "labels": [{"name": "good first issue"}],
        "assignee": None, "assignees": [],
    }
    base.update(over)
    return base

def test_keeps_a_good_issue():
    out = filter_issues([make()], CUTOFF)
    assert len(out) == 1
    assert out[0]["repo"] == "acme/tool"
    assert out[0]["labels"] == ["good first issue"]

def test_drops_pull_requests():
    assert filter_issues([make(pull_request={})], CUTOFF) == []

def test_drops_assigned():
    assert filter_issues([make(assignee={"login": "x"})], CUTOFF) == []

def test_drops_stale():
    assert filter_issues([make(updated_at="2026-01-01T00:00:00Z")], CUTOFF) == []

def test_handles_missing_body():
    assert filter_issues([make(body=None)], CUTOFF) == []

def test_drops_busy_threads():
    assert filter_issues([make(comments=25)], CUTOFF) == []

def test_dedupes_and_truncates():
    out = filter_issues([make(body="x" * 5000), make()], CUTOFF)
    assert len(out) == 1
    assert len(out[0]["body"]) <= 800