from scout.validate import validate_results

CANDS = [
    {"title": f"Issue {i}", "repo": "acme/tool", "url": f"https://github.com/acme/tool/issues/{i}",
     "comments": 1, "updated_at": f"2026-11-0{i}T10:00:00Z"} for i in range(1, 7)
]

def good(n, score=8, **over):
    r = {"n": n, "fit_score": score, "difficulty": "easy",
         "reason": "Small Go change.", "first_step": "Read the README."}
    r.update(over)
    return r

def run(results, top_n=5):
    return validate_results({"results": results}, CANDS, top_n)

def test_good_reply_is_sorted_and_limited():
    out = run([good(1, 5), good(2, 9), good(3, 7), good(4, 6), good(5, 8), good(6, 4)])
    assert out["ok"] and out["errors"] == []
    assert [p["fit_score"] for p in out["picks"]] == [9, 8, 7, 6, 5]
    assert out["picks"][0]["url"].endswith("/2")

def test_ties_prefer_recently_updated():
    out = run([good(1, 8), good(3, 8)])
    assert out["picks"][0]["title"] == "Issue 3"

def test_invented_issue_number_is_dropped():
    out = run([good(1), good(99)])
    assert len(out["picks"]) == 1 and len(out["errors"]) == 1

def test_bad_scores_are_dropped():
    out = run([good(1, 11), good(2, 0), good(3, "8"), good(4, True), good(5, 7.5), good(6, 7)])
    assert [p["title"] for p in out["picks"]] == ["Issue 6"]

def test_bad_difficulty_dropped():
    assert run([good(1, difficulty="impossible")])["ok"] is False

def test_duplicate_numbers_keep_first():
    out = run([good(1, 5), good(1, 9)])
    assert len(out["picks"]) == 1 and out["picks"][0]["fit_score"] == 5

def test_links_in_ai_text_are_rejected():
    out = run([good(1, reason="Visit http://evil.example now"), good(2)])
    assert [p["title"] for p in out["picks"]] == ["Issue 2"]

def test_missing_results_key_fails():
    assert validate_results({"answer": []}, CANDS)["ok"] is False

def test_non_dict_reply_fails():
    assert validate_results("sorry, I cannot help", CANDS)["ok"] is False
    assert validate_results(None, CANDS)["ok"] is False

def test_all_invalid_fails():
    out = run([good(50), "junk"])
    assert out["ok"] is False and out["picks"] == []