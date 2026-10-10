# Security policy

## Reporting a vulnerability

Please report suspected security vulnerabilities privately. Do not disclose
vulnerability details in public issues, discussions, or pull requests.

When this repository is public and private vulnerability reporting is enabled,
open **Security → Advisories → Report a vulnerability** on GitHub, or use the
[private reporting form](https://github.com/fctr-identity/netra-ai-agent/security/advisories/new).

If that option is unavailable, contact [support@fctr.io](mailto:support@fctr.io)
to request a private security-reporting channel. Do not include sensitive
details in that initial message.

Include the following in your private report:

- Affected Netra AI version or commit and relevant deployment details.
- A description of the issue and its potential impact.
- Steps to reproduce using synthetic or redacted data.
- Relevant sanitized logs or screenshots, if available.

Do not include credentials, access tokens, or real tenant or personal data.
Only test systems you own or have permission to assess.

## How reports are handled

We review reports privately, assess their impact, and work to reproduce and
address confirmed vulnerabilities. We coordinate with the reporter on fixes
and disclosure, including a security advisory when appropriate. Please allow
time for assessment and remediation before publishing details.

Security fixes target the latest Netra AI release, including the current beta.
Users of older versions may need to upgrade; backports are not guaranteed.
Reports and fixes are handled on a best-effort basis, without a guaranteed
response or resolution deadline.

## Security disclaimer

We work to improve Netra AI's security, but no software is guaranteed to be free
of vulnerabilities. Netra AI is provided "as is," without warranty, under the
[license](../LICENSE). Users are responsible for evaluating its suitability,
configuring access and permissions, protecting credentials and tenant data,
and keeping their deployments up to date.

Generated scripts run with the application's operating-system privileges;
code validation is not an operating-system sandbox. Protect local directory
snapshots, conversation history, saved results, and logs as sensitive data.
This policy does not change the license terms.
