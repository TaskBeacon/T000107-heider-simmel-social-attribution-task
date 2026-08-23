# Task Logic Audit — Heider–Simmel Social Attribution Task

This audit was written from the cited literature before task code. The implementation does not reproduce the 1944 film or any later published animation set; it uses newly scripted trajectories that preserve only the paradigm-level contrast between socially contingent, mechanically constrained, and random motion.

## 1. Paradigm Intent

- Task: Heider–Simmel Social Attribution Task.
- Primary construct: spontaneous social attribution / mentalizing from geometric motion.
- Manipulated factors: motion family (`social`, `mechanical`, `random`) with two newly authored scenarios per family.
- Dependent measures: free narrative, forced-choice motion-family judgment, response time, timeout rate, and condition-wise classification accuracy. Offline narrative coding may derive cognitive, affective, and imagination-term indices.
- Key citations: Heider & Simmel (1944); Abell, Happé, & Frith (2000); Martin & Weisberg (2003); Isik et al. (2017); Ratajska, Brown, & Chabris (2021).

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 1.
- Trials per block: 6 (two social, two mechanical, two random).
- Randomization/counterbalancing: all six scenario labels are scheduled once in a seeded random order. No scenario is selected inside `run_trial.py`.
- Condition weight policy:
  - `task.condition_weights` is omitted/null because every scenario label is presented once.
  - Runtime resolution is delegated to `TaskSettings.resolve_condition_weights()`.
- Condition generation method:
  - Built-in `BlockUnit.generate_conditions(...)` with six label-level conditions and random order.
  - Each scalar condition label is passed directly into `run_trial.py`.
- Runtime-generated trial values: none. Video identity, motion family, response target, and stimulus file are fixed by the scheduled condition label.

### Trial State Machine

1. `fixation`
   - Onset trigger: `fixation_onset` (10).
   - Stimuli shown: black fixation cross centered on a white background.
   - Valid keys: none.
   - Timeout behavior: advances after 0.5 s.
   - Next state: first playback.
2. `animation_first`
   - Onset trigger: family-specific animation trigger (`social_animation_onset`, `mechanical_animation_onset`, or `random_animation_onset`).
   - Stimuli shown: the scheduled 15 s silent geometric animation.
   - Valid keys: none.
   - Timeout behavior: advances when the 15 s playback window ends.
   - Next state: replay interval.
3. `replay_interval`
   - Onset trigger: `replay_interval_onset` (14).
   - Stimuli shown: fixation cross.
   - Valid keys: none.
   - Timeout behavior: advances after 0.5 s.
   - Next state: second playback.
4. `animation_second`
   - Onset trigger: `animation_replay_onset` (15).
   - Stimuli shown: a fresh instance of the same scheduled 15 s animation.
   - Valid keys: none.
   - Timeout behavior: advances when the 15 s playback window ends.
   - Next state: narrative response.
5. `narrative_response`
   - Onset trigger: `narrative_onset` (20).
   - Stimuli shown: neutral prompt, editable multiline text box, and submit hint.
   - Valid keys: Return/Enter submits; typed characters populate the focused text box.
   - Timeout behavior: saves current text and advances after 60 s.
   - Next state: motion-family judgment.
6. `motion_family_judgment`
   - Onset trigger: `judgment_onset` (30).
   - Stimuli shown: neutral question and three spatially separated response options: `1 社会互动`, `2 机械运动`, `3 随机运动`.
   - Valid keys: `1`, `2`, `3`.
   - Timeout behavior: records no classification and advances after 8 s.
   - Next state: inter-trial interval.
7. `inter_trial_interval`
   - Onset trigger: `iti_onset` (40).
   - Stimuli shown: blank white screen with fixation cross.
   - Valid keys: none.
   - Timeout behavior: advances after 0.75 s.
   - Next state: next scheduled trial or task completion.

## 3. Condition Semantics

- Condition ID: `social_helping`
  - Participant-facing meaning: a large triangle notices and assists a circle that cannot pass a barrier.
  - Concrete stimulus realization: contingent approach, pause/orientation, joint movement, and coordinated completion by triangle/circle/small triangle near an outlined enclosure.
  - Outcome rules: correct family key `1`.
- Condition ID: `social_chasing`
  - Participant-facing meaning: a large triangle pursues a smaller triangle while a circle alternately approaches and intervenes.
  - Concrete stimulus realization: contingent pursuit/evasion, pauses, redirection, and interpersonal spacing changes.
  - Outcome rules: correct family key `1`.
- Condition ID: `mechanical_bounce`
  - Participant-facing meaning: shapes behave like pinballs governed by collisions and reflection.
  - Concrete stimulus realization: constant-speed trajectories, wall/obstacle bounces, no reaction to another shape's inferred state.
  - Outcome rules: correct family key `2`.
- Condition ID: `mechanical_conveyor`
  - Participant-facing meaning: shapes move as objects on a conveyor/gear-like transport sequence.
  - Concrete stimulus realization: fixed lanes, constant timing, rigid hand-offs, and repeated synchronized displacement.
  - Outcome rules: correct family key `2`.
- Condition ID: `random_drift_a`
  - Participant-facing meaning: independent purposeless motion.
  - Concrete stimulus realization: separately seeded smooth random waypoints with no contingency or common destination.
  - Outcome rules: correct family key `3`.
- Condition ID: `random_drift_b`
  - Participant-facing meaning: a second independent purposeless motion realization.
  - Concrete stimulus realization: different deterministic waypoints, matched duration/speed envelope, no inter-shape reaction.
  - Outcome rules: correct family key `3`.

Participant-facing text source: all instructions, prompts, option labels, and hints are defined in `config/*.yaml`; the generated movies contain shapes only and no condition labels. This keeps localization separate from trial code. Chinese variants swap config text without editing `src/run_trial.py`.

## 4. Response and Scoring Rules

- Response mapping: Return submits the narrative; `1=社会互动`, `2=机械运动`, `3=随机运动` for the classification judgment.
- Response key source: config fields `submit_key`, `judgment_keys`, and `family_key_map`.
- Missing-response policy: preserve any text already entered; set `narrative_timeout` and/or `judgment_timeout`; no feedback or penalty.
- Correctness logic: classification key is compared with the scheduled condition family's config-defined target key.
- Reward/penalty updates: none.
- Running metrics: classification accuracy may be summarized at session end; narrative content is not auto-scored during data collection.

## 5. Stimulus Layout Plan

- Screen name: animation playback.
  - Stimulus IDs shown together: one full animation movie containing the three agent shapes and outlined enclosure/obstacles.
  - Layout anchors: movie centered at `[0, 0]`, 960 × 540 px in a 1280 × 720 window.
  - Size/spacing: shapes remain at least 24 px from frame edges; the outlined enclosure occupies the right-middle region without covering agents.
  - Readability/overlap checks: generated frames are inspected at first, middle, and final time points for clipping and correct scale.
  - Rationale: silent, centered geometric motion removes linguistic cues during attribution.
- Screen name: narrative response.
  - Stimulus IDs shown together: `narrative_prompt`, `narrative_entry`, `narrative_submit_hint`.
  - Layout anchors: prompt `[0, 245]`; text box `[0, -5]`; hint `[0, -285]` in pixel units.
  - Size/spacing: prompt wrap 1040 px; entry 980 × 360 px; hint wrap 900 px.
  - Readability/overlap checks: 95 px vertical gap between prompt and entry; 80 px between entry and hint.
  - Rationale: large multiline area supports paragraph-length reports.
- Screen name: motion-family judgment.
  - Stimulus IDs shown together: `judgment_prompt`, `judgment_option_social`, `judgment_option_mechanical`, `judgment_option_random`.
  - Layout anchors: prompt `[0, 190]`; options `[-350, -45]`, `[0, -45]`, `[350, -45]`.
  - Size/spacing: each option box 280 × 120 px; 70 px horizontal gap.
  - Readability/overlap checks: labels use 30 px SimHei and remain within their boxes at 1280 × 720.
  - Rationale: equal visual weight avoids cueing the true family.

## 6. Trigger Plan

- Experiment/block: `experiment_start=1`, `experiment_end=2`, `block_start=3`, `block_end=4`.
- Fixation/replay: `fixation_onset=10`, `social_animation_onset=11`, `mechanical_animation_onset=12`, `random_animation_onset=13`, `replay_interval_onset=14`, `animation_replay_onset=15`.
- Narrative: `narrative_onset=20`, `narrative_submit=21`, `narrative_timeout=22`.
- Judgment: `judgment_onset=30`, `judgment_social=31`, `judgment_mechanical=32`, `judgment_random=33`, `judgment_timeout=34`.
- ITI/completion: `iti_onset=40`, `goodbye_onset=50`.

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: one direct `human|qa|sim` flow with built-in condition scheduling.
- `utils.py` used: yes, only for scalar condition-to-family/stimulus lookup and narrative summary helpers.
- Custom controller used: no.
- Legacy/backward-compatibility fallback logic required: no.
- Animation generation: a task-local asset-generation script deterministically renders six original MP4 files from documented trajectories. Runtime uses PsyFlow `MovieStim`/`StimUnit`; no manual draw loop lives in `run_trial.py`.
- Open text entry: a config-defined editable `TextBox2` is captured through public `StimUnit.capture_response`, matching existing PsyFlow task practice.

## 8. Inference Log

- Decision: six 15 s animations rather than the original single 2.5 min film or all 32 modern clips.
  - Why inference was required: the requested task calls for new social/mechanical/random contrasts at medium implementation cost.
  - Citation-supported rationale: Ratajska et al. used newly authored 13–23 s clips (mean 17 s); 15 s stays within that range and supports balanced repeated-measures contrasts.
- Decision: two playbacks per trial.
  - Why inference was required: short task variants vary in replay count.
  - Citation-supported rationale: Ratajska et al. presented every clip twice to reduce memory burden before narrative writing.
- Decision: add a forced-choice family judgment after the narrative.
  - Why inference was required: classic responses are open narratives, but automated behavioral comparison requires a direct dependent measure.
  - Citation-supported rationale: Abell et al. contrasted random, goal-directed, and ToM animations and rated description accuracy/type; the extra judgment is placed after the spontaneous narrative so it cannot prime that report.
- Decision: use Chinese participant-facing instructions and 60 s narrative / 8 s judgment windows.
  - Why inference was required: source studies do not specify a fixed narrative deadline for this shortened computerized variant.
  - Citation-supported rationale: bounded windows preserve practical administration while allowing a paragraph response; both are marked as inferred rather than source-exact.

