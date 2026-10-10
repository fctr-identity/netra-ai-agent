# Teams runtime and validation

Implementation details for the optional Netra AI Teams integration. For installation,
follow the [Teams setup guide](README.md).

## Behavior and limits

- Messages continue the user's current personal-chat session, including clarification answers.
  **New Query** (or `new`) resets context for the next message. Previous result cards stay visible.
  Session IDs are stored in the durable inbox database and survive restarts.
- Only authenticated Bot Service activities from the configured tenant's personal chats are accepted.
  Direct Entra/Agent ID callers, channel/group chats, incoming files, and unrelated card actions remain unsupported.
- Graph membership is checked before execution and again before delivering results.
  Authorization failures never start Entra or LLM work. Membership is not cached.
- One query per user, two simultaneous queries per instance, at most 16 pending or
  active queries. A separate command worker handles `help`, `status`, and `cancel`.
  Query messages are limited to 8,000 characters. Overloaded requests return 429.
- The whole request has a 15-minute deadline from arrival, with a 120-second script
   limit. `cancel` stops the sender's pending/running query. Generated script subprocesses are killed and reaped on
  cancellation and timeout.
- A temporary working card is removed after a new final answer is delivered.
  Table previews show the first ten
  rows and four columns using the native Adaptive Card Table element, with an
  aligned-column fallback for older clients. Header labels and data keys are
  normalized separately; long values are visibly truncated. Native typing dots
  refresh while a query runs and stop on completion, error, or cancellation.
  Typing failures are best-effort and never fail the query. Partial answers and
  clarifications are distinct from successful empty results. Errors do not include
  raw stack traces or generated scripts.
- **Download CSV** exports the saved retrieved rows without rerunning the question. Teams first asks
  permission to save the file to the user's OneDrive, then shows a native file card. Consent is
  single-use, expires after one hour, and is bound to the requesting tenant, user, conversation,
  and result. Only Microsoft-hosted OneDrive/SharePoint upload URLs are accepted; uploads use
  bounded sequential chunks with no redirects or bot/Graph authorization headers. No extra Graph
  file permissions are required. The app package must have `supportsFiles=true` (version 0.2.0).
- Identical activity redeliveries are deduplicated for 24 hours. Queued, unexpired
  jobs survive restarts; in-flight jobs become interrupted and are not replayed.
  The inbox stores queries and trusted routing identifiers under `DB_DIR`, not
  bearer tokens. File-consent upload URLs are temporarily held only in queued/running upload jobs and cleared at completion, expiry, or interruption. Terminal inbox rows are purged after 24 hours. Teams runtime
  folders under `CHAT_SESSIONS_DIR` are swept at startup and hourly, including
  while the bot is idle. `TEAMS_SESSION_RETENTION_HOURS` defaults to 24 (valid
  range: 1–8760); any recent file activity extends retention. Queued/running jobs
  are protected. Expiry removes the entire Teams session folder and its artifacts,
  results, exports, and associated conversation database rows. Web sessions and linked directories are
  not deleted by this cleanup. Already-delivered Teams messages/files remain in Teams.
- Failed/uncertain message delivery never reruns the query. Only explicit 429
  sends are retried. Restart interruptions require the user to resend the question;
  there is no automatic recovery notification yet.
- Treat already-sent Teams content as disclosed to the recipient; membership
  revocation cannot recall previously delivered data.

## Verification

Incoming decisions are logged to the console and `logs/netra_ai_agent.log`.
Rejections include a fixed reason, text length, attachment counts, and whether a
card-action value was present; accepted requests include the queued job ID.
These diagnostics exclude message text, attachment contents, URLs, and tokens.
Worker failures include the processing stage, code locations, missing filename,
and HTTP status when available. Runtime folders stay under the configured
`CHAT_SESSIONS_DIR`; a compact tenant/user hash avoids unnecessarily long Windows
paths. Cards are sent without a separate text message so Teams preserves the
activity ID used to update progress with the final result or error.
Before saving a request, Netra AI normalizes pasted line endings and nonbreaking
spaces, trims outer whitespace, and removes control characters and invisible
direction overrides. It preserves punctuation, query operators, Unicode text,
and emoji joiners. Empty cleaned messages and raw text over 8,000 characters are
rejected. This input cleanup does not replace authorization, generated-code
validation, or output escaping, and does not claim to prevent prompt injection.
Teams' `text/html` companion attachments are ignored when message text is present;
incoming file attachments and unrelated card actions remain unsupported. See Microsoft's
[message activity example](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/build-conversational-capability#receive-a-message-activity).

The [package builder](app_package/README.md) can validate the manifest inputs and
icon dimensions locally using a synthetic client ID. Building a ZIP does not
validate Bot Service authentication, Microsoft Graph access, or live delivery.

Before release, validate an actual package installation, connector JWT/proactive
send roundtrip, nested group access and revocation, desktop/mobile card rendering,
and a real query/cancel/restart flow. Linux Docker execution also needs a smoke
test. Follow-up and CSV flows still require live validation in a configured Teams tenant.

References: [Teams Python SDK](https://github.com/microsoft/teams.py/tree/v2.1.0),
[SDK HTTP integration](https://learn.microsoft.com/en-us/microsoftteams/platform/teams-sdk/in-depth-guides/server/http-server),
[Graph transitive membership](https://learn.microsoft.com/en-us/graph/api/user-list-transitivememberof?view=graph-rest-1.0),
[Azure configuration](https://learn.microsoft.com/en-us/microsoftteams/platform/teams-sdk/teams/azure-configuration).
