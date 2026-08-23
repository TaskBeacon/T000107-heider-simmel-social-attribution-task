# Heider–Simmel Social Attribution Task

| Field                | Value                        |
|----------------------|------------------------------|
| Name | Heider–Simmel Social Attribution Task |
| Version | 0.1.0 |
| URL / Repository | https://github.com/TaskBeacon/T000107-heider-simmel-social-attribution-task |
| Short Description | Social, mechanical, and random geometric-motion attribution with open narratives. |
| Created By | TaskBeacon |
| Date Updated | 2026-08-24 |
| PsyFlow Version | 0.1.12 |
| PsychoPy Version | 2025.2.4 |
| Modality | Behavior |
| Language | Chinese |
| Voice Name | zh-CN-YunyangNeural (disabled by default) |

## 1. Task Overview

This task measures spontaneous social attribution and mentalizing from sparse geometric motion. Participants watch newly generated silent animations containing two triangles, one circle, and an outlined enclosure. The six clips form three matched motion families: socially contingent interaction, mechanically constrained movement, and independent random movement.

Each clip is shown twice. Participants first provide an open narrative without being shown the category labels, then classify the movement as social, mechanical, or random. The implementation preserves the classic paradigm logic while avoiding any copy of the 1944 film or later published animation sets.

Primary outcomes are narrative text, narrative timing, three-alternative classification, classification accuracy, and timeouts. Narrative term indices can be coded offline using a preregistered language-specific dictionary or human coding manual.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

| Step | Implementation |
|---|---|
| Instruction | Neutral description of viewing and later reporting; Space begins. |
| Condition scheduling | One seeded-random block presents six scenario labels exactly once: two social, two mechanical, and two random. |
| Trial execution | `BlockUnit.generate_conditions(...)` owns scheduling; `run_trial.py` receives a scalar scenario label. |
| Completion | Six logical-trial rows and one session summary JSON are saved before the goodbye screen. |

### Trial-Level Flow

| Phase | Duration | Participant-visible content / response |
|---|---:|---|
| `fixation` | 0.5 s | Centered `+`. |
| `animation_first` | 15.0 s | Scheduled silent geometric animation; no response. |
| `replay_interval` | 0.5 s | Centered `+`. |
| `animation_second` | 15.0 s | Fresh replay of the same animation; no response. |
| `narrative_response` | 60.0 s max | Neutral prompt and multiline entry; Return submits. |
| `motion_family_judgment` | 8.0 s max | `1=社会互动`, `2=机械运动`, `3=随机运动`. |
| `inter_trial_interval` | 0.75 s | Centered `+`; no feedback. |

### Controller Logic

| Component | Rule |
|---|---|
| Adaptive controller | None. |
| Balance | Six scheduled labels provide two exemplars per family. |
| Correctness | Config-defined family key is compared with the post-narrative judgment. |

### Other Logic

| Component | Rule |
|---|---|
| Animation generation | `scripts/generate_animations.py` renders deterministic original trajectories. |
| Reproducibility | `assets/animations/manifest.json` records dimensions, duration, frame rate, and SHA-256 hashes. |
| Smoke profiles | One representative clip per family with shortened real timings; human parameters remain unchanged. |

## 3. Configuration Summary

### a. Subject Info

| Field | Type | Constraint |
|---|---|---|
| subject_id | integer | 3 digits, 101–999 |
| age | integer | 18–80 |
| gender | choice | 女性 / 男性 / 其他或不愿说明 |

### b. Window Settings

| Parameter | Value |
|---|---|
| size | 1280 × 720 px |
| background | `#FAFAF8` |
| movie size | 960 × 540 px |
| human fullscreen | false (lab deployment may override) |

### c. Stimuli

| Family | Conditions | Visible motion principle |
|---|---|---|
| social | `social_helping`, `social_chasing` | contingent helping or pursuit/intervention |
| mechanical | `mechanical_bounce`, `mechanical_conveyor` | collision/reflection or rigid transport |
| random | `random_drift_a`, `random_drift_b` | independent smooth waypoints, no contingency |

### d. Timing

| Phase | Duration / deadline |
|---|---:|
| fixation | 0.5 s |
| first animation | 15.0 s |
| replay interval | 0.5 s |
| second animation | 15.0 s |
| narrative | 60.0 s max |
| family judgment | 8.0 s max |
| ITI | 0.75 s |

### e. Responses and Triggers

| Event | Key / trigger |
|---|---|
| narrative submit | Return / 21 |
| narrative timeout | none / 22 |
| social judgment | 1 / 31 |
| mechanical judgment | 2 / 32 |
| random judgment | 3 / 33 |
| judgment timeout | none / 34 |

Animation onset triggers distinguish social (11), mechanical (12), and random (13) first playbacks; replay onset uses 15. See `config/config.yaml` for the complete lifecycle map.

### f. Adaptive Controller

None. QA and simulation shorten timing through the standard runtime scaling profiles while preserving all six conditions and every trial phase.

## 4. Methods (for academic publication)

Participants viewed six newly authored, silent geometric animations in a seeded random order. Each 15 s animation contained two colored triangles, one colored circle, and a dark outlined enclosure on a near-white background. Two clips depicted socially contingent trajectories (helping and chasing/intervention), two depicted mechanically constrained motion (pinball-like reflection and conveyor-like transport), and two depicted independently seeded smooth random trajectories without inter-agent contingency. Every animation was presented twice, separated by a 0.5 s fixation, following the replay procedure used to reduce memory burden in the primary modern protocol.

After the second playback, participants typed a neutral description of what happened into a multiline response box (60 s maximum). Only after submitting this spontaneous narrative did participants classify the clip as social interaction, mechanical motion, or random motion (8 s maximum). No correctness feedback or reward was provided. The main behavioral outcome was motion-family classification accuracy; narrative text and timing were retained for later social-attribution coding. All six MP4 stimuli were generated from deterministic task-local code and were not reconstructed from the original Heider–Simmel film or any later stimulus set.

## Run and validation

```powershell
python main.py
python main.py qa --config config/config_qa.yaml
python main.py sim --config config/config_scripted_sim.yaml
python main.py sim --config config/config_sampler_sim.yaml
```

Reference provenance and every adapted/inferred parameter are documented under `references/`.
