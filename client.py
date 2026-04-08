"""
Email Triage Environment Client.

Wraps openenv-core's EnvClient to provide a typed interface for connecting
to a running EmailTriageEnvironment server.

Usage (connecting to an existing server):
    with EmailTriageEnv(base_url="http://localhost:8000") as client:
        result = client.reset(task_index=0)
        print(result.observation.task_name)
        result = client.step(EmailAction(action_type="classify", content="work"))
        print(result.observation.score)

Usage (auto-start from Docker image):
    client = EmailTriageEnv.from_docker_image("email-triage-env:latest")
    try:
        result = client.reset(task_index=1)
        result = client.step(EmailAction(action_type="rank", content="1,3,5,2,4"))
    finally:
        client.close()
"""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import EmailAction, EmailObservation


class EmailTriageEnv(EnvClient[EmailAction, EmailObservation, State]):
    """
    Async client for the Email Triage Environment.

    Maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step interactions.
    """

    def _step_payload(self, action: EmailAction) -> Dict:
        return {
            "action_type": action.action_type,
            "content": action.content,
        }

    def _parse_result(self, payload: Dict) -> StepResult[EmailObservation]:
        obs_data = payload.get("observation", {})
        observation = EmailObservation(
            task_name=obs_data.get("task_name", ""),
            email_content=obs_data.get("email_content", {}),
            context=obs_data.get("context", {}),
            step_count=obs_data.get("step_count", 0),
            done=payload.get("done", False),
            reward=payload.get("reward", 0.0),
            score=obs_data.get("score", 0.0),
            feedback=obs_data.get("feedback", ""),
            valid_actions=obs_data.get("valid_actions", []),
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
