# 05 · Voice Recipes: from analysis to a voice you can write

A voice is not a mood. It is a set of decisions about **what the prose is allowed to do**. This chapter
turns the twenty series into parameters you can set, combine, and test.

---

## 1. The twelve dials

Defined in [`data/series.json`](../../data/series.json). Each runs 0–10. They are editorial estimates, not
measurements; their purpose is calibration.

| Dial | 0 | 5 | 10 |
| --- | --- | --- | --- |
| **sentence_len** | clipped, paratactic | mixed | long, periodic |
| **variance** | uniform | moderate | extreme long/short |
| **figuration** | bare | occasional | dense simile/metaphor |
| **interiority** | camera | reported thought | confessional |
| **dialogue** | narration-dominant | half | almost all dialogue |
| **description** | minimal | selective | lush, sustained |
| **violence** | off-page | depicted | graphic, dwelling |
| **irony** | earnest | dry | savage/black comedy |
| **fatalism** | order restored | ambivalent | doom |
| **procedure** | none | present | manual-like |
| **sex** | absent | implied | explicit |
| **distance** | deep inside one skull | limited | cold omniscient camera |

### How to set them

1. Pick the **base** series whose engine matches your book (not necessarily your favourite writer).
2. Copy its dials into a project card. Adjust no more than three dials; if you change more, you are writing
   a different voice, which is fine — but choose a base that is closer.
3. Write 1,000 words. Run the linter. Compare.
4. Adjust **one** dial at a time, and only in response to a specific weakness.

### Dial arithmetic

- Raising **figuration** without raising **variance** produces purple prose.
- Raising **interiority** without raising **figuration** produces confession; with it, lyricism.
- Raising **dialogue** lowers the need for **description**, but not for **action beats**.
- Raising **procedure** lowers the tolerable **coincidence**; a procedural reader will notice.
- Raising **violence** requires raising **aftermath**, or the book loses moral authority.
- Raising **distance** lowers **interiority**; you cannot have a cold camera and a confessional narrator.

### From dials to numbers

`tools/style_lint.py` converts four dials into measurable targets, using deliberately simple linear maps so
that every verdict can be audited:

| Dial | Target | Tolerance |
| --- | --- | --- |
| `sentence_len` | narration mean = 7 + 2.0 × dial | ±2.5 words |
| `variance` | narration SD = 3.5 + 0.65 × dial | ±1.5 words |
| `dialogue` | dialogue share = 5 + 6.5 × dial | ±8 points |
| `figuration` | similes/1,000 = 0.45 × dial | ±1.0 |
| `description` | sensory words/1,000 = 2 + 1.4 × dial | ±8.0 |
| `procedure` | numbers/1,000 = 1 + 1.2 × dial | ±7.0 |

The remaining dials — violence, irony, fatalism, sex, distance — are not countable, and the linter does not
pretend otherwise. Test those against the voice-consistency checks in
[`04-style-grammar.md`](04-style-grammar.md#12-voice-consistency-tests) and by reading the draft aloud.

---

## 2. Eight modules

Modules are combinable units of craft. A voice is usually **one base module + one texture module + one
prohibition**.

### M1 · Objective Camera

**Based on:** Hammett, Leonard, Child.
**Syntax:** short declaratives, parataxis, fragments permitted.
**Moves:** load-bearing detail; dialogue as negotiation; inference left to the reader.
**Forbids:** interiority, simile, explanation of motive.
**Best for:** hardboiled PI, heist, procedural action, any narrator who refuses to explain himself.

### M2 · Lyric Interior

**Based on:** Chandler, Macdonald, Burke.
**Syntax:** long cumulative sentences alternating with short verdicts; hypotaxis; sensory accumulation.
**Moves:** diagnostic simile; landscape as moral weather; memory as exposition.
**Forbids:** decorative figuration; beauty without threat.
**Best for:** PI, Southern/gothic noir, cold case, any book where the past is a character.

### M3 · Telegraphic Montage

**Based on:** Ellroy, late Child.
**Syntax:** fragments, verbless constructions, alliteration, dates as joints.
**Moves:** documentary cut; the secret that organises a life; history as suspect.
**Forbids:** transitions, throat-clearing, unearned obscurity.
**Best for:** historical noir, conspiracy, ensemble crime, any book with more plot than page.

### M4 · Dialogic Engine

**Based on:** Leonard, McBain, Rankin.
**Syntax:** plain sentences, minimal description, heavy dialogue.
**Moves:** transaction and subtext; idiolect; comedy as survival; the skipped part.
**Forbids:** adverbs, said-bookisms, authorial commentary.
**Best for:** comic crime, caper, squad room, any book where people talk for a living.

### M5 · Procedural Grid

**Based on:** Connelly, Cornwell, Sjöwall & Wahlöö, Mankell.
**Syntax:** plain, ordered, medium-length; documents and sequences.
**Moves:** procedure as suspense; the cold case; the institutional obstacle; expertise under pressure.
**Forbids:** coincidence, super-detective deduction, procedure without cost.
**Best for:** police procedural, forensic thriller, social crime, any book where the system is the maze.

### M6 · Gothic Predator

**Based on:** Harris, Himes, Nesbø.
**Syntax:** precise procedural sentences interrupted by sensory shocks; free indirect access.
**Moves:** courtesy as threat; the monster as critic; the body as evidence and horror.
**Forbids:** gore without etiquette; explaining the monster; aestheticised cruelty without judgment.
**Best for:** psychological thriller, serial-killer novel, any book that needs dread rather than action.

### M7 · Social Documentary

**Based on:** Sjöwall & Wahlöö, Larsson, Rankin.
**Syntax:** plain, expository, ensemble; documents and statistics.
**Moves:** the case as social symptom; institutional irony; the archive as weapon.
**Forbids:** pamphleteering, individual-villain explanations, glamorous policing.
**Best for:** political crime, investigative thriller, any book where the crime is a system.

### M8 · Comic Noir

**Based on:** Leonard, Himes, McBain.
**Syntax:** short, flat, deadpan; comedy in the rhythm, not the adjectives.
**Moves:** self-deception; competence porn; the joke that is also a threat.
**Forbids:** whimsy, punchlines that stop the plot, laughing at your own characters.
**Best for:** caper, lowlife, any book that needs to survive its own darkness.

---

## 3. The twenty recipes

Each recipe is a one-screen instruction. Dials are in the order:
`sentence · variance · figuration · interiority · dialogue · description · violence · irony · fatalism ·
procedure · sex · distance`.

### R1 · Hammett

**Base:** M1. **Texture:** M5 (procedure). **Prohibition:** no interiority, no decorative simile.
**Dials:** 3·4·2·2·7·3·5·5·6·6·2·8.
**If you remember one thing:** the narrator reports; the reader judges.

### R2 · Chandler

**Base:** M2. **Texture:** M4 (dialogue). **Prohibition:** no simile that does not judge.
**Dials:** 6·8·8·8·6·6·5·8·7·3·4·3.
**If you remember one thing:** the long sentence sets the mood; the short one tells the truth.

### R3 · Simenon

**Base:** M5. **Texture:** M2 (lyric, restrained). **Prohibition:** no cleverness.
**Dials:** 4·3·3·6·6·4·4·3·7·5·4·5.
**If you remember one thing:** atmosphere is an accumulation of ordinary facts, not adjectives.

### R4 · Macdonald

**Base:** M2. **Texture:** M5 (procedure). **Prohibition:** no pop-Freudian explanation.
**Dials:** 6·6·7·8·6·6·4·4·7·3·4·3.
**If you remember one thing:** the case is a family; the detective is the listener.

### R5 · McBain

**Base:** M4. **Texture:** M5 (procedure). **Prohibition:** no super-detective.
**Dials:** 4·5·2·4·8·3·5·5·4·8·3·7.
**If you remember one thing:** give them head colds, first names, and homey dialogue.

### R6 · Sjöwall & Wahlöö

**Base:** M7. **Texture:** M5. **Prohibition:** no sermon.
**Dials:** 5·4·2·4·5·4·3·4·6·7·3·6.
**If you remember one thing:** the case is a symptom; the procedure is the argument.

### R7 · Himes

**Base:** M8. **Texture:** M6. **Prohibition:** no violence without consequence.
**Dials:** 4·7·6·4·7·5·8·8·7·2·5·6.
**If you remember one thing:** let the joke and the corpse share a paragraph.

### R8 · Ellroy

**Base:** M3. **Texture:** M6. **Prohibition:** no alliteration without rhythm.
**Dials:** 2·3·5·3·4·3·9·7·9·5·7·7.
**If you remember one thing:** cut every word that is not doing damage.

### R9 · Leonard

**Base:** M4. **Texture:** M8. **Prohibition:** no adverbs, no description, no cleverness.
**Dials:** 3·5·2·3·9·2·6·7·6·3·5·8.
**If you remember one thing:** leave out the part the reader would skip.

### R10 · Burke

**Base:** M2. **Texture:** M6 (restrained). **Prohibition:** no beauty without threat.
**Dials:** 7·8·9·9·4·9·7·3·5·3·3·2.
**If you remember one thing:** the landscape is a moral instrument.

### R11 · Paretsky

**Base:** M2. **Texture:** M5. **Prohibition:** no speeches about feminism.
**Dials:** 6·7·5·8·6·6·6·5·5·5·3·3.
**If you remember one thing:** the money trail is the plot; the anger has an address.

### R12 · Grafton

**Base:** M4. **Texture:** M5. **Prohibition:** no anachronism.
**Dials:** 4·5·4·8·6·5·4·6·4·5·3·3.
**If you remember one thing:** the report frame makes the reader a confidant.

### R13 · Cornwell

**Base:** M5. **Texture:** M6 (controlled). **Prohibition:** no gore without procedure.
**Dials:** 5·5·3·8·5·6·7·3·6·9·5·4.
**If you remember one thing:** order is the suspense; the body is a person.

### R14 · Harris

**Base:** M6. **Texture:** M5. **Prohibition:** no explanation of the monster.
**Dials:** 5·7·6·6·4·7·9·4·8·7·6·6.
**If you remember one thing:** courtesy is the threat; free indirect is the door.

### R15 · Connelly

**Base:** M5. **Texture:** M1. **Prohibition:** no procedure without cost.
**Dials:** 4·4·3·5·6·4·6·4·6·9·3·6.
**If you remember one thing:** the file is the plot; the city is the moral map.

### R16 · Rankin

**Base:** M5. **Texture:** M2. **Prohibition:** no tourist Edinburgh.
**Dials:** 6·7·5·7·7·6·5·6·5·6·4·5.
**If you remember one thing:** the city is vertical; the monologue is detection.

### R17 · Mankell

**Base:** M5. **Texture:** M7. **Prohibition:** no irony.
**Dials:** 5·3·3·6·5·5·3·2·6·7·2·6.
**If you remember one thing:** the silence is the subject; the thought is the action.

### R18 · Larsson

**Base:** M7. **Texture:** M3. **Prohibition:** no info-dump without a want.
**Dials:** 5·4·2·4·5·5·6·3·4·8·7·8.
**If you remember one thing:** build the book like a dossier; let the reader reconstruct it.

### R19 · Child

**Base:** M1. **Texture:** M5 (measurement). **Prohibition:** no metaphor, no long paragraph.
**Dials:** 2·4·1·2·4·2·6·4·4·5·2·8.
**If you remember one thing:** write the fast stuff slow and the slow stuff fast.

### R20 · Nesbø

**Base:** M6. **Texture:** M3. **Prohibition:** no gore without moral cost.
**Dials:** 4·6·4·5·4·5·8·5·8·6·6·6.
**If you remember one thing:** cut on the image; withhold the identity.

---

## 4. Blending

### The three-slot method

1. **Base** — the engine that decides what the prose is for. Choose one.
2. **Texture** — a secondary device that colours the surface. Choose one.
3. **Prohibition** — the rule that keeps the blend from becoming mush. Choose one.

Do not blend three bases. A book cannot be simultaneously a lyric meditation and a telegraphic montage and
a dialogic caper; it can be a lyric meditation **with** dialogue **and** a prohibition on decoration.

### Compatibility table

| Base ↓ / Texture → | M1 Objective | M2 Lyric | M3 Telegraphic | M4 Dialogic | M5 Procedural | M6 Gothic |
| --- | --- | --- | --- | --- | --- | --- |
| **M1 Objective** | — | strong | strong | strong | strong | risky |
| **M2 Lyric** | strong | — | risky | strong | strong | strong |
| **M3 Telegraphic** | strong | risky | — | risky | strong | strong |
| **M4 Dialogic** | strong | strong | risky | — | strong | risky |
| **M5 Procedural** | strong | strong | strong | strong | — | strong |
| **M6 Gothic** | risky | strong | strong | risky | strong | — |

"Risky" means the blend can work but needs a governing idea. Lyric + telegraphic, for example, is a
contradiction unless the book has two narrators or two time periods.

### Three worked blends

**Blend A — "Cold case elegy"**
Base M5 (procedural), texture M2 (lyric), prohibition: no decorative simile.
Dials: sentence 6 · variance 7 · figuration 6 · interiority 6 · dialogue 5 · description 6 · violence 4 ·
irony 4 · fatalism 7 · procedure 8 · sex 3 · distance 5.
Effect: a procedural that grieves. The procedure supplies structure; the lyricism supplies moral weight.

> The file had been closed for thirty-one years, and the box had been moved four times. The lid was soft
> with damp. Inside, the photographs had stuck together at one corner, and the corner had been torn when
> someone separated them, which meant someone had looked at them recently. I set them out on the table in
> the order they had been taken. Then I read the first page of the report, and then I read it again, because
> the first time I had been looking for a name and the second time I was looking for a lie.

**Blend B — "Comic caper with teeth"**
Base M4 (dialogic), texture M8 (comic noir), prohibition: no joke that stops the plot.
Dials: sentence 3 · variance 5 · figuration 2 · interiority 2 · dialogue 8 · description 2 · violence 6 ·
irony 8 · fatalism 5 · procedure 3 · sex 4 · distance 8.
Effect: speed, pleasure, sudden violence that lands because no one has been taking it seriously.

> "You brought a gun to a wedding."
>
> "I brought a gun to a wedding," Vince said. "I didn't bring it *out* at the wedding. There's a
> difference."
>
> "The difference is a felony."
>
> "The difference is manners."

**Blend C — "Nordic social gothic"**
Base M7 (social documentary), texture M6 (gothic), prohibition: no aestheticised cruelty.
Dials: sentence 5 · variance 4 · figuration 3 · interiority 4 · dialogue 5 · description 5 · violence 6 ·
irony 3 · fatalism 7 · procedure 8 · sex 3 · distance 7.
Effect: a social novel with dread. The documentary surface makes the horror credible; the horror makes the
social argument urgent.

> The apartment had been rented in the name of a company that had been dissolved in 2019 and had continued
> to pay rent for four years, which was the first thing that did not fit. The second thing was the freezer.
> It was new, and it was empty, and it had been switched off at the wall with the door left open, as if
> someone had wanted to make sure that nothing in it would be preserved.

---

## 5. Pastiche, imitation, and plagiarism

- **Pastiche** is writing under a voice's constraints with your own characters and sentences. It is a
  legitimate exercise and, in this book, the main teaching method.
- **Imitation** is copying a voice's surface tics without its permissions. It produces cliché.
- **Plagiarism** is reproducing another writer's sentences, characters, or plot. It is not a style.

The diagnostic passages in the series cards are original prose. If you publish pastiche, label it as such,
and never borrow a distinctive character or a plot.

---

## 6. Calibration workflow

1. Write a **1,000-word calibration sample** in the voice.
2. Run:
   ```bash
   python3 tools/style_lint.py sample.md --voice chandler
   ```
3. Read the **deltas**, not the raw numbers. The linter tells you where the draft is unlike the card.
4. Choose **one** delta to fix. Rewrite 200 words. Re-run.
5. When the sample is close, write the chapter. Re-calibrate every 10,000 words; voices drift.

### What to do when the linter disagrees with your ear

Trust your ear first, then investigate. The linter measures **surface** features; it cannot hear whether a
joke lands or a silence is earned. If the sample is working and the numbers are off, the card may be wrong
for the book. Write a note explaining the deviation, and adjust the card — not the prose.

---

**Next:** [`06-structure-and-plot.md`](06-structure-and-plot.md) — the architecture that carries the voice.
