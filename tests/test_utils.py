from types import SimpleNamespace

from src.utils import resolve_condition, summarize_trials


def _settings():
    return SimpleNamespace(
        condition_family={"social_helping": "social"},
        condition_movie={"social_helping": "movie_social_helping"},
        family_key_map={"social": "1"},
    )


def test_resolve_condition_returns_fixed_factors():
    assert resolve_condition(_settings(), "social_helping") == {
        "condition_id": "social_helping",
        "motion_family": "social",
        "movie_stim_id": "movie_social_helping",
        "correct_key": "1",
    }


def test_summarize_trials_ignores_timeouts():
    summary = summarize_trials(
        [
            {"motion_family": "social", "judgment_correct": True},
            {"motion_family": "social", "judgment_correct": False},
            {"motion_family": "random", "judgment_correct": None},
        ]
    )
    assert summary["scored_count"] == 2
    assert summary["accuracy"] == 0.5
    assert summary["by_family"]["social"]["accuracy"] == 0.5
