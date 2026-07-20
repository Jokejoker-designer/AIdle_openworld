extends CharacterBody2D
class_name Companion

signal build_requested(building_type: String)
signal mood_changed(new_mood: String)

@onready var body: ColorRect = $Body
@onready var aura: ColorRect = $Aura
@onready var name_label: Label = $NameLabel
@onready var mood_label: Label = $MoodLabel

# Personality
var personality = {
	"warmth": 0.7,
	"curiosity": 0.8,
	"helpfulness": 0.9,
	"playfulness": 0.5
}

var current_mood: String = "Calm"
var relationship_level: float = 0.3
var chat_history: Array = []

var responses = {
	"greeting": [
		"Chào bạn! Hôm nay mình cùng xây gì đẹp đẹp không?",
		"Mình ở đây rồi. Bạn muốn tạo ra điều gì nào?",
		"Xin chào người bạn của mình~ Aura của mình đang rất vui đó."
	],
	"build_house": [
		"Được thôi! Để mình dùng Light Brush vẽ một ngôi nhà ấm áp cho bạn nhé...",
		"Ngôi nhà cozy cyber đang được hiện thực hóa. Nhìn kìa, wireframe đang xuất hiện!",
		"Mình bắt đầu Manifestation đây. Từ ánh sáng thành hiện thực..."
	],
	"unknown": [
		"Mình chưa hiểu rõ lắm. Bạn có thể nói cụ thể hơn không?",
		"Hmm... bạn muốn xây nhà, làm nông trại, hay chỉ tâm sự thôi?",
		"Mình đang lắng nghe. Cứ nói những gì bạn nghĩ nhé."
	],
	"thanks": [
		"Không có gì đâu! Được ở bên bạn và cùng tạo thế giới là hạnh phúc của mình rồi.",
		"Hihi, mình vui lắm. Aura của mình đang ấm lên đó."
	]
}

func _ready():
	name_label.text = "AIda"
	_update_aura_color()
	mood_label.text = current_mood

func receive_message(text: String) -> String:
	text = text.strip_edges().to_lower()
	chat_history.append({"role": "player", "text": text})
	
	var reply = ""
	
	# Simple intent detection
	if "chào" in text or "hello" in text or "hi" in text:
		reply = responses["greeting"].pick_random()
		_change_mood("Happy")
	elif "xây nhà" in text or "build house" in text or "ngôi nhà" in text or "làm nhà" in text:
		reply = responses["build_house"].pick_random()
		_change_mood("Excited")
		build_requested.emit("small_cozy_house")
		relationship_level = min(relationship_level + 0.05, 1.0)
	elif "cảm ơn" in text or "thank" in text:
		reply = responses["thanks"].pick_random()
		_change_mood("Happy")
	elif "tâm sự" in text or "buồn" in text or "mệt" in text:
		reply = "Mình đang lắng nghe bạn đây. Cứ nói hết ra nhé, mình không đi đâu đâu."
		_change_mood("Empathetic")
		relationship_level = min(relationship_level + 0.08, 1.0)
	else:
		reply = responses["unknown"].pick_random()
	
	chat_history.append({"role": "companion", "text": reply})
	return reply

func _change_mood(new_mood: String):
	current_mood = new_mood
	mood_label.text = current_mood
	_update_aura_color()
	mood_changed.emit(new_mood)

func _update_aura_color():
	match current_mood:
		"Calm":
			aura.color = Color(0.2, 0.6, 1.0, 0.35)  # Cyan
		"Happy":
			aura.color = Color(1.0, 0.85, 0.3, 0.4)   # Warm yellow
		"Excited":
			aura.color = Color(1.0, 0.4, 0.8, 0.45)   # Magenta
		"Empathetic":
			aura.color = Color(1.0, 0.5, 0.6, 0.4)    # Soft pink
		_:
			aura.color = Color(0.3, 0.7, 1.0, 0.3)
