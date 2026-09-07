"""Pure helpers for repository search pattern construction."""


def search_pattern(text: str) -> str:
    """Build a literal case-insensitive SQL LIKE containment pattern."""
    escaped = text.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"
