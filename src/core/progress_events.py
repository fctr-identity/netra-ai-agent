"""Small public progress contract; model prose and diagnostics stay server-side."""
import re
import time
from functools import lru_cache

PHASES = {
    'planning': 'Understanding your question', 'sql': 'Querying the database',
    'api': 'Retrieving live data', 'processor': 'Processing saved results',
    'analysis': 'Analyzing saved results', 'review': 'Checking retrieved data',
    'special': 'Running a specialized check', 'synthesis': 'Preparing the answer',
    'reuse': 'Running a saved query', 'reuse_adapt': 'Adapting a saved query',
    'reuse_search': 'Matching saved queries', 'reuse_inspect': 'Checking query fit',
    'execution_repair': 'Refining retrieval',
}
TOOLS = {
    'get_sql_context': 'Read database schema',
    'load_comprehensive_api_endpoints': 'Find available API endpoints',
    'filter_endpoints_by_operations': 'Select API endpoints',
    'execute_test_query_api': 'Check API retrieval',
    'execute_test_query_sql': 'Check database query',
    'load_artifacts': 'Read saved results', 'save_artifact': 'Save retrieval evidence',
}
REQUEST_STATES = {'running', 'retrying', 'retry_wait', 'success', 'empty',
                  'failed', 'cancelled', 'unknown', 'timed_out'}


@lru_cache(maxsize=1)
def operation_labels():
    from src.core.entra.client.graph_client import catalog
    return {entry['id']: entry['name'] for entry in catalog()}


def identifier(value):
    return value if isinstance(value, str) and re.fullmatch(r'[\w-]{1,120}', value, re.ASCII) else None


def public_progress(details):
    if not isinstance(details, dict):
        return None
    kind = details.get('kind')
    if kind not in {'api_test_request', 'graph_request', 'api_test_end'}:
        return None
    state = details.get('status')
    if state not in REQUEST_STATES:
        return None
    clean = {'kind': kind, 'status': state}
    if kind.startswith('api_test'):
        test_id = identifier(details.get('test_id'))
        if not test_id:
            return None
        clean['test_id'] = test_id
    if kind != 'api_test_end':
        request_id = identifier(details.get('request_id'))
        if not request_id:
            return None
        clean['request_id'] = request_id
        operation = details.get('operation')
        known = operation in operation_labels() if isinstance(operation, str) else False
        clean['operation'] = operation if known else 'unknown'
        clean['label'] = operation_labels()[operation] if known else 'Graph request'
    for field, maximum in [('elapsed_ms', 86400000), ('retry_after_seconds', 86400), ('attempt', 100)]:
        value = details.get(field)
        if type(value) in (int, float) and 0 <= value <= maximum:
            clean[field] = round(value)
    return {'type': 'STEP-PROGRESS', 'details': clean, 'timestamp': time.time()}


def public_agent_event(kind, data):
    """Allowlist fields rather than forwarding free-form agent/tool payloads."""
    if kind == 'progress':
        return public_progress(data.get('details'))
    if kind == 'step_start':
        phase = data.get('phase') if data.get('phase') in PHASES else 'planning'
        return {'type': 'STEP-START', 'step': data.get('step', 0), 'phase': phase,
                'title': PHASES[phase], 'timestamp': time.time()}
    if kind == 'step_end':
        success = data.get('success', True) is True
        return {'type': 'STEP-END', 'step': data.get('step', 0), 'success': success,
                'title': 'Step finished' if success else 'Step failed', 'timestamp': time.time()}
    if kind == 'tool_call':
        name = data.get('tool_name')
        return {'type': 'TOOL-CALL', 'tool_name': name if name in TOOLS else 'other',
                'description': TOOLS.get(name, 'Processing your request'),
                'test_id': identifier(data.get('test_id')), 'timestamp': time.time()}
    return None
