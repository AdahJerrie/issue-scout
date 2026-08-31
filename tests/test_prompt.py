from scout.prompt import build_prompt

CANDS = [
    {"id": 111, "title": "Add flag", "repo": "acme/tool", "url": "u1",
     "labels": ["good first issue", "go"], "comments": 2,
     "updated_at": "2026-11-05T10:00:00Z", "body": "Please add a flag."},
    {"id": 222, "title": "Fix typo", "repo": "acme/docs", "url": "u2",
     "labels": ["docs"], "comments": 0,
     "updated_at": "2026-11-06T10:00:00Z", "body": "Typo in README."},
]

def test_numbers_issues_from_one():
    p = build_prompt(CANDS)
    assert "ISSUE 1\n" in p and "ISSUE 2\n" in p and "ISSUE 3" not in p

def test_contains_issue_details_but_not_long_ids():
    p = build_prompt(CANDS)
    assert "acme/tool" in p and "good first issue, go" in p
    assert "111" not in p and "222" not in p

def test_json_example_braces_survive_formatting():
    p = build_prompt(CANDS)
    assert '{"results": [{"n": 1' in p

def test_empty_list_still_returns_instructions():
    assert "TASK" in build_prompt([])