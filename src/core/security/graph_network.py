"""Validate planned requests against the same catalog used by the SDK adapter."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class NetworkSecurityResult:
    is_allowed: bool
    violations: list[str]
    blocked_reason: Optional[str]
    risk_level: str


class NetworkSecurityValidator:
    def validate_url(self, url):
        from src.core.entra.client.graph_client import operation_for, validate_graph_url
        try:
            if url.startswith('/') and not url.startswith('//'):
                operation_for(url)
            else:
                validate_graph_url(url)
            return NetworkSecurityResult(True, [], None, 'LOW')
        except ValueError as exc:
            return NetworkSecurityResult(False, [str(exc)], str(exc), 'HIGH')

    def validate_request_data(self, method, url, headers=None, data=None):
        if method != 'GET' or data is not None:
            return NetworkSecurityResult(False, ['Only body-free GET requests are allowed'], 'Read only', 'HIGH')
        return self.validate_url(url)

    def get_security_headers(self):
        return {'Accept': 'application/json'}


def validate_url(url):
    return NetworkSecurityValidator().validate_url(url)


def validate_request(method, url, headers=None, data=None):
    return NetworkSecurityValidator().validate_request_data(method, url, headers, data)


def get_security_headers():
    return NetworkSecurityValidator().get_security_headers()
