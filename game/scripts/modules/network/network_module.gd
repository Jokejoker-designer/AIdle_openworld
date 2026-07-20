## Network module surface for AIdle Openworld.
##
## G6-001 M2 LOCAL POC only under this tree:
##   - world_authority_local.gd — in-process World Commit simulator
##   - authority_client.gd — two-client adapter + local mirror
##   - g6_two_client_smoke.gd — headless two-client smoke
##
## This is NOT Nakama, NOT Colyseus, NOT a public multiplayer stack.
## No HTTP listen, no outbound internet, no secrets, no cloud credentials.
## Production Online Private Reality / Shared District authority remains
## architecture-lock server-owned; this module only hosts the local harness.
##
## INetworkModule (start_session / sync_manifestation_progress) is the product
## session interface; the G6 POC uses AuthorityClient against WorldAuthorityLocal.
class_name NetworkModule
extends RefCounted

const POC_CLASS := "LOCAL_IN_PROCESS_WORLD_AUTHORITY"
const POC_NOT := ["Nakama", "Colyseus", "public_bind", "cloud_credentials"]

const AuthorityClientScript = preload("res://scripts/modules/network/authority_client.gd")
const WorldAuthorityLocalScript = preload("res://scripts/modules/network/world_authority_local.gd")


## Factory for the local POC server (in-process only).
static func create_local_authority(space_id: String = "home_01", seed_revision: int = 0) -> RefCounted:
	return WorldAuthorityLocalScript.new(space_id, seed_revision)


## Factory for one logical client bound to a local authority instance.
static func create_authority_client(client_id: String, server: RefCounted) -> RefCounted:
	return AuthorityClientScript.new(client_id, server)


## Product interface stubs — not used by G6 two-client POC smoke.
func start_session(mode: String) -> void:
	# offline | listen | client — product path; G6 POC does not bind ports.
	pass


func sync_manifestation_progress(_prompt_id: String, _progress: float, _stage: String) -> void:
	pass


func sync_emotional_aura(_companion_id: String, _mood: String, _color: Color) -> void:
	pass
