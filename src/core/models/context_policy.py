"""Project all model-bound context to text without external hyperlinks.

Source records and saved artifacts are unchanged; projection happens at the model
boundary, covering instructions, tool results, history and structured schemas.
"""
import dataclasses
import re
from contextlib import asynccontextmanager
from pydantic_ai.models.wrapper import WrapperModel

_URL = re.compile(r'(?i)\b(?:https?://|ftp://|file://|www\.)[^\s<>"\]\\]+')
_DOMAIN = re.compile(r'(?i)(?<![\w@.])(?:[a-z0-9-]+\.)+(?:com|org|net|io|dev|gov|edu)(?:/[^\s<>"\]\\]*)?\b')


def sanitize_text(value: str) -> str:
    value = re.sub(r'!?\[([^\]]*)\]\((?:https?://|www\.)[^)]*\)', r'\1 [link omitted]', value, flags=re.I)
    return _DOMAIN.sub('[link omitted]', _URL.sub('[link omitted]', value))


def project_context(value):
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, dict):
        return {sanitize_text(key) if isinstance(key, str) else key: project_context(item)
                for key, item in value.items() if key not in {'@odata.context', '@odata.nextLink', '@odata.deltaLink'}}
    if isinstance(value, list):
        return [project_context(item) for item in value]
    if isinstance(value, tuple):
        return tuple(project_context(item) for item in value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.replace(value, **{field.name: project_context(getattr(value, field.name))
                                          for field in dataclasses.fields(value) if field.init})
    return value


class ContextPolicyModel(WrapperModel):
    async def request(self, messages, model_settings, model_request_parameters):
        if getattr(model_request_parameters, 'builtin_tools', None):
            raise ValueError('Provider browsing and other built-in tools are disabled in Netra')
        return await self.wrapped.request(project_context(messages), model_settings, project_context(model_request_parameters))

    @asynccontextmanager
    async def request_stream(self, messages, model_settings, model_request_parameters, run_context=None):
        if getattr(model_request_parameters, 'builtin_tools', None):
            raise ValueError('Provider built-in tools are disabled in Netra')
        async with self.wrapped.request_stream(project_context(messages), model_settings,
                project_context(model_request_parameters), run_context) as stream:
            yield stream

    async def count_tokens(self, messages, model_settings, model_request_parameters):
        return await self.wrapped.count_tokens(project_context(messages), model_settings, project_context(model_request_parameters))
