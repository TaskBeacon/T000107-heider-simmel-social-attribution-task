from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class ScriptedResponder:
    rt_s: float = 0.05

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        return None

    def on_feedback(self, feedback: Feedback) -> None:
        return None

    def end_session(self) -> None:
        return None

    def act(self, observation: Observation) -> Action:
        keys = [str(key) for key in observation.valid_keys]
        if not keys:
            return Action(key=None, rt_s=None)
        if observation.phase == "narrative_response":
            return Action(key="return" if "return" in keys else keys[0], rt_s=float(self.rt_s))
        if observation.phase == "motion_family_judgment":
            correct = str(observation.task_factors.get("correct_key", keys[0]))
            return Action(key=correct if correct in keys else keys[0], rt_s=float(self.rt_s))
        return Action(key="space" if "space" in keys else keys[0], rt_s=float(self.rt_s))


@dataclass
class TaskSamplerResponder:
    accuracy: float = 0.84
    timeout_rate: float = 0.08
    rt_s: float = 0.05

    def __post_init__(self) -> None:
        self._rng: Any = None

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, feedback: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _random(self) -> float:
        return float(self._rng.random()) if self._rng is not None else 0.5

    def act(self, observation: Observation) -> Action:
        keys = [str(key) for key in observation.valid_keys]
        if not keys:
            return Action(key=None, rt_s=None)
        if observation.phase == "narrative_response":
            if self._random() < float(self.timeout_rate):
                return Action(key=None, rt_s=None)
            return Action(key="return" if "return" in keys else keys[0], rt_s=float(self.rt_s))
        if observation.phase == "motion_family_judgment":
            if self._random() < float(self.timeout_rate):
                return Action(key=None, rt_s=None)
            correct = str(observation.task_factors.get("correct_key", keys[0]))
            if self._random() <= float(self.accuracy) and correct in keys:
                key = correct
            else:
                alternatives = [key for key in keys if key != correct]
                key = alternatives[int(self._random() * len(alternatives)) % len(alternatives)] if alternatives else keys[0]
            return Action(key=key, rt_s=float(self.rt_s))
        return Action(key="space" if "space" in keys else keys[0], rt_s=float(self.rt_s))
