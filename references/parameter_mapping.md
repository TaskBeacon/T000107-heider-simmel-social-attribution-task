# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `motion_families` | `task.condition_family` | social / mechanical / random | `ABELL_HAPPE_FRITH_2000`; `MARTIN_WEISBERG_2003`; `RATAJSKA2021` | Abell et al. distinguish random, goal-directed, and ToM motion; Martin & Weisberg distinguish mechanical action and social interaction; Ratajska et al. summarize both contrasts. | `adapted` | Six new scenarios implement two exemplars per family. |
| `total_trials` | `task.total_trials` | 6 | `RATAJSKA2021` | The primary source used subsets rather than requiring all available clips from each participant. | `inferred` | Medium-cost balanced baseline with two clips per family. |
| `condition_order` | `BlockUnit.generate_conditions(order="random")` | seeded random order | `RATAJSKA2021` | The primary source randomized and counterbalanced video order. | `adapted` | One seeded within-participant random block. |
| `animation_duration_s` | `timing.animation_duration_s` | 15.0 s | `RATAJSKA2021` | Materials report 13–23 s clips (mean 17 s). | `adapted` | Fifteen seconds is inside the published range. |
| `playback_count` | trial state machine | 2 | `RATAJSKA2021` | Procedure presented every video twice before narrative entry to reduce memory burden. | `direct` | Same generated asset rebuilt for a fresh second playback. |
| `fixation_duration_s` | `timing.fixation_duration_s` | 0.5 s | `RATAJSKA2021` | No fixed fixation duration is reported for the online survey. | `inferred` | Brief neutral lead-in. |
| `replay_interval_s` | `timing.replay_interval_s` | 0.5 s | `RATAJSKA2021` | The source used separate survey pages for the two playbacks. | `inferred` | Brief fixation separates two automatic playbacks. |
| `narrative_prompt` | `stimuli.narrative_prompt.text` | neutral open description | `HEIDER_SIMMEL_1944`; `RATAJSKA2021` | Both protocols ask participants to describe what happened without first labeling the clip as social. | `adapted` | Chinese wording asks for behavior, relationships, or the complete process. |
| `narrative_response_window_s` | `timing.narrative_response_window_s` | 60.0 s | `RATAJSKA2021` | The source used a text box but did not report a per-clip deadline. | `inferred` | Bounded administration window; typed text is preserved on timeout. |
| `judgment_options` | `task.family_key_map` | 1 social / 2 mechanical / 3 random | `ABELL_HAPPE_FRITH_2000`; `MARTIN_WEISBERG_2003` | Supporting paradigms operationalize separable social/mentalizing, mechanical/goal-directed, and random motion categories. | `adapted` | Judgment follows the narrative to avoid priming spontaneous attribution. |
| `judgment_response_window_s` | `timing.judgment_response_window_s` | 8.0 s | `ABELL_HAPPE_FRITH_2000` | A fixed response window is not reported. | `inferred` | Sufficient for a three-choice classification. |
| `font` | `stimuli.*.font` | SimHei for Chinese text | TaskBeacon language policy | Chinese participant-facing text requires a font with appropriate glyph coverage. | `inferred` | Shape-only movies contain no text. |
| `window_size` | `window.size` | 1280 × 720 px | implementation constraint | Source studies used computer presentation but do not define this display. | `inferred` | Movie occupies 960 × 540 px with no stretching. |
| `trigger_map` | `triggers.map` | phase/family-specific codes 1–50 | implementation constraint | Behavioral source studies do not prescribe hardware trigger codes. | `inferred` | Codes distinguish playback family, replay, narrative, judgment, and timeout events. |

