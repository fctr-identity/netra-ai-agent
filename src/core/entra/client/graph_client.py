"""Approved Graph reads through Microsoft's SDK, shared by discovery and sync."""
import asyncio
import hashlib
import json
import re
import sys
import time
from uuid import uuid4
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode, urlsplit, unquote
from .request_trace import request_context, emit_progress, http_diagnostic

GRAPH_BASE = 'https://graph.microsoft.com/v1.0'
CATALOG_PATH = Path(__file__).resolve().parents[3] / 'data/schemas/graph_get_endpoints.json'


@lru_cache(maxsize=1)
def catalog():
    return json.loads(CATALOG_PATH.read_text(encoding='utf-8'))['endpoints']


def operation_for(path):
    decoded = unquote(path)
    if any(part in {'.', '..'} for part in decoded.split('/')) or any(value in path.lower() for value in ('%2f', '%5c', '%25')) or '\\' in decoded:
        raise ValueError('Invalid Graph resource path')
    for operation in sorted(catalog(), key=lambda item: len(item['url_pattern']), reverse=True):
        pattern = re.escape(operation['url_pattern'])
        pattern = re.sub(r'\\\{[^}]+\\\}', lambda _: r'[^/\s?#]+', pattern)
        if re.fullmatch(pattern, path):
            return operation
    raise ValueError('This resource is outside the supported Graph read catalog')


def validate_graph_url(url, expected_path=None):
    parsed = urlsplit(str(url))
    if parsed.scheme != 'https' or parsed.hostname != 'graph.microsoft.com' or parsed.port not in (None, 443) or parsed.username or parsed.password or parsed.fragment:
        raise ValueError('Only the fixed commercial Microsoft Graph endpoint is allowed')
    if not parsed.path.startswith('/v1.0/'):
        raise ValueError('Only Microsoft Graph v1.0 is allowed')
    path = parsed.path[len('/v1.0'):]
    operation_for(path)
    if expected_path and path != expected_path:
        raise ValueError('Continuation changed the requested resource')
    return path


class EntraAPIClient:
    """Returns a stable status/data/complete envelope; never exposes raw SDK clients."""
    def __init__(self, timeout=None, max_pages=None, *, page_reader=None):
        from src.config.settings import settings
        self._settings = settings
        self.concurrent_limit = settings.GRAPH_CONCURRENT_LIMIT
        self._timeout = timeout or settings.GRAPH_TIMEOUT_SECONDS
        self._max_pages = max_pages or settings.GRAPH_MAX_PAGES
        self._semaphore = asyncio.Semaphore(self.concurrent_limit)
        self._reader = page_reader
        self._sdk = self._credential = self._http = None
        self.test_mode = False
        self._entity_errors = {}

    def _initialize_sdk(self):
        if self._sdk is not None:
            return
        if not all((self._settings.ENTRA_TENANT_ID, self._settings.ENTRA_CLIENT_ID, self._settings.ENTRA_CLIENT_SECRET)):
            raise ValueError('Configure ENTRA_TENANT_ID, ENTRA_CLIENT_ID and ENTRA_CLIENT_SECRET before Graph reads')
        import httpx
        from azure.identity.aio import ClientSecretCredential
        from kiota_authentication_azure.azure_identity_authentication_provider import AzureIdentityAuthenticationProvider
        from msgraph import GraphServiceClient
        from msgraph.graph_request_adapter import GraphRequestAdapter
        from msgraph_core import GraphClientFactory

        class ReadTransport(httpx.AsyncHTTPTransport):
            async def handle_async_request(self, request):
                if request.method != 'GET':
                    raise ValueError('Graph data requests must be GET')
                path = validate_graph_url(str(request.url))
                operation = operation_for(path)['id']
                raw_attempt = request.headers.get('Retry-Attempt', '0')
                attempt = int(raw_attempt) if raw_attempt.isdigit() else 0
                context = request_context.get()
                if attempt:
                    emit_progress(context, 'retrying', attempt=attempt)
                started = time.monotonic()
                try:
                    response = await super().handle_async_request(request)
                except BaseException:
                    http_diagnostic(operation, started, attempt, outcome='interrupted')
                    raise
                http_diagnostic(operation, started, attempt, status=response.status_code)
                if response.status_code in (429, 503, 504):
                    delay = response.headers.get('Retry-After', '')
                    fields = {'retry_after_seconds': min(int(delay), 86400)} if delay.isdigit() else {}
                    # Reports a transient response, not a promise that another retry will occur.
                    emit_progress(context, 'retry_wait', **fields)
                return response

        self._credential = ClientSecretCredential(self._settings.ENTRA_TENANT_ID, self._settings.ENTRA_CLIENT_ID,
            self._settings.ENTRA_CLIENT_SECRET, authority='login.microsoftonline.com', disable_instance_discovery=True)
        auth = AzureIdentityAuthenticationProvider(self._credential, scopes=['https://graph.microsoft.com/.default'], allowed_hosts=['graph.microsoft.com'])
        self._http = GraphClientFactory.create_with_default_middleware(client=httpx.AsyncClient(
            transport=ReadTransport(), timeout=self._timeout, follow_redirects=False, trust_env=False))
        self._sdk = GraphServiceClient(request_adapter=GraphRequestAdapter(auth, client=self._http))

    async def _read_page(self, url, headers):
        validate_graph_url(url)
        if self._reader:
            return await self._reader(url, headers)
        self._initialize_sdk()
        from kiota_abstractions.method import Method
        from kiota_abstractions.request_information import RequestInformation
        from msgraph.generated.models.o_data_errors.o_data_error import ODataError
        request = RequestInformation()
        request.http_method = Method.GET
        request.url = url
        for name, value in {'Accept': 'application/json', **headers}.items():
            request.headers.add(name, value)
        raw = await self._sdk.request_adapter.send_primitive_async(request, 'bytes', {'4XX': ODataError, '5XX': ODataError})
        if raw is None:
            raise ValueError('Graph returned no JSON body')
        return json.loads(raw)

    async def make_request(self, endpoint, method='GET', params=None, body=None, max_results=None, entity_label=None):
        inherited_context = request_context.get()
        context = inherited_context or {
            'kind': 'graph_request', 'request_id': uuid4().hex,
            'operation': 'unknown', 'started': time.monotonic(),
        }
        context_token = request_context.set(context)
        def progress(status):
            if inherited_context is None:
                emit_progress(context, status)
        if isinstance(method, str):
            method = method.upper()
        fingerprint = hashlib.sha256(json.dumps([endpoint, method, params, max_results], sort_keys=True, default=str).encode()).hexdigest()
        def record(state, **extra):
            print('__NETRA_RETRIEVAL__' + json.dumps({'request': fingerprint, 'state': state, **extra}), file=sys.stderr, flush=True)
        record('started')
        try:
            if method != 'GET' or body is not None:
                raise ValueError('Only body-free GET requests are supported')
            if not isinstance(endpoint, str) or not endpoint.startswith('/') or endpoint.startswith('//') or '?' in endpoint or '#' in endpoint:
                raise ValueError('Use a catalog relative path and separate query parameters')
            operation = operation_for(endpoint)
            context['operation'] = operation['id']
            progress('running')
            params = dict(params or {})
            unknown = set(params) - set(operation['parameters']['optional'])
            if unknown:
                raise ValueError('Unsupported query parameter: ' + ', '.join(sorted(unknown)))
            if max_results is not None and (type(max_results) is not int or max_results < 1):
                raise ValueError('max_results must be a positive integer')
            if '$top' in params and (not str(params['$top']).isdigit() or not 1 <= int(params['$top']) <= 999):
                raise ValueError('$top must be between 1 and 999')
            if operation['entity'] in {'sign_in', 'directory_audit'} and operation['operation'] == 'list':
                field = 'createdDateTime' if operation['entity'] == 'sign_in' else 'activityDateTime'
                if not re.search(r'\b' + field + r'\s+(?:ge|gt)\s+', str(params.get('$filter', '')), re.I):
                    raise ValueError('An explicit event-time lower bound is required')
            headers = {}
            if operation.get('require_count'):
                # Some relationships require count + eventual consistency even for simple reads.
                params['$count'] = 'true'
                headers['ConsistencyLevel'] = 'eventual'
            if operation.get('advanced_query') and (any(key in params for key in ('$filter', '$search', '$count', '$orderby')) or '/microsoft.graph.' in endpoint):
                headers['ConsistencyLevel'] = 'eventual'
                if '$count' in operation['parameters']['optional']:
                    params.setdefault('$count', 'true')
            for key, value in list(params.items()):
                if isinstance(value, (list, tuple)):
                    params[key] = ','.join(map(str, value))
                elif isinstance(value, bool):
                    params[key] = str(value).lower()
            limit = min(max_results or 3, 3) if self.test_mode else max_results
            url = GRAPH_BASE + endpoint + ('?' + urlencode(params) if params else '')
            rows, seen = [], set()
            complete = True
            async with self._semaphore, asyncio.timeout(self._timeout):
                for _ in range(self._max_pages):
                    validate_graph_url(url, endpoint)
                    if url in seen:
                        raise ValueError('Graph pagination repeated a continuation')
                    seen.add(url)
                    payload = await self._read_page(url, headers)
                    if not isinstance(payload, dict) or 'error' in payload:
                        raise ValueError('Unexpected Graph response')
                    if 'value' not in payload:
                        if operation['response']['collection']:
                            raise ValueError('Graph collection response omitted value')
                        data = {key: value for key, value in payload.items() if key not in {'@odata.context', '@odata.nextLink', '@odata.deltaLink'}}
                        break
                    if not isinstance(payload['value'], list):
                        raise ValueError('Graph collection value is not an array')
                    rows.extend(payload['value'])
                    next_url = payload.get('@odata.nextLink')
                    if limit and len(rows) >= limit:
                        complete = len(rows) == limit and not next_url
                        data = rows[:limit]
                        break
                    if not next_url:
                        data = rows
                        break
                    url = next_url
                else:
                    raise ValueError('Pagination safety limit reached before completion')
            result = {'status': 'success', 'data': data, 'complete': complete, 'count': len(data) if isinstance(data, list) else 1}
            record('success')
            progress('empty' if data == [] or data == {} else 'success')
            return result
        except asyncio.CancelledError:
            record('error', category='unknown', message='Request cancelled')
            progress('cancelled')
            raise
        except Exception as exc:
            from src.core.models.context_policy import sanitize_text
            status = getattr(exc, 'response_status_code', None)
            details = getattr(exc, 'error', None)
            code = getattr(details, 'code', None) or type(exc).__name__
            message = sanitize_text(str(getattr(details, 'message', None) or exc))[:1000]
            # Never include credential values in returned exceptions.
            if self._settings.ENTRA_CLIENT_SECRET:
                message = message.replace(self._settings.ENTRA_CLIENT_SECRET, '[credential]')
            category = 'access' if status in (401, 403) else 'missing' if status == 404 else 'transient' if status == 429 or isinstance(exc, TimeoutError) or status and status >= 500 else 'request'
            record('error', category=category, http_status=status, error_code=code, message=message)
            progress('timed_out' if isinstance(exc, TimeoutError) else 'failed')
            if entity_label:
                self._entity_errors[entity_label] = self._entity_errors.get(entity_label, 0) + 1
            return {'status': 'error', 'error': message, 'error_code': code, 'http_status': status, 'complete': False}
        finally:
            request_context.reset(context_token)

    async def close_session(self):
        if self._http:
            await self._http.aclose()
        if self._credential:
            await self._credential.close()
        self._sdk = self._http = self._credential = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close_session()

    def start_entity_progress(self, label, total):
        self._entity_errors[label] = 0

    def update_entity_progress(self, label, processed):
        pass

    def complete_entity_progress(self, label, success=True):
        pass
