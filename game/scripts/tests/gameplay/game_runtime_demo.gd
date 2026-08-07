## Runtime gameplay demo — chạy trong scene tree thật của game.
## Hook vào signal của GamePlaySession và WorldAuthority sau khi scene sẵn sàng,
## thực hiện vòng loop gameplay đầy đủ và in kết quả snapshot.
extends SceneTree

var _step: int = 0
var _main_node: Node = null
var _session: Node = null

func _init() -> void:
	var t := create_timer(1.0)
	t.timeout.connect(_on_frame)

func _reschedule() -> void:
	var t := create_timer(0.3)
	t.timeout.connect(_on_frame)

func _on_frame() -> void:
	if _main_node == null:
		_main_node = root.get_node_or_null("Main")
		if _main_node == null:
			return
		_session = _main_node.get_node_or_null("GamePlaySession")
		if _session == null:
			print("[DEMO] ERROR: GamePlaySession not mounted")
			quit()
			return
		_step = 1
	# Run steps sequentially.
	if _step == 1:
		_step = 2
		var snap: Dictionary = _session.call("snapshot")
		print("[DEMO STEP 1] Initial snapshot:")
		print("[DEMO]   economy=%s" % str(snap.get("economy", {}).get("balance", {})))
		print("[DEMO]   quests=%s" % str(snap.get("quests", {}).get("quests", [])))
		print("[DEMO]   relationship=%s" % str(snap.get("relationship", {}).get("level_name", "")))
	if _step == 2:
		_step = 3
		var acc: Dictionary = _session.call("accept_quest", "q_starter_garden")
		print("[DEMO STEP 2] accept quest: %s" % str(acc.get("state", acc.get("reason", ""))))
	if _step == 3:
		_step = 4
		var adv: Dictionary = _session.call("advance_goal", "q_starter_garden", "collect", "vegetable_bed", 1)
		print("[DEMO STEP 3] advance 1/3: ok=%s goals_met=%s" % [str(adv.get("ok", false)), str(adv.get("goals_met", false))])
	if _step == 4:
		_step = 5
		var adv2: Dictionary = _session.call("advance_goal", "q_starter_garden", "collect", "vegetable_bed", 1)
		var adv3: Dictionary = _session.call("advance_goal", "q_starter_garden", "collect", "vegetable_bed", 1)
		print("[DEMO STEP 4] advance 2/3 & 3/3: ok=%s goals_met=%s (reward granted → see next snapshot)" % [str(adv3.get("ok", false)), str(adv3.get("goals_met", false))])
	if _step == 5:
		_step = 6
		var talk: Dictionary = _session.call("talk_npc", "bac_bap")
		print("[DEMO STEP 5] talk Bac Bap: %s" % str(talk.get("line", talk.get("reason", ""))))
		var pet: Dictionary = _session.call("pet_npc")
		print("[DEMO STEP 5b] pet Bui Mo: %s" % str(pet.get("line", pet.get("reason", ""))))
		var gift: Dictionary = _session.call("npc_gift", "nori7", "cozy_garden_lamp")
		print("[DEMO STEP 5c] Nori gift proposal code=%s preview_required=%s" % [str(gift.get("code", "")), str(gift.get("proposal", {}).get("preview_required", false))])
		var pay: Dictionary = _session.call("pay_for_build", "cozy_house_small_A")
		print("[DEMO STEP 5d] pay_for_build cozy_house_small_A: %s" % str(pay.get("code", pay.get("reason", ""))))
	if _step == 6:
		_step = 7
		var after: Dictionary = _session.call("snapshot")
		print("[DEMO STEP 6] After loop snapshot:")
		print("[DEMO]   economy=%s" % str(after.get("economy", {}).get("balance", {})))
		var qs: Array = after.get("quests", {}).get("quests", [])
		for q in qs:
			print("[DEMO]   active quest: %s [%s] progress=%s" % [str(q.get("quest_id", "")), str(q.get("state", "")), str(q.get("progress", {}))])
		var mems: Array = after.get("journal_recent", [])
		for m in mems:
			print("[DEMO]   journal: %s — %s" % [str(m.get("kind", "")), str(m.get("text", ""))])
		print("[DEMO] DONE — gameplay loop chạy đầy đủ trong game thật.")
		quit()
		return
	_reschedule()
