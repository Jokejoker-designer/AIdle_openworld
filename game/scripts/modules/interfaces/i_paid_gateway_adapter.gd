## Interface contract for Paid AGM Gateway client adapter (G5-001 A2).
## Godot calls a trusted gateway only (fixture path in tests). No provider SDK,
## no secrets, no outbound internet. Decision remains untrusted proposal.
## Same Snapshot/Decision contracts as Free Desktop Bridge (edition=api_paid).
class_name IPaidGatewayAdapter
extends RefCounted

## Expected methods:
## func build_snapshot(context: Dictionary = {}) -> Dictionary
## func handle_request(gateway_request: Dictionary) -> Dictionary
## func request_decision(context: Dictionary = {}) -> Dictionary
## func receive_untrusted_response(response: Dictionary, auto_consent: bool = false) -> Dictionary
## func has_pending_consent() -> bool
## func get_pending_decision() -> Dictionary
## func confirm_pending_decision() -> Dictionary
## func reject_pending_decision(reason: String = "player_rejected") -> Dictionary
## func get_accepted_decision() -> Dictionary
## func get_live_snapshot_id() -> String
## func get_edition() -> String
## func get_provider_mode() -> String
## func uses_network() -> bool
## func holds_provider_secrets() -> bool
## func list_error_categories() -> PackedStringArray

const REQUIRED_METHODS := [
	"build_snapshot",
	"handle_request",
	"request_decision",
	"receive_untrusted_response",
	"has_pending_consent",
	"get_pending_decision",
	"confirm_pending_decision",
	"reject_pending_decision",
	"get_accepted_decision",
	"get_live_snapshot_id",
	"get_edition",
	"get_provider_mode",
	"uses_network",
	"holds_provider_secrets",
	"list_error_categories",
]

## Forbidden symbols/tokens in adapter source or runtime config (no provider SDK/secrets).
## Names only — never store live credential values in this list or elsewhere in Godot.
const FORBIDDEN_SECRET_NAME_HINTS := [
	"provider_sdk",
	"live_credential",
	"auth_header_value",
	"client_secret_value",
]

const FORBIDDEN_NETWORK_SYMBOLS := [
	"HTTPRequest",
	"HTTPClient",
	"WebSocketPeer",
	"WebSocketClient",
	"PacketPeerUDP",
	"StreamPeerTCP",
	"MultiplayerAPI",
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
		issues.append("uses_network() returned true (fixture/test adapter must stay offline)")
	return issues


static func audit_no_secrets(module: Object) -> PackedStringArray:
	var issues: PackedStringArray = []
	if module.has_method("holds_provider_secrets") and bool(module.call("holds_provider_secrets")):
		issues.append("holds_provider_secrets() returned true")
	return issues
