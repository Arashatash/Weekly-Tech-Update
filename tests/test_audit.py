"""Tests for src.audit."""

from src.audit import audit_briefing


def test_audit_briefing_passes_valid_sample(sample_briefing):
    result = audit_briefing(sample_briefing)
    assert result["passed"] is True, result["issues"]
    assert result["issues"] == []
    assert result["scores"]["url_integrity"] == 1.0
    assert result["scores"]["leader_voices_count"] == 3
    assert result["scores"]["ph_alignment"] == 1.0
    assert result["scores"]["ph_picks_count"] >= 2


def test_audit_flags_missing_https_url(sample_briefing):
    sample_briefing["leader_voices"][0]["url"] = "http://insecure.example.com"
    result = audit_briefing(sample_briefing)
    assert result["passed"] is False
    assert any(i["check"] == "url_integrity" for i in result["issues"])


def test_audit_flags_blocklisted_title(sample_briefing):
    sample_briefing["categories"][0]["items"][0]["title"] = "SpaceX launches new rocket"
    result = audit_briefing(sample_briefing)
    assert result["passed"] is False
    assert any(i["check"] == "ai_relevance" for i in result["issues"])


def test_audit_flags_horizon_mismatch(sample_briefing):
    sample_briefing["categories"][2]["items"][0]["horizon"] = "mid"
    result = audit_briefing(sample_briefing)
    assert result["passed"] is False
    assert any(i["check"] == "horizon" for i in result["issues"])


def test_audit_warns_on_thin_summary(sample_briefing):
    sample_briefing["categories"][0]["items"][0]["summary"] = "Too short."
    result = audit_briefing(sample_briefing)
    assert any(
        i["level"] == "warning" and i["check"] == "strategic_depth"
        for i in result["issues"]
    )


def test_audit_flags_missing_leader_voices(sample_briefing):
    del sample_briefing["leader_voices"]
    result = audit_briefing(sample_briefing)
    assert result["passed"] is False
    assert any("leader_voices" in i["message"] for i in result["issues"])


def _set_categories(briefing, cat_id, items):
    for cat in briefing["categories"]:
        if cat["id"] == cat_id:
            cat["items"] = items
            return


def _ph_items_in(briefing):
    out = []
    for cat in briefing["categories"]:
        if cat["id"] in ("building", "opp_now"):
            out.extend(i for i in cat["items"] if i["source"] == "Product Hunt")
    return out


def test_audit_fails_when_no_product_hunt_items(sample_briefing):
    # remove PH from building and opp_now
    for cat in sample_briefing["categories"]:
        if cat["id"] in ("building", "opp_now"):
            cat["items"] = [i for i in cat["items"] if i["source"] != "Product Hunt"]
    result = audit_briefing(sample_briefing)
    assert result["passed"] is False
    assert any(
        i["check"] == "product_hunt_alignment" and "at least" in i["message"]
        for i in result["issues"]
    )
    assert result["scores"]["ph_picks_count"] == 0
    assert result["scores"]["ph_alignment"] == 0.0


def test_audit_fails_when_only_one_product_hunt_item(sample_briefing):
    # keep only one PH item
    seen = False
    for cat in sample_briefing["categories"]:
        if cat["id"] not in ("building", "opp_now"):
            continue
        new_items = []
        for item in cat["items"]:
            if item["source"] == "Product Hunt":
                if seen:
                    continue
                seen = True
            new_items.append(item)
        cat["items"] = new_items
    result = audit_briefing(sample_briefing)
    assert result["passed"] is False
    assert any(
        i["check"] == "product_hunt_alignment" for i in result["issues"]
    )


def test_audit_fails_when_ph_item_lacks_thesis_tie(sample_briefing):
    ph = _ph_items_in(sample_briefing)
    assert ph, "sample fixture should include PH items"
    # strip both the aligned_thesis field and the 'Validates' phrase
    target = ph[0]
    target.pop("aligned_thesis", None)
    target["summary"] = (
        "Generic descriptive summary that does not name any capital thesis "
        "or use the required tie language anywhere in the text."
    )
    result = audit_briefing(sample_briefing)
    assert result["passed"] is False
    assert any(
        i["check"] == "product_hunt_alignment"
        and "thesis tie" in i["message"]
        for i in result["issues"]
    )
    assert 0.0 <= result["scores"]["ph_alignment"] < 1.0


def test_audit_warns_when_ph_in_other_category_lacks_tie(sample_briefing):
    # add a PH item in opp_mid without a thesis tie — should warn, not fail
    for cat in sample_briefing["categories"]:
        if cat["id"] == "opp_mid":
            cat["items"].append(
                {
                    "title": "Untied PH item",
                    "source": "Product Hunt",
                    "url": "https://www.producthunt.com/products/untied",
                    "summary": "Just a description with no thesis reference at all here.",
                    "signal": "low",
                    "tags": ["misc"],
                    "horizon": "mid",
                }
            )
    result = audit_briefing(sample_briefing)
    # the building+opp_now PH picks still pass critical; this is warn-only
    assert any(
        i["level"] == "warning" and i["check"] == "product_hunt_alignment"
        for i in result["issues"]
    )
    # critical issues from other checks should be absent
    assert not any(
        i["level"] == "critical" and i["check"] == "product_hunt_alignment"
        for i in result["issues"]
    )
