# Swatantra Backend Package
__version__ = "1.0.0"
__author__ = "Swatantra Team"

from app.config import settings, get_settings
from app.db import db, get_db

__all__ = ["settings", "get_settings", "db", "get_db"]
