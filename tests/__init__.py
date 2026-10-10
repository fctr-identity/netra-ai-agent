"""All offline checks use disposable local storage and synthetic configuration."""
import os
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / 'DO_NOT_SHARE' / 'checks' / str(uuid4())
CHECKS.mkdir(parents=True)
os.environ.update({
    'NETRA_ENV_FILE': str(CHECKS / 'no-configuration-file'),
    'DB_DIR': str(CHECKS / 'database'),
    'CHAT_SESSIONS_DIR': str(CHECKS / 'conversations'),
    'ENTRA_TENANT_ID': '00000000-0000-0000-0000-000000000001',
    'ENTRA_CLIENT_ID': '', 'ENTRA_CLIENT_SECRET': '',
    'JWT_SECRET_KEY': '', 'TEAMS_ENABLE': 'false', 'QUERY_PROCEDURES_ENABLED': 'false',
    'AI_PROVIDER': 'openai_compatible', 'OPENAI_COMPATIBLE_TOKEN': 'offline-check-only',
    'OPENAI_COMPATIBLE_BASE_URL': 'https://models.invalid/v1',
    'OPENAI_COMPATIBLE_REASONING_MODEL': 'offline', 'OPENAI_COMPATIBLE_CODING_MODEL': 'offline',
})
