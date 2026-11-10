DIFFICULTIES = ("easy", "medium", "hard")
MAX_TEXT = 300


def _is_whole_number(value):
    """True for 7 or 7.0, but not True/False or strings like '7'."""
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float)) and value == int(value)


def _clean_text(value):
    """Return trimmed text, or '' if it is missing, not text, or contains a link."""
    if not isinstance(value, str):
        return ""
    text = " ".join(value.split())[:MAX_TEXT]
    if "http" in text.lower():  # links may only come from GitHub data, never from the AI
        return ""
    return text


def validate_results(ai, candidates, top_n=5):
    """Check the AI's reply against the candidates and pick the best issues.

    Returns {"ok": bool, "errors": [str], "picks": [dict]}.
    """
    errors = []

    if not isinstance(ai, dict) or not isinstance(ai.get("results"), list):
        return {"ok": False, "errors": ["AI reply is not an object with a 'results' list"], "picks": []}

    valid = []
    seen = set()

    for index, result in enumerate(ai["results"]):
        label = "result " + str(index + 1)
        if not isinstance(result, dict):
            errors.append(label + ": not an object")
            continue

        n = result.get("n")
        if not _is_whole_number(n) or not 1 <= int(n) <= len(candidates):
            errors.append(label + ": 'n' is not a real issue number")
            continue
        n = int(n)
        if n in seen:
            errors.append(label + ": duplicate issue " + str(n))
            continue

        score = result.get("fit_score")
        if not _is_whole_number(score) or not 1 <= int(score) <= 10:
            errors.append(label + ": fit_score must be a whole number from 1 to 10")
            continue

        difficulty = result.get("difficulty")
        if difficulty not in DIFFICULTIES:
            errors.append(label + ": difficulty must be easy, medium or hard")
            continue

        reason = _clean_text(result.get("reason"))
        first_step = _clean_text(result.get("first_step"))
        if not reason or not first_step:
            errors.append(label + ": reason/first_step missing, not text, or contains a link")
            continue

        seen.add(n)
        candidate = candidates[n - 1]
        valid.append({
            "title": candidate["title"],
            "repo": candidate["repo"],
            "url": candidate["url"],
            "comments": candidate["comments"],
            "updated_at": candidate["updated_at"],
            "fit_score": int(score),
            "difficulty": difficulty,
            "reason": reason,
            "first_step": first_step,
        })

    if not valid:
        errors.append("no valid results in the AI reply")
        return {"ok": False, "errors": errors, "picks": []}

    # best score first; ties broken by most recently updated
    valid.sort(key=lambda r: (r["fit_score"], r["updated_at"]), reverse=True)
    return {"ok": True, "errors": errors, "picks": valid[:top_n]}