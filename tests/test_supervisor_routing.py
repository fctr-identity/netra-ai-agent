"""Small offline regression checks for dependent discovery steps."""
from tests import CHECKS  # Initialize synthetic configuration before agent imports.
import unittest
from unittest.mock import AsyncMock, Mock, patch

from src.core.agents.supervisor_agent import (
    SupervisorDecision, _normalize_after_delegation_decision,
)
from src.data.schemas.artifact_manifest import DelegationResult
from src.core.agents.orchestrator import (
    OrchestratorResult, _ask_supervisor_after_delegation, _next_target_transition,
)


class SupervisorRoutingTests(unittest.TestCase):
    def test_successful_device_list_allows_a_dependent_device_detail_lookup(self):
        listed = DelegationResult(
            success=True, source_specialist='api', result_mode='synthesis_ready',
            summary='Device list retrieved successfully.',
            artifact_keys=['device_list'], result_set_refs=['device_rows'],
        )
        next_step = SupervisorDecision(
            mode='delegate', target='API',
            reasoning='The first device still needs its approximate last sign-in.',
            requested_data=['Retrieve the first listed device detail, including approximateLastSignInDateTime.'],
        )

        decision = _normalize_after_delegation_decision(next_step, listed)

        self.assertEqual((decision.mode, decision.target), ('delegate', 'API'))
        self.assertEqual(decision.requested_data, next_step.requested_data)

    def test_completion_still_requires_success_and_evidence(self):
        for success in (False, True):
            with self.subTest(success=success):
                latest = DelegationResult(
                    success=success, source_specialist='api',
                    result_mode='synthesis_ready' if success else 'failed',
                    summary='No usable evidence.',
                )
                decision = _normalize_after_delegation_decision(
                    SupervisorDecision(mode='complete', target='SYNTHESIS', reasoning='Finish.'),
                    latest,
                )
                self.assertEqual(decision.mode, 'fail')


class FollowupRoutingTests(unittest.IsolatedAsyncioTestCase):
    async def test_distinct_api_steps_continue_but_duplicate_work_stops(self):
        result = OrchestratorResult()
        seen = set()
        aggregator = Mock(step_start=AsyncMock())
        requirements = [
            'Fetch direct and transitive group memberships for user u1.',
            'Fetch app assignments for user u1 and their direct groups.',
            'Fetch app assignments for user u1 and their direct groups.',
        ]
        for index, requirement in enumerate(requirements):
            with self.subTest(step=index):
                latest = DelegationResult(
                    success=True, source_specialist='api', result_mode='synthesis_ready',
                    summary='Previous step completed.', artifact_keys=['saved_evidence'],
                )
                decision = SupervisorDecision(
                    mode='delegate', target='API', reasoning=requirement,
                    requested_data=[requirement],
                )
                with patch('src.core.agents.orchestrator.supervise_next_step',
                           new=AsyncMock(return_value=(decision, None))):
                    target = await _ask_supervisor_after_delegation(
                        user_query='Compare memberships and app assignments.',
                        correlation_id='offline-routing', artifacts_file=CHECKS / 'unused.json',
                        result=result, latest_delegation=latest, db_runtime_summary={},
                        special_tool_capabilities={}, workflow_state={}, aggregator=aggregator,
                    )
                transition = _next_target_transition(
                    next_target=target, source_label='API', source_delegation=latest,
                    seen_requirement_steps=seen,
                )
                self.assertEqual(transition.repeated, index == 2)
                if index < 2:
                    self.assertEqual(transition.pending_api_request, [requirement])


if __name__ == '__main__':
    unittest.main()
