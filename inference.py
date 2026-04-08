"""
inference.py - Email Triage Environment baseline inference script.

Runs all 3 tasks (classify_email, prioritize_inbox, draft_reply) sequentially
using an OpenAI-compatible LLM to generate actions.

The script connects to the environment via WebSocket (persistent session), so
state from reset() is preserved when step() is called.

Environment variables
---------------------
API_BASE_URL   OpenAI-compatible API base URL
               (default: https://router.huggingface.co/v1)
MODEL_NAME     Model identifier
               (default: Qwen/Qwen2.5-72B-Instruct)
HF_TOKEN       HuggingFace / API token (required for default endpoint)
IMAGE_NAME     Docker image name (default: email-triage-env:latest)
ENV_URL        Override to connect to a running server instead of Docker
               (e.g. https://your-space.hf.space)

Stdout format
-------------
[START] task=<task_name> env=<benchmark> model=<model_name>
[STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
[END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Any, Dict, List, Optional

from openai import OpenAI

from email_triage_env import EmailTriageEnv, EmailAction

# ─── Configuration ────────────────────────────────────────────────────────────

API_BASE_URL: str = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME: str = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN: Optional[str] = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME: str = os.getenv("LOCAL_IMAGE_NAME", "email-triage-env:latest")
ENV_URL: Optional[str] = os.getenv("ENV_URL") or "https://violinadoley25-email-triage-env.hf.space"

BENCHMARK = "email-triage-env"
MAX_STEPS = 3
TEMPERATURE = 0.1
MAX_TOKENS = 512
SUCCESS_THRESHOLD = 0.1

TASKS = [
    {"index": 0, "name": "classify_email",   "action_type": "classify"},
    {"index": 1, "name": "prioritize_inbox", "action_type": "rank"},
    {"index": 2, "name": "draft_reply",      "action_type": "reply"},
]

# ─── OpenAI client ────────────────────────────────────────────────────────────

_llm: Optional[OpenAI] = None


def get_llm() -> OpenAI:
    global _llm
    if _llm is None:
        _llm = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    return _llm


# ─── Logging ──────────────────────────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    safe = action.replace("\n", " ").replace("\r", "")[:120]
    err = error if error else "null"
    done_str = "true" if done else "false"
    print(f"[STEP] step={step} action={safe} reward={reward:.2f} done={done_str} error={err}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
    success_str = "true" if success else "false"
    print(f"[END] success={success_str} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)


# ─── Prompt builders ─────────────────────────────────────────────────────────

def _build_prompt(obs: Any) -> str:
    task = obs.task_name
    email = obs.email_content
    ctx = obs.context

    if task == "classify_email":
        return (
            "You are an email classification assistant.\n\n"
            f"From: {email.get('sender', '')}\n"
            f"Subject: {email.get('subject', '')}\n"
            f"Body:\n{email.get('body', '')}\n\n"
            "Instructions: Classify this email into exactly one of: spam, work, personal, newsletter.\n"
            "Respond with ONLY the single category word. No explanation."
        )

    elif task == "prioritize_inbox":
        emails = email.get("emails", [])
        lines = [
            f"--- Email ID {e['id']} ---\n"
            f"From: {e.get('sender', '')}\n"
            f"Subject: {e.get('subject', '')}\n"
            f"Body: {e.get('body', '')[:250]}"
            for e in emails
        ]
        return (
            "You are an inbox prioritization assistant.\n\n"
            f"Instructions: {ctx.get('instructions', '')}\n\n"
            + "\n".join(lines)
            + "\n\nRespond with ONLY a comma-separated list of email IDs from most to least urgent. "
            "Example: '3,1,5,2,4'. No explanation."
        )

    elif task == "draft_reply":
        instructions = ctx.get("instructions", "Write a professional reply.")
        return (
            "You are a professional email writer.\n\n"
            f"From: {email.get('sender', '')}\n"
            f"Subject: {email.get('subject', '')}\n"
            f"Body:\n{email.get('body', '')}\n\n"
            f"Task: {instructions}\n\n"
            "Write a complete professional reply with: greeting, substantive body "
            "(at least 3 sentences), professional closing. Keep it under 300 words."
        )

    return f"Task: {task}\n{str(obs)[:400]}"


def generate_action(obs: Any) -> str:
    prompt = _build_prompt(obs)
    completion = get_llm().chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant completing email management tasks. "
                    "Follow instructions precisely. Respond in the exact format requested."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    return (completion.choices[0].message.content or "").strip()


# ─── Task runner ─────────────────────────────────────────────────────────────

async def run_task(
    env: EmailTriageEnv,
    task_index: int,
    task_name: str,
    action_type: str,
) -> Dict[str, Any]:
    """Run one task episode. Emits [START], [STEP], [END] to stdout."""
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    rewards: List[float] = []
    steps_taken = 0
    final_score = 0.0
    success = False
    last_error: Optional[str] = None

    try:
        # reset() stores state in the env instance (stateful WebSocket session)
        result = await env.reset(task_index=task_index)
        obs = result.observation

        for step_n in range(1, MAX_STEPS + 1):
            if obs.done:
                break

            try:
                content = generate_action(obs)
            except Exception as exc:
                last_error = f"LLM error: {exc}"
                log_step(step=step_n, action="null", reward=0.0, done=False, error=last_error)
                break

            try:
                # step() uses state stored by reset() — no extra kwargs needed
                result = await env.step(EmailAction(action_type=action_type, content=content))
            except Exception as exc:
                last_error = f"Env error: {exc}"
                log_step(step=step_n, action=content, reward=0.0, done=False, error=last_error)
                break

            obs = result.observation
            reward = float(result.reward) if result.reward is not None else 0.0
            done = bool(result.done)
            steps_taken = step_n
            rewards.append(reward)
            last_error = None

            log_step(step=step_n, action=content, reward=reward, done=done, error=None)

            if done:
                final_score = float(obs.score) if obs.score is not None else reward
                final_score = max(0.0, min(1.0, final_score))
                success = final_score >= SUCCESS_THRESHOLD
                break

    except Exception as exc:
        last_error = str(exc)
        print(f"[DEBUG] run_task error: {exc}", file=sys.stderr, flush=True)

    finally:
        log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards)

    return {
        "task_name": task_name,
        "success": success,
        "steps": steps_taken,
        "score": final_score,
        "rewards": rewards,
        "error": last_error,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main() -> None:
    if ENV_URL:
        print(f"Connecting to environment at {ENV_URL} ...", flush=True)
        env = EmailTriageEnv(base_url=ENV_URL)
    else:
        print(f"Starting environment from Docker image: {LOCAL_IMAGE_NAME} ...", flush=True)
        env = await EmailTriageEnv.from_docker_image(LOCAL_IMAGE_NAME)

    all_results: List[Dict[str, Any]] = []

    try:
        for task in TASKS:
            result = await run_task(
                env=env,
                task_index=task["index"],
                task_name=task["name"],
                action_type=task["action_type"],
            )
            all_results.append(result)
            print(flush=True)

    finally:
        try:
            await env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error: {e}", file=sys.stderr, flush=True)

    total = sum(r["score"] for r in all_results) / len(all_results)
    print("=" * 60, flush=True)
    print(f"OVERALL SCORE: {total:.4f}", flush=True)
    for r in all_results:
        tag = "PASS" if r["success"] else "FAIL"
        print(f"  [{tag}] {r['task_name']:25s} score={r['score']:.4f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
