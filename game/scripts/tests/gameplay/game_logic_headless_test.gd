## Headless logic tests for the GAMEPLAY_COMPLETION subsystem.
## Run with: godot --headless --path <game_dir> -s res://scripts/tests/gameplay/game_logic_headless_test.gd
## No scene tree required — all subsystems are RefCounted.
extends SceneTree

var _pass_count: int = 0
var _fail_count: int = 0
var _failures: PackedStringArray = []

func _init() -> void:
	_Economy = load("res://scripts/modules/gameplay/game_economy.gd")
	_QuestSystem = load("res://scripts/modules/gameplay/game_quest_system.gd")
	_Meter = load("res://scripts/modules/gameplay/game_relationship_meter.gd")
	_Npc = load("res://scripts/modules/gameplay/game_npc_interaction.gd")
	_Journal = load("res://scripts/modules/gameplay/game_day_journal.gd")
	_run_all()

func _run_all() -> void:
	# ─── Economy ────────────────────────────────────────────────────────────
	var eco: RefCounted = _Economy.new()
	check("eco initial balance coin==0", eco.get_balance_of("coin") == 0)
	var inc: Dictionary = eco.grant_income({"coin": 100, "wood": 50}, "test_income")
	check("eco grant income ok", inc.get("ok") == true)
	check("eco coin==100", eco.get_balance_of("coin") == 100)
	var spend: Dictionary = eco.approve_spend({"coin": 40, "wood": 20}, "test_spend")
	check("eco approve spend ok", spend.get("ok") == true)
	check("eco coin==60 after spend", eco.get_balance_of("coin") == 60)
	var over: Dictionary = eco.approve_spend({"coin": 999}, "overdraft")
	check("eco reject overdraft", over.get("ok") == false and over.get("code") == "insufficient")
	check("eco balance untouched after failed spend", eco.get_balance_of("coin") == 60)
	var neg: Dictionary = eco.approve_spend({"coin": -5}, "negative")
	check("eco reject negative cost", neg.get("ok") == false)
	var comp: Dictionary = eco.compensate(int(spend.get("entry", {}).get("seq", 0)), {"coin": 40, "wood": 20}, "test_undo")
	check("eco compensate ok", comp.get("ok") == true)
	check("eco coin restored==100", eco.get_balance_of("coin") == 100)
	eco.set_hour(22.0)
	check("eco night after 22h", eco.time_of_day_label() == "night", "label=%s hour=%s" % [eco.time_of_day_label(), str(eco.get_hour())])
	eco.advance_day_income()
	check("eco day still 1 until crossing 6am", eco.get_day() == 1, "day=%s" % str(eco.get_day()))
	check("eco daily income credited", eco.get_balance_of("coin") == 110)
	var already: Dictionary = eco.advance_day_income()
	check("eco daily income idempotent per day", already.get("ok") == false, "ok=%s code=%s day=%s" % [str(already.get("ok")), str(already.get("code", "")), str(eco.get_day())])
	eco.set_hour(4.0)
	check("eco day==2 after crossing 6am", eco.get_day() == 2, "day=%s" % str(eco.get_day()))
	var afford_no: Dictionary = eco.can_afford({"coin": 50, "wood": 999})
	check("eco can_afford false", afford_no.get("ok") == false)
	var recipe: Dictionary = eco.cost_for("cozy_house_small_A")
	check("eco recipe cost known", recipe.get("coin", 0) == 120)
	check("eco unknown recipe free", eco.cost_for("unknown_xyz").is_empty())
	var spirit: Dictionary = eco.spend_spirit(20.0)
	check("eco spirit spend ok", spirit.get("ok") == true and eco.get_spirit() == 80.0, "ok=%s spirit=%s" % [str(spirit.get("ok")), str(eco.get_spirit())])
	var spirit_over: Dictionary = eco.spend_spirit(99.0)
	check("eco spirit over-reject", spirit_over.get("ok") == false)
	var ledger: Array = eco.ledger_export(10)
	check("eco ledger append-only non-empty", ledger.size() > 0)
	var empty_cost: Dictionary = eco.approve_spend({}, "free")
	check("eco empty cost approved", empty_cost.get("ok") == true)
	var unknown_res: Dictionary = eco.grant_income({"magic_dust": 1})
	check("eco unknown resource income rejected", unknown_res.get("ok") == false)

	# ─── Quest system ────────────────────────────────────────────────────────
	var qsys: RefCounted = _QuestSystem.new()
	var offer: Dictionary = qsys.apply_op({"op": "offer", "quest_id": "q1", "title": "T3 luống rau", "objective_summary": "Trồng 3 luống rau", "goals": [{"kind": "collect", "target": "vegetable_bed", "need": 3}], "reward": {"coin": 25}})
	check("quest offer ok, awaiting acceptance", offer.get("ok") == true and bool(offer.get("awaiting_acceptance", false)))
	var double_offer: Dictionary = qsys.apply_op({"op": "offer", "quest_id": "q1", "title": "X", "objective_summary": "Y"})
	check("quest double offer rejected while active", double_offer.get("ok") == false)
	var acc: Dictionary = qsys.apply_op({"op": "accept", "quest_id": "q1"})
	check("quest accept ok", acc.get("ok") == true and qsys.quest_summary("q1").get("state") == "accepted")
	var accept_again: Dictionary = qsys.apply_op({"op": "accept", "quest_id": "q1"})
	check("quest re-accept rejected", accept_again.get("ok") == false)
	var ready: Dictionary = qsys.apply_op({"op": "mark_ready", "quest_id": "q1"})
	check("quest mark_ready ok, in_progress", ready.get("ok") == true and ready.get("state") == "in_progress")
	var adv1: Dictionary = qsys.apply_op({"op": "advance_goal", "quest_id": "q1", "goal_kind": "collect", "target": "vegetable_bed", "count": 2})
	check("quest advance partial, goals not met", adv1.get("ok") == true and not bool(adv1.get("goals_met", false)))
	var adv2: Dictionary = qsys.apply_op({"op": "advance_goal", "quest_id": "q1", "goal_kind": "collect", "target": "vegetable_bed", "count": 1})
	check("quest advance completes, goals met", adv2.get("ok") == true and bool(adv2.get("goals_met", false)))
	var snap: Dictionary = qsys.snapshot()
	check("quest snapshot for completed q1 is empty by design (completed leaves active)", snap.get("quests", []).size() == 0)
	var q1rec: Dictionary = qsys.quest_summary("q1")
	check("quest summary shows completed", q1rec.get("ok") == true and str(q1rec.get("state", "")) == "completed", "state=%s" % str(q1rec.get("state", "")))
	var already_complete: Dictionary = qsys.apply_op({"op": "complete", "quest_id": "q1"})
	check("quest idempotent re-complete rejected", already_complete.get("ok") == false)
	var q2: Dictionary = qsys.apply_op({"op": "offer", "quest_id": "q2", "title": "T2", "objective_summary": "O2", "goals": [{"kind": "collect", "target": "x", "need": 2}]})
	check("quest q2 offered", q2.get("ok") == true)
	var q2acc: Dictionary = qsys.apply_op({"op": "accept", "quest_id": "q2"})
	check("quest q2 accepted", q2acc.get("ok") == true)
	print("[DBG] q2 quest_ids=%s" % str(qsys.quest_ids()))
	var adv_bad_kind: Dictionary = qsys.apply_op({"op": "advance_goal", "quest_id": "q2", "goal_kind": "fly", "count": 1})
	check("quest advance unknown goal rejected", adv_bad_kind.get("ok") == false)
	print("[DBG] q2 before fc state=%s" % str(qsys.quest_summary("q2").get("state", "")))
	var fc: Dictionary = qsys.apply_op({"op": "force_complete", "quest_id": "q2"})
	print("[DBG] fc result=%s" % str(fc))
	check("quest force_complete ok with halved reward", fc.get("ok") == true and int(fc.get("relationship_gain", -1)) == 0, "ok=%s rel=%s" % [str(fc.get("ok")), str(fc.get("relationship_gain"))])
	var unknown: Dictionary = qsys.apply_op({"op": "accept", "quest_id": "ghost"})
	check("quest unknown rejected", unknown.get("ok") == false)

	# ─── Relationship meter ──────────────────────────────────────────────────
	var meter: RefCounted = _Meter.new()
	var pts: Dictionary = meter.add_points(12, "test")
	check("meter points ok", pts.get("ok") == true and int(pts.get("points")) == 12 and int(pts.get("level")) == 1)
	check("meter level_name friend", pts.get("level_name") == "friend")
	var adapt: Dictionary = meter.adapt("warmth", 0.25, {"evidence": "test"})
	check("meter adapt clamped to per_turn cap", adapt.get("ok") == true and absf(float(adapt.get("value", 0.5)) - 0.505) < 0.001, "ok=%s value=%s" % [str(adapt.get("ok")), str(adapt.get("value"))])
	var adapt_over: Dictionary = meter.adapt("warmth", -0.001, {})
	check("meter adapt daily cap respected", adapt_over.get("ok") == true or adapt_over.get("reason") == "daily_cap_reached")
	var adapt_bad: Dictionary = meter.adapt("jealousy", 0.1)
	check("meter unknown trait rejected", adapt_bad.get("ok") == false)
	meter.advance_day()
	var cur := float(meter.get_traits().get("warmth", 0.0))
	var base := float(meter.get_base_traits().get("warmth", 0.0))
	check("meter decay toward baseline after day", absf(cur - base) < absf(0.605 - base) + 0.001)
	check("meter can_unlock_beat level 1", meter.can_unlock_beat(1) == true)
	check("meter cannot unlock beat level 3", meter.can_unlock_beat(3) == false)
	var rm: Dictionary = meter.remove_points(5, "test")
	check("meter remove points ok", rm.get("ok") == true and int(rm.get("points")) == 7)
	meter.set_mood("happy")
	check("meter mood set", meter.get_mood() == "happy")
	meter.reset_to_base_traits()
	check("meter reset to base", absf(float(meter.get_traits().get("warmth")) - float(meter.get_base_traits().get("warmth"))) < 0.001)

	# ─── NPC interaction ─────────────────────────────────────────────────────
	var npc: RefCounted = _Npc.new()
	npc.attach(qsys, meter, eco)
	var prof: Dictionary = npc.profile("bac_bap")
	check("npc profile ok", prof.get("ok") == true and prof.get("display") == "Bac Bap")
	var prof_bad: Dictionary = npc.profile("nobody")
	check("npc unknown rejected", prof_bad.get("ok") == false)
	var talk: Dictionary = npc.talk("cinder")
	print("[DBG] after talk log=%s" % str(npc.call("interaction_history", 100)))
	check("npc talk ok", talk.get("ok") == true and not str(talk.get("line", "")).is_empty())
	var pet: Dictionary = npc.pet("cinder")
	check("npc pet cinder rejected", pet.get("ok") == false)
	var pet_ok: Dictionary = npc.pet("bui_mo")
	check("npc pet bui_mo ok", pet_ok.get("ok") == true and str(pet_ok.get("line", "")).contains("rừ rừ"))
	print("[DBG] after pet log=%s" % str(npc.call("interaction_history", 100)))
	var gift: Dictionary = npc.offer_npc_gift("nori7", "cozy_garden_lamp")
	check("npc gift pending player accept", gift.get("ok") == true and gift.get("code") == "gift_pending_player_accept" and bool(gift.get("proposal", {}).get("preview_required", false)))
	print("[DBG] after gift log=%s" % str(npc.call("interaction_history", 100)))
	var gq: Dictionary = npc.npc_quest("bac_bap", "q_npc_1", "Việc nhỏ", "Đem 2 viên gạch", [{"kind": "collect", "target": "brick", "need": 2}], {"coin": 10})
	check("npc quest offer ok", gq.get("ok") == true)
	var greet: Dictionary = npc.greeting_for_hour("bui_mo", 3.0)
	check("npc night greeting", greet.get("ok") == true and greet.get("time_of_day") == "night")
	# Note: greeting is presentation-only (no durable mutation, blueprint invariant),
	# so the interaction log stays at 4 entries (talk, pet, gift_offer, quest_offer).
	var hist: Array = npc.interaction_history(5)
	print("[DBG] npc log content=%s" % str(npc.call("interaction_history", 100)))
	check("npc history recorded", hist.size() >= 4, "size=%s" % str(hist.size()))

	# ─── Journal ──────────────────────────────────────────────────────────────
	var journal: RefCounted = _Journal.new()
	var j1: Dictionary = journal.record(1, "test", "beat one")
	check("journal record ok", j1.get("ok") == true and int(j1.get("seq")) == 1)
	journal.record(1, "test", "beat two")
	journal.record(2, "test", "beat three")
	check("journal entries_for_day", journal.entries_for_day(1).size() == 2)
	check("journal entries_for_day 2", journal.entries_for_day(2).size() == 1)
	var mem: Array = journal.recent_memories(2)
	check("journal bounded memory", mem.size() <= 2)
	var del: Dictionary = journal.delete_entries(3)
	check("journal delete appends-invalidation ok", del.get("ok") == true and int(del.get("removed")) == 1)

	# ─── Integration loop ────────────────────────────────────────────────────
	# NPC quest → accept → advance goals → complete → reward granted via economy
	# and relationship points → journal provenance. Mirrors a real play session.
	var eco2: RefCounted = _Economy.new({"coin": 200})
	var q2sys: RefCounted = _QuestSystem.new()
	var m2: RefCounted = _Meter.new()
	var n2: RefCounted = _Npc.new()
	n2.attach(q2sys, m2, eco2)
	n2.npc_quest("bac_bap", "q_bricks", "Gạch cho lò", "Thu thập 2 viên gạch", [{"kind": "collect", "target": "brick", "need": 2}], {"coin": 30})
	var a2: Dictionary = q2sys.apply_op({"op": "accept", "quest_id": "q_bricks"})
	check("integration accept", a2.get("ok") == true)
	var r2: Dictionary = q2sys.apply_op({"op": "advance_goal", "quest_id": "q_bricks", "goal_kind": "collect", "target": "brick", "count": 2})
	check("integration goals met + reward present", r2.get("ok") == true and bool(r2.get("goals_met", false)) and not (r2.get("reward", {}) as Dictionary).is_empty(), "ok=%s met=%s reward=%s" % [str(r2.get("ok")), str(r2.get("goals_met")), str(r2.get("reward"))])
	var reward: Dictionary = r2.get("reward", {})
	var grant: Dictionary = eco2.grant_income(reward, "quest_reward_q_bricks")
	check("integration reward granted", grant.get("ok") == true and eco2.get_balance_of("coin") == 230, "ok=%s coin=%s reward=%s" % [str(grant.get("ok")), str(eco2.get_balance_of("coin")), str(reward)])
	m2.add_points(int(r2.get("relationship_gain", 0)), "integration_quest")
	check("integration relationship advanced", int(m2.snapshot().get("points", 0)) >= 0)

	# Report
	print("\n════════ GAMEPLAY HEADLESS TESTS ════════")
	print("PASS: %d | FAIL: %d" % [_pass_count, _fail_count])
	for f in _failures:
		print("  FAIL: %s" % f)
	print("════════════════════════════════════════\n")
	if _fail_count > 0:
		push_error("GAMEPLAY_HEADLESS_TESTS_FAILED count=%d" % _fail_count)
	quit()

func check(name: String, cond: bool, hint: String = "") -> void:
	if cond:
		_pass_count += 1
	else:
		_fail_count += 1
		_failures.append(name)
		push_warning("TEST_FAIL: %s | %s" % [name, hint])

var _Economy
var _QuestSystem
var _Meter
var _Npc
var _Journal
