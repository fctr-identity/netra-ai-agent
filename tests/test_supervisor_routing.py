"""Small offline regression checks for dependent discovery steps."""
from tests import CHECKS  # Initialize synthetic configuration before agent imports.
import unittest

from src.core.agents.supervisor_agent import (
    SupervisorDecision, _normalize_after_delegation_decision,
)
from src.data.schemas.artifact_manifest import DelegationResult


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


if __name__ == '__main__':
    unittest.main()
