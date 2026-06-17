"""Shared pytest fixtures."""

import pytest

from bayesian_control_tower.models.schemas import (
    AgentState,
    BayesianAdviceRequest,
    DecisionOption,
    DecisionPoint,
    PriorBelief,
)


@pytest.fixture
def agent_state() -> AgentState:
    return AgentState(
        agent_id="agent-1",
        role="planner",
        current_action="evaluate_options",
        confidence=0.72,
        observations=["data ingested", "anomaly detected in stream-A"],
    )


@pytest.fixture
def decision_point() -> DecisionPoint:
    return DecisionPoint(
        description="Should the orchestrator escalate to a human reviewer?",
        options=[
            DecisionOption(label="escalate", description="Route to human", prior_likelihood=0.3),
            DecisionOption(
                label="continue", description="Proceed autonomously", prior_likelihood=0.7
            ),
        ],
        context="Anomaly score exceeded threshold twice in last 5 minutes.",
    )


@pytest.fixture
def advice_request(agent_state: AgentState, decision_point: DecisionPoint) -> BayesianAdviceRequest:
    return BayesianAdviceRequest(
        system_id="sys-test-001",
        agent_states=[agent_state],
        decision_point=decision_point,
        prior_beliefs=[PriorBelief(name="anomaly_is_critical", probability=0.4)],
        evidence=["threshold_exceeded_twice", "no_prior_false_positives"],
        session_id="session-abc",
    )
