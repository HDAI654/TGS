#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
    from django.core.management import execute_from_command_line
    from src.settings import BASE_DIR

    load_dotenv(BASE_DIR / ".env")

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
