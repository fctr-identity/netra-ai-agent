"""Load the project's environment before any settings are captured."""

from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = Path(os.environ.get("NETRA_ENV_FILE", str(BASE_DIR / ".env")))


@lru_cache(maxsize=1)
def load_environment() -> None:
    # Explicit environment variables take precedence, including isolated checks.
    load_dotenv(ENV_FILE, override=False, encoding="utf-8")
