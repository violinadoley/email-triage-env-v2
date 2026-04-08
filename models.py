"""
Data models for the Email Triage Environment.

EmailAction  - action the agent submits (classification, ranking, or reply text)
EmailObservation - what the agent observes (email content + feedback after step)
"""

from typing import Any, Dict, List, Optional

from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class EmailAction(Action):
    """Action submitted by the agent for any email triage task."""

    action_type: str = Field(
        ...,
        description=(
            "Type of action: 'classify' | 'rank' | 'reply'. "
            "Must match the current task."
        ),
    )
    content: str = Field(
        ...,
        description=(
            "The agent's response. "
            "For classify: one of spam/work/personal/newsletter. "
            "For rank: comma-separated email IDs from most to least urgent, e.g. '3,1,5,2,4'. "
            "For reply: the full reply text."
        ),
    )


class EmailObservation(Observation):
    """Observation returned by the environment after reset() or step()."""

    task_name: str = Field(default="", description="Current task name")
    email_content: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "For classify/reply: dict with subject, body, sender, timestamp. "
            "For rank: dict with key 'emails' containing a list of email dicts."
        ),
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Task instructions, valid categories, email IDs, etc.",
    )
    step_count: int = Field(default=0, description="Number of steps taken this episode")
    score: float = Field(default=0.0, description="Score from last step (0.0 before first step)")
    feedback: str = Field(default="", description="Grader feedback from last step")
    valid_actions: List[str] = Field(
        default_factory=list,
        description="Valid action_type values for the current task",
    )
