extends SceneTree
## Roster UI smoke test: the weekly applicant pool is visible and hiring through its
## buttons updates the department and rebuilds the roster without stale callbacks.
##   godot --headless --path . -s res://tests/ops_ui_test.gd

const Campaign = preload("res://scripts/campaign/campaign.gd")
const OpsUI = preload("res://scripts/ui/ops_ui.gd")

var fails := 0


class FakeMain:
	var campaign
	var changes := 0

	func ops_dept_changed() -> void:
		changes += 1


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		fails += 1


func _buttons(n: Node, out: Array = []) -> Array:
	if n is Button:
		out.append(n)
	for child in n.get_children():
		_buttons(child, out)
	return out


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	Campaign.read_city_file = false
	var c = Campaign.new()
	c.start(99)
	var main = FakeMain.new()
	main.campaign = c
	var ui = OpsUI.new()
	root.add_child(ui)
	ui.build(main)
	ui._roster()
	await process_frame

	var pool: Array = c.dept.applicants_now()
	var hire: Array = _buttons(ui.box).filter(func(b): return String(b.text).begins_with("Hire  ($"))
	_check(pool.size() >= 2 and hire.size() == pool.size(), "one Hire button for each of the %d visible applicants" % pool.size())
	_check(_buttons(ui.box).all(func(b): return not String(b.text).begins_with("Hire a recruit") and not String(b.text).begins_with("Hire laterally")),
		"the removed blind-hire buttons stay removed")
	if not hire.is_empty():
		var before: int = c.dept.officers.size()
		var chosen: Dictionary = pool[0]
		hire[0].pressed.emit()
		await process_frame
		_check(c.dept.officers.size() == before + 1 and c.dept.officers.has(chosen), "clicking Hire adds the chosen applicant to the roster")
		_check(chosen["status"] in ["academy", "active"] and String(chosen["id"]).begins_with("PC-"), "the hire reports to the academy or duty with a department id")
		_check(c.dept.applicants_now().is_empty(), "the unchosen applicants walk after one hire")
		_check(main.changes == 1, "the UI propagates one department change")

	c.dept.next_week()
	ui._roster()
	await process_frame
	_check(not c.dept.applicants_now().is_empty(), "a fresh applicant pool appears the next week")
	ui.queue_free()
	await process_frame
	print("ops ui test: %s" % ("ALL OK" if fails == 0 else "%d FAILURES" % fails))
	quit(1 if fails > 0 else 0)
