"""Request timing without URLs, headers, identifiers or response bodies."""
from contextvars import ContextVar
import json
import sys
import time

request_context = ContextVar('graph_request_context', default=None)


def emit_progress(context, status, **fields):
    if not context:
        return
    details = {key: context[key] for key in ('kind', 'request_id', 'operation', 'test_id') if key in context}
    details.update(status=status, elapsed_ms=round((time.monotonic() - context['started']) * 1000), **fields)
    print('__PROGRESS__' + json.dumps({'details': details}), file=sys.stderr, flush=True)


def http_diagnostic(operation, started, attempt, status=None, outcome='response'):
    print('__NETRA_HTTP__' + json.dumps({
        'operation': operation, 'attempt': attempt, 'http_status': status,
        'elapsed_ms': round((time.monotonic() - started) * 1000), 'outcome': outcome,
    }), file=sys.stderr, flush=True)
