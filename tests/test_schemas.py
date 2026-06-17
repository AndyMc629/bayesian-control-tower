"""Tests for Pydantic domain schemas."""

import pytest
from pydantic import ValidationError

from bayesian_control_tower.models.schemas import (
    AgentState,
    BayesianAdviceRequest,
    BayesianAdviceResponse,
    DecisionOption,
    DecisionPoint,
    PriorBelief,
    Recommendation,
)


class TestAgentState:
    def test_valid(self, agent_state: AgentState) -> None:
        assert agent_state.agent_id == "agent-1"
        assert 0.0 <= agent_state.confidence <= 1.0

    def test_confidence_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            AgentState(agent_id="x", role="r", current_action="a", confidence=1.5)

    def test_defaults(self) -> None:
        state = AgentState(agent_id="x", role="r", current_action="a", confidence=0.5)
        assert state.observations == []
        assert state.metadata == {}


class TestDecisionPoint:
    def test_valid(self, decision_point: DecisionPoint) -> None:
        assert len(decision_point.options) == 2

    def test_requires_at_least_two_options(self) -> None:
        with pytest.raises(ValidationError):
            DecisionPoint(
                description="test",
                options=[DecisionOption(label="only-one")],
            )

    def test_duplicate_labels_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DecisionPoint(
                description="test",
                options=[
                    DecisionOption(label="same"),
                    DecisionOption(label="same"),
                ],
            )

    def test_prior_likelihood_bounds(self) -> None:
        with pytest.raises(ValidationError):
            DecisionOption(label="bad", prior_likelihood=1.5)


class TestPriorBelief:
    def test_valid(self) -> None:
        belief = PriorBelief(name="hypothesis_a", probability=0.6)
        assert belief.probability == 0.6

    def test_probability_clamped(self) -> None:
        with pytest.raises(ValidationError):
            PriorBelief(name="bad", probability=-0.1)


class TestBayesianAdviceRequest:
    def test_valid(self, advice_request: BayesianAdviceRequest) -> None:
        assert advice_request.system_id == "sys-test-001"
        assert len(advice_request.agent_states) == 1
        assert len(advice_request.prior_beliefs) == 1

    def test_requires_at_least_one_agent_state(self, decision_point: DecisionPoint) -> None:
        with pytest.raises(ValidationError):
            BayesianAdviceRequest(
                system_id="x",
                agent_states=[],
                decision_point=decision_point,
            )

    def test_roundtrip_json(self, advice_request: BayesianAdviceRequest) -> None:
        restored = BayesianAdviceRequest.model_validate_json(advice_request.model_dump_json())
        assert restored == advice_request


class TestBayesianAdviceResponse:
    def test_valid(self) -> None:
        resp = BayesianAdviceResponse(
            system_id="sys-001",
            recommendations=[
                Recommendation(
                    option_label="escalate",
                    posterior_probability=0.68,
                    rationale="Evidence shifts prior upward significantly.",
                )
            ],
            uncertainty_summary="Moderate uncertainty; CI is wide.",
        )
        assert resp.recommendations[0].posterior_probability == 0.68

    def test_requires_at_least_one_recommendation(self) -> None:
        with pytest.raises(ValidationError):
            BayesianAdviceResponse(
                system_id="x",
                recommendations=[],
                uncertainty_summary="n/a",
            )
