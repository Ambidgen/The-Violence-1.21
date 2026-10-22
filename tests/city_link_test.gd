extends SceneTree
## The endless-battle link (playtest pass Q7): the city scene's per-precinct
## tallies (Director.pressure_data) become campaign weights
## (Campaign.pressure_from_city) and lean on the operations board — gang
## houses where crews hold ground, work where the precinct has been loud,
## less where police pressure is landing. The director side wants a whole
## city (tests/city_sim.gd --min=10 exercises it); this gates everything
## downstream of the file, and above all the iron rule: with no city read,
## the board is the unlinked board, roll for roll.
##   godot --headless --path . -s res://tests/city_link_test.gd

const Campaign = preload("res://scripts/campaign/campaign.gd")
const Situations = preload("res://scripts/campaign/situations.gd")

var fails := 0


func _check(ok: bool, what: String) -> void:
	if not ok:
		fails += 1
	print(("  ok   " if ok else "  FAIL ") + what)


func _city(over: Dictionary) -> Dictionary:
	var ps: Array = []
	for i in 6:
		ps.append({"incidents": 2, "reports": 3, "captures": 1, "deaths": 0, "gang": 0.05})
	for k in over:
		for f in over[k]:
			ps[int(k)][f] = over[k][f]
	return {"version": 1, "minutes": 37.5, "precincts": ps}


func _init() -> void:
	print("-- city link test (Q7)")

	# raw counts become weights, normalised by the loudest precinct
	var data := _city({"3": {"incidents": 40, "reports": 60, "deaths": 9, "gang": 0.8, "captures": 2},
		"0": {"captures": 12}})
	var pr: Dictionary = Campaign.pressure_from_city(data)
	var w: Array = pr.get("wards", [])
	_check(w.size() == 6, "six precincts in, six wards out")
	_check(is_equal_approx(float(w[3]["gang"]), 1.0) and float(w[3]["hot"]) > 0.95,
		"the Ironworks of this city is gang-held (%.2f) and loud (%.2f)" % [float(w[3]["gang"]), float(w[3]["hot"])])
	_check(is_equal_approx(float(w[0]["quiet"]), 1.0) and float(w[0]["hot"]) < 0.2,
		"Northgate is where pressure is working (quiet %.2f, hot %.2f)" % [float(w[0]["quiet"]), float(w[0]["hot"])])
	_check(is_equal_approx(float(pr["minutes"]), 37.5), "the watched minutes ride along for the summary")
	_check(Campaign.pressure_from_city({}).is_empty() and Campaign.pressure_from_city({"version": 2, "precincts": []}).is_empty(),
		"nonsense in, no reading out")

	# the iron rule: empty pressure, identical board
	for seed_v in [1, 42, 1001]:
		for wk in [1, 7, 33]:
			var a: Array = Situations.board(seed_v, wk)
			var b: Array = Situations.board(seed_v, wk, [], true, {})
			var same := a.size() == b.size()
			for i in mini(a.size(), b.size()):
				same = same and a[i]["type"] == b[i]["type"] and int(a[i]["ward_i"]) == int(b[i]["ward_i"]) \
					and int(a[i]["map"]) == int(b[i]["map"]) and int(a[i]["visibility"]) == int(b[i]["visibility"]) \
					and int(a[i]["seed"]) == int(b[i]["seed"])
			_check(same, "seed %d week %d: no reading, same board (%d situations)" % [seed_v, wk, a.size()])

	# placement: gang houses gather where the crews hold ground
	var base3 := 0
	var link3 := 0
	for s in 300:
		if int(Situations.make("gang", 5000 + s)["ward_i"]) == 3:
			base3 += 1
		if int(Situations.make("gang", 5000 + s, 1, 0, [], true, pr)["ward_i"]) == 3:
			link3 += 1
	_check(link3 > base3 + 25, "of 300 gang houses, Ironworks takes %d unlinked and %d linked" % [base3, link3])

	# frequency: a gang-held, loud city fills the board with more gang work
	var g_base := 0
	var g_link := 0
	var tot := 0
	for wk2 in 40:
		for s2 in Situations.board(99, wk2 + 1):
			tot += 1
			if s2["type"] == "gang":
				g_base += 1
		for s3 in Situations.board(99, wk2 + 1, [], true, pr):
			if s3["type"] == "gang":
				g_link += 1
	_check(g_link > g_base, "over 40 boards (%d situations): %d gang houses unlinked, %d linked" % [tot, g_base, g_link])

	# the file the city scene writes, read back whole
	var path := "user://city_pressure_test.json"
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify(data))
	f.close()
	var back: Dictionary = Campaign.load_city_pressure(path)
	_check(JSON.stringify(back) == JSON.stringify(pr), "the pressure file round-trips")
	_check(Campaign.load_city_pressure("user://no_such_city.json").is_empty(), "and no file is simply no reading")
	DirAccess.open("user://").remove("city_pressure_test.json")

	# saved with the campaign, and old saves load without one
	var c = Campaign.new()
	c.start(7)
	c.pressure = pr
	var saved: Dictionary = c.to_data()
	var c2 = Campaign.new()
	_check(c2.from_data(JSON.parse_string(JSON.stringify(saved))), "a version 3 campaign loads")
	_check(not (c2.pressure.get("wards", []) as Array).is_empty(), "with its city reading kept")
	saved.erase("pressure")
	saved["version"] = 2
	var c3 = Campaign.new()
	_check(c3.from_data(JSON.parse_string(JSON.stringify(saved))) and c3.pressure.is_empty(),
		"a version 2 campaign loads with no reading")
	_check(c2.pressure_summary().find("Ironworks") >= 0, "the summary names the loud ward: %s" % c2.pressure_summary())

	print("city link test: %s" % ("ALL OK" if fails == 0 else "%d FAILURES" % fails))
	quit(1 if fails > 0 else 0)
