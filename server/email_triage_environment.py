"""
Email Triage Environment.

DESIGN: Stateful environment that stores reset() state in self.
- WebSocket sessions (used by inference.py + eval): reset() -> step() share state
- HTTP /reset with empty body: still returns 200 (pre-submission validator requirement)
- HTTP /step without prior reset: falls back to defaults safely

Three tasks (difficulty ascending):
  0  classify_email   (easy)    exact-match 0.0/1.0
  1  prioritize_inbox (medium)  Kendall-tau distance 0.0-1.0
  2  draft_reply      (hard)    rubric-based 0.0-1.0
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import EmailAction, EmailObservation
    from .email_data import CLASSIFY_EMAILS, PRIORITIZE_SCENARIOS, DRAFT_REPLY_EMAILS
    from .graders import grade_classify, grade_prioritize, grade_draft_reply
except ImportError:
    try:
        from models import EmailAction, EmailObservation
        from server.email_data import CLASSIFY_EMAILS, PRIORITIZE_SCENARIOS, DRAFT_REPLY_EMAILS
        from server.graders import grade_classify, grade_prioritize, grade_draft_reply
    except ImportError:
        from models import EmailAction, EmailObservation  # type: ignore[no-redef]
        from email_data import CLASSIFY_EMAILS, PRIORITIZE_SCENARIOS, DRAFT_REPLY_EMAILS  # type: ignore[no-redef]
        from graders import grade_classify, grade_prioritize, grade_draft_reply  # type: ignore[no-redef]

TASK_NAMES = ["classify_email", "prioritize_inbox", "draft_reply"]
_DATASETS = [CLASSIFY_EMAILS, PRIORITIZE_SCENARIOS, DRAFT_REPLY_EMAILS]


class EmailTriageEnvironment(Environment):
    """Stateful email triage environment. Each WebSocket session gets its own instance."""

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self) -> None:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task_index: int = 0
        self._scenario_idx: int = 0
        self._classify_label: Optional[str] = None
        self._prioritize_ranking: Optional[List[int]] = None
        self._draft_data: Optional[Dict[str, Any]] = None
        self._current_email: Optional[Dict[str, Any]] = None
        self._current_context: Dict[str, Any] = {}

    def reset(self, task_index: int = 0, scenario_idx: Optional[int] = None, **kwargs: Any) -> EmailObservation:
        """Reset for the given task. Stores state for use by step()."""
        self._task_index = int(task_index) % len(TASK_NAMES)
        dataset = _DATASETS[self._task_index]

        if scenario_idx is None:
            self._scenario_idx = random.randint(0, len(dataset) - 1)
        else:
            self._scenario_idx = int(scenario_idx) % len(dataset)

        self._state = State(episode_id=str(uuid4()), step_count=0)
        task = TASK_NAMES[self._task_index]

        if task == "classify_email":
            sample = dataset[self._scenario_idx]
            self._classify_label = sample["label"]
            self._current_email = sample["email"]
            self._current_context = {
                "task_index": self._task_index,
                "scenario_idx": self._scenario_idx,
                "instructions": (
                    "Classify this email into exactly one category: "
                    "spam, work, personal, or newsletter. "
                    "Respond with ONLY the category name."
                ),
                "valid_categories": ["spam", "work", "personal", "newsletter"],
                "difficulty": "easy",
            }

        elif task == "prioritize_inbox":
            scenario = dataset[self._scenario_idx]
            self._prioritize_ranking = scenario["correct_ranking"]
            rng = random.Random(self._scenario_idx * 137)
            emails = list(scenario["emails"])
            rng.shuffle(emails)
            self._current_email = {"emails": emails}
            self._current_context = {
                "task_index": self._task_index,
                "scenario_idx": self._scenario_idx,
                "instructions": (
                    "Rank these 5 emails by urgency, most urgent first. "
                    "Respond with ONLY a comma-separated list of email IDs. "
                    "Example: '3,1,5,2,4'"
                ),
                "email_ids": [e["id"] for e in emails],
                "difficulty": "medium",
            }

        else:  # draft_reply
            sample = dataset[self._scenario_idx]
            self._draft_data = sample
            self._current_email = sample["email"]
            self._current_context = {
                "task_index": self._task_index,
                "scenario_idx": self._scenario_idx,
                **sample.get("context", {}),
                "difficulty": "hard",
                "rubric": (
                    "greeting(0.10) + body>=30words(0.20) + closing(0.10) "
                    "+ length50-1000chars(0.20) + keyword_overlap(0.40)"
                ),
            }

        return EmailObservation(
            task_name=task,
            email_content=self._current_email,
            context=self._current_context,
            step_count=0,
            done=False,
            reward=0.0,
            score=0.0,
            feedback="",
            valid_actions=[TASK_NAMES[self._task_index].split("_")[0]
                          if self._task_index == 0 else
                          "rank" if self._task_index == 1 else "reply"],
        )

    def step(self, action: EmailAction, **kwargs: Any) -> EmailObservation:  # type: ignore[override]
        """Grade the action using state stored by reset()."""
        self._state.step_count += 1
        task = TASK_NAMES[self._task_index]

        if task == "classify_email":
            label = self._classify_label or _DATASETS[0][self._scenario_idx]["label"]
            reward, score, feedback = grade_classify(action.content, label)
            email_content = self._current_email or _DATASETS[0][self._scenario_idx]["email"]

        elif task == "prioritize_inbox":
            scenario = _DATASETS[1][self._scenario_idx]
            ranking = self._prioritize_ranking or scenario["correct_ranking"]
            reward, score, feedback = grade_prioritize(action.content, ranking)
            email_content = self._current_email or {"emails": scenario["emails"]}

        else:  # draft_reply
            sample = self._draft_data or _DATASETS[2][self._scenario_idx]
            reward, score, feedback = grade_draft_reply(action.content, sample)
            email_content = self._current_email or sample["email"]

        return EmailObservation(
            task_name=task,
            email_content=email_content,
            context={
                "task_index": self._task_index,
                "scenario_idx": self._scenario_idx,
                "last_action": action.content[:200],
            },
            step_count=self._state.step_count,
            done=True,
            reward=reward,
            score=score,
            feedback=feedback,
            valid_actions=[],
        )

    @property
    def state(self) -> State:
        return self._state
