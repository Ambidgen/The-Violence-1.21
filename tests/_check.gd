extends SceneTree
## Compile check: loads every script so parse errors surface.
##   godot --headless --path . -s res://tests/_check.gd
##
## Exits non-zero when a script fails to load (it used to print FAILED and exit 0, so
## the cheapest gate in the tree could not fail a build), names a directory it cannot
## open instead of skipping it silently, and scans `tests/` and `tools/` as well as
## `scripts/` — the tier is called "load every script". The directories are listed
## explicitly because DirAccess is not recursive.


func _init() -> void:
	var fails := 0
	var scanned := 0
	var dirs := ["res://scripts", "res://scripts/sim", "res://scripts/data", "res://scripts/maps",
		"res://scripts/view", "res://scripts/ui", "res://scripts/city", "res://scripts/campaign",
		"res://tools", "res://tests"]
	for d in dirs:
		var da := DirAccess.open(d)
		if da == null:
			print("FAILED  ", d, " does not open")
			fails += 1
			continue
		for f in da.get_files():
			if not f.ends_with(".gd"):
				continue
			scanned += 1
			var s = load(d + "/" + f)
			if s == null:
				print("FAILED ", d, "/", f)
				fails += 1
	print("check done: %d scripts, %d failed" % [scanned, fails])
	quit(1 if fails > 0 else 0)
