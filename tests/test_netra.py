"""Focused POC checks. No tenant, model-provider calls, or real configuration file."""
import asyncio
import json
import unittest
from tests import CHECKS

from src.core.entra.client.graph_client import EntraAPIClient, catalog, operation_for
from src.core.models.context_policy import project_context, ContextPolicyModel


class GraphChecks(unittest.IsolatedAsyncioTestCase):
    async def test_paging_and_read_boundary(self):
        calls = []
        async def page(url, headers):
            calls.append((url, headers))
            if len(calls) == 1:
                return {'value': [{'id': 'first'}], '@odata.nextLink': 'https://graph.microsoft.com/v1.0/users?$skiptoken=opaque'}
            return {'value': [{'id': 'second'}]}
        client = EntraAPIClient(page_reader=page)
        result = await client.make_request('/users', params={'$filter': 'accountEnabled eq true'})
        self.assertEqual([item['id'] for item in result['data']], ['first', 'second'])
        self.assertTrue(result['complete'])
        self.assertEqual(calls[0][1], calls[1][1])
        for endpoint, method in [('/users', 'POST'), ('https://example.org/users', 'GET'), ('/me/messages', 'GET')]:
            self.assertEqual((await client.make_request(endpoint, method=method))['status'], 'error')
        self.assertEqual(len(calls), 2)

    async def test_hostile_continuation_and_discovery_limit(self):
        async def bad_page(url, headers):
            return {'value': [{'id': 'first'}], '@odata.nextLink': 'https://example.org/v1.0/users'}
        result = await EntraAPIClient(page_reader=bad_page).make_request('/users')
        self.assertEqual(result['status'], 'error')
        async def page(url, headers):
            return {'value': [{'id': str(i)} for i in range(5)]}
        client = EntraAPIClient(page_reader=page)
        client.test_mode = True
        result = await client.make_request('/users')
        self.assertEqual(len(result['data']), 3)
        self.assertFalse(result['complete'])

    async def test_sdk_response_contract_without_network(self):
        import httpx
        from kiota_abstractions.authentication.anonymous_authentication_provider import AnonymousAuthenticationProvider
        from msgraph.graph_request_adapter import GraphRequestAdapter
        from msgraph import GraphServiceClient
        async def respond(request):
            self.assertEqual(request.method, 'GET')
            self.assertEqual(request.url.host, 'graph.microsoft.com')
            return httpx.Response(200, json={'value': [{'id': 'sdk-user', 'accountEnabled': True}]})
        http = httpx.AsyncClient(transport=httpx.MockTransport(respond))
        client = EntraAPIClient()
        client._http = http
        client._sdk = GraphServiceClient(request_adapter=GraphRequestAdapter(AnonymousAuthenticationProvider(), client=http))
        try:
            result = await client.make_request('/users', params={'$select': 'id,accountEnabled'})
            self.assertEqual(result['data'][0]['accountEnabled'], True)
        finally:
            await client.close_session()

    async def test_catalog_and_model_boundary(self):
        entries = catalog()
        self.assertGreaterEqual(len(entries), 20)
        self.assertNotRegex(json.dumps(entries), r'https?://|www\.')
        for entry in entries:
            path = entry['url_pattern']
            import re
            self.assertEqual(operation_for(re.sub(r'\{[^}]+\}', 'known-id', path))['id'], entry['id'])
            self.assertIn('## Interpretation and Related Data', entry['notes'])
        from pydantic_ai.messages import ModelRequest, UserPromptPart, ToolReturnPart, ModelResponse, TextPart
        from pydantic_ai.models.function import FunctionModel
        from pydantic_ai.models import ModelRequestParameters
        captured = []
        def respond(messages, info):
            captured.extend(messages)
            return ModelResponse(parts=[TextPart('Done')])
        original = [ModelRequest(parts=[UserPromptPart('Read https://example.org/help'),
                    ToolReturnPart('lookup', {'homepage': 'https://example.org', 'mail': 'alex@contoso.com'})])]
        await ContextPolicyModel(FunctionModel(respond)).request(original, None, ModelRequestParameters())
        self.assertNotIn('https://', str(captured))
        self.assertIn('alex@contoso.com', str(captured))
        self.assertIn('https://', str(original))

    async def test_failed_snapshot_preserves_prior_rows_and_empty_is_valid(self):
        from src.core.storage.operations import DatabaseOperations
        from src.core.entra.sync.engine import SyncOrchestrator
        from src.core.entra.sync.models import User, DirectorySnapshot
        from src.config.settings import settings
        from sqlalchemy import select
        db = DatabaseOperations()
        await db.init_db()
        sync = SyncOrchestrator(db=db)
        async def populated():
            return [{'id': 'stored-user', 'displayName': 'Stored User', 'accountEnabled': True}]
        async def failed():
            raise RuntimeError('second page failed')
        async def empty():
            return []
        try:
            self.assertEqual((await sync._snapshot(User, populated))[0], 1)
            self.assertIsNotNone((await sync._snapshot(User, failed))[1])
            async with db.get_session() as session:
                self.assertIsNotNone(await session.get(User, 'stored-user'))
                snapshot = await session.get(DirectorySnapshot, (settings.tenant_id, 'users'))
                self.assertEqual(snapshot.status, 'failed')
                self.assertIsNotNone(snapshot.last_successful_at)
            from src.core.entra.client.read_database import open_database
            connection = open_database()
            with self.assertRaises(Exception):
                connection.execute('DELETE FROM users')
            with self.assertRaises(Exception):
                connection.execute('SELECT password_hash FROM auth_users')
            connection.close()
            self.assertEqual((await sync._snapshot(User, empty))[0], 0)
            async with db.get_session() as session:
                self.assertIsNone(await session.get(User, 'stored-user'))
        finally:
            await db.close()
            DatabaseOperations._engine = DatabaseOperations._SessionLocal = None
            DatabaseOperations._initialized = False

    async def test_generated_code_uses_only_approved_helpers(self):
        from src.utils.security_config import validate_generated_code
        valid = "from base_graph_client import EntraAPIClient, open_database\nasync def main():\n    client = EntraAPIClient()\n    return await client.make_request('/users')\n"
        self.assertTrue(validate_generated_code(valid).is_valid)
        for code in ('import httpx\nhttpx.get("https://example.org")', 'import aiohttp',
                     'from src.config.settings import settings', 'client._sdk.request_adapter',
                     'import asyncio\nasyncio.open_connection("example.org", 80)'):
            self.assertFalse(validate_generated_code(code).is_valid, code)


if __name__ == '__main__':
    unittest.main()
