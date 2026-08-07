## Day / night & weather cycle — implements the blueprint Event Bus allowlist
## (`ambient.weather_hint`, `ambient.time_of_day_hint`, `pacing.slow_down`,
## `pacing.speed_up`) and feeds the economy ledger's clock.
##
## A real Godot Node (mount under Main so it receives _process/_physics_process
## ticks). In headless runs the clock can also be driven manually via
## advance_by_hours() — all game logic is decoupled from frame ticks.
##
## Visual mood is presentation data only (blueprint: visual duration is
## presentation data); the canonical clock state lives here.
class_name GameDayNightWeather
extends Node

signal time_of_day_changed(hour: float, label: String, light_intensity: float)
signal weather_changed(weather: String, intensity: float)
signal day_advanced(day: int)

const WEATHER_TYPES := ["clear", "partly_cloudy", "cloudy", "rain", "storm", "mist"]
const DAY_SECONDS := 600.0  # 10 real minutes = 1 in-game day (tunable per session)

enum WeatherMood { CALM, COZY, MELANCHOLY, FESTIVE }

var _day: int = 1
var _seconds_into_day: float = 0.0
var _weather: String = "clear"
var _weather_intensity: float = 0.0
var _paused: bool = false
var _weather_hold: float = 0.0
var _rng := RandomNumberGenerator.new()

func _ready() -> void:
	_rng.randomize()
	name = "GameDayNightWeather"
	_weather_hold = _next_weather_change_in()

func _process(delta: float) -> void:
	if _paused:
		return
	_seconds_into_day += float(delta)
	if _seconds_into_day >= DAY_SECONDS:
		_seconds_into_day -= DAY_SECONDS
		_day += 1
		day_advanced.emit(_day)
	_evaluate_weather(delta)
	_publish_time_of_day()

## Manual drive (headless tests / AGM pacing decisions).
func advance_by_hours(hours: float) -> void:
	_seconds_into_day += float(hours) / 24.0 * DAY_SECONDS
	while _seconds_into_day >= DAY_SECONDS:
		_seconds_into_day -= DAY_SECONDS
		_day += 1
		day_advanced.emit(_day)
	_evaluate_weather(0.0)
	_publish_time_of_day()

func get_hour() -> float:
	return _seconds_into_day / DAY_SECONDS * 24.0

func get_day() -> int:
	return _day

func time_of_day_label() -> String:
	var h := get_hour()
	if h >= 6.0 and h < 12.0:
		return "morning"
	if h >= 12.0 and h < 17.0:
		return "afternoon"
	if h >= 17.0 and h < 20.0:
		return "evening"
	return "night"

func get_weather() -> String:
	return _weather

## Presentation helper: ambient light intensity 0..1 by hour + weather.
func ambient_light_intensity() -> float:
	var h := get_hour()
	var base := 1.0
	if h < 5.0:
		base = 0.18
	elif h < 7.0:
		base = 0.18 + (h - 5.0) / 2.0 * 0.52
	elif h >= 19.0 and h < 21.0:
		base = 0.7 - (h - 19.0) / 2.0 * 0.52
	elif h >= 21.0:
		base = 0.18
	var weather_dim := {
		"partly_cloudy": 0.92, "cloudy": 0.78, "rain": 0.62, "storm": 0.5, "mist": 0.85,
	}
	base *= float(weather_dim.get(_weather, 1.0))
	return clampf(base, 0.15, 1.0)

func set_weather(weather: String, intensity: float = 0.0) -> Dictionary:
	if weather not in WEATHER_TYPES:
		return {"ok": false, "reason": "unknown_weather"}
	_weather = weather
	_weather_intensity = clampf(float(intensity), 0.0, 1.0)
	weather_changed.emit(_weather, _weather_intensity)
	return {"ok": true, "weather": _weather, "intensity": _weather_intensity}

func set_paused(paused: bool) -> void:
	_paused = bool(paused)

func _evaluate_weather(_delta: float) -> void:
	_weather_hold -= _delta
	if _weather_hold > 0.0:
		return
	_weather_hold = _next_weather_change_in()
	# weighted random weather: mostly calm, occasional cozy rain.
	var roll := _rng.randf()
	var next_weather := "clear"
	if roll < 0.30:
		next_weather = "clear"
	elif roll < 0.55:
		next_weather = "partly_cloudy"
	elif roll < 0.75:
		next_weather = "cloudy"
	elif roll < 0.92:
		next_weather = "rain"
	else:
		next_weather = "mist"
	if next_weather != _weather:
		set_weather(next_weather, _rng.randf_range(0.3, 0.9))

func _next_weather_change_in() -> float:
	# weather holds 40–120 in-game seconds
	return _rng.randf_range(40.0, 120.0)

func _publish_time_of_day() -> void:
	var h := get_hour()
	var label := time_of_day_label()
	time_of_day_changed.emit(h, label, ambient_light_intensity())

func snapshot() -> Dictionary:
	return {
		"day": _day,
		"hour": get_hour(),
		"time_of_day": time_of_day_label(),
		"weather": _weather,
		"weather_intensity": _weather_intensity,
		"ambient_light": ambient_light_intensity(),
	}
