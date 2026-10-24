extends RefCounted
## The campaign (v0.7): forty weeks to the election. Each week the operations board
## fills with situations; the player sends officers to some of them, plans and runs
## each one, and ends the week. Officers sent to one situation, or out canvassing for
## tips, are not available for any other that week. Situations nobody was sent to are
## written down as unattended, and the city remembers them (v0.9).
##
## One ironman save slot: the campaign is saved after every operation and every week.

const Department = preload("res://scripts/campaign/department.gd")
const Situations = preload("res://scripts/campaign/situations.gd")
const Politics = preload("res://scripts/campaign/politics.gd")

const VERSION := 3        # 2: v0.9, the city's politics; 3: the endless-battle link (Q7)
const SAVE_PATH := "user://campaign.json"
const PRESSURE_PATH := "user://city_pressure.json"   # written by the city scene (Q7)
static var read_city_file := true   # the determinism fixture turns this off: a hashed board may not depend on whether someone watched the city on this machine
const WEEKS := 40

var seed_val := 1001
var dept
var board: Array = []          # this week's situations
var past: Array = []           # every situation of earlier weeks, with its outcome
var rng := RandomNumberGenerator.new()
var politics                   # v0.9: wards, allies, candidates, the press, the election
var pressure := {}             # Q7: {wards: [{gang, hot, quiet} x6]} from the endless battle; {} = no city read yet
# Presentation history is additive save data: it never enters simulation decisions.
var short_history := {}         # key -> week last played; each shipped short once per campaign
var short_last_week := -99
const SHORT_COOLDOWN_WEEKS := 3


func start(seed_v: int) -> void:
	seed_val = seed_v
	rng.seed = seed_v * 31 + 7
	dept = Department.new()
	dept.found(seed_v)
	politics = Politics.new()
	politics.start(seed_v)
	pressure = load_city_pressure()   # Q7: inherit the watched city, if there is one
	board = _new_board()
	dept.note("Week 1: %d situations on the board." % board.size())
	if not pressure.is_empty():
		dept.note("The board is drawn from the city as it stands: %s." % pressure_summary())


func week() -> int:
	return dept.week


func _new_board() -> Array:
	if politics != null and politics.ended:
		return []
	return Situations.board(seed_val, dept.week, politics.trust if politics != null else [],
		politics == null or not politics.lost("coalition"), pressure)


func over() -> bool:
	return politics != null and politics.ended


## Rare interstitials: one play per key per campaign, and no ordinary shorts in
## adjacent weeks. Election night may override the gap, but not the per-key limit.
func claim_short(key: String, force := false) -> bool:
	if short_history.has(key):
		return false
	if not force and week() - int(short_last_week) < SHORT_COOLDOWN_WEEKS:
		return false
	short_history[key] = week()
	short_last_week = week()
	return true


## An operation's consequences for the city (v0.9). Returns readable lines.
func after_operation(sid: String, result: Dictionary, w) -> Array:
	var s := get_sit(sid)
	if s.is_empty():
		return []
	return politics.on_operation(dept.week, s, result, w, dept)


## The account four weeks out (Q8): the department's books against the city's
## pending ledger (the lawsuits already filed).
func forecast(weeks_n := 4) -> Array:
	return dept.forecast(weeks_n, politics.pending if politics != null else [])


## Decide an internal affairs case: the department carries it out, the city watches.
func decide_case(c: Dictionary, decision: String) -> String:
	var ln: String = dept.decide(c, decision)
	if ln != "":
		for l2 in politics.on_decision(dept.week, c, decision, dept):
			ln += " " + l2
	return ln


func get_sit(sid: String) -> Dictionary:
	for s in board:
		if s["id"] == sid:
			return s
	return {}


## Officer ids already committed this week: planned into a situation, run in one, or
## out canvassing.
func committed(except_sid := "") -> Dictionary:
	var out := {}
	for s in board:
		if s["id"] == except_sid and s["status"] == "open":
			continue
		for oid in s.get("canvass", []):
			out[oid] = s["id"]
		for oid2 in plan_members(s):
			out[oid2] = s["id"]
	return out


static func plan_members(s: Dictionary) -> Array:
	var out: Array = []
	for sq in s.get("plan", {}).get("squads", []):
		for oid in sq.get("members", []):
			out.append(oid)
	return out


## Fit officers not committed to another situation this week.
func available_for(sid: String) -> Array:
	var busy := committed(sid)
	return dept.available().filter(func(r): return not busy.has(r["id"]) or busy[r["id"]] == sid)


## Send one officer to canvass the neighbourhood of a situation: two more tips, and the
## officer is gone for the week.
func canvass(sid: String, oid: String) -> Array:
	var s := get_sit(sid)
	if s.is_empty() or s["status"] != "open":
		return []
	var busy := committed()
	if busy.has(oid):
		return []
	s["canvass"].append(oid)
	var r: Dictionary = dept.get_officer(oid)
	var lines: Array = []
	for k in 2:
		lines.append(Situations.tip(s, rng, "canvass"))
	if not r.is_empty():
		r["file"].append({"week": dept.week, "text": "Canvassed for %s." % s["title"]})
	return lines


## An operation has been run: keep its plan and outcome on the situation.
func record(sid: String, result: Dictionary) -> void:
	var s := get_sit(sid)
	if s.is_empty():
		return
	s["status"] = "done"
	s["result"] = result


## The week ends: situations nobody went to are written down, wounds heal, and a new
## board fills. Returns readable lines.
func end_week() -> Array:
	var lines: Array = []
	for s in board:
		if s["status"] == "open":
			s["status"] = "unattended"
			lines.append("Unattended: %s." % s["title"])
			dept.note("Week %d: nobody went to %s." % [dept.week, s["title"]])
		past.append(_brief_record(s))
	if past.size() > 400:
		past = past.slice(past.size() - 400)
	# the city's week: what was left undone, what lands, the polls; at week 40 the election
	lines.append_array(politics.week_end(dept.week, board, dept))
	lines.append_array(dept.next_week())
	var triage := Department.triage_line(dept.cases, dept.week)
	if triage != "":
		lines.append(triage)
	# Q7: if the endless battle has been watched since, the new board knows it —
	# the city file is re-read; without one the campaign keeps its own reading
	var fresh := load_city_pressure()
	if not fresh.is_empty():
		pressure = fresh
	board = _new_board()
	if not over():
		dept.note("Week %d: %d situations on the board." % [dept.week, board.size()])
		if not pressure.is_empty():
			lines.append("The city: %s." % pressure_summary())
	return lines


## What is kept of a past situation (the full intel and plan are dropped).
static func _brief_record(s: Dictionary) -> Dictionary:
	return {"id": s["id"], "week": s["week"], "type": s["type"], "title": s["title"], "ward": s["ward"],
		"visibility": s["visibility"], "status": s["status"], "result": s.get("result", {}).duplicate(true)}


# ================================================================== saving
func to_data() -> Dictionary:
	return {"version": VERSION, "seed": seed_val, "rng_state": str(rng.state), "department": dept.to_data(),
		"board": board.duplicate(true), "past": past.duplicate(true), "politics": politics.to_data(),
		"pressure": pressure.duplicate(true), "short_history": short_history.duplicate(true), "short_last_week": short_last_week}


func from_data(d: Dictionary) -> bool:
	var ver := int(d.get("version", 0))
	if ver < 1 or ver > VERSION:
		return false
	# 4.72: as in Department.from_data, a save that parses but lost a key must not
	# throw here — this runs before the title screen and SaveFile only falls back to
	# the .bak when the file fails to *parse*, not when it is merely incomplete.
	seed_val = int(d.get("seed", 1001))
	rng.seed = seed_val * 31 + 7
	rng.state = String(d.get("rng_state", "0")).to_int()
	dept = Department.new()
	if not dept.from_data(d.get("department", {}) if d.get("department", {}) is Dictionary else {}):
		return false
	board = []
	var raw_board: Array = d.get("board", []) if d.get("board", []) is Array else []
	for b0 in raw_board:
		if b0 is Dictionary:
			board.append(b0)
			_ints(b0)
	past = []
	var raw_past: Array = d.get("past", []) if d.get("past", []) is Array else []
	for p0 in raw_past:
		if p0 is Dictionary:
			past.append(p0)
			_ints(p0)
	pressure = d.get("pressure", {}) if d.get("pressure", {}) is Dictionary else {}   # version 2 and earlier: no city was ever read
	short_history = {}
	if d.get("short_history", {}) is Dictionary:
		short_history = d["short_history"].duplicate(true)
	short_last_week = int(d.get("short_last_week", -99))
	# version 1 (before v0.9) had no politics: the city starts from the wards' trust now
	politics = Politics.new()
	politics.from_data(d.get("politics", {}) if d.get("politics", {}) is Dictionary else {}, seed_val)
	return true


## JSON keeps every number as a float: put back the ones that are integers.
## 4.72: guarded — board/past entries come from a file, and `int(null)` silently
## becomes 0 while `int("abc")` also becomes 0, so a junk value degrades instead
## of throwing mid-boot.
static func _ints(s: Dictionary) -> void:
	if not (s is Dictionary):
		return
	for k in ["week", "seed", "map", "ward_i", "trust", "visibility", "crowd", "duration", "attack_t", "deadline", "tip_count"]:
		if s.has(k):
			s[k] = int(s[k])


func save(path := SAVE_PATH) -> bool:
	return load("res://scripts/campaign/save_file.gd").write_json(path, to_data())


static func load_from(path := SAVE_PATH):
	var d = load("res://scripts/campaign/save_file.gd").read_json(path)
	if d == null:
		return null
	var c = load("res://scripts/campaign/campaign.gd").new()
	if not c.from_data(d):
		return null
	return c


# ================================================================= the endless-battle link (Q7)
## The campaign's six wards are the endless battle's six precincts, in the same
## order. What the city scene writes (Director.pressure_data: raw per-precinct
## counts) becomes, here, three weights per ward in 0..1 that Situations.board
## and .make read: gang (how much ground the crews hold), hot (how loud the
## precinct has been: incidents, reports, bodies), quiet (how often buildings
## changed hands back — police pressure working). Normalised against the
## loudest precinct, so the reading is about *where*, not how long anyone
## watched; a city nobody has played yields {} and the board is exactly the
## unlinked one, roll for roll.
static func pressure_from_city(data: Dictionary) -> Dictionary:
	var raw: Array = data.get("precincts", [])
	if int(data.get("version", 0)) != 1 or raw.size() != Situations.WARDS.size():
		return {}
	var act_max := 1.0
	var cap_max := 1.0
	var dead_max := 1.0
	for r in raw:
		act_max = maxf(act_max, float(int(r.get("incidents", 0)) + int(r.get("reports", 0))))
		cap_max = maxf(cap_max, float(int(r.get("captures", 0))))
		dead_max = maxf(dead_max, float(int(r.get("deaths", 0))))
	var wards: Array = []
	for r2 in raw:
		var act: float = float(int(r2.get("incidents", 0)) + int(r2.get("reports", 0))) / act_max
		wards.append({
			"gang": clampf(float(r2.get("gang", 0.0)) * 2.0, 0.0, 1.0),
			"hot": clampf(0.6 * act + 0.4 * (float(int(r2.get("deaths", 0))) / dead_max), 0.0, 1.0),
			"quiet": clampf(float(int(r2.get("captures", 0))) / cap_max, 0.0, 1.0)})
	return {"wards": wards, "minutes": float(data.get("minutes", 0.0))}


static func load_city_pressure(path := PRESSURE_PATH) -> Dictionary:
	if not read_city_file and path == PRESSURE_PATH:
		return {}
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var d = JSON.parse_string(f.get_as_text())
	f.close()
	return pressure_from_city(d) if d is Dictionary else {}


## One readable line for the week-end report and the department log.
func pressure_summary() -> String:
	var wards: Array = pressure.get("wards", [])
	if wards.is_empty():
		return "no reading from the street"
	var hot_i := 0
	var gang_i := 0
	for i in wards.size():
		if float(wards[i].get("hot", 0.0)) > float(wards[hot_i].get("hot", 0.0)):
			hot_i = i
		if float(wards[i].get("gang", 0.0)) > float(wards[gang_i].get("gang", 0.0)):
			gang_i = i
	return "%s is the loudest ward this week; the crews hold most ground in %s (from %d watched minutes of the city)" % [
		Situations.WARDS[hot_i]["name"], Situations.WARDS[gang_i]["name"], int(pressure.get("minutes", 0.0))]
