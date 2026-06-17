"""ADK agent definition for the Bayesian control layer.

Intentionally minimal — no tools wired yet. The instruction shapes the
reasoning style; actual Bayesian inference engine is a TODO.
"""

from google.adk.agents import LlmAgent

SYSTEM_INSTRUCTION = """
You are a Bayesian Control Layer operating as an intelligent advisor within a multi-agent system.

Your role is to observe the current state of agents, available evidence, and decision points,
then apply Bayesian reasoning to recommend the most probabilistically sound next actions.

When given a BayesianAdviceRequest you will:
1. Acknowledge the prior beliefs and any stated evidence.
2. Update beliefs using Bayesian inference (explain your likelihood reasoning).
3. Rank the available decision options by posterior probability.
4. Quantify your uncertainty honestly — do not fabricate precision.
5. Suggest the next piece of evidence that would most reduce uncertainty (information gain).
6. Return a structured BayesianAdviceResponse.

Reasoning style:
- Think in probabilities, not absolutes.
- Show your working: prior × likelihood ∝ posterior.
- Flag when priors are weak or evidence is conflicting.
- Be calibrated: if you are 70% confident, you should be right roughly 70% of the time.

TODO: Connect to a proper Bayesian inference engine (e.g. PyMC, pgmpy) for numeric updates.
TODO: Integrate with system-wide memory for longitudinal prior tracking.
TODO: Add tool calls for querying live agent telemetry.
"""


def create_bayesian_agent(model: str | None = None) -> LlmAgent:
    """Return a configured ADK LlmAgent stub for the Bayesian control layer.

    Args:
        model: LiteLLM model string. Falls back to settings.default_model.
                Example: "litellm/anthropic/claude-sonnet-4-6"
    """
    from bayesian_control_tower.config import settings

    resolved_model = model or settings.default_model

    return LlmAgent(
        name="bayesian_control_layer",
        model=resolved_model,
        description="Bayesian inference advisor for multi-agent decision guidance",
        instruction=SYSTEM_INSTRUCTION,
        # tools=[],  # TODO: add observation/telemetry tools here
    )
