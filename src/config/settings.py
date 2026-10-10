"""Local, single-tenant Netra configuration."""
import re
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.config.environment import BASE_DIR, ENV_FILE, load_environment

load_environment()


@lru_cache(maxsize=1)
def _process_jwt_secret() -> str:
    return secrets.token_urlsafe(64)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra='ignore', hide_input_in_errors=True)
    ENTRA_TENANT_ID: str = ''
    ENTRA_CLIENT_ID: str = ''
    ENTRA_CLIENT_SECRET: str = Field(default='', repr=False)
    ENTRA_USER_CUSTOM_ATTRIBUTES: str = ''
    GRAPH_CONCURRENT_LIMIT: int = Field(default=4, ge=1, le=20)
    GRAPH_MAX_PAGES: int = Field(default=1000, ge=1)
    GRAPH_TIMEOUT_SECONDS: int = Field(default=90, ge=10, le=600)
    SYNC_MFA_REGISTRATION: bool = True
    SYNC_DIRECTORY_ROLES: bool = False
    SYNC_CONDITIONAL_ACCESS: bool = False
    SYNC_DEVICES: bool = False
    DB_DIR: str = str(BASE_DIR / 'sqlite_db')
    DB_FILENAME: str = 'netra.db'
    CHAT_SESSIONS_DIR: str = str(BASE_DIR / 'chat_sessions')
    DATABASE_URL: Optional[str] = None
    SQLITE_PATH: Optional[str] = None
    LOG_LEVEL: str = 'INFO'
    NUM_OF_THREADS: int = 4
    JWT_SECRET_KEY: str = Field(default='', repr=False, validate_default=True)
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ISSUER: str = 'netra-ai-agent'
    JWT_AUDIENCE: str = 'ui-user'
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = 'lax'
    COOKIE_MAX_AGE_MINUTES: int = 30
    AI_PROVIDER: str = 'openai_compatible'
    USE_PRE_REASONING: bool = True
    QUERY_PROCEDURES_ENABLED: bool = False
    QUERY_PROCEDURES_MAX_PER_TENANT: int = Field(default=100, ge=1, le=500)
    QUERY_PROCEDURES_CATALOG_CHARS: int = Field(default=32000, ge=1000, le=100000)
    TEAMS_ENABLE: bool = False

    @field_validator('JWT_SECRET_KEY', mode='before')
    @classmethod
    def resolve_jwt_secret(cls, value):
        if not value or str(value).strip().lower() in {'change-this-key-in-production-environments', 'default_secret_insecure'}:
            return _process_jwt_secret()
        if len(str(value).encode('utf-8')) < 32:
            raise ValueError('JWT_SECRET_KEY must be at least 32 bytes or blank for a temporary local key.')
        return value

    @field_validator('ENTRA_USER_CUSTOM_ATTRIBUTES')
    @classmethod
    def validate_attributes(cls, value):
        for name in filter(None, (item.strip() for item in value.split(','))):
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)?', name):
                raise ValueError('Custom attributes must be Graph property names, optionally with one nested property.')
            if name.split('.')[0] in {'passwordProfile', 'extensions', 'customSecurityAttributes'}:
                raise ValueError('This attribute type is not supported by the initial sync. Use selected user properties, directory/schema extensions, or onPremisesExtensionAttributes.')
        return value

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        path = Path(self.DB_DIR).resolve() / self.DB_FILENAME
        path.parent.mkdir(parents=True, exist_ok=True)
        Path(self.CHAT_SESSIONS_DIR).mkdir(parents=True, exist_ok=True)
        self.SQLITE_PATH = str(path)
        self.DATABASE_URL = f'sqlite+aiosqlite:///{path}'

    @property
    def tenant_id(self) -> str:
        return self.ENTRA_TENANT_ID.strip()

    @property
    def entra_user_custom_attributes_list(self) -> list[str]:
        return list(dict.fromkeys(item.strip() for item in self.ENTRA_USER_CUSTOM_ATTRIBUTES.split(',') if item.strip()))


settings = Settings()
