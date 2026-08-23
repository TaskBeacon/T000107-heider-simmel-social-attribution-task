"""Generate complete QA and simulation configs from the canonical human config."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml


def _base(root: Path) -> dict:
    return yaml.safe_load((root / "config" / "config.yaml").read_text(encoding="utf-8"))


def _write(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _shorten_timing(payload: dict) -> None:
    """Keep every phase while making non-human profiles fast and deterministic."""

    payload["timing"].update(
        {
            "fixation_duration_s": 0.05,
            "animation_duration_s": 0.12,
            "replay_interval_s": 0.05,
            "narrative_response_window_s": 0.25,
            "judgment_response_window_s": 0.20,
            "iti_duration_s": 0.05,
        }
    )


def _shorten_schedule(payload: dict) -> None:
    """Use one representative clip per family in smoke profiles."""

    conditions = ["social_helping", "mechanical_bounce", "random_drift_a"]
    payload["task"].update(
        {
            "total_trials": 3,
            "trial_per_block": 3,
            "trials_per_block": 3,
            "conditions": conditions,
        }
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    base = _base(root)

    qa = deepcopy(base)
    qa["task"]["save_path"] = "./outputs/qa"
    qa["window"]["fullscreen"] = False
    _shorten_timing(qa)
    _shorten_schedule(qa)
    qa["qa"] = {
        "output_dir": "outputs/qa",
        "enable_scaling": True,
        "timing_scale": 0.05,
        "min_frames": 1,
        "strict": False,
        "max_wait_s": 60.0,
        "acceptance_criteria": {
            "required_columns": [
                "trial_id", "block_id", "condition", "motion_family", "movie_stim_id",
                "narrative_text", "judgment_key", "judgment_correct", "outcome",
            ],
            "expected_trial_count": 3,
            "allowed_keys": ["space", "return", "1", "2", "3"],
            "triggers_required": True,
        },
    }
    qa["responder"] = {
        "type": "responders.task_sampler:TaskSamplerResponder",
        "kwargs": {"accuracy": 0.84, "timeout_rate": 0.0, "rt_s": 0.05},
    }
    _write(root / "config" / "config_qa.yaml", qa)

    scripted = deepcopy(base)
    scripted["task"]["save_path"] = "./outputs/sim"
    scripted["window"]["fullscreen"] = False
    _shorten_timing(scripted)
    _shorten_schedule(scripted)
    scripted["sim"] = {
        "output_dir": "outputs/sim",
        "seed": 107107,
        "participant_id": "sim107",
        "session_id": "sub-sim107_task-heider-simmel_seed107107",
        "log_path": "outputs/sim/sub-sim107_task-heider-simmel_seed107107_sim_events.jsonl",
        "policy": "warn",
        "default_rt_s": 0.05,
        "clamp_rt": True,
        "enable_scaling": True,
        "timing_scale": 0.02,
        "min_frames": 1,
        "responder": {
            "type": "scripted",
            "kwargs": {"key": None, "rt_s": 0.05},
        },
    }
    _write(root / "config" / "config_scripted_sim.yaml", scripted)

    sampler = deepcopy(base)
    sampler["task"]["save_path"] = "./outputs/sim_sampler"
    sampler["window"]["fullscreen"] = False
    _shorten_timing(sampler)
    _shorten_schedule(sampler)
    sampler["sim"] = {
        "output_dir": "outputs/sim_sampler",
        "seed": 107207,
        "participant_id": "sim207",
        "session_id": "sub-sim207_task-heider-simmel_seed107207",
        "log_path": "outputs/sim_sampler/sub-sim207_task-heider-simmel_seed107207_sim_events.jsonl",
        "policy": "warn",
        "default_rt_s": 0.05,
        "clamp_rt": True,
        "enable_scaling": True,
        "timing_scale": 0.02,
        "min_frames": 1,
        "responder": {
            "type": "responders.task_sampler:TaskSamplerResponder",
            "kwargs": {"accuracy": 0.84, "timeout_rate": 0.08, "rt_s": 0.05},
        },
    }
    _write(root / "config" / "config_sampler_sim.yaml", sampler)


if __name__ == "__main__":
    main()
