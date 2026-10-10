"""Authorize authenticated Bot Service activities; never trust body identity alone."""
import asyncio
from dataclasses import dataclass
from urllib.parse import urlsplit
from uuid import UUID

import httpx

from .config import TeamsConfig


class AccessUnavailable(Exception):
    """Graph could not establish membership; callers must fail closed."""


@dataclass(frozen=True)
class Sender:
    tenant: str
    user: str
    conversation: str
    activity: str
    service_url: str


def authenticated_sender(body: dict, issuer: str | None, config: TeamsConfig) -> Sender:
    """Called only AFTER the SDK validates the bearer signature, audience and expiry."""
    if issuer != "https://api.botframework.com":
        raise ValueError("Only Bot Service connector activities are supported")
    conversation = body.get("conversation") or {}
    channel = body.get("channelData") or {}
    sender = body.get("from") or {}
    tenant = str(UUID((channel.get("tenant") or {}).get("id", "")))
    user = str(UUID(sender.get("aadObjectId", "")))
    if body.get("channelId") != "msteams" or conversation.get("conversationType") != "personal":
        raise ValueError("Only Teams personal chats are supported")
    if tenant != config.tenant_id or sender.get("role") == "bot":
        raise ValueError("Untrusted tenant or sender")
    if conversation.get("tenantId") and str(UUID(conversation["tenantId"])) != tenant:
        raise ValueError("Conflicting tenant identity")
    service_url = body.get("serviceUrl", "")
    url = urlsplit(service_url)
    # A connector-authenticated body must still not become an arbitrary outbound target.
    if (url.scheme != "https" or url.username or url.password or url.port not in (None, 443)
            or url.query or url.fragment or not url.hostname
            or not (url.hostname == "smba.trafficmanager.net"
                    or url.hostname.endswith(".smba.trafficmanager.net")
                    or url.hostname.endswith(".botframework.com"))):
        raise ValueError("Unsupported Bot Service URL")
    if not conversation.get("id") or not body.get("id"):
        raise ValueError("Missing activity identity")
    if len(conversation["id"]) > 2048 or len(body["id"]) > 2048:
        raise ValueError("Invalid activity identity")
    return Sender(tenant, user, conversation["id"], body["id"], service_url)


class GroupAuthorizer:
    """Check allowed-group membership using the same approved read-only SDK adapter."""
    def __init__(self, config: TeamsConfig, *, client=None):
        from src.config.settings import settings
        from src.core.entra.client import EntraAPIClient
        if config.tenant_id != settings.tenant_id:
            raise ValueError('Teams and directory tenant IDs must match')
        self.config = config
        self.client = client or EntraAPIClient()

    async def allowed(self, user: str) -> bool:
        user = str(UUID(user))
        result = await self.client.make_request(f'/users/{user}/transitiveMemberOf/microsoft.graph.group', params={'$select': 'id'})
        if result.get('status') != 'success' or not result.get('complete'):
            raise AccessUnavailable('Directory membership could not be verified')
        return bool({str(group['id']).lower() for group in result['data']}.intersection(self.config.group_ids))

    async def close(self):
        await self.client.close_session()
