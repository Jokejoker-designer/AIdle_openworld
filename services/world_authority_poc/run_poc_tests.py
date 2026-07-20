#!/usr/bin/env python3
"""Run G6-001 World Authority POC acceptance tests (stdlib unittest, in-process only)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def main() -> int:
    from services.world_authority_poc.tests import test_poc

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_poc)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("G6_WORLD_AUTHORITY_SMOKE=PASS")
        return 0
    print("G6_WORLD_AUTHORITY_SMOKE=FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
