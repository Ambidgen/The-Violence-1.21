# The Violence

**The Violence** is a Godot 4 police-command and close-quarters autobattler set in Port Carrick. You are the chief: choose which situations to answer, assign officers, write their orders, and watch the operation resolve hands-off. The campaign lasts forty weeks and ends with an election.

This checkout contains the game source, maps, campaign systems, cutscenes, and headless test harnesses. It is not a design document or a prose story.

## Run the game

1. Install **Godot 4.4 or newer**. The primary engine is **4.7.2**; **4.4.1**
   is still supported and both are declared in `project.godot`.
2. Import `project.godot` in the Godot editor.
3. Run the main scene (`scenes/main.tscn`) or press **F6/F5** as appropriate for your editor setup.

The project uses the compatibility renderer. The title screen offers three ways to play:

- **New campaign / Continue:** the persistent forty-week department campaign. There is one ironman-style save slot, saved after operations and weeks.
- **Test range:** a configurable sandbox for two teams, officers, habits, equipment, and the twelve tactical maps.
- **Endless battle: Port Carrick:** a continuous city simulation with gangs, police precincts, reports, QRFs, captures, and ambulances.

The shipped Ogg Theora opening and short interstitials are optional. Shorts can be skipped with **Space**, **Enter**, **Escape**, a mouse click, or the on-screen **Skip** button. Missing video files do not block campaign flow.

## The campaign loop

Each week the operations board deals warrants, crew-house raids, barricaded suspects, hostage takings, and public events. Officers committed to one situation or to canvassing cannot be sent to another that week. Unanswered situations are recorded and can have consequences.

For a situation, work through:

1. **Briefing:** read confirmed facts, estimates, confidence, tips, time pressure, and the readiness range. The range is a planning index built from public intelligence and assigned force; it is **not a win probability**. Canvassing buys two tips but commits an officer for the week.
2. **Force:** form up to five squads of six, assign officers, and buy or return equipment within the budget and training restrictions. **Suggest a plan** is an editable starting point; Veteran chief mode removes it.
3. **Orders:** choose objectives and constraints. Order points depend on squad leadership and experience. The plan is a starting intention, not a script that guarantees compliance.
4. **Run:** watch the operation under fog of war. Officers judge, perceive, react, and fight using their training, habits, stress, and orders. You do not steer individual officers.
5. **Debrief:** read the itemized score arithmetic, officer and civilian outcomes, findings, and department consequences. Click any timeline event to seek the replay to that moment.

The first operation includes an optional four-step guide covering Briefing, Force, Orders, and Debrief. It can be skipped and is controlled by the first-weeks tips setting.

After an operation, review **Internal affairs**. Cases are sorted by severity and evidence, with filters for grave cases, video, and cases approaching lapse. Every case still requires its own decision: clear, retrain, suspend, or dismiss. The weekly board includes a triage summary.

## Controls and playback

| Input | Action |
| --- | --- |
| Mouse wheel | Zoom |
| Middle- or right-drag | Pan |
| Home | Refit the view |
| Space | Pause/resume an operation; skip a short when one is playing |
| 1–7 | Select operation speed in the test range/run controls |
| F2 | Toggle red ink / monochrome presentation |
| F3 | Toggle gore; evidence markers remain |
| Escape | Open the menu or go back one front-end screen |

The operation speed buttons provide the available playback rates. The rewind slider is a viewing tool: it never rolls back the simulation. Replay is available from the debrief.

**Contact-aware fast-forward** is an optional Settings toggle. At speeds above 1×, contact, casualties, and important radio events temporarily return playback to 1× for a short readable interval, then resume the selected speed after quiet. This changes presentation timing only, not simulation decisions or deterministic results.

Other settings include fullscreen, volume buses, red ink, gore, first-weeks tips, opening/rare campaign shorts, and Veteran chief mode. Presentation settings do not alter the simulation.

## The city and the campaign link

The endless city's six precincts correspond to the campaign's six wards. Its pressure file can influence later campaign boards: gang-held ground, reports and incidents, deaths, and police captures are read as broad weights rather than as a scripted outcome.

Reports cluster at precinct scale: within **140 metres**, **90 seconds**, and the same precinct. A QRF searches the nearby buildings. Hospital ambulances respond after all-clear; a guarded early response can collect living non-police casualties when a QRF is assigned and the incident's local report area has been quiet for twelve seconds. Police paramedics continue to prioritize downed officers.

City navigation caches static gate-to-gate street routes. The headless city soak reports AI, pathfinding, dormancy, and route-cache timings so optimization can be checked without changing seeded decisions.

## Saves and version

Campaign and settings data live under Godot's `user://` directory. The campaign save is versioned and older compatible saves are accepted. Do not run multiple game instances against the same save slot.

The canonical runtime version is `scripts/version.gd` (`Version.VALUE`). After changing it, synchronize Godot's metadata with:

```sh
python3 tools/sync_version.py
```

Commit `scripts/version.gd`, `project.godot`, and `export_presets.cfg` together. The improvement regression suite checks that these values agree.

## Headless checks

Run from the repository root with a Godot executable on your PATH (or substitute its absolute path):

```sh
godot --headless --path . -s res://tests/_check.gd
godot --headless --path . -s res://tests/improvements_test.gd
godot --headless --path . -s res://tests/city_improvements_test.gd
godot --headless --path . -s res://tests/ops_ui_test.gd
godot --headless --path . -s res://tests/dept_test.gd
godot --headless --path . -s res://tests/orders_test.gd
godot --headless --path . -s res://tests/determinism_test.gd -- --verbose
godot --headless --path . -s res://tests/city_sim.gd -- --seed=1001 --min=6 --quiet --fine
godot --headless --path . -s res://tests/godot472_test.gd
```

`tests/godot472_test.gd` is the Godot 4.7.2 compatibility regression: it feeds
the save path deliberately malformed-but-parseable data, checks the navigator's
unbuilt fallback, and re-checks that the version metadata is in sync.

### Static checks without an engine

`tools/gd47_check.py` is the audit used for the 4.7.2 pass. It needs no Godot
binary, so it runs in CI or in a sandbox with no engine:

```sh
python3 tools/gd47_check.py            # scripts/, tests/, tools/
python3 tools/gd47_check.py scripts/   # or one subtree
```

It checks bracket balance (with strings and comments stripped), duplicate class
members, tab-only indentation, `:=` inference from an untyped receiver — the
construct 4.7 rejects — the GDScript-breaking APIs from 4.4 to 4.7, and
statements that escaped into class scope. It is a linter, not a parser: confirm
anything it reports with `tests/_check.gd`.

Some harnesses accept additional options documented in their script headers. Headless execution validates logic and scene automation; it is not a substitute for visual or manual playtesting.

## Source map

- `scripts/main.gd`: application flow, operation playback, replay, and cutscene integration.
- `scripts/ui/ops_ui.gd`: board, planner, debrief, IA, and first-operation guide.
- `scripts/campaign/`: situations, planning, public-intel readiness, outcomes, department, politics, and saves.
- `scripts/sim/`: deterministic world, operators, navigation, combat, recorder, and pacing classifiers.
- `scripts/city/`: city generation, navigation, director, roads, and emergency response.
- `scripts/view/`: plan, actors, overlays, decals, replay, and presentation settings.
- `tests/`: engine-backed unit, regression, determinism, balance, and soak harnesses.

See `CHANGELOG.md` for historical release notes and the in-game **How to play** pages for the full mechanics reference.
