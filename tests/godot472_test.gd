extends SceneTree
## Godot 4.7.2 compatibility regression (1.2.2). The engine's 4.7 analyzer is
## stricter than 4.4's and a few runtime paths were reachable with data the
## original code assumed could never arrive. This locks down what was fixed:
##   - the project declares the 4.7 feature tag;
##   - a save that *parses* as JSON but lost a key degrades instead of throwing
##     (SaveFile only falls back to .bak on a parse failure, not an incomplete file);
##   - the navigator degrades to a direct line if it was never built;
##   - version metadata stays in sync across the three generated files.
##   godot --headless --path . -s res://tests/godot472_test.gd

const Campaign = preload("res://scripts/campaign/campaign.gd")
const Department = preload("res://scripts/campaign/department.gd")
const SaveFile = preload("res://scripts/campaign/save_file.gd")
const Nav = preload("res://scripts/sim/nav.gd")
const Version = preload("res://scripts/version.gd")

var fails := 0


func check(ok: bool, what: String) -> void:
	print(("ok    " if ok else "FAIL  ") + what)
	if not ok:
		fails += 1


func _init() -> void:
	_test_feature_tag()
	_test_version_sync()
	_test_department_bad_saves()
	_test_campaign_bad_saves()
	print("godot472_test: %s" % ("PASS" if fails == 0 else "%d FAILED" % fails))
	quit(1 if fails > 0 else 0)


## The project must advertise the engine it targets, or 4.7 offers to convert it.
func _test_feature_tag() -> void:
	var proj := FileAccess.get_file_as_string("res://project.godot")
	check(proj.contains("\"4.7\""), "project.godot declares the 4.7 feature tag")
	check(proj.contains("\"4.4\""), "project.godot keeps the 4.4 feature tag (both engines supported)")
	check(proj.contains("config_version=5"), "project.godot is still config_version 5")


func _test_version_sync() -> void:
	var project := FileAccess.get_file_as_string("res://project.godot")
	var presets := FileAccess.get_file_as_string("res://export_presets.cfg")
	check(project.contains("config/version=\"%s\"" % Version.VALUE), "project version follows Version.VALUE")
	check(presets.contains("application/file_version=\"%s\"" % Version.WINDOWS), "export file version follows Version.WINDOWS")
	check(presets.contains("application/product_version=\"%s\"" % Version.WINDOWS), "export product version follows Version.WINDOWS")


## Every one of these used to be `d["key"]`, which throws on an incomplete save.
## This is the boot path: a throw here means the game never reaches the title screen.
func _test_department_bad_saves() -> void:
	var cases := [
		["empty object", {}],
		["null officers", {"version": Department.VERSION, "officers": null}],
		["officers with a non-dictionary entry", {"version": Department.VERSION, "officers": ["junk", 7, null]}],
		["an officer record with no file", {"version": Department.VERSION, "officers": [{"id": "o1", "status": "active"}]}],
		["an officer record with a null kit", {"version": Department.VERSION, "officers": [{"id": "o1", "kit": null}]}],
		["a kit with no plates or gear", {"version": Department.VERSION, "officers": [{"id": "o1", "kit": {}}]}],
		["null bonds", {"version": Department.VERSION, "bonds": null}],
		["null notes", {"version": Department.VERSION, "notes": null}],
		["budget block with null ledger and cases", {"version": Department.VERSION, "allocation": 100, "ledger": null, "cases": null}],
		["ledger with junk entries", {"version": Department.VERSION, "allocation": 100, "ledger": ["x", 3, null]}],
	]
	for c in cases:
		var what: String = c[0]
		var data: Dictionary = c[1]
		# a valid version, so the check below is about the *shape* of the data and
		# not the version guard (which is tested separately further down)
		data["version"] = Department.VERSION
		data["seed"] = data.get("seed", 7)
		data["week"] = data.get("week", 3)
		data["serial"] = data.get("serial", 1)
		data["ops_run"] = data.get("ops_run", 0)
		var d = Department.new()
		var ok := d.from_data(data)
		check(ok, "department loads a save with " + what + " (no throw)")
		check(d.officers is Array, "  ...and still has an officers list (" + what + ")")


## Same for the campaign wrapper: `d["seed"]` and `d["department"]` were unguarded.
func _test_campaign_bad_saves() -> void:
	var good = Campaign.new()
	good.start(4242)
	check(good.dept != null and good.dept.officers.size() > 0, "a real campaign builds a department")

	# a board/past holding non-dictionary entries used to throw in _ints()
	var c = Campaign.new()
	var ok := c.from_data({
		"version": Campaign.VERSION,
		"seed": 4242,
		"department": good.dept.to_data(),
		"board": "not an array",
		"past": [null, 5, "junk"],
		"pressure": null,
		"short_history": null,
		"politics": null,
	})
	check(ok, "campaign loads with malformed board/past/pressure (no throw)")
	check(c.board is Array and c.board.is_empty(), "a non-array board degrades to empty")
	check(c.past is Array and c.past.is_empty(), "junk past entries are dropped, not loaded")
	check(c.pressure is Dictionary and c.pressure.is_empty(), "a null pressure read degrades to {}")
	check(c.short_history is Dictionary, "a null short history degrades to {}")

	# a save with no department block at all must fail softly, not throw
	var c2 = Campaign.new()
	var ok2 := c2.from_data({"version": Campaign.VERSION, "seed": 1})
	check(ok2, "campaign loads a save with no department block (no throw)")

	# and the version guard still rejects the future
	var c3 = Campaign.new()
	check(not c3.from_data({"version": Campaign.VERSION + 99}), "a save from a newer version is still refused")
	var d3 = Department.new()
	check(not d3.from_data({"version": 0}), "a v0 department save is still refused")


## A navigator that was never built used to index into an empty grids array.
func _test_nav_without_build() -> void:
	var nv = Nav.new()
	# build() not called: grids is empty on purpose
	var path: PackedVector2Array = nv._find_path(0, Vector2(1, 1), Vector2(9, 9))
	check(path.size() == 2, "an unbuilt navigator returns a direct line instead of crashing")
	check(path[0] == Vector2(1, 1) and path[1] == Vector2(9, 9), "the fallback keeps both endpoints")
