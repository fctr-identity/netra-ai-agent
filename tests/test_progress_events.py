"""Focused offline checks for public status and bounded Graph waiting."""
from tests import CHECKS
import contextlib
import io
import json
import time
import unittest
from unittest.mock import AsyncMock, patch

from src.core.progress_events import public_agent_event, public_progress


class PublicProgressChecks(unittest.IsolatedAsyncioTestCase):
    def test_public_events_exclude_internal_payloads(self):
        private = {'text': 'PRIVATE_REASONING', 'description': 'PRIVATE_USER',
                   'headers': {'Authorization': 'PRIVATE_TOKEN'}, 'data': ['PRIVATE_RECORD']}
        events = [public_agent_event('step_start', {**private, 'phase': 'api', 'step': 1}),
                  public_agent_event('tool_call', {**private, 'tool_name': 'execute_test_query_api', 'test_id': 'test-1'}),
                  public_agent_event('step_end', {**private, 'success': False}),
                  public_progress({**private, 'kind': 'api_test_request', 'test_id': 'test-1',
                                   'request_id': 'request-1', 'operation': 'sign_in.get',
                                   'status': 'retry_wait', 'elapsed_ms': 20000, 'retry_after_seconds': 3})]
        self.assertNotIn('PRIVATE', json.dumps(events))
        self.assertEqual(events[-1]['details']['retry_after_seconds'], 3)
        self.assertNotIn('text', events[0])
        self.assertIsNone(public_progress({'kind': 'internal', **private}))

    def test_graph_deadline_leaves_worker_headroom(self):
        from src.config.settings import settings
        from src.core.process_runner import graph_execution_timeout
        for seconds, expected in [(90, 120), (120, 150)]:
            with patch.object(settings, 'GRAPH_TIMEOUT_SECONDS', seconds):
                self.assertEqual(graph_execution_timeout(), expected)

    async def test_discovery_timeout_emits_a_terminal_status(self):
        from src.core.agents.api_discovery_agent import APIDiscoveryDeps, create_api_toolset
        progress = AsyncMock()
        deps = APIDiscoveryDeps(correlation_id='offline-timeout', artifacts_file=CHECKS / 'unused.json',
                                progress_callback=progress)
        with patch('src.core.process_runner.run_worker', new=AsyncMock(side_effect=TimeoutError())):
            result = await create_api_toolset(deps).tools['execute_test_query'].function('async def sample():\n    return []')
        self.assertFalse(result.metadata['success'])
        self.assertEqual(progress.call_args.args[0]['details']['status'], 'timed_out')

    async def test_sdk_retry_is_visible_without_leaking_http_payload(self):
        import httpx
        from src.config.settings import settings
        from src.core.entra.client.graph_client import EntraAPIClient
        from src.core.entra.client.request_trace import request_context

        attempts = []
        async def respond(transport, request):
            attempts.append(request)
            if len(attempts) == 1:
                return httpx.Response(429, headers={'Retry-After': '1'}, request=request)
            return httpx.Response(200, json={'id': 'PRIVATE_RECORD'}, request=request)

        output = io.StringIO()
        client = EntraAPIClient()
        token = request_context.set({'kind': 'graph_request', 'request_id': 'request-1',
                                     'operation': 'user.get', 'started': time.monotonic()})
        try:
            with patch.object(settings, 'ENTRA_CLIENT_ID', 'fixture-id'), \
                 patch.object(settings, 'ENTRA_CLIENT_SECRET', 'PRIVATE_SECRET'), \
                 patch.object(httpx.AsyncHTTPTransport, 'handle_async_request', respond), \
                 patch('kiota_http.middleware.retry_handler.asyncio.sleep', new=AsyncMock()), \
                 contextlib.redirect_stderr(output):
                client._initialize_sdk()
                response = await client._http.get('https://graph.microsoft.com/v1.0/users/PRIVATE_ID',
                                                  extensions={'kiota_request_options': {}})
                self.assertEqual(response.status_code, 200)
        finally:
            request_context.reset(token)
            await client.close_session()
        captured = output.getvalue()
        self.assertNotIn('PRIVATE', captured)
        self.assertNotIn('https://', captured)
        states = [json.loads(line[len('__PROGRESS__'):])['details']['status']
                  for line in captured.splitlines() if line.startswith('__PROGRESS__')]
        self.assertEqual(states, ['retry_wait', 'retrying'])
        first = json.loads(next(line[len('__PROGRESS__'):] for line in captured.splitlines()
                               if line.startswith('__PROGRESS__')))
        self.assertEqual(public_progress(first['details'])['details']['reason'], 'rate_limit')
        timings = [json.loads(line[len('__NETRA_HTTP__'):]) for line in captured.splitlines()
                   if line.startswith('__NETRA_HTTP__')]
        self.assertEqual([item['http_status'] for item in timings], [429, 200])
        self.assertEqual([item['attempt'] for item in timings], [0, 1])
