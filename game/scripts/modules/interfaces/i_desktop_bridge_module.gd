## Interface contract for Free Desktop Bridge (G2-005).
## Transport only: export World State Snapshot, import Decision Envelope with
## visible manual consent. No network/API SDK. No durable world mutation.
## AGM Decision execution is owned by G2-006 executor — bridge never commits.
class_name IDesktopBridgeModule
extends RefCounted

## Expected methods:
## func build_snapshot(context: Dictionary = {}) -> Dictionary
## func export_snapshot_to_clipboard(context: Dictionary = {}) -> Dictionary
## func export_snapshot_to_file(context: Dictionary = {}, path: String = "") -> Dictionary
## func import_decision_from_text(raw_text: String, auto_consent: bool = false) -> Dictionary
## func import_decision_from_clipboard(auto_consent: bool = false) -> Dictionary
## func import_decision_from_file(path: String = "", auto_consent: bool = false) -> Dictionary
## func has_pending_consent() -> bool
## func get_pending_decision() -> Dictionary
## func confirm_pending_decision() -> Dictionary
## func reject_pending_decision(reason: String = "player_rejected") -> Dictionary
## func get_live_snapshot_id() -> String
## func get_accepted_decision() -> Dictionary
## func list_seen_decision_ids() -> PackedStringArray
## func get_last_rejection() -> Dictionary
## func uses_network() -> bool  # must return false

const REQUIRED_METHODS := [
	"build_snapshot",
	"export_snapshot_to_clipboard",
	"export_snapshot_to_file",
	"import_decision_from_text",
	"import_decision_from_clipboard",
	"import_decision_from_file",
	"has_pending_consent",
	"get_pending_decision",
	"confirm_pending_decision",
	"reject_pending_decision",
	"get_live_snapshot_id",
	"get_accepted_decision",
	"list_seen_decision_ids",
	"get_last_rejection",
	"uses_network",
]

const FORBIDDEN_NETWORK_SYMBOLS := [
	"HTTPRequest",
	"HTTPClient",
	"WebSocketPeer",
	"WebSocketClient",
	"PacketPeerUDP",
	"StreamPeerTCP",
	"MultiplayerAPI",
	"api_key",
	"OPENAI",
	"Bearer ",
]


static func validate(module: Object) -> PackedStringArray:
	var missing: PackedStringArray = []
	for m in REQUIRED_METHODS:
		if not module.has_method(m):
			missing.append(m)
	return missing


static func audit_no_network(module: Object) -> PackedStringArray:
	var issues: PackedStringArray = []
	if module.has_method("uses_network") and bool(module.call("uses_network")):
		issues.append("uses_network() returned true")
	return issues
