#!/usr/bin/env python3
"""Run G5-001 AGM gateway acceptance tests (stdlib unittest, no network)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def main() -> int:
    # Import suite directly to avoid package discover recursion under services/
    from services.agm_gateway.tests import test_gateway

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_gateway)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("G5_AGM_GATEWAY_SMOKE=PASS")
        return 0
    print("G5_AGM_GATEWAY_SMOKE=FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
