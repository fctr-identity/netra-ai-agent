# Runtime boundaries and data

Saved procedure reuse is optional. Set `QUERY_PROCEDURES_ENABLED=true` to enable
reuse of compatible successful workflows; otherwise queries use fresh
orchestration. A failed reuse attempt falls back to fresh orchestration.

The agent receives local descriptions, notes, parameters, and JSON response
contracts for **53 approved GET operations**, not the entire Microsoft Graph API.
The SDK adapter restricts directory traffic to those v1.0 paths on the commercial
Graph host and handles pagination/retries. OAuth token acquisition is separate
from the read-only directory calls. No agent browser or arbitrary HTTP tool is
provided. Model-bound context has external hyperlinks removed, including links
found in directory values and tool results; stored source data is retained.

Queries and selected directory data are sent to the configured model provider.
SQLite snapshots, conversation history, generated scripts, results, and logs are
local sensitive data; keep them out of Git. Generated-code validation and the
read-only SQL connection are POC guardrails, not an OS sandbox for hostile users.
Python validators enforce explicit imports/members and calls, reject opaque
string-format traversal and helper rebinding, and run before script staging or
saved-result analysis. Prompt instructions are not a security boundary. Accepted
Python still runs with the application's operating-system privileges.

Generated API discovery, SQL discovery, and saved-result analysis run in local
child processes. The shared supervisor also covers final UI, CLI, Teams, and
saved-procedure retrieval scripts. Graph operations default to 90 seconds.
API discovery and final retrieval execution allow at least 120 seconds, or the
configured `GRAPH_TIMEOUT_SECONDS` plus 30 seconds when that is longer. These are
whole-script deadlines, including worker startup; a script with several slow
operations can still reach its limit. Analysis retains a 60-second deadline and
SQL discovery a 15-second deadline. Captured output is capped at 8 MiB stdout and 1 MiB stderr;
oversized output fails rather than returning truncated success. Cancellation is
checked independently of progress messages, and children are killed and reaped
on failure/cancellation. These are time/output bounds, not memory/CPU quotas or
filesystem/credential isolation.

While a query runs, the activity panel shows its current phase or Graph operation,
elapsed time, and a slow-operation notice after 20 seconds. Completed requests and
retry/timeout states remain in expandable activity; Stop cancels the running work.
Progress events carry only fixed phase/tool labels, catalog operation labels,
correlation IDs, status, elapsed time, and optional retry timing. Model reasoning,
tenant records, raw URLs, headers, and error bodies are excluded from this feed.
The existing result, optional generated-script, and token-usage events serve their
separate UI views. Per-attempt HTTP timing/status diagnostics stay in server logs;
they omit request URLs, credentials, and response bodies. Timers update locally
without per-second server events.

Graph 429s and AI provider throttling appear as rate-limit status in query activity
and the CLI. Model status covers planning, discovery, review, and synthesis through
the shared model boundary. A countdown displays the provider's `Retry-After` hint
(seconds or HTTP date; millisecond hints are also accepted). Without a valid hint,
the UI shows rate limiting without inventing a countdown. This is a requested
retry delay, not a guaranteed quota reset. Existing SDK retries and query deadlines
remain unchanged; completion, failure, or cancellation clears the waiting state.
Only throttled model calls add activity entries, keeping normal progress compact.

API discovery retains each returned test payload and its exact tested code in a
temporary folder under the current turn's artifacts. The model receives a valid,
bounded JSON preview and a test ID; `save_artifact` promotes that ID's original
payload and code into the existing durable artifact/result-set storage. The
model does not copy response JSON back into the save call. `inspect_test_result`
can preview a nested value locally without repeating a Graph request.

Temporary test folders are removed when discovery finishes, fails, or is
cancelled. After an abrupt process exit, the next web, CLI, or integration query
sweeps abandoned test folders with no changes in the last 24 hours. This is
opportunistic cleanup, not a timer. Selected artifacts remain with the conversation
and follow its existing retention; CLI evaluation output is still retained in
its chosen runtime directory. No new storage service is required.

Assignments are not effective access. MFA registration is not successful MFA use.
Direct and transitive memberships differ, and nested groups do not confer
group-based app assignments. The v1.0 group-members source has a documented
service-principal omission; Netra records that limit. PIM eligibility, risk
analysis, Intune management, and write operations are outside this release.
