extends SceneTree
## Deterministic city regressions: report clustering, guarded early EMS, and the
## static gate-route cache. Run headless; no city scene or renderer is required.

const CityLevel = preload("res://scripts/city/city_level.gd")
const CityNav = preload("res://scripts/city/city_nav.gd")
const Director = preload("res://scripts/city/director.gd")

var failures := 0


func check(ok: bool, message: String) -> void:
	if not ok:
		failures += 1
		print("FAIL: ", message)


func _init() -> void:
	var inc := {"p": Vector2.ZERO, "t": 10.0}
	check(Director.report_cluster_match(inc, Vector2(139, 0), 99.0), "reports inside 140 m / 90 s cluster")
	check(not Director.report_cluster_match(inc, Vector2(141, 0), 99.0), "reports beyond 140 m do not cluster")
	check(not Director.report_cluster_match(inc, Vector2(10, 0), 101.0), "reports beyond 90 s do not cluster")
	check(not Director.report_cluster_match(inc, Vector2(10, 0), 99.0, false), "different precincts never cluster")
	var medical := {"state": "assigned", "qrf": 0, "t": 0.0, "points": [Vector2.ZERO]}
	check(Director.early_medical_ready(medical, 20.0, []), "quiet assigned incident allows early EMS")
	check(not Director.early_medical_ready(medical, 19.9, []), "early EMS waits for incident age")
	check(not Director.early_medical_ready({"state": "assigned", "qrf": -1, "t": 0.0, "points": [Vector2.ZERO]}, 30.0, []), "early EMS needs a QRF")
	check(not Director.early_medical_ready(medical, 30.0, [{"p": Vector2.ZERO, "t": 20.0}]), "recent local gunfire holds EMS")
	check(Director.early_medical_ready(medical, 30.0, [{"p": Vector2.ZERO, "t": 10.0}]), "old local gunfire does not hold EMS")
	check(Director.early_medical_ready(medical, 30.0, [{"p": Vector2(121, 0), "t": 20.0}]), "distant gunfire does not hold local EMS")
	_test_routes()
	print("city improvements: ", "ALL OK" if failures == 0 else "%d failures" % failures)
	quit(0 if failures == 0 else 1)


func _test_routes() -> void:
	var lv := CityLevel.new(1001)
	lv.build()
	var nav := CityNav.new()
	nav.build(lv)
	var found := false
	for ai in mini(8, lv.lots.size()):
		for bi in range(ai + 1, mini(12, lv.lots.size())):
			var a: Vector2 = lv.lots[ai]["gate_out"]
			var b: Vector2 = lv.lots[bi]["gate_out"]
			nav.path_cache_hits = 0
			nav.path_cache_misses = 0
			var first := nav._street_path(a, b, ai, bi)
			if first.is_empty():
				continue
			var second := nav._street_path(a, b, ai, bi)
			check(first == second, "cached gate route is byte-for-byte identical")
			check(nav.path_cache_hits == 1 and nav.path_cache_misses == 1, "gate route cache hit/miss counters")
			found = true
			break
		if found:
			break
	check(found, "seeded city has a testable gate route")
