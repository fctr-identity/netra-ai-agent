"""Portable import shim. Downloaded scripts run from a configured Netra checkout."""
from src.core.entra.client.graph_client import EntraAPIClient
from src.core.entra.client.read_database import open_database

__all__ = ['EntraAPIClient', 'open_database']
