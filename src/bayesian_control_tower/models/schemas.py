"""Domain schemas for the Bayesian control layer.

These are the typed contracts for what the A2A server accepts and returns.
The A2A protocol wraps these as task message parts.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class AgentState(BaseModel):
    """Current state snapshot of a single agent in the multi-agent system."""

    agent_id: str
    role: str
    current_action: str
    confidence: float = Field(ge=0.0, le=1.0, description="Agent's self-reported confidence 0–1")
    observations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PriorBelief(BaseModel):
    """A named prior probability belief to seed Bayesian inference."""

    name: str
    probability: float = Field(ge=0.0, le=1.0)
    description: str = ""


class DecisionOption(BaseModel):
    """One branch of a decision point, with an optional prior likelihood."""

    label: str
    description: str = ""
    prior_likelihood: float | None = Field(default=None, ge=0.0, le=1.0)


class DecisionPoint(BaseModel):
    """A decision junction the multi-agent system needs guidance on."""

    description: str
    options: list[DecisionOption] = Field(min_length=2)
    context: str = ""

    @field_validator("options")
    @classmethod
    def options_have_unique_labels(cls, v: list[DecisionOption]) -> list[DecisionOption]:
        labels = [o.label for o in v]
        if len(labels) != len(set(labels)):
            raise ValueError("DecisionOption labels must be unique")
        return v


class BayesianAdviceRequest(BaseModel):
    """Full request payload sent to the Bayesian control agent."""

    system_id: str = Field(description="Identifier for the multi-agent system instance")
    agent_states: list[AgentState] = Field(min_length=1)
    decision_point: DecisionPoint
    prior_beliefs: list[PriorBelief] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list, description="Observed evidence strings")
    session_id: str | None = None


class Recommendation(BaseModel):
    """A single ranked recommendation from the Bayesian layer."""

    option_label: str
    posterior_probability: float = Field(ge=0.0, le=1.0)
    rationale: str
    confidence_interval: tuple[float, float] | None = None


class BayesianAdviceResponse(BaseModel):
    """Response from the Bayesian control agent."""

    system_id: str
    recommendations: list[Recommendation] = Field(min_length=1)
    uncertainty_summary: str
    next_evidence_to_seek: list[str] = Field(default_factory=list)
    raw_reasoning: str = ""
