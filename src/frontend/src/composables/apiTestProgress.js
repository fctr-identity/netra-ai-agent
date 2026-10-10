// Sparse server events; elapsed/countdown rendering happens locally.
export const activeRequestStates = new Set(['running', 'retrying', 'retry_wait'])
const statuses = new Set([...activeRequestStates, 'success', 'empty', 'failed', 'cancelled', 'unknown', 'timed_out'])

export function applyRequestProgress(requests, event, now = Date.now()) {
    if (!event.request_id || !statuses.has(event.status)) return
    let request = requests.find(item => item.id === event.request_id)
    if (request && !activeRequestStates.has(request.status)) return
    if (!request) {
        request = { id: event.request_id, operation: event.operation, label: event.label,
            startedAt: now - (event.elapsed_ms || 0) }
        requests.push(request)
    }
    request.status = event.status
    if (Number.isFinite(event.elapsed_ms)) request.elapsedMs = event.elapsed_ms
    request.attempt = event.attempt || request.attempt || 0
    request.retryUntil = event.status === 'retry_wait' && Number.isFinite(event.retry_after_seconds)
        ? now + event.retry_after_seconds * 1000 : null
}

export function applyApiTestProgress(steps, event, now = Date.now()) {
    if (!['api_test_request', 'api_test_end'].includes(event?.kind)) return false
    const tool = steps.flatMap(step => step.tools || []).find(tool => tool.testId === event.test_id)
    if (!tool) return true
    tool.requests ||= []
    if (event.kind === 'api_test_end') {
        tool.status = event.status
        for (const request of tool.requests.filter(item => activeRequestStates.has(item.status))) {
            request.status = ['timed_out', 'failed', 'cancelled'].includes(event.status) ? event.status : 'unknown'
            request.elapsedMs = Math.max(0, now - request.startedAt)
        }
        tool.finishedAt = now
    } else {
        applyRequestProgress(tool.requests, event, now)
    }
    return true
}

export function interruptRequests(requests, status = 'unknown', now = Date.now()) {
    for (const request of requests) {
        if (activeRequestStates.has(request.status)) {
            request.status = status
            request.elapsedMs = Math.max(0, now - request.startedAt)
        }
    }
}

export function interruptApiTests(steps, status = 'unknown') {
    for (const step of steps) {
        for (const tool of step.tools || []) interruptRequests(tool.requests || [], status)
    }
}

export function requestElapsed(request, now) {
    return Math.max(0, Math.floor((activeRequestStates.has(request.status)
        ? now - (request.startedAt || now) : request.elapsedMs || 0) / 1000))
}

export function requestStatus(request, now) {
    if (request.status === 'retry_wait' && request.retryUntil > now) {
        return `Graph requested a wait · ${Math.ceil((request.retryUntil - now) / 1000)}s remaining`
    }
    return requestStatusLabels[request.status] || 'Unconfirmed'
}

export const requestStatusLabels = {
    running: 'Waiting on Microsoft Graph', retrying: 'Retrying Graph request',
    retry_wait: 'Graph returned a temporary error',
    success: 'Returned data', empty: 'No data', timed_out: 'Timed out',
    failed: 'Failed', cancelled: 'Cancelled', unknown: 'Unconfirmed',
}
