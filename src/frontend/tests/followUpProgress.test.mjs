import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { createServer } from 'vite'
import vue from '@vitejs/plugin-vue'

test('follow-up phase events reach Activity without tools or internal reasoning', async (t) => {
    const server = await createServer({ configFile: false, envDir: false, plugins: [vue()],
        optimizeDeps: { noDiscovery: true, include: [] },
        server: { middlewareMode: true, watch: null, ws: false } })
    t.mock.method(console, 'log', () => {})
    const previous = globalThis.EventSource
    let stream
    globalThis.EventSource = class {
        constructor() { stream = this }
        addEventListener() {}
        close() {}
    }
    try {
        const { useReactStream } = await server.ssrLoadModule('/src/composables/useReactStream.js')
        const { default: Activity } = await server.ssrLoadModule('/src/components/messages/DiscoveryPanel.vue')
        const state = useReactStream()
        await state.connectToStream('fixture')
        const render = () => renderToString(createSSRApp({ render: () => h(Activity, {
            steps: state.discoverySteps.value, isComplete: Boolean(state.results.value),
        }) }))
        for (const [phase, label] of [
            ['planning', 'Understanding your question'], ['processor', 'Processing saved results'],
            ['review', 'Reviewing results'], ['analysis', 'Analyzing saved results'],
            ['reuse_search', 'Matching saved queries'], ['reuse_inspect', 'Evaluating query fit'],
            ['reuse', 'Running a saved query'],
            ['reuse_adapt', 'Adapting a saved query'],
        ]) {
            stream.onmessage({ data: JSON.stringify({ type: 'STEP-START', phase, step: 1,
                title: 'PRIVATE_TITLE', text: 'PRIVATE_RESULT_SET_AND_REASONING', timestamp: 1 }) })
            const html = await render()
            assert.match(html, new RegExp(label))
            assert.match(html, /In progress/)
            assert.doesNotMatch(html, /Preparing your request|No tool calls recorded|PRIVATE_|tool call/)
        }
        // Tool calls stay beneath their phase instead of collecting at the bottom.
        const modelEvent = status => ({ type: 'STEP-PROGRESS', details: {
            kind: 'model_request', request_id: 'fixture-model', reason: 'rate_limit',
            status, retry_after_seconds: 30, elapsed_ms: 2000,
        } })
        stream.onmessage({ data: JSON.stringify(modelEvent('retry_wait')) })
        assert.match(await render(), /AI provider rate limited.*requested wait/)
        stream.onmessage({ data: JSON.stringify(modelEvent('retrying')) })
        assert.match(await render(), /Retrying AI provider request/)
        stream.onmessage({ data: JSON.stringify(modelEvent('success')) })
        assert.doesNotMatch(await render(), /AI provider rate limited|Retrying AI provider request/)

        const grouped = await renderToString(createSSRApp({ render: () => h(Activity, {
            isComplete: true,
            steps: [
                { phase: 'planning', tools: [] },
                { phase: 'sql', tools: [{ name: 'get_sql_context' }] },
                { phase: 'sql', tools: [{ name: 'execute_test_query_sql' }] },
                { phase: 'review', tools: [] },
                { phase: 'api', tools: [{ name: 'load_comprehensive_api_endpoints' }] },
                { phase: 'api', tools: [{ name: 'save_artifact', description: 'Save retrieval evidence' }] },
                { phase: 'review', tools: [] },
                { phase: 'synthesis', tools: [{ name: 'load_artifacts' }] },
            ],
        }) }))
        const orderedLabels = ['Understanding your question', 'Querying the database',
            'Read database schema', 'Test database query', 'Reviewing results',
            'Retrieving live data', 'Find available API endpoints', 'Save discovery evidence', 'Reviewing results',
            'Preparing the answer', 'Read discovery evidence']
        let previousLabelEnd = 0
        for (const label of orderedLabels) {
            const position = grouped.indexOf(label, previousLabelEnd)
            assert.ok(position >= previousLabelEnd, `Missing or out-of-order activity label: ${label}`)
            previousLabelEnd = position + label.length
        }
        assert.doesNotMatch(grouped, /Planning next step|Save results|Read saved results|Checking retrieved evidence|Reviewing results ·/)
        assert.equal(grouped.split('Querying the database').length - 1, 1)
        assert.match(grouped, /5 tool calls/)
        // Unknown phase values and old prose are never rendered as public progress.
        stream.onmessage({ data: JSON.stringify({ type: 'STEP-START', phase: 'PRIVATE_UNKNOWN',
            step: 1, title: 'PRIVATE_TITLE', text: 'PRIVATE_TEXT', timestamp: 1 }) })
        stream.onmessage({ data: JSON.stringify({ type: 'COMPLETE', display_type: 'table',
            results: [{ count: 3 }], count: 1, metadata: {} }) })
        const complete = await render()
        assert.match(complete, /Analyzing saved results/)
        assert.doesNotMatch(complete, /In progress|PRIVATE_|No tool calls recorded/)
        stream.onmessage({ data: JSON.stringify({ type: 'DONE' }) })
    } finally {
        globalThis.EventSource = previous
        await server.close()
    }
})
