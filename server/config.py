"""Shared settings and path helpers for the server."""

from pathlib import Path

SERVER_NAME = "lab-server"

# Paths are anchored to the project folder, so the server behaves the same
# no matter which directory it is launched from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESOURCES_DIR = PROJECT_ROOT / "resources"


def safe_path(base: Path, relative: str) -> Path:
    """Join `relative` onto `base`, refusing paths that escape `base` (e.g. '../')."""
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError(f"Path '{relative}' is outside the allowed folder")
    return path
