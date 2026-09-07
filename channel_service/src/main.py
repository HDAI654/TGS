"""Channels service entrypoint."""

from src.presentation.app import app
from src.logging_config import setup_logging
import os

setup_logging()

__all__ = ["app"]
