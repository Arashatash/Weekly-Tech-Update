"""Multi-angle quality audit for weekly AI strategy briefings."""

from __future__ import annotations

from src.analyser import (
    ALLOWED_SOURCES,
    MIN_CATEGORY_ITEMS,
    OPPORTUNITY_CATEGORY_IDS,
    PH_MAX_PICKS,
    PH_MIN_PICKS,
    PH_REQUIRED_CATEGORIES,
    PH_SOURCE,
    REQUIRED_CATEGORY_IDS,
    VALID_HORIZONS,
    VALID_SIGNALS,
    VALID_STANCES,
    VALID_URGENCY,
    _has_thesis_tie,
    collect_ph_items,
)

AI_BLOCKLIST = (
    "spacex",
    "wordpress",
    "woocommerce",
    "shopify theme",
    "crypto casino",
    "sports betting",
    "dating app",
    "nft marketplace",
    "fantasy sports",
    "recipe sharing",
    "weather widget",
    "fitness tracker",
    "food delivery app",
    "real estate listing",
    "social media scheduler",
)

THIN_SUMMARY_CHARS = 40


def _issue(level: str, check: str, message: str) -> dict:
    return {"level": level, "check": check, "message": message}


def _is_https_url(url: object) -> bool:
    return isinstance(url, str) and url.strip().startswith("https://")


def audit_briefing(briefing: dict) -> dict:
    """
    Run multi-angle checks on a briefing dict.

    Returns:
        {
            "passed": bool,
            "issues": [{"level": "critical"|"warning", "check": str, "message": str}, ...],
            "scores": {"url_integrity": float, ...},
        }
    """
    issues: list[dict] = []
    leader_count = 0

    # --- Schema completeness ---
    for key in (
        "weekly_theme",
        "theme_context",
        "categories",
        "leader_voices",
        "top_signals",
        "commentary_synthesis",
        "follow_the_money",
    ):
        if key not in briefing:
            issues.append(
                _issue("critical", "schema", f"Missing required top-level key: {key}")
            )

    categories = briefing.get("categories", [])
    if not isinstance(categories, list) or len(categories) != 5:
        issues.append(
            _issue(
                "critical",
                "schema",
                f"Expected exactly 5 categories, got "
                f"{len(categories) if isinstance(categories, list) else 'invalid'}",
            )
        )
    else:
        found_ids = {c.get("id") for c in categories if isinstance(c, dict)}
        missing = set(REQUIRED_CATEGORY_IDS) - found_ids
        if missing:
            issues.append(
                _issue("critical", "schema", f"Missing category ids: {sorted(missing)}")
            )

    leader_voices = briefing.get("leader_voices", [])
    if not isinstance(leader_voices, list):
        issues.append(
            _issue("critical", "schema", "leader_voices must be a list")
        )
    else:
        leader_count = len(leader_voices)
        if leader_count < 3:
            issues.append(
                _issue(
                    "critical",
                    "schema",
                    f"Expected at least 3 leader_voices, got {leader_count}",
                )
            )

    top_signals = briefing.get("top_signals", [])
    if not isinstance(top_signals, list) or not (3 <= len(top_signals) <= 5):
        issues.append(
            _issue(
                "critical",
                "schema",
                f"Expected 3-5 top_signals, got "
                f"{len(top_signals) if isinstance(top_signals, list) else 'invalid'}",
            )
        )

    commentary = briefing.get("commentary_synthesis")
    if isinstance(commentary, dict):
        if not str(commentary.get("grounded_view", "")).strip():
            issues.append(_issue("critical", "schema", "commentary_synthesis missing grounded_view"))
        if not isinstance(commentary.get("comparison_table"), list):
            issues.append(_issue("critical", "schema", "commentary_synthesis missing comparison_table list"))

    ftm = briefing.get("follow_the_money")
    if isinstance(ftm, list):
        if len(ftm) < 4:
            issues.append(
                _issue("critical", "schema", f"Expected at least 4 follow_the_money entries, got {len(ftm)}")
            )

    # --- Category item count ---
    category_item_count = 0
    if isinstance(categories, list):
        for cat in categories:
            if isinstance(cat, dict):
                category_item_count += len(cat.get("items", []))
    if category_item_count < MIN_CATEGORY_ITEMS:
        issues.append(
            _issue(
                "critical",
                "schema",
                f"Expected at least {MIN_CATEGORY_ITEMS} category items, got {category_item_count}",
            )
        )

    # --- URL integrity ---
    url_total = 0
    url_ok = 0

    if isinstance(categories, list):
        for cat in categories:
            if not isinstance(cat, dict):
                continue
            cat_id = cat.get("id", "?")
            for item in cat.get("items", []):
                if not isinstance(item, dict):
                    continue
                url_total += 1
                title = item.get("title", "(untitled)")
                url = item.get("url", "")
                if _is_https_url(url):
                    url_ok += 1
                else:
                    issues.append(
                        _issue(
                            "critical",
                            "url_integrity",
                            f"Category {cat_id} item '{title}' missing valid https URL",
                        )
                    )

    if isinstance(leader_voices, list):
        for lv in leader_voices:
            if not isinstance(lv, dict):
                continue
            name = lv.get("name", "(unknown)")
            url_total += 1
            if _is_https_url(lv.get("url", "")):
                url_ok += 1
            else:
                issues.append(
                    _issue(
                        "critical",
                        "url_integrity",
                        f"Leader voice '{name}' missing valid https URL",
                    )
                )

    if isinstance(top_signals, list):
        for sig in top_signals:
            if not isinstance(sig, dict):
                continue
            headline = sig.get("headline", "(untitled)")
            url = sig.get("url")
            if url is not None:
                url_total += 1
                if _is_https_url(url):
                    url_ok += 1
                else:
                    issues.append(
                        _issue(
                            "critical",
                            "url_integrity",
                            f"Top signal '{headline}' has invalid https URL",
                        )
                    )

    # --- Leader voice field completeness ---
    if isinstance(leader_voices, list):
        for lv in leader_voices:
            if not isinstance(lv, dict):
                continue
            name = lv.get("name", "(unknown)")
            for field in (
                "name",
                "org",
                "quote_or_paragraph",
                "url",
                "stance",
                "strategic_implication",
            ):
                if not str(lv.get(field, "")).strip():
                    issues.append(
                        _issue(
                            "critical",
                            "schema",
                            f"Leader voice '{name}' missing required field: {field}",
                        )
                    )
            stance = lv.get("stance")
            if stance and stance not in VALID_STANCES:
                issues.append(
                    _issue(
                        "critical",
                        "schema",
                        f"Leader voice '{name}' has invalid stance: {stance!r}",
                    )
                )

    # --- Horizon consistency ---
    if isinstance(categories, list):
        for cat in categories:
            if not isinstance(cat, dict):
                continue
            cat_id = cat.get("id")
            if cat_id not in OPPORTUNITY_CATEGORY_IDS:
                continue
            expected = cat_id.replace("opp_", "")
            for item in cat.get("items", []):
                if not isinstance(item, dict):
                    continue
                title = item.get("title", "(untitled)")
                horizon = item.get("horizon")
                if horizon not in VALID_HORIZONS:
                    issues.append(
                        _issue(
                            "critical",
                            "horizon",
                            f"Item '{title}' in {cat_id} missing valid horizon",
                        )
                    )
                elif horizon != expected:
                    issues.append(
                        _issue(
                            "critical",
                            "horizon",
                            f"Item '{title}' in {cat_id} has horizon={horizon!r}, "
                            f"expected {expected!r}",
                        )
                    )

    # --- Source whitelist ---
    if isinstance(categories, list):
        for cat in categories:
            if not isinstance(cat, dict):
                continue
            cat_id = cat.get("id", "?")
            for item in cat.get("items", []):
                if not isinstance(item, dict):
                    continue
                source = item.get("source")
                if source not in ALLOWED_SOURCES:
                    issues.append(
                        _issue(
                            "critical",
                            "source_whitelist",
                            f"Item in {cat_id} has disallowed source: {source!r}",
                        )
                    )
                signal = item.get("signal")
                if signal not in VALID_SIGNALS:
                    issues.append(
                        _issue(
                            "critical",
                            "schema",
                            f"Item in {cat_id} has invalid signal: {signal!r}",
                        )
                    )

    if isinstance(top_signals, list):
        for sig in top_signals:
            if not isinstance(sig, dict):
                continue
            for field in ("headline", "why_it_matters", "urgency"):
                if not str(sig.get(field, "")).strip():
                    issues.append(
                        _issue(
                            "critical",
                            "schema",
                            f"Top signal missing required field: {field}",
                        )
                    )
            if sig.get("urgency") not in VALID_URGENCY:
                issues.append(
                    _issue(
                        "critical",
                        "schema",
                        f"Top signal has invalid urgency: {sig.get('urgency')!r}",
                    )
                )

    # --- AI relevance (blocklist) ---
    ai_flagged = 0
    if isinstance(categories, list):
        for cat in categories:
            if not isinstance(cat, dict):
                continue
            for item in cat.get("items", []):
                if not isinstance(item, dict):
                    continue
                title_lower = str(item.get("title", "")).lower()
                for term in AI_BLOCKLIST:
                    if term in title_lower:
                        ai_flagged += 1
                        issues.append(
                            _issue(
                                "critical",
                                "ai_relevance",
                                f"Likely non-AI item flagged: '{item.get('title')}' "
                                f"(matched '{term}')",
                            )
                        )
                        break

    # --- Product Hunt thesis alignment ---
    ph_picks = collect_ph_items(briefing) if isinstance(categories, list) else []
    ph_total = len(ph_picks)
    ph_with_tie = 0

    if ph_total < PH_MIN_PICKS:
        issues.append(
            _issue(
                "critical",
                "product_hunt_alignment",
                f"Need at least {PH_MIN_PICKS} Product Hunt items in "
                f"{'+'.join(PH_REQUIRED_CATEGORIES)} (each validating a capital thesis); "
                f"found {ph_total}.",
            )
        )
    elif ph_total > PH_MAX_PICKS:
        issues.append(
            _issue(
                "critical",
                "product_hunt_alignment",
                f"Too many Product Hunt items in {'+'.join(PH_REQUIRED_CATEGORIES)} "
                f"({ph_total}); keep to {PH_MIN_PICKS}-{PH_MAX_PICKS} highest-conviction picks.",
            )
        )

    for cat_id, item in ph_picks:
        title = item.get("title", "(untitled)")
        if not str(item.get("url", "")).strip():
            issues.append(
                _issue(
                    "critical",
                    "product_hunt_alignment",
                    f"Product Hunt item '{title}' in {cat_id} missing Product Hunt URL.",
                )
            )
        if _has_thesis_tie(item):
            ph_with_tie += 1
        else:
            issues.append(
                _issue(
                    "critical",
                    "product_hunt_alignment",
                    f"Product Hunt item '{title}' in {cat_id} lacks an explicit "
                    "thesis tie (set aligned_thesis or start summary with 'Validates ...').",
                )
            )

    # Catch PH items placed outside building/opp_now without a thesis tie (warn-only)
    if isinstance(categories, list):
        for cat in categories:
            if not isinstance(cat, dict):
                continue
            cat_id = cat.get("id")
            if cat_id in PH_REQUIRED_CATEGORIES:
                continue
            for item in cat.get("items", []):
                if not isinstance(item, dict):
                    continue
                if item.get("source") != PH_SOURCE:
                    continue
                if not _has_thesis_tie(item):
                    issues.append(
                        _issue(
                            "warning",
                            "product_hunt_alignment",
                            f"Product Hunt item '{item.get('title')}' in {cat_id} "
                            "has no thesis tie; either add one or move to "
                            f"{'+'.join(PH_REQUIRED_CATEGORIES)}.",
                        )
                    )

    # --- Strategic depth (warnings only) ---
    thin_count = 0
    if isinstance(categories, list):
        for cat in categories:
            if not isinstance(cat, dict):
                continue
            cat_id = cat.get("id", "?")
            for item in cat.get("items", []):
                if not isinstance(item, dict):
                    continue
                summary = str(item.get("summary", ""))
                if len(summary.strip()) < THIN_SUMMARY_CHARS:
                    thin_count += 1
                    issues.append(
                        _issue(
                            "warning",
                            "strategic_depth",
                            f"Summary under {THIN_SUMMARY_CHARS} chars in {cat_id}: "
                            f"'{item.get('title')}'",
                        )
                    )

    url_score = 1.0 if url_total == 0 else url_ok / url_total
    ai_score = 1.0 if ai_flagged == 0 else max(0.0, 1.0 - ai_flagged * 0.25)
    schema_critical = sum(
        1 for i in issues if i["level"] == "critical" and i["check"] == "schema"
    )
    schema_score = 1.0 if schema_critical == 0 else max(0.0, 1.0 - schema_critical * 0.2)

    ph_score = 0.0 if ph_total == 0 else round(ph_with_tie / ph_total, 2)
    if ph_total < PH_MIN_PICKS:
        ph_score = 0.0

    scores = {
        "url_integrity": round(url_score, 2),
        "ai_relevance": round(ai_score, 2),
        "schema_completeness": round(schema_score, 2),
        "leader_voices_count": leader_count,
        "thin_summaries": thin_count,
        "ph_alignment": ph_score,
        "ph_picks_count": ph_total,
    }

    passed = not any(i["level"] == "critical" for i in issues)

    return {"passed": passed, "issues": issues, "scores": scores}
