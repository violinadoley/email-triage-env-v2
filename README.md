---
title: Email Triage Environment
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Email Triage Environment

An OpenEnv environment for training and evaluating AI agents on real-world email management tasks.

## Overview

Email triage is one of the most common daily tasks for knowledge workers — sorting through inboxes, identifying urgent messages, and crafting professional replies. This environment provides a standardized benchmark where agents learn to:

1. **Classify emails** into spam, work, personal, or newsletter categories
2. **Prioritize an inbox** by urgency using Kendall-tau-scored ranking
3. **Draft professional replies** evaluated by a deterministic rubric

All tasks use deterministic graders with no LLM dependency — results are fully reproducible.

---

## Tasks

| Task | Difficulty | Action Type | Scoring |
|---|---|---|---|
| `classify_email` | Easy | `classify` | Exact match → 0.0 or 1.0 |
| `prioritize_inbox` | Medium | `rank` | Kendall-tau distance → 0.0–1.0 |
| `draft_reply` | Hard | `reply` | Rubric-based → 0.0–1.0 |

### Task 1: classify_email (Easy)
The agent receives a single email (subject, body, sender, timestamp) and must classify it as exactly one of: `spam`, `work`, `personal`, `newsletter`.

- **Score 1.0**: correct label
- **Score 0.0**: wrong label or invalid response

### Task 2: prioritize_inbox (Medium)
The agent sees 5 emails and must return a comma-separated list of email IDs ranked from most to least urgent (e.g., `"3,1,5,2,4"`).

- **Score 1.0**: perfect ranking
- **Score 0.0**: completely reversed
- **Partial credit**: proportional to Kendall-tau distance from ground truth

### Task 3: draft_reply (Hard)
The agent drafts a professional reply to a work email. Scored on a 5-criterion rubric:

| Criterion | Weight |
|---|---|
| Greeting present | 0.10 |
| Body ≥ 30 words | 0.20 |
| Closing present | 0.10 |
| Length 50–1000 chars | 0.20 |
| Keyword overlap with original email | 0.40 |

---

## Action & Observation Spaces

### Action: `EmailAction`
```json
{
  "action_type": "classify | rank | reply",
  "content": "<string response>"
}
```

### Observation: `EmailObservation`
```json
{
  "task_name": "classify_email",
  "email_content": { "subject": "...", "body": "...", "sender": "...", "timestamp": "..." },
  "context": {
    "instructions": "...",
    "valid_categories": ["spam", "work", "personal", "newsletter"],
    "difficulty": "easy"
  },
  "step_count": 0,
  "done": false,
  "reward": 0.0,
  "score": 0.0,
  "feedback": "",
  "valid_actions": ["classify"]
}
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe |
| `GET` | `/state` | Current environment state |
| `POST` | `/reset` | Reset to a task (`{"task_index": 0}`) |
| `POST` | `/step` | Submit action (`{"action_type": "classify", "content": "spam"}`) |
| `GET` | `/schema` | Action/observation JSON schemas |
| `WS` | `/ws` | WebSocket for persistent sessions |

---

## Setup

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Docker
- Hugging Face CLI

### Install
```bash
git clone https://github.com/violinadoley/email-triage-env
cd email-triage-env
uv sync
```

### Run locally
```bash
uv run server
# or
python -m server.app
```
Server starts at `http://localhost:8000`.

### Test with curl
```bash
# Reset to classify_email task
curl -X POST http://localhost:8000/reset -H 'Content-Type: application/json' \
  -d '{"task_index": 0}'

# Submit a classification
curl -X POST http://localhost:8000/step -H 'Content-Type: application/json' \
  -d '{"action_type": "classify", "content": "spam"}'
```

### Docker
```bash
docker build -t email-triage-env:latest -f server/Dockerfile .
docker run -p 8000:8000 email-triage-env:latest
```

---

## Running the Inference Script

```bash
# Against Docker (default)
export HF_TOKEN=hf_...
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export API_BASE_URL=https://router.huggingface.co/v1
python inference.py

# Against a deployed HF Space
export ENV_URL=https://your-username-email-triage-env.hf.space
python inference.py
```

### Expected output format
```
[START] task=classify_email env=email-triage-env model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=spam reward=1.00 done=true error=null
[END] success=true steps=1 score=1.00 rewards=1.00

[START] task=prioritize_inbox env=email-triage-env model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=1,2,5,3,4 reward=0.90 done=true error=null
[END] success=true steps=1 score=0.90 rewards=0.90

[START] task=draft_reply env=email-triage-env model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=Dear James, Thank you for... reward=0.80 done=true error=null
[END] success=true steps=1 score=0.80 rewards=0.80
```

---

## Baseline Scores

Measured with `Qwen/Qwen2.5-72B-Instruct` via HuggingFace router:

| Task | Score |
|---|---|
| classify_email | ~0.90 |
| prioritize_inbox | ~0.75 |
| draft_reply | ~0.70 |
| **Overall** | **~0.78** |

---

## Deploy to Hugging Face Spaces

```bash
openenv push --repo-id <your-username>/email-triage-env
```

Or manually:
```bash
huggingface-cli login
git remote add hf https://huggingface.co/spaces/<your-username>/email-triage-env
git push hf main
```

---

## Validation

```bash
# Install validator dependencies
pip install openenv-core docker

# Run pre-submission validation
./validate-submission.sh https://<your-space>.hf.space .
```

---

## License

MIT
