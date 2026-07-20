## TEST_ONLY journal HMAC key provider for G4 smoke / unit tests.
## Never use as a shipping/production default. provider_id contains TEST marker.
class_name TestJournalKeyProvider
extends RefCounted

## Must contain "test" / "TEST" marker for smoke evidence.
const PROVIDER_ID := "TEST_ONLY_G4"
const TEST_KEY_LABEL := "AIDLE_G4_JOURNAL_HMAC_TEST_KEY_V1"

## Alternate label for wrong-key fail-closed tests.
const WRONG_KEY_LABEL := "AIDLE_G4_JOURNAL_HMAC_WRONG_KEY_V1"
const WRONG_PROVIDER_ID := "TEST_ONLY_G4_WRONG"

var _provider_id: String = PROVIDER_ID
var _key_label: String = TEST_KEY_LABEL


func _init(use_wrong_key: bool = false) -> void:
	if use_wrong_key:
		_provider_id = WRONG_PROVIDER_ID
		_key_label = WRONG_KEY_LABEL
	else:
		_provider_id = PROVIDER_ID
		_key_label = TEST_KEY_LABEL


func get_provider_id() -> String:
	return _provider_id


## R0 name.
func get_journal_hmac_key() -> PackedByteArray:
	return _derive_key(_key_label)


## Alias accepted by PersistModule / journal_store injection.
func get_hmac_key() -> PackedByteArray:
	return get_journal_hmac_key()


static func _derive_key(label: String) -> PackedByteArray:
	# 32-byte key = SHA-256(UTF-8 label). Deterministic, test-only, never logged as secret.
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(label.to_utf8_buffer())
	return ctx.finish()


static func make_test() -> RefCounted:
	return new(false)


static func make_wrong() -> RefCounted:
	return new(true)
