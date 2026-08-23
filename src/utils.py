from __future__ import annotations

from typing import Any


def resolve_condition(settings: Any, condition: Any) -> dict[str, str]:
    """Resolve one scheduled scalar condition into its fixed task factors."""

    condition_id = str(condition).strip()
    family_by_condition = dict(settings.condition_family)
    movie_by_condition = dict(settings.condition_movie)
    family_key_map = {str(key): str(value) for key, value in dict(settings.family_key_map).items()}
    if condition_id not in family_by_condition or condition_id not in movie_by_condition:
        raise ValueError(f"Unsupported social-attribution condition: {condition_id}")
    family = str(family_by_condition[condition_id])
    if family not in family_key_map:
        raise ValueError(f"Missing response key for motion family: {family}")
    return {
        "condition_id": condition_id,
        "motion_family": family,
        "movie_stim_id": str(movie_by_condition[condition_id]),
        "correct_key": family_key_map[family],
    }


def summarize_trials(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [row for row in rows if isinstance(row.get("judgment_correct"), bool)]
    correct = sum(bool(row["judgment_correct"]) for row in scored)
    by_family: dict[str, dict[str, int | float | None]] = {}
    for family in ("social", "mechanical", "random"):
        family_rows = [row for row in scored if row.get("motion_family") == family]
        family_correct = sum(bool(row["judgment_correct"]) for row in family_rows)
        by_family[family] = {
            "n": len(family_rows),
            "correct": family_correct,
            "accuracy": family_correct / len(family_rows) if family_rows else None,
        }
    return {
        "trial_count": len(rows),
        "scored_count": len(scored),
        "correct_count": correct,
        "accuracy": correct / len(scored) if scored else None,
        "by_family": by_family,
    }
