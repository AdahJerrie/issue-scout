from scout.email_builder import build_email, build_failure_email

PICK = {"title": "Add <b>flag</b> & more", "repo": "acme/tool",
        "url": "https://github.com/acme/tool/issues/7", "comments": 2,
        "updated_at": "2026-11-05T10:00:00Z", "fit_score": 8, "difficulty": "easy",
        "reason": "Small Go change.", "first_step": "Read cmd/list.go."}

def test_subject_counts_picks():
    assert build_email([PICK, PICK])["subject"].startswith("Issue Scout: your top 2")

def test_html_is_escaped():
    html = build_email([PICK])["html"]
    assert "<b>flag</b>" not in html and "&lt;b&gt;flag&lt;/b&gt; &amp; more" in html

def test_only_github_links_are_linked():
    bad = dict(PICK, url="https://evil.example/x")
    out = build_email([bad])
    assert "evil.example" not in out["html"] and "evil.example" not in out["text"]
    assert "https://github.com/acme/tool/issues/7" in build_email([PICK])["html"]

def test_disclaimer_present():
    assert "AI-generated" in build_email([PICK])["text"]

def test_failure_email_lists_errors():
    out = build_failure_email(["boom", "bang"])
    assert "boom" in out["text"] and out["subject"] == "Issue Scout: run failed"