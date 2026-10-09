"""Offline catalog and SDK-envelope checks; no tenant or model calls."""
import json
import re
import unittest
from tests import ROOT

from src.core.entra.client.graph_client import EntraAPIClient, catalog, operation_for


class ExpandedCatalogChecks(unittest.IsolatedAsyncioTestCase):
    def test_routing_provenance_and_published_inventory_agree(self):
        entries = catalog()
        index = json.loads((ROOT / 'src/data/schemas/graph_read_operations.json').read_text())['operations']
        provenance = json.loads((ROOT / 'docs/graph_catalog_sources.json').read_text())['operations']
        published = (ROOT / 'docs/SUPPORTED_GRAPH_READS.md').read_text()
        self.assertEqual(len(entries), 53)
        self.assertEqual(len(set(index)), len(entries))
        self.assertEqual([entry['id'] for entry in entries], index)
        self.assertEqual({entry['operation'] for entry in provenance}, set(index))
        self.assertNotRegex(json.dumps(entries), r'https?://|www\.')
        for entry in entries:
            with self.subTest(operation=entry['id']):
                path = re.sub(r'\{[^}]+\}', 'fixture-id', entry['url_pattern'])
                self.assertEqual(operation_for(path)['id'], entry['id'])
                self.assertEqual(entry['method'], 'GET')
                self.assertNotIn('Write', ' '.join(entry['application_permissions']))
                self.assertIn(f"| {entry['id']} | {entry['url_pattern']} |", published)
                self.assertTrue(entry['availability'])
                self.assertTrue(entry['sync_support'])
        for path in ('/users/fixture/manager', '/users/fixture/licenseDetails',
                     '/users/fixture/ownedDevices', '/users/fixture/registeredDevices',
                     '/deviceManagement/managedDevices', '/identityProtection/riskyUsers'):
            with self.assertRaises(ValueError):
                operation_for(path)

    async def test_user_app_assignments_sdk_paging_preserves_group_provenance(self):
        import httpx
        from kiota_abstractions.authentication.anonymous_authentication_provider import AnonymousAuthenticationProvider
        from msgraph.graph_request_adapter import GraphRequestAdapter
        from msgraph import GraphServiceClient

        calls = []
        async def respond(request):
            calls.append(request)
            self.assertEqual(request.method, 'GET')
            self.assertEqual(request.headers['ConsistencyLevel'], 'eventual')
            if len(calls) == 1:
                self.assertEqual(request.url.params['$count'], 'true')
                return httpx.Response(200, json={'value': [{'id': 'direct', 'principalType': 'User', 'principalId': 'u1'}],
                    '@odata.nextLink': 'https://graph.microsoft.com/v1.0/users/u1/appRoleAssignments?$skiptoken=fixture'})
            self.assertEqual(request.url.params['$skiptoken'], 'fixture')
            return httpx.Response(200, json={'value': [{'id': 'inherited', 'principalType': 'Group', 'principalId': 'g1'}]})
        http = httpx.AsyncClient(transport=httpx.MockTransport(respond))
        client = EntraAPIClient()
        client._http = http
        client._sdk = GraphServiceClient(request_adapter=GraphRequestAdapter(AnonymousAuthenticationProvider(), client=http))
        try:
            result = await client.make_request('/users/u1/appRoleAssignments', params={'$count': False})
            self.assertEqual(result['status'], 'success')
            self.assertTrue(result['complete'])
            self.assertEqual([row['principalType'] for row in result['data']], ['User', 'Group'])
            self.assertEqual(len(calls), 2)
        finally:
            await client.close_session()

    async def test_singletons_relationships_and_permission_failure(self):
        from msgraph.generated.models.o_data_errors.o_data_error import ODataError
        responses = {
            '/policies/authenticationMethodsPolicy': {'id': 'authenticationMethodsPolicy',
                'authenticationMethodConfigurations': [{'id': 'Fido2', 'state': 'enabled'}]},
            '/organization': {'value': [{'id': 'tenant', 'displayName': 'Fixture tenant'}]},
            '/devices/d1/registeredOwners': {'value': [{'id': 'u1', '@odata.type': '#microsoft.graph.user', 'displayName': None}]},
            '/policies/authenticationStrengthPolicies/s1': {'id': 's1', 'allowedCombinations': ['fido2']},
        }
        from urllib.parse import urlsplit
        async def read(url, headers):
            path = urlsplit(url).path.removeprefix('/v1.0')
            if path == '/users/u1/authentication/methods':
                raise ODataError(response_status_code=403)
            return responses[path]
        client = EntraAPIClient(page_reader=read)
        for path, payload in responses.items():
            with self.subTest(path=path):
                result = await client.make_request(path)
                self.assertEqual(result['status'], 'success')
                self.assertTrue(result['complete'])
                self.assertEqual(result['data'], payload.get('value', payload))
        denied = await client.make_request('/users/u1/authentication/methods')
        self.assertEqual(denied['status'], 'error')
        self.assertEqual(denied['http_status'], 403)
        self.assertFalse(denied['complete'])
        self.assertNotIn('data', denied)
