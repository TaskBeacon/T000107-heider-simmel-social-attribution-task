from __future__ import annotations

from functools import partial
from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import resolve_condition


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """Present one twice-viewed animation, narrative report, and family judgment."""

    spec = resolve_condition(settings, condition)
    condition_id = spec["condition_id"]
    motion_family = spec["motion_family"]
    movie_stim_id = spec["movie_stim_id"]
    correct_key = spec["correct_key"]
    trial_id = int(next_trial_id())
    block_id_value = str(block_id or "animation_block")
    block_idx_value = int(block_idx or 0)
    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)
    task_factors = {
        "motion_family": motion_family,
        "movie_stim_id": movie_stim_id,
        "correct_key": correct_key,
        "block_idx": block_idx_value,
    }
    trial_data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_id_value,
        "block_idx": block_idx_value,
        "condition": condition_id,
        "condition_id": condition_id,
        **task_factors,
    }

    fixation = make_unit(unit_label="fixation").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        fixation,
        trial_id=trial_id,
        phase="fixation",
        deadline_s=float(settings.fixation_duration_s),
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id="fixation",
    )
    fixation.show(
        duration=float(settings.fixation_duration_s),
        onset_trigger=settings.triggers.get("fixation_onset"),
    ).to_dict(trial_data)

    first_movie = stim_bank.rebuild(movie_stim_id, update_cache=False)
    first = make_unit(unit_label="animation_first").add_stim(first_movie)
    set_trial_context(
        first,
        trial_id=trial_id,
        phase="animation_first",
        deadline_s=float(settings.animation_duration_s),
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id=movie_stim_id,
        stim_features={"playback_index": 1, "motion_family": motion_family},
    )
    first.capture_response(
        keys=[],
        duration=float(settings.animation_duration_s),
        onset_trigger=settings.triggers.get(f"{motion_family}_animation_onset"),
        terminate_on_response=False,
    ).to_dict(trial_data)

    replay_interval = make_unit(unit_label="replay_interval").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        replay_interval,
        trial_id=trial_id,
        phase="replay_interval",
        deadline_s=float(settings.replay_interval_s),
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id="fixation",
    )
    replay_interval.show(
        duration=float(settings.replay_interval_s),
        onset_trigger=settings.triggers.get("replay_interval_onset"),
    ).to_dict(trial_data)

    second_movie = stim_bank.rebuild(movie_stim_id, update_cache=False)
    second = make_unit(unit_label="animation_second").add_stim(second_movie)
    set_trial_context(
        second,
        trial_id=trial_id,
        phase="animation_second",
        deadline_s=float(settings.animation_duration_s),
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id=movie_stim_id,
        stim_features={"playback_index": 2, "motion_family": motion_family},
    )
    second.capture_response(
        keys=[],
        duration=float(settings.animation_duration_s),
        onset_trigger=settings.triggers.get("animation_replay_onset"),
        terminate_on_response=False,
    ).to_dict(trial_data)

    submit_key = str(settings.submit_key)
    response_box = stim_bank.rebuild("narrative_entry", update_cache=False, text="", editable=True)
    response_box.hasFocus = True
    narrative = make_unit(unit_label="narrative_response").add_stim(
        stim_bank.get("narrative_prompt"),
        response_box,
        stim_bank.get("narrative_submit_hint"),
    )
    set_trial_context(
        narrative,
        trial_id=trial_id,
        phase="narrative_response",
        deadline_s=float(settings.narrative_response_window_s),
        valid_keys=[submit_key],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id="narrative_prompt+narrative_entry+narrative_submit_hint",
        stim_features={"response_mode": "open_narrative"},
    )
    narrative.capture_response(
        keys=[submit_key],
        duration=float(settings.narrative_response_window_s),
        onset_trigger=settings.triggers.get("narrative_onset"),
        response_trigger={submit_key: settings.triggers.get("narrative_submit")},
        timeout_trigger=settings.triggers.get("narrative_timeout"),
    ).to_dict(trial_data)
    response_box.editable = False
    narrative_key = str(narrative.get_state("response", "") or "")
    narrative_text = str(response_box.getText() or "").strip()
    narrative_rt = narrative.get_state("rt", None)

    judgment_keys = [str(key) for key in settings.judgment_keys]
    judgment = make_unit(unit_label="motion_family_judgment").add_stim(
        stim_bank.get("judgment_prompt"),
        stim_bank.get("judgment_option_social"),
        stim_bank.get("judgment_option_mechanical"),
        stim_bank.get("judgment_option_random"),
    )
    set_trial_context(
        judgment,
        trial_id=trial_id,
        phase="motion_family_judgment",
        deadline_s=float(settings.judgment_response_window_s),
        valid_keys=judgment_keys,
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id="judgment_prompt+judgment_options",
        stim_features={"response_mode": "three_alternative_forced_choice"},
    )
    judgment.capture_response(
        keys=judgment_keys,
        correct_keys=[correct_key],
        duration=float(settings.judgment_response_window_s),
        onset_trigger=settings.triggers.get("judgment_onset"),
        response_trigger={
            judgment_keys[0]: settings.triggers.get("judgment_social"),
            judgment_keys[1]: settings.triggers.get("judgment_mechanical"),
            judgment_keys[2]: settings.triggers.get("judgment_random"),
        },
        timeout_trigger=settings.triggers.get("judgment_timeout"),
    ).to_dict(trial_data)
    judgment_key = str(judgment.get_state("response", "") or "")
    judgment_rt = judgment.get_state("rt", None)
    judgment_correct = judgment_key == correct_key if judgment_key else None

    iti = make_unit(unit_label="inter_trial_interval").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="inter_trial_interval",
        deadline_s=float(settings.iti_duration_s),
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id="fixation",
    )
    iti.show(
        duration=float(settings.iti_duration_s),
        onset_trigger=settings.triggers.get("iti_onset"),
    ).to_dict(trial_data)

    trial_data.update(
        {
            "narrative_text": narrative_text,
            "narrative_word_count": len(narrative_text.split()),
            "narrative_character_count": len(narrative_text),
            "narrative_submit_key": narrative_key,
            "narrative_rt": float(narrative_rt) if isinstance(narrative_rt, (int, float)) else None,
            "narrative_timeout": not bool(narrative_key),
            "judgment_key": judgment_key,
            "judgment_rt": float(judgment_rt) if isinstance(judgment_rt, (int, float)) else None,
            "judgment_correct": judgment_correct,
            "judgment_timeout": not bool(judgment_key),
            "outcome": int(judgment_correct) if isinstance(judgment_correct, bool) else None,
        }
    )
    return trial_data
