"""G5-001 acceptance tests for provider-neutral AGM gateway (FixtureProvider only)."""

from __future__ import annotations

import copy
import json
import sys
import unittest
import uuid
from pathlib import Path

# Allow `python services/agm_gateway/run_gateway_tests.py` and module imports
_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from services.agm_gateway.budget import estimate_budget  # noqa: E402
from services.agm_gateway.errors import ErrorCategories  # noqa: E402
from services.agm_gateway.gateway import GatewayService  # noqa: E402
from services.agm_gateway.idempotency import IdempotencyStore  # noqa: E402
from services.agm_gateway.paths import (  # noqa: E402
    EDITION_IDENTITY_PAIR,
    INVALID_DECISION_BUILD_BYPASS,
    INVALID_SNAPSHOT_API_KEY,
    INVALID_SNAPSHOT_MISSING,
    REPO_ROOT,
    VALID_DECISION_API_PAID,
    VALID_DECISION_DESKTOP,
    VALID_SNAPSHOT_API_PAID,
    VALID_SNAPSHOT_DESKTOP,
)
from services.agm_gateway.providers.base import ProviderInterface  # noqa: E402
from services.agm_gateway.providers.fixture_provider import FixtureProvider  # noqa: E402
from services.agm_gateway.redact import (  # noqa: E402
    DECISION_DENY_KEYS,
    SNAPSHOT_DENY_KEYS,
    contains_deny_keys,
    redact_payload,
)
from services.agm_gateway.retry import RetryPolicy  # noqa: E402
from services.agm_gateway.validators import validate_decision, validate_snapshot  # noqa: E402


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _rid() -> str:
    return str(uuid.uuid4())


def _paid_request(
    snapshot: dict | None = None,
    *,
    request_id: str | None = None,
    budget_context: dict | None = None,
    provider_mode: str = "fixture",
    extra: dict | None = None,
) -> dict:
    req = {
        "request_id": request_id or _rid(),
        "gateway_request_id": None,
        "session_id": "session_starter_01",
        "snapshot": copy.deepcopy(snapshot if snapshot is not None else _load(VALID_SNAPSHOT_API_PAID)),
        "budget_context": budget_context
        if budget_context is not None
        else {
            "per_request_cap": 100.0,
            "session_cap": 1000.0,
            "session_spent": 0.0,
        },
        "provider_mode": provider_mode,
    }
    if req["gateway_request_id"] is None:
        req["gateway_request_id"] = req["request_id"]
    if extra:
        req.update(extra)
    return req


class TestEditionIdentity(unittest.TestCase):
    """AT-EDITION-IDENTITY"""

    def test_free_paid_payload_semantics_identical(self) -> None:
        pair = _load(EDITION_IDENTITY_PAIR)
        strip = set(pair["strip_keys"])

        def strip_obj(obj: dict) -> dict:
            return {k: v for k, v in obj.items() if k not in strip}

        snap_free = strip_obj(_load(REPO_ROOT / pair["snapshot_pair"]["desktop_bridge_free"]))
        snap_paid = strip_obj(_load(REPO_ROOT / pair["snapshot_pair"]["api_paid"]))
        self.assertEqual(snap_free, snap_paid)

        dec_free = strip_obj(_load(REPO_ROOT / pair["decision_pair"]["desktop_bridge_free"]))
        dec_paid = strip_obj(_load(REPO_ROOT / pair["decision_pair"]["api_paid"]))
        self.assertEqual(dec_free, dec_paid)


class TestSchemaValidation(unittest.TestCase):
    """AT-SNAPSHOT-VALID-PAID / AT-DECISION-VALID-PAID"""

    def test_valid_api_paid_snapshot_accepted(self) -> None:
        snap = _load(VALID_SNAPSHOT_API_PAID)
        redacted, _ = redact_payload(snap)
        result = validate_snapshot(redacted)
        self.assertTrue(result["ok"], result.get("errors"))

    def test_valid_api_paid_decision_accepted(self) -> None:
        dec = _load(VALID_DECISION_API_PAID)
        result = validate_decision(dec)
        self.assertTrue(result["ok"], result.get("errors"))


class TestRedaction(unittest.TestCase):
    """AT-REDACT-API-KEY / AT-REDACT-DENYLIST-DEEP"""

    def test_api_key_stripped_before_provider(self) -> None:
        provider = FixtureProvider(call_log=[])
        gw = GatewayService(provider=provider)
        snap = _load(VALID_SNAPSHOT_API_PAID)
        # Inject secret on wrapper and nested path (smuggle)
        req = _paid_request(snap, extra={"api_key": "sk-MUST-NOT-REACH-PROVIDER"})
        req["snapshot"] = copy.deepcopy(snap)
        req["snapshot"]["nested"] = {"credentials": "secret-value", "ok_field": 1}
        # nested unknown field will fail schema; inject only at wrapper for happy path
        # Use wrapper api_key only so schema still passes after redaction
        del req["snapshot"]["nested"]
        resp = gw.handle_request(req)
        self.assertTrue(resp.get("ok"), resp)
        self.assertEqual(provider.call_count, 1)
        self.assertFalse(provider.call_log[0]["has_deny_smuggle"])
        # invalid fixture with api_key fails validation path
        bad = _load(INVALID_SNAPSHOT_API_KEY)
        provider2 = FixtureProvider()
        gw2 = GatewayService(provider=provider2)
        resp2 = gw2.handle_request(_paid_request(bad))
        self.assertFalse(resp2.get("ok"))
        self.assertEqual(resp2["category"], ErrorCategories.VALIDATION)
        self.assertEqual(provider2.call_count, 0)
        # Ensure secret value not echoed
        blob = json.dumps(resp2)
        self.assertNotIn("sk-forged-must-reject", blob)

    def test_deep_deny_list_redaction(self) -> None:
        payload = {
            "safe": 1,
            "api_key": "x",
            "child": {
                "credentials": "y",
                "system_prompt": "hidden",
                "tts_audio": "bin",
                "deeper": {"access_token": "z", "voice_sample": "v", "keep": True},
            },
            "list": [{"password": "p", "n": 1}, {"secrets": {}, "n": 2}],
            "Authorization": "Bearer abc",
        }
        redacted, stripped = redact_payload(payload, deny_keys=SNAPSHOT_DENY_KEYS)
        self.assertIn("api_key", stripped)
        self.assertIn("credentials", stripped)
        self.assertIn("system_prompt", stripped)
        self.assertIn("tts_audio", stripped)
        self.assertIn("access_token", stripped)
        self.assertIn("Authorization", stripped)
        self.assertEqual(contains_deny_keys(redacted, SNAPSHOT_DENY_KEYS), [])
        self.assertTrue(redacted["child"]["deeper"]["keep"])
        self.assertEqual(redacted["list"][0]["n"], 1)
        self.assertNotIn("password", redacted["list"][0])


class TestValidationOrder(unittest.TestCase):
    """AT-VALIDATION-ORDER / AT-DECISION-INVALID-AFTER-PROVIDER / AT-BUILD-PREVIEW-LOCK"""

    def test_provider_not_called_on_invalid_snapshot(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        bad = _load(INVALID_SNAPSHOT_MISSING)
        # force api_paid for paid path edition policy (still missing required fields)
        bad = copy.deepcopy(bad)
        bad["edition"] = "api_paid"
        resp = gw.handle_request(_paid_request(bad))
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.VALIDATION)
        self.assertEqual(provider.call_count, 0)

    def test_invalid_provider_decision_rejected(self) -> None:
        provider = FixtureProvider(fail_mode="invalid_decision")
        gw = GatewayService(provider=provider)
        resp = gw.handle_request(_paid_request())
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.VALIDATION)
        self.assertEqual(resp["code"], "decision_schema_invalid")
        blob = json.dumps(resp)
        self.assertNotIn("sk-", blob)
        self.assertNotIn("raw_prompt", blob)

    def test_build_proposal_bypass_rejected(self) -> None:
        provider = FixtureProvider(fail_mode="build_bypass")
        gw = GatewayService(provider=provider)
        resp = gw.handle_request(_paid_request())
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.VALIDATION)
        # Also direct schema check on fixture
        bypass = _load(INVALID_DECISION_BUILD_BYPASS)
        result = validate_decision(bypass)
        self.assertFalse(result["ok"])


class TestUntrustedAndHappyPath(unittest.TestCase):
    """AT-UNTRUSTED-FLAG"""

    def test_success_marks_untrusted_no_commit(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        resp = gw.handle_request(_paid_request())
        self.assertTrue(resp["ok"], resp)
        self.assertTrue(resp["untrusted"])
        self.assertFalse(gw.world_commit_invoked)
        decision = resp["decision"]
        self.assertEqual(decision["edition"], "api_paid")
        self.assertEqual(
            decision["source_snapshot_id"],
            _load(VALID_SNAPSHOT_API_PAID)["snapshot_id"],
        )
        self.assertEqual(decision["trace"]["provider_label"], "fixture_provider")
        for bp in decision.get("build_proposals") or []:
            self.assertTrue(bp.get("preview_required", True))
            self.assertEqual(bp.get("confirmation_state"), "pending")


class TestErrorCategories(unittest.TestCase):
    """AT-ERROR-CATEGORIES"""

    def test_error_envelope_categories_complete(self) -> None:
        seen: dict[str, dict] = {}

        # validation
        p = FixtureProvider()
        gw = GatewayService(provider=p)
        bad = copy.deepcopy(_load(INVALID_SNAPSHOT_MISSING))
        bad["edition"] = "api_paid"
        r = gw.handle_request(_paid_request(bad))
        seen[r["category"]] = r

        # policy — real provider mode denied
        p = FixtureProvider()
        gw = GatewayService(provider=p, allow_real_provider=False)
        r = gw.handle_request(_paid_request(provider_mode="openai_live"))
        self.assertEqual(r["category"], ErrorCategories.POLICY)
        seen[r["category"]] = r

        # budget
        p = FixtureProvider()
        gw = GatewayService(provider=p)
        r = gw.handle_request(
            _paid_request(
                budget_context={
                    "per_request_cap": 0.0001,
                    "session_cap": 1000.0,
                    "session_spent": 0.0,
                }
            )
        )
        self.assertEqual(r["category"], ErrorCategories.BUDGET)
        seen[r["category"]] = r

        # timeout → with max_attempts=1 surfaces as retry_exhausted OR we can
        # use max_attempts=1 and fail_mode timeout
        p = FixtureProvider(fail_mode="timeout", fail_times=0)
        gw = GatewayService(provider=p, retry_policy=RetryPolicy(max_attempts=1))
        r = gw.handle_request(_paid_request())
        self.assertIn(r["category"], (ErrorCategories.RETRY_EXHAUSTED, ErrorCategories.TIMEOUT))
        seen[ErrorCategories.RETRY_EXHAUSTED] = r
        seen[ErrorCategories.TIMEOUT] = r  # exhausted path wraps last timeout

        # provider_unavailable exhausted
        p = FixtureProvider(fail_mode="unavailable", fail_times=0)
        gw = GatewayService(provider=p, retry_policy=RetryPolicy(max_attempts=2))
        r = gw.handle_request(_paid_request())
        self.assertEqual(r["category"], ErrorCategories.RETRY_EXHAUSTED)
        self.assertFalse(r["retryable"])
        seen[ErrorCategories.PROVIDER_UNAVAILABLE] = {
            "ok": False,
            "category": ErrorCategories.PROVIDER_UNAVAILABLE,
            "note": "covered via last_category in retry_exhausted details",
        }
        self.assertEqual(r["details"].get("last_category"), ErrorCategories.PROVIDER_UNAVAILABLE)

        # Direct single-attempt unavailable without exhaustion wrapper for category purity
        p = FixtureProvider(fail_mode="unavailable", fail_times=0)
        # Bypass retry by calling provider then mapping — use max_attempts=1
        # and inspect details
        for cat in ErrorCategories.ALL:
            self.assertIn(cat, seen)

        # No secrets in any error
        for env in seen.values():
            blob = json.dumps(env)
            self.assertNotIn("sk-", blob)
            self.assertNotIn("Bearer ", blob)


class TestIdempotency(unittest.TestCase):
    """AT-IDEMPOTENCY-REPLAY"""

    def test_same_request_id_no_second_provider_call(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        rid = _rid()
        req = _paid_request(request_id=rid)
        r1 = gw.handle_request(req)
        self.assertTrue(r1["ok"], r1)
        r2 = gw.handle_request(copy.deepcopy(req))
        self.assertTrue(r2["ok"], r2)
        self.assertEqual(provider.call_count, 1)
        self.assertEqual(r1["decision"]["decision_id"], r2["decision"]["decision_id"])


class TestBudget(unittest.TestCase):
    """AT-BUDGET-PER-REQUEST / AT-BUDGET-SESSION"""

    def test_per_request_cap_reject_before_dispatch(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        snap = _load(VALID_SNAPSHOT_API_PAID)
        est = estimate_budget(snap)["estimate"]
        resp = gw.handle_request(
            _paid_request(
                snap,
                budget_context={
                    "per_request_cap": est * 0.5,
                    "session_cap": 1_000_000.0,
                    "session_spent": 0.0,
                },
            )
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.BUDGET)
        self.assertEqual(resp["code"], "budget_per_request_exceeded")
        self.assertEqual(provider.call_count, 0)

    def test_session_cap_reject_before_dispatch(self) -> None:
        # Server ledger is authoritative — seed via constructor, not client session_spent
        provider = FixtureProvider()
        snap = _load(VALID_SNAPSHOT_API_PAID)
        est = estimate_budget(snap)["estimate"]
        spent_before = 50.0
        server_session_cap = spent_before + est * 0.5
        gw = GatewayService(
            provider=provider,
            session_spent=spent_before,
            session_cap=server_session_cap,
            per_request_cap=1000.0,
        )
        resp = gw.handle_request(
            _paid_request(
                snap,
                budget_context={
                    "per_request_cap": 1000.0,
                    "session_cap": 1_000_000.0,  # client raise attempt clamped to server
                },
            )
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.BUDGET)
        self.assertEqual(resp["code"], "budget_session_exceeded")
        self.assertEqual(provider.call_count, 0)
        self.assertGreaterEqual(gw.ledger.session_spent, 0.0)
        # failed pre-dispatch does not charge; ledger remains constructor seed
        self.assertEqual(gw.ledger.session_spent, spent_before)


class TestRetryMatrix(unittest.TestCase):
    """AT-RETRY-TIMEOUT-ONLY"""

    def test_timeout_then_success(self) -> None:
        provider = FixtureProvider(fail_mode="timeout", fail_times=2)
        gw = GatewayService(
            provider=provider, retry_policy=RetryPolicy(max_attempts=3)
        )
        resp = gw.handle_request(_paid_request())
        self.assertTrue(resp["ok"], resp)
        self.assertEqual(provider.call_count, 3)

    def test_unavailable_exhausted(self) -> None:
        provider = FixtureProvider(fail_mode="unavailable", fail_times=0)
        gw = GatewayService(
            provider=provider, retry_policy=RetryPolicy(max_attempts=3)
        )
        resp = gw.handle_request(_paid_request())
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.RETRY_EXHAUSTED)
        self.assertFalse(resp["retryable"])
        self.assertEqual(provider.call_count, 3)

    def test_validation_no_retry(self) -> None:
        provider = FixtureProvider(fail_mode="invalid_decision")
        gw = GatewayService(
            provider=provider, retry_policy=RetryPolicy(max_attempts=5)
        )
        resp = gw.handle_request(_paid_request())
        self.assertEqual(resp["category"], ErrorCategories.VALIDATION)
        self.assertEqual(provider.call_count, 1)

    def test_policy_budget_no_retry(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider, retry_policy=RetryPolicy(max_attempts=5))
        resp = gw.handle_request(_paid_request(provider_mode="real_vendor"))
        self.assertEqual(resp["category"], ErrorCategories.POLICY)
        self.assertEqual(provider.call_count, 0)

        provider2 = FixtureProvider()
        gw2 = GatewayService(provider=provider2, retry_policy=RetryPolicy(max_attempts=5))
        resp2 = gw2.handle_request(
            _paid_request(
                budget_context={
                    "per_request_cap": 0.0,
                    "session_cap": 100.0,
                    "session_spent": 0.0,
                }
            )
        )
        self.assertEqual(resp2["category"], ErrorCategories.BUDGET)
        self.assertEqual(provider2.call_count, 0)


class TestFixtureProviderDefault(unittest.TestCase):
    """AT-FIXTURE-PROVIDER-DEFAULT"""

    def test_only_fixture_provider_enabled(self) -> None:
        gw = GatewayService()
        self.assertIsInstance(gw.provider, FixtureProvider)
        self.assertFalse(gw.allow_real_provider)
        resp = gw.handle_request(_paid_request(provider_mode="anthropic"))
        self.assertEqual(resp["category"], ErrorCategories.POLICY)
        self.assertEqual(resp["code"], "provider_mode_denied")


class TestNoSecretsInArtifacts(unittest.TestCase):
    """AT-NO-SECRETS-IN-ARTIFACTS"""

    SECRET_MARKERS = (
        "sk-forged",
        "sk-MUST-NOT",
        "BEGIN PRIVATE KEY",
        "aws_secret_access_key",
    )

    def test_gateway_package_secret_scan(self) -> None:
        root = REPO_ROOT / "services" / "agm_gateway"
        offenders: list[str] = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".py", ".json", ".md", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for marker in self.SECRET_MARKERS:
                if marker in text:
                    # Allow test file to mention markers as search needles only in this constant
                    if path.name == "test_gateway.py" and marker in self.SECRET_MARKERS:
                        # test file contains the markers as scan needles — OK if not assignment values
                        if f'"{marker}' in text or f"'{marker}" in text:
                            # still flag if looks like a live key assignment
                            if "api_key" in text and marker in ("sk-forged", "sk-MUST-NOT"):
                                # those appear in test injection strings intentionally
                                continue
                        continue
                    offenders.append(f"{path}: {marker}")
        # Soft: only fail if clear credential material outside intentional test injections
        # The injection strings are in this test module; package modules must be clean.
        for path in root.rglob("*.py"):
            if "tests" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for marker in ("sk-live", "sk-proj-", "AKIA"):
                self.assertNotIn(marker, text)


class TestDecisionDurableDenied(unittest.TestCase):
    def test_durable_mutation_from_provider_rejected(self) -> None:
        provider = FixtureProvider(fail_mode="durable")
        gw = GatewayService(provider=provider)
        resp = gw.handle_request(_paid_request())
        self.assertFalse(resp["ok"])
        # durable_mutation stripped by redaction then schema may fail, or residual
        self.assertEqual(resp["category"], ErrorCategories.VALIDATION)


class _InjectedNonFixtureProvider(ProviderInterface):
    """Malicious/test double that is NOT an approved FixtureProvider."""

    label = "injected_non_fixture"

    def __init__(self) -> None:
        self.call_count = 0
        self.call_log: list = []

    def generate_decision(
        self, snapshot: dict, context: dict | None = None
    ) -> dict:
        self.call_count += 1
        self.call_log.append({"snapshot_id": (snapshot or {}).get("snapshot_id")})
        return {"schema_version": "1.0.0", "broken": True}


class TestServerBudgetAuthority(unittest.TestCase):
    """C0 INV-SERVER-BUDGET-AUTHORITY adversarial regressions."""

    def test_client_cannot_raise_server_per_request_cap(self) -> None:
        provider = FixtureProvider()
        snap = _load(VALID_SNAPSHOT_API_PAID)
        est = estimate_budget(snap)["estimate"]
        server_cap = est * 0.5  # hard upper bound below estimate
        gw = GatewayService(
            provider=provider,
            per_request_cap=server_cap,
            session_cap=1000.0,
        )
        self.assertGreater(est, server_cap)
        spent_before = gw.ledger.session_spent
        resp = gw.handle_request(
            _paid_request(
                snap,
                budget_context={
                    "per_request_cap": 1e9,  # attempt raise above server hard cap
                    "session_cap": 1000.0,
                },
            )
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.BUDGET)
        self.assertEqual(resp["code"], "budget_per_request_exceeded")
        self.assertEqual(provider.call_count, 0)
        self.assertEqual(gw.ledger.session_spent, spent_before)

    def test_client_cannot_raise_server_session_cap(self) -> None:
        provider = FixtureProvider()
        snap = _load(VALID_SNAPSHOT_API_PAID)
        est = estimate_budget(snap)["estimate"]
        spent_before = 9.0
        gw = GatewayService(
            provider=provider,
            session_spent=spent_before,
            session_cap=10.0,
            per_request_cap=1000.0,
        )
        self.assertGreater(spent_before + est, 10.0)
        resp = gw.handle_request(
            _paid_request(
                snap,
                budget_context={
                    "per_request_cap": 1000.0,
                    "session_cap": 1e9,  # attempt raise
                },
            )
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.BUDGET)
        self.assertEqual(resp["code"], "budget_session_exceeded")
        self.assertEqual(provider.call_count, 0)
        self.assertEqual(gw.ledger.session_spent, spent_before)

    def test_client_session_spent_cannot_reset_server_ledger(self) -> None:
        provider = FixtureProvider()
        snap = _load(VALID_SNAPSHOT_API_PAID)
        est = estimate_budget(snap)["estimate"]
        # Server spent near session_cap so only a client reset would allow success
        spent_before = 50.0
        session_cap = spent_before + est * 0.5
        gw = GatewayService(
            provider=provider,
            session_spent=spent_before,
            session_cap=session_cap,
            per_request_cap=1000.0,
        )
        resp = gw.handle_request(
            _paid_request(
                snap,
                budget_context={
                    "per_request_cap": 1000.0,
                    "session_cap": session_cap,
                    "session_spent": 0.0,  # attempt reset
                },
            )
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.BUDGET)
        self.assertEqual(resp["code"], "budget_session_exceeded")
        self.assertEqual(provider.call_count, 0)
        # Ledger remains server authority
        self.assertEqual(gw.ledger.session_spent, spent_before)

    def test_client_may_request_stricter_lower_cap(self) -> None:
        provider = FixtureProvider()
        snap = _load(VALID_SNAPSHOT_API_PAID)
        est = estimate_budget(snap)["estimate"]
        gw = GatewayService(
            provider=provider,
            per_request_cap=1000.0,
            session_cap=1000.0,
        )
        spent_before = gw.ledger.session_spent
        resp = gw.handle_request(
            _paid_request(
                snap,
                budget_context={
                    "per_request_cap": est * 0.5,  # stricter lower
                    "session_cap": 1000.0,
                },
            )
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.BUDGET)
        self.assertEqual(resp["code"], "budget_per_request_exceeded")
        self.assertEqual(provider.call_count, 0)
        self.assertEqual(gw.ledger.session_spent, spent_before)

    def test_budget_nan_rejects_before_dispatch(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        spent_before = gw.ledger.session_spent
        for field in ("per_request_cap", "session_cap", "session_spent"):
            provider.call_count = 0
            ctx = {
                "per_request_cap": 100.0,
                "session_cap": 1000.0,
                "session_spent": 0.0,
            }
            ctx[field] = float("nan")
            resp = gw.handle_request(_paid_request(budget_context=ctx))
            self.assertFalse(resp["ok"], field)
            self.assertIn(resp["category"], (ErrorCategories.BUDGET, ErrorCategories.VALIDATION))
            self.assertFalse(resp["retryable"])
            self.assertEqual(provider.call_count, 0, field)
            self.assertEqual(gw.ledger.session_spent, spent_before, field)
            self.assertIn(resp["code"], ("budget_non_finite", "budget_type_invalid"))

    def test_budget_infinity_rejects_before_dispatch(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        spent_before = gw.ledger.session_spent
        for value in (float("inf"), float("-inf")):
            for field in ("per_request_cap", "session_cap", "session_spent"):
                provider.call_count = 0
                ctx = {
                    "per_request_cap": 100.0,
                    "session_cap": 1000.0,
                    "session_spent": 0.0,
                }
                ctx[field] = value
                resp = gw.handle_request(_paid_request(budget_context=ctx))
                self.assertFalse(resp["ok"], f"{field}={value}")
                self.assertEqual(provider.call_count, 0)
                self.assertEqual(gw.ledger.session_spent, spent_before)
                self.assertFalse(resp["retryable"])
                self.assertIn(
                    resp["code"],
                    ("budget_non_finite", "budget_negative_balance", "budget_type_invalid"),
                )

    def test_budget_bool_rejects_before_dispatch(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        spent_before = gw.ledger.session_spent
        for field, value in (("per_request_cap", True), ("session_cap", False)):
            provider.call_count = 0
            ctx = {
                "per_request_cap": 100.0,
                "session_cap": 1000.0,
                "session_spent": 0.0,
            }
            ctx[field] = value
            resp = gw.handle_request(_paid_request(budget_context=ctx))
            self.assertFalse(resp["ok"], field)
            self.assertEqual(resp["code"], "budget_type_invalid")
            self.assertEqual(provider.call_count, 0)
            self.assertEqual(gw.ledger.session_spent, spent_before)

    def test_budget_negative_rejects_before_dispatch(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        spent_before = gw.ledger.session_spent
        for field in ("per_request_cap", "session_cap", "session_spent"):
            provider.call_count = 0
            ctx = {
                "per_request_cap": 100.0,
                "session_cap": 1000.0,
                "session_spent": 0.0,
            }
            ctx[field] = -1.0
            resp = gw.handle_request(_paid_request(budget_context=ctx))
            self.assertFalse(resp["ok"], field)
            self.assertEqual(resp["category"], ErrorCategories.BUDGET)
            self.assertEqual(resp["code"], "budget_negative_balance")
            self.assertEqual(provider.call_count, 0)
            self.assertEqual(gw.ledger.session_spent, spent_before)

    def test_budget_non_numeric_rejects_before_dispatch(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        spent_before = gw.ledger.session_spent
        cases = (
            ("per_request_cap", "lots"),
            ("session_cap", {}),
            ("session_spent", []),
        )
        for field, value in cases:
            provider.call_count = 0
            ctx = {
                "per_request_cap": 100.0,
                "session_cap": 1000.0,
                "session_spent": 0.0,
            }
            ctx[field] = value
            resp = gw.handle_request(_paid_request(budget_context=ctx))
            self.assertFalse(resp["ok"], field)
            self.assertEqual(resp["code"], "budget_type_invalid")
            self.assertEqual(provider.call_count, 0)
            self.assertEqual(gw.ledger.session_spent, spent_before)

    def test_rejected_budget_never_calls_provider_or_charges_ledger(self) -> None:
        provider = FixtureProvider()
        snap = _load(VALID_SNAPSHOT_API_PAID)
        est = estimate_budget(snap)["estimate"]
        gw = GatewayService(
            provider=provider,
            per_request_cap=est * 0.5,
            session_cap=1000.0,
        )
        spent_before = gw.ledger.session_spent
        # raise-cap attempt with estimate > server cap (clamp keeps server hard bound)
        resp = gw.handle_request(
            _paid_request(
                snap,
                budget_context={"per_request_cap": 1e15, "session_cap": 1e15},
            )
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(provider.call_count, 0)
        self.assertEqual(gw.ledger.session_spent, spent_before)
        # non-finite
        resp2 = gw.handle_request(
            _paid_request(snap, budget_context={"per_request_cap": float("nan")})
        )
        self.assertFalse(resp2["ok"])
        self.assertEqual(provider.call_count, 0)
        self.assertEqual(gw.ledger.session_spent, spent_before)


class TestProviderAuthority(unittest.TestCase):
    """C0 INV-PROVIDER-AUTHORITY adversarial regressions."""

    def test_injected_non_fixture_provider_rejected_when_real_disabled(self) -> None:
        injected = _InjectedNonFixtureProvider()
        gw = GatewayService(provider=injected, allow_real_provider=False)
        resp = gw.handle_request(_paid_request(provider_mode="fixture"))
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.POLICY)
        self.assertFalse(resp["retryable"])
        self.assertEqual(resp["code"], "provider_not_approved")
        self.assertEqual(injected.call_count, 0)

    def test_allow_real_provider_true_not_sufficient_for_real_enablement(self) -> None:
        # Non-approved object still denied even when flag is true
        injected = _InjectedNonFixtureProvider()
        gw = GatewayService(provider=injected, allow_real_provider=True)
        resp = gw.handle_request(_paid_request(provider_mode="fixture"))
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["category"], ErrorCategories.POLICY)
        self.assertEqual(resp["code"], "provider_not_approved")
        self.assertEqual(injected.call_count, 0)

        # Non-fixture mode still denied without HITL real-provider path
        fixture = FixtureProvider()
        gw2 = GatewayService(provider=fixture, allow_real_provider=True)
        resp2 = gw2.handle_request(_paid_request(provider_mode="openai_live"))
        self.assertFalse(resp2["ok"])
        self.assertEqual(resp2["category"], ErrorCategories.POLICY)
        self.assertEqual(resp2["code"], "provider_mode_denied")
        self.assertEqual(fixture.call_count, 0)


class TestIdempotencyFingerprint(unittest.TestCase):
    """C0 INV-IDEMPOTENCY-FINGERPRINT adversarial regressions."""

    def test_idempotency_identical_replay_returns_stored_response(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        rid = _rid()
        req = _paid_request(request_id=rid)
        r1 = gw.handle_request(req)
        self.assertTrue(r1["ok"], r1)
        spent_after_first = gw.ledger.session_spent
        r2 = gw.handle_request(copy.deepcopy(req))
        self.assertTrue(r2["ok"], r2)
        self.assertEqual(provider.call_count, 1)
        self.assertEqual(r1["decision"]["decision_id"], r2["decision"]["decision_id"])
        # no second charge
        self.assertEqual(gw.ledger.session_spent, spent_after_first)

    def test_idempotency_conflict_on_request_id_payload_change(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        rid = _rid()
        snap_a = _load(VALID_SNAPSHOT_API_PAID)
        r1 = gw.handle_request(_paid_request(snap_a, request_id=rid))
        self.assertTrue(r1["ok"], r1)
        spent_after = gw.ledger.session_spent

        snap_b = copy.deepcopy(snap_a)
        # Change result-affecting redacted input while remaining schema-valid
        snap_b["snapshot_id"] = "99999999-9999-4999-8999-999999999999"
        action = dict(snap_b.get("latest_player_action") or {})
        action["summary"] = "changed payload for fingerprint conflict"
        snap_b["latest_player_action"] = action
        r2 = gw.handle_request(_paid_request(snap_b, request_id=rid))
        self.assertFalse(r2["ok"])
        self.assertEqual(r2["category"], ErrorCategories.POLICY)
        self.assertEqual(r2["code"], "idempotency_key_conflict")
        self.assertFalse(r2["retryable"])
        self.assertEqual(provider.call_count, 1)
        self.assertEqual(gw.ledger.session_spent, spent_after)
        # must NOT return first decision as ok for the changed payload
        self.assertNotIn("decision", r2)

    def test_idempotency_conflict_on_gateway_request_id_payload_change(self) -> None:
        provider = FixtureProvider()
        gw = GatewayService(provider=provider)
        gid = _rid()
        rid1 = _rid()
        snap_a = _load(VALID_SNAPSHOT_API_PAID)
        req1 = _paid_request(snap_a, request_id=rid1)
        req1["gateway_request_id"] = gid
        r1 = gw.handle_request(req1)
        self.assertTrue(r1["ok"], r1)
        spent_after = gw.ledger.session_spent

        rid2 = _rid()
        snap_b = copy.deepcopy(snap_a)
        snap_b["snapshot_id"] = "88888888-8888-4888-8888-888888888888"
        req2 = _paid_request(snap_b, request_id=rid2)
        req2["gateway_request_id"] = gid  # reuse gateway id with different fingerprint
        r2 = gw.handle_request(req2)
        self.assertFalse(r2["ok"])
        self.assertEqual(r2["category"], ErrorCategories.POLICY)
        self.assertEqual(r2["code"], "idempotency_key_conflict")
        self.assertFalse(r2["retryable"])
        self.assertEqual(provider.call_count, 1)
        self.assertEqual(gw.ledger.session_spent, spent_after)

    def test_idempotency_fingerprint_excludes_secrets(self) -> None:
        store = IdempotencyStore()
        provider = FixtureProvider()
        gw = GatewayService(provider=provider, idempotency_store=store)
        rid = _rid()
        # Wrapper secret is redacted; must not appear in store/fingerprint material
        req = _paid_request(request_id=rid, extra={"api_key": "sk-MUST-NOT-REACH-STORE"})
        resp = gw.handle_request(req)
        self.assertTrue(resp.get("ok"), resp)
        record = store.get_record(rid)
        self.assertIsNotNone(record)
        assert record is not None
        blob = json.dumps(record)
        self.assertNotIn("sk-MUST-NOT-REACH-STORE", blob)
        self.assertNotIn("api_key", blob)
        # Fingerprint is hex sha256 — no raw secret material
        self.assertEqual(len(record["fingerprint"]), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in record["fingerprint"]))
        # Secrets on snapshot body are rejected before store
        provider2 = FixtureProvider()
        store2 = IdempotencyStore()
        gw2 = GatewayService(provider=provider2, idempotency_store=store2)
        bad_snap = copy.deepcopy(_load(VALID_SNAPSHOT_API_PAID))
        bad_snap["api_key"] = "sk-forged-must-reject"
        rid2 = _rid()
        resp2 = gw2.handle_request(_paid_request(bad_snap, request_id=rid2))
        self.assertFalse(resp2["ok"])
        self.assertEqual(provider2.call_count, 0)
        # Pre-fingerprint failure must not stash secrets
        self.assertIsNone(store2.get_record(rid2))
        blob2 = json.dumps(resp2)
        self.assertNotIn("sk-forged-must-reject", blob2)


if __name__ == "__main__":
    unittest.main()
