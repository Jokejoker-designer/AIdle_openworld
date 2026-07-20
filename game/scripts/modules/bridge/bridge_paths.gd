## Free Desktop Bridge path conventions (G2-005).
## Blueprint 08: file mode uses outbound/inbound bridge JSON under a locked layout.
## Paths are non-secret delivery metadata only (see transport.bridge_path_hint).
class_name BridgePaths
extends RefCounted

const EDITION_DESKTOP_BRIDGE_FREE := "desktop_bridge_free"
const SCHEMA_VERSION := "1.0.0"

## user:// layout (local only — no network).
const BRIDGE_ROOT := "user://bridge"
const OUTBOX_DIR := "user://bridge/outbox"
const INBOX_DIR := "user://bridge/inbox"
const OUTBOX_SNAPSHOT := "user://bridge/outbox/snapshot.json"
const INBOX_DECISION := "user://bridge/inbox/decision.json"

## Optional instruction wrapper prefix when copying "Send to AI" clipboard payload.
const CLIPBOARD_INSTRUCTION_HEADER := """# AIdle AGM Desktop Bridge — paste into your AI Desktop chat.
# Reply with ONE JSON object matching the AGM Decision Envelope schema.
# Do not include API keys, credentials, or executable code.
# --- WORLD STATE SNAPSHOT JSON ---
"""

const CHANNEL_CLIPBOARD := "clipboard"
const CHANNEL_FILE := "inbox_outbox_file"

## Rejection reason codes (stable for receipts / UI / smoke).
const REJECT_MALFORMED_JSON := "malformed_json"
const REJECT_NOT_OBJECT := "not_object"
const REJECT_SCHEMA_INVALID := "schema_invalid"
const REJECT_FORBIDDEN_FIELD := "forbidden_field"
const REJECT_STALE_SNAPSHOT := "stale_snapshot"
const REJECT_REPLAYED_DECISION := "replayed_decision"
const REJECT_WRONG_EDITION := "wrong_edition"
const REJECT_NO_LIVE_SNAPSHOT := "no_live_snapshot"
const REJECT_NO_PENDING := "no_pending_consent"
const REJECT_EMPTY_INPUT := "empty_input"


static func ensure_bridge_dirs() -> void:
	_ensure_dir(BRIDGE_ROOT)
	_ensure_dir(OUTBOX_DIR)
	_ensure_dir(INBOX_DIR)


static func _ensure_dir(path: String) -> void:
	var abs_path := ProjectSettings.globalize_path(path)
	if DirAccess.dir_exists_absolute(abs_path):
		return
	var err := DirAccess.make_dir_recursive_absolute(abs_path)
	if err != OK:
		push_warning("[BridgePaths] make_dir_recursive failed for %s err=%s" % [path, err])


static func outbox_snapshot_path() -> String:
	return OUTBOX_SNAPSHOT


static func inbox_decision_path() -> String:
	return INBOX_DECISION
