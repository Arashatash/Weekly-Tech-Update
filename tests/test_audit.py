"""Tests for src.audit."""

from src.audit import audit_briefing


def test_audit_briefing_passes_valid_sample(sample_briefing):
    result = audit_briefing(sample_briefing)
    assert result["passed"] is True
    assert result["issues"] == []
    assert result["scores"]["url_integrity"] == 1.0
    assert result["scores"]["leader_voices_count"] == 3


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
