from __future__ import annotations

import json
from contextlib import nullcontext
from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core
from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskRunOptions,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    next_trial_id,
    parse_task_run_options,
    reset_trial_counter,
    runtime_context,
    set_trial_context,
)

from src import run_trial, summarize_trials


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _continue_screen(*, bank, win, kb, triggers, settings, stim_id: str, phase: str, terminate: bool = False) -> None:
    continue_key = str(settings.continue_key)
    unit = StimUnit(phase, win, kb, runtime=triggers).add_stim(bank.get(stim_id))
    set_trial_context(
        unit,
        trial_id=int(next_trial_id()),
        phase=phase,
        deadline_s=None,
        valid_keys=[continue_key],
        block_id=phase,
        condition_id=phase,
        task_factors={"stage": phase},
        stim_id=stim_id,
    )
    unit.wait_and_continue(keys=[continue_key], terminate=terminate)


def run(options: TaskRunOptions) -> None:
    root = Path(__file__).resolve().parent
    config = load_config(str(options.config_path))
    output_dir, scope, context = None, nullcontext(), None
    if options.mode in ("qa", "sim"):
        context = context_from_config(task_dir=root, config=config, mode=options.mode)
        output_dir, scope = context.output_dir, runtime_context(context)

    with scope:
        if options.mode == "qa":
            subject = {"subject_id": "qa107"}
        elif options.mode == "sim":
            subject = {"subject_id": str(context.session.participant_id or "sim107")}
        else:
            subject = SubInfo(config["subform_config"]).collect()

        settings = TaskSettings.from_dict(config["task_config"])
        settings.add_subinfo(subject)
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.save_path = str(output_dir)
            prefix = "qa" if options.mode == "qa" else "sim"
            settings.res_file = str(output_dir / f"{prefix}_trace.csv")
            settings.log_file = str(output_dir / f"{prefix}_psychopy.log")
            settings.json_file = str(output_dir / f"{prefix}_settings.json")

        settings.triggers = config["trigger_config"]
        triggers = initialize_triggers(mock=True) if options.mode in ("qa", "sim") else initialize_triggers(config)
        win, kb = initialize_exp(settings)
        # Movie stimuli are created lazily so smoke profiles only decode the
        # representative clips they actually schedule.
        bank = StimBank(win, config["stim_config"])
        settings.save_to_json()
        reset_trial_counter()

        triggers.send(settings.triggers.get("experiment_start"))
        _continue_screen(
            bank=bank,
            win=win,
            kb=kb,
            triggers=triggers,
            settings=settings,
            stim_id="instruction",
            phase="instruction",
        )

        condition_labels = [str(label) for label in settings.conditions]
        condition_weights = settings.resolve_condition_weights()
        block = (
            BlockUnit(
                block_id="animation_block",
                block_idx=0,
                settings=settings,
                window=win,
                keyboard=kb,
            )
            .generate_conditions(
                condition_labels=condition_labels,
                weights=condition_weights,
                order="random",
            )
            .on_start(lambda _: triggers.send(settings.triggers.get("block_start")))
            .on_end(lambda _: triggers.send(settings.triggers.get("block_end")))
            .run_trial(
                partial(
                    run_trial,
                    stim_bank=bank,
                    trigger_runtime=triggers,
                    block_id="animation_block",
                    block_idx=0,
                )
            )
        )
        rows = list(block.get_all_data())
        summary = summarize_trials(rows)
        result_path = Path(settings.res_file)
        pd.DataFrame(rows).to_csv(result_path, index=False)
        result_path.with_name(f"{result_path.stem}_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        triggers.send(settings.triggers.get("goodbye_onset"))
        _continue_screen(
            bank=bank,
            win=win,
            kb=kb,
            triggers=triggers,
            settings=settings,
            stim_id="good_bye",
            phase="good_bye",
            terminate=True,
        )
        triggers.send(settings.triggers.get("experiment_end"))
        triggers.close()
        win.close()
        core.quit()


def main() -> None:
    run(
        parse_task_run_options(
            task_root=Path(__file__).resolve().parent,
            description="Run the Heider–Simmel Social Attribution Task.",
            default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
            modes=MODES,
        )
    )


if __name__ == "__main__":
    main()
