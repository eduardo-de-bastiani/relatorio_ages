#!/usr/bin/env python3
"""Command-line entrypoint; does not convert documentary content."""
from migration_harness.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
