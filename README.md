# bayesian-control-tower

An [A2A-protocol](https://google.github.io/A2A/) server that exposes a **Bayesian control layer** as a sidecar for multi-agent systems. Any orchestrator can call it mid-decision to get probabilistically ranked next-step recommendations, uncertainty estimates, and guidance on what evidence to collect next.

- **Problem-agnostic** — advises on any decision point; no domain-specific logic baked in
- **Sidecar deployment** — sits alongside your existing agents, not a centralised controller
- **Model-agnostic** — ships with Anthropic (Claude), OpenAI, and Gemini support via LiteLLM

> Reference: [Bayesian approaches to multi-agent decision making (arXiv 2605.00742)](https://arxiv.org/pdf/2605.00742)

---

## Quickstart

**Prerequisites:** [uv](https://docs.astral.sh/uv/getting-started/installation/), Python ≥ 3.11, Docker (optional).

```bash
# 1. Clone and install
git clone <repo-url> && cd bayesian-control-tower
cp .env.example .env          # add your API keys
make install-dev

# 2. Run tests
make test

# 3. Start the server (auto-reload)
make dev
# → http://localhost:8000
# → http://localhost:8000/.well-known/agent.json  (agent card)
```

**Or with Docker:**
```bash
make build-image
make run-image
```

---

## Project layout

```
src/bayesian_control_tower/
│
├── server.py               # ← Entry point. A2A routes + agent card.
├── config.py               # ← Env vars / settings (DEFAULT_MODEL, PORT, etc.)
│
├── agent/
│   ├── bayesian_agent.py   # ← PRIMARY EDIT POINT: ADK LlmAgent instruction + model
│   ├── executor.py         # ← Bridges A2A protocol → ADK runner (task lifecycle)
│   └── memory.py           # ← Session service stub (swap for persistent backend here)
│
├── models/
│   └── schemas.py          # ← Pydantic contracts: BayesianAdviceRequest/Response
│
└── services/
    └── model_registry.py   # ← LiteLLM model aliases (add/swap models here)

notebooks/                  # Experimentation — run schema queries, manual Bayes updates
tests/                      # pytest suite (88% coverage); mirrors src/ structure
```

---

## Where to build

| What you're adding | Where to edit |
|---|---|
| Agent reasoning / system prompt | `agent/bayesian_agent.py` — `SYSTEM_INSTRUCTION` |
| Bayesian inference engine (PyMC, pgmpy) | `agent/bayesian_agent.py` + new `services/inference.py` |
| Agent tools (telemetry, state queries) | `agent/bayesian_agent.py` — `tools=[]` |
| Persistent memory / cross-session recall | `agent/memory.py` — swap `InMemorySessionService` |
| New LLM provider or model alias | `services/model_registry.py` — `_CATALOGUE` |
| Additional A2A skills | `server.py` — `_AGENT_CARD.skills` |
| New request/response fields | `models/schemas.py` |

---

## Configuration

All config is via environment variables (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `DEFAULT_MODEL` | `litellm/anthropic/claude-sonnet-4-6` | LiteLLM model string |
| `ANTHROPIC_API_KEY` | — | Required for Claude models |
| `OPENAI_API_KEY` | — | Required for OpenAI models |
| `GOOGLE_API_KEY` | — | Required for Gemini models |
| `PORT` | `8000` | Server port |

**Model string format** (LiteLLM prefix for non-Gemini):
```
litellm/anthropic/claude-sonnet-4-6
litellm/openai/gpt-4o
gemini-2.0-flash              ← Gemini needs no prefix
```

---

## Development

```bash
make test          # run pytest with coverage
make lint          # ruff check
make format        # ruff format
make typecheck     # mypy
make check         # all of the above
```

Tests live in `tests/` and mirror `src/`. The executor's live ADK calls are not exercised in unit tests — mock the runner at that boundary when you add integration tests.

---

## A2A protocol

The server speaks the [A2A protocol](https://google.github.io/A2A/). Key endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/.well-known/agent.json` | GET | Agent card (capabilities, skills) |
| `/message:send` | POST | Send a task, get a synchronous response |
| `/message:stream` | POST | Send a task, stream events (SSE) |
| `/tasks/{id}` | GET | Fetch task status |

Send a request:
```bash
curl -X POST http://localhost:8000/message:send \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [{ "text": "<BayesianAdviceRequest JSON here>" }]
    }
  }'
```

See `notebooks/01_bayesian_exploration.ipynb` for schema construction examples.

---

## Contributing

Branch from `main`, open a PR — CI must pass before merge. See `.github/workflows/ci.yml`.
