"""
FastAPI application for the Email Triage Environment.

Uses openenv-core's create_app factory which provides:
  POST /reset   — reset the environment
  POST /step    — take one action
  GET  /state   — current state
  GET  /schema  — action/observation JSON schemas
  WS   /ws      — WebSocket endpoint for persistent sessions
  GET  /health  — liveness probe
"""

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv-core is required. Install with: pip install openenv-core"
    ) from e

try:
    from ..models import EmailAction, EmailObservation
    from .email_triage_environment import EmailTriageEnvironment
except ImportError:
    from models import EmailAction, EmailObservation
    from server.email_triage_environment import EmailTriageEnvironment


app = create_app(
    EmailTriageEnvironment,
    EmailAction,
    EmailObservation,
    env_name="email_triage_env",
    max_concurrent_envs=4,
)


@app.get("/")
def root():
    return {"status": "ok", "env": "email-triage-env", "tasks": ["classify_email", "prioritize_inbox", "draft_reply"]}


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
