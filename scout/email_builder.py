GITHUB_PREFIX = "https://github.com/"
DISCLAIMER = ("Scores and suggestions are AI-generated. Always open the issue and check it is "
              "still available before you start.")


def _esc(text):
    """Make text safe to place inside HTML (no html module allowed in n8n)."""
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def build_email(picks):
    """Turn validated picks into {'subject', 'html', 'text'}."""
    subject = "Issue Scout: your top " + str(len(picks)) + " open-source issues"
    html = ["<h2>Issue Scout: today's picks</h2>"]
    text = ["Issue Scout: today's picks", ""]

    for rank, p in enumerate(picks, start=1):
        # links must be real GitHub links coming from GitHub data
        link = p["url"] if str(p["url"]).startswith(GITHUB_PREFIX) else ""
        title = _esc(p["title"])
        heading = '<a href="' + _esc(link) + '">' + title + "</a>" if link else title
        html.append(
            "<p><b>" + str(rank) + ". " + heading + "</b><br>"
            + _esc(p["repo"]) + " &middot; fit " + str(p["fit_score"]) + "/10 &middot; "
            + _esc(p["difficulty"]) + " &middot; " + str(p["comments"]) + " comments<br>"
            + "<i>Why:</i> " + _esc(p["reason"]) + "<br>"
            + "<i>First step:</i> " + _esc(p["first_step"]) + "</p>"
        )
        text.append(str(rank) + ". " + p["title"] + " (" + p["repo"] + ")")
        text.append("   fit " + str(p["fit_score"]) + "/10, " + p["difficulty"] + ", "
                    + str(p["comments"]) + " comments")
        text.append("   Why: " + p["reason"])
        text.append("   First step: " + p["first_step"])
        if link:
            text.append("   " + link)
        text.append("")

    html.append("<p><small>" + _esc(DISCLAIMER) + "</small></p>")
    text.append(DISCLAIMER)
    return {"subject": subject, "html": "\n".join(html), "text": "\n".join(text)}


def build_failure_email(errors):
    """Short alert for when the AI reply could not be used."""
    lines = ["Issue Scout could not produce picks this run.", ""]
    for e in errors[:10]:
        lines.append("- " + str(e))
    lines.append("")
    lines.append("Open the workflow's Executions tab in n8n to see the details.")
    return {"subject": "Issue Scout: run failed", "html": _esc("\n".join(lines)).replace("\n", "<br>"),
            "text": "\n".join(lines)}