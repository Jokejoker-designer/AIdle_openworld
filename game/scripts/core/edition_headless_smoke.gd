## Headless smoke for G2-007 (Godot -s).
## Verifies edition enums, persistence API, consent gate, and no client secrets.
## Autoloads are resolved at runtime (not compile-time) for -s SceneTree scripts.
extends SceneTree

var _failures: PackedStringArray = []
var _C: Node
var _SM: Node


func _initialize() -> void:
	print("[G2-007 smoke] starting…")
	_C = root.get_node_or_null("AIdleConstants")
	_SM = root.get_node_or_null("SettingsManager")
	if _C == null:
		_fail("autoload AIdleConstants missing")
		_finish()
		return
	if _SM == null:
		_fail("autoload SettingsManager missing")
		_finish()
		return

	_test_enums()
	_test_ephemeral_and_consent()
	_test_no_secrets()
	_test_export_meta()
	_finish()


func _fail(msg: String) -> void:
	_failures.append(msg)


func _test_enums() -> void:
	if str(_C.EDITION_DESKTOP_BRIDGE_FREE) != "desktop_bridge_free":
		_fail("EDITION_DESKTOP_BRIDGE_FREE mismatch")
	if str(_C.EDITION_API_PAID) != "api_paid":
		_fail("EDITION_API_PAID mismatch")
	if _C.AGM_EDITIONS.size() != 2:
		_fail("AGM_EDITIONS size != 2")
	if not bool(_SM.is_valid_edition("desktop_bridge_free")):
		_fail("desktop_bridge_free not valid")
	if not bool(_SM.is_valid_edition("api_paid")):
		_fail("api_paid not valid")
	if bool(_SM.is_valid_edition("enterprise_secret")):
		_fail("bogus edition accepted")
	if not bool(_SM.uses_same_agm_contracts()):
		_fail("uses_same_agm_contracts false")


func _test_ephemeral_and_consent() -> void:
	var free_id: String = str(_C.EDITION_DESKTOP_BRIDGE_FREE)
	var paid_id: String = str(_C.EDITION_API_PAID)

	if not bool(_SM.set_edition(free_id, false, false)):
		_fail("set free edition (ephemeral) failed")
	if str(_SM.get_edition()) != free_id:
		_fail("get free edition mismatch")
	if not bool(_SM.has_chosen_edition()):
		_fail("has_chosen_edition false after set")

	# Ephemeral free → paid (runtime-only; no disk choice yet → no consent).
	if not bool(_SM.set_edition(paid_id, false, false)):
		_fail("ephemeral switch free→paid failed")
	if str(_SM.get_edition()) != paid_id:
		_fail("ephemeral paid not active")

	# Persist free, then change without consent → must fail; with consent → ok.
	if not bool(_SM.set_edition(free_id, true, true)):
		_fail("persist free failed")
	if bool(_SM.set_edition(paid_id, true, false)):
		_fail("edition change without consent should fail")
	if not bool(_SM.set_edition(paid_id, true, true)):
		_fail("edition change with consent failed")
	if str(_SM.get_edition()) != paid_id:
		_fail("paid edition not active after consent change")


func _test_no_secrets() -> void:
	var section: String = str(_SM.SECTION_AGM)
	_SM.set_value(section, "api_key", "sk-forged-must-reject", false)
	if _SM.get_value(section, "api_key", null) != null:
		_fail("api_key was stored via set_value")
	_SM.set_value(section, "client_secret", "shh", false)
	if _SM.get_value(section, "client_secret", null) != null:
		_fail("client_secret was stored via set_value")
	if not bool(_SM.has_no_client_secrets()):
		_fail("has_no_client_secrets returned false")


func _test_export_meta() -> void:
	var paid_id: String = str(_C.EDITION_API_PAID)
	var export_meta: Dictionary = _SM.get_edition_export()
	if str(export_meta.get("edition", "")) != paid_id:
		_fail("export edition mismatch")
	if export_meta.get("stores_api_key", true) != false:
		_fail("export claims stores_api_key")
	if export_meta.get("stores_client_secret", true) != false:
		_fail("export claims stores_client_secret")
	if str(export_meta.get("contract_semantics", "")) != "identical":
		_fail("export contract_semantics not identical")
	for eid in ["desktop_bridge_free", "api_paid"]:
		if not bool(_SM.is_valid_edition(eid)):
			_fail("contract edition missing: %s" % eid)


func _finish() -> void:
	if _failures.is_empty():
		print("G2-007_GODOT_SMOKE=PASS")
		print(
			"edition=%s same_contracts=%s no_secrets=%s"
			% [
				_SM.get_edition(),
				_SM.uses_same_agm_contracts(),
				_SM.has_no_client_secrets(),
			]
		)
		quit(0)
	else:
		print("G2-007_GODOT_SMOKE=FAIL")
		for f in _failures:
			print(" - ", f)
		quit(1)
