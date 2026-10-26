# 00 · Preface: What this book is, and how to use it

## The problem this solves

Most writing advice about crime fiction is either too abstract ("raise the stakes") or too local ("cut
adverbs"). Neither tells you why Chandler's paragraphs accelerate, why Hammett's narrator seems to have no
feelings, why Simenon's plots are often implausible yet his books are hypnotic, why Ellroy's fragments feel
dense rather than thin, or why Leonard's pages read faster than everyone else's.

This bible answers those questions at the level of **mechanics**, and then converts the answers into
reusable instructions.

It exists because crime is a genre of *voice*. Readers forgive an implausible plot; they rarely forgive a
narration that sounds like nobody. The twenty series studied here are the ones that taught the last
century how a crime novel should sound.

## Scope

**Included:** adult (18+) noir, hardboiled, police-procedural, private-eye, forensic, and crime-thriller
**series** — twenty of them, selected for commercial reach, durability, and demonstrated influence on the
prose of later crime writing.

**Excluded, deliberately:**

- **Young-adult fiction.** No YA, no "crossover" YA, no teen-protagonist thrillers. The user brief for
  this project excludes it, and the psychology and content of the adult canon is different in kind.
- **Puzzle mysteries and cozies** (Christie, Sayers, Chesterton). Enormously popular, but their engine is
  ratiocination and their register is comic-domestic; they are not noir, and their prose teaches different
  lessons.
- **Legal thrillers** (Grisham), **conspiracy/religious thrillers** (Brown), **spy fiction** (le Carré,
  Fleming), and **domestic-suspense standalones** (*Gone Girl*, *The Girl on the Train*). All are crime
  adjacents; none is a noir/crime *series* in the sense studied here.
- **James Patterson.** The largest-selling crime-adjacent novelist alive, and a genuinely instructive
  commercial object — but his method (co-authored outlines, two-page chapters, plot-first assembly) is a
  different craft from the sentence-level voice work this book is about. He is discussed as a boundary
  case in [`01-the-canon.md`](01-the-canon.md#boundary-cases-and-why-they-are-outside).

The reasons matter more than the list. A canon is an argument, and
[`01-the-canon.md`](01-the-canon.md) makes the argument explicitly, including who got left out and why.

## The method

Each series was studied on five passes:

1. **Position** — what the series did first, or better than anyone, and what later writers borrowed from it.
2. **Syntax** — sentence length and cadence, clause architecture, paragraph shape, punctuation habits,
   ratio of dialogue to narration, tense and point of view, chapter length, handling of exposition.
3. **Figuration** — the simile and metaphor budget, what the images are drawn from, whether they decorate
   or diagnose.
4. **Psychology** — how the protagonist's wound is structured; how antagonists are motivated; how trauma,
   addiction, shame, and power are rendered on the page rather than described.
5. **Pressure test** — write an original passage under the voice's constraints, then annotate what the
   passage had to do to sound like that.

The findings were then compressed into a common template so that a Hammett sentence and a Burke sentence
could be compared without metaphor.

### What the numbers are, and are not

Three kinds of quantitative statements appear in this book, and they are never mixed:

| Type | Example | Status |
| --- | --- | --- |
| **Publisher/industry estimate** | "Cornwell: 120+ million copies" | Reported figure, source named, not audited |
| **Critic's measurement** | "Hammett's average sentence in the early work is thirteen words" (William Marling) | Attributed measurement on a defined corpus |
| **Editorial dial** | "Chandler figuration: 8/10" | This book's judgement, for calibration only |

The twelve dials in [`data/series.json`](../../data/series.json) are **not** corpus statistics. They are
expert ratings on defined axes, meant to be argued with. If you measure a Chandler novel and get a different
number, your measurement wins; the dial is a writing target, not a claim about the text.

## How to use this book

### Workflow A — you are starting a book and choosing a voice

1. Read [`05-voice-recipes.md`](05-voice-recipes.md) and pick a **base register** (objective, lyric,
   telegraphic, dialogic, procedural, gothic).
2. Read the matching series card in [`series/`](series/).
3. Set your dials in `data/series.json` or a project-local copy.
4. Write 1,500 words. Run `tools/style_lint.py` against the nearest voice card.
5. Adjust the *draft*, not the card — unless you can articulate why the card is wrong.

### Workflow B — you have a draft that feels flat

1. Run the linter. Look first at **sentence-length standard deviation** and **dialogue ratio**. Most flat
   drafts are rhythmically monotonous, not lexically poor.
2. Go to [`02-prose-and-syntax.md`](02-prose-and-syntax.md) and diagnose the paragraph shape.
3. Apply the relevant rule from [`04-style-grammar.md`](04-style-grammar.md).
4. Revise one page aloud. If you run out of breath in the same place twice, the syntax is wrong.

### Workflow C — you are writing a scene with a psychological problem

1. Look up the pattern in [`03-character-psychology.md`](03-character-psychology.md) (trauma, moral injury,
   addiction, psychopathy, shame, coercive control).
2. Read the two or three series cards that handle it best.
3. Check the scene against the **accuracy tests** at the end of that chapter: symptom specificity, cost,
   consequence, and point of view.
4. Do not diagnose a character in narration unless the point of view would actually use that vocabulary.

### Workflow D — you want to hear what register actually changes

1. Take a scene you have already drafted, or the neutral draft in [`09-variants.md`](09-variants.md).
2. Rewrite it four times, once per register, **without changing the facts**.
3. Measure all five versions with `tools/style_lint.py`. The numbers will show you which choices were
   carrying the voice and which were decoration.
4. Keep the register that makes the scene's *problem* most visible, not the one that was most fun to write.

## The ethics of adult crime fiction

This canon is full of rape, torture, child murder, addiction, and suicide. Pretending otherwise would be
cowardice. But the difference between the books that last and the ones that do not is almost never the
quantity of transgression; it is whether the transgression is **caused, witnessed, and paid for**.

The bible therefore treats the 18+ material as a craft discipline with four non-negotiables, expanded in
[`04-style-grammar.md`](04-style-grammar.md#9-violence-and-sex-on-the-page):

- **Point of view earns the camera.** Graphic detail is licensed by whose eyes we are behind and what they
  would actually notice.
- **Violence has aftermath.** Bodies bruise, hands shake, cases collapse, sleep fails.
- **Sex is never a reward for the plot.** It is character, power, or consequence.
- **The victim is a person before and after being a body.** If the only function of a character is to be
  found, the scene is pornography of a not-very-interesting kind.

## Conventions used in this book

- **Steal** = a device worth copying, stated as a rule.
- **Avoid** = a failure mode the same writer demonstrates or invites.
- **Diagnostic** = a short original passage written to the series' constraints, annotated to show the
  mechanism.
- **Dial** = a 0–10 editorial rating on an axis defined in [`data/series.json`](../../data/series.json).
- **Hard rule** = a rule this book treats as binding unless deliberately broken for a stated effect.
- **Soft rule** = a default you should have a reason to leave.

Quotations from the canon are short, attributed, and used for criticism. All pastiche passages are
original prose written for this project.

## Limitations

1. **Anglophone bias.** The canon is dominated by American, British, and translated Scandinavian writing.
   Simenon and Himes widen it; it is still narrow. French, Japanese, Latin American, Italian, and African
   crime traditions are underrepresented for reasons of market reach, not merit.
2. **Survivorship bias.** These are the series that lasted. For every one, a hundred equally instructive
   failures are out of print.
3. **Translation.** Simenon, Sjöwall & Wahlöö, Mankell, Larsson, and Nesbø are studied in English
   translation. Their syntax is partly the translator's. Where this matters, the series cards say so.
4. **The market moves.** Sales estimates decay; a series can be culturally central and commercially modest,
   or the reverse. The ranking is a snapshot with an argument attached.

---

**Next:** [`01-the-canon.md`](01-the-canon.md) — the twenty, the evidence, and the exclusions.
