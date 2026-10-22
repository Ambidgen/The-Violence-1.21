# Crime-Thriller — The Noir Prose Bible

A working craft manual distilled from close study of the twenty most popular adult noir and crime-thriller
book series in English and translation — their sentences, their syntax, their dialogue, and the psychology
of the people they put on the page.

This is not a reading list, an encyclopedia, or a set of plot templates. It is a **prose bible**: a
reference you keep open beside the manuscript, with rules, dial settings, diagnostic tests, pastiche
exercises, and a linter that measures your draft against the voice you are trying to write.

> **Content note — 18+.**
> The source canon is adult fiction. It contains graphic violence, sexual violence, addiction, child abuse,
> and suicide. This bible discusses those elements as craft problems and includes an explicit ethics and
> handling chapter (`docs/prose-bible/04-style-grammar.md#9-violence-and-sex-on-the-page`). Nothing here is
> intended for younger readers or for YA projects; young-adult fiction is excluded from the research by
> design.

---

## Start here

| If you want to… | Read |
| --- | --- |
| Understand the project and its method | [`docs/prose-bible/00-preface.md`](docs/prose-bible/00-preface.md) |
| See the twenty series and why they were chosen | [`docs/prose-bible/01-the-canon.md`](docs/prose-bible/01-the-canon.md) |
| Fix a sentence, a paragraph, or a scene | [`docs/prose-bible/04-style-grammar.md`](docs/prose-bible/04-style-grammar.md) |
| Pick and tune a voice | [`docs/prose-bible/05-voice-recipes.md`](docs/prose-bible/05-voice-recipes.md) |
| Build plot and structure | [`docs/prose-bible/06-structure-and-plot.md`](docs/prose-bible/06-structure-and-plot.md) |
| Handle character psychology with accuracy | [`docs/prose-bible/03-character-psychology.md`](docs/prose-bible/03-character-psychology.md) |
| Understand how the canon actually writes | [`docs/prose-bible/02-prose-and-syntax.md`](docs/prose-bible/02-prose-and-syntax.md) |
| Study one series in depth | [`docs/prose-bible/series/`](docs/prose-bible/series/) (20 cards) |
| See one scene written five ways | [`docs/prose-bible/09-variants.md`](docs/prose-bible/09-variants.md) |
| Revise a draft or run drills | [`docs/prose-bible/07-revision-and-drills.md`](docs/prose-bible/07-revision-and-drills.md) |
| Check a source or a term | [`docs/prose-bible/08-sources-and-glossary.md`](docs/prose-bible/08-sources-and-glossary.md) |
| Measure a manuscript | [`tools/style_lint.py`](tools/style_lint.py) |

---

## The twenty

Ranked by a composite of commercial reach, durability, and demonstrated influence on later crime prose.
Sales figures are estimates; ranking rationale and exclusions are argued in
[`01-the-canon.md`](docs/prose-bible/01-the-canon.md).

| # | Series | Author | Years | Books | Engine |
| --- | --- | --- | --- | --- | --- |
| 1 | The Continental Op | Dashiell Hammett | 1923–1930 | 2 novels + stories | Behaviourist hardboiled |
| 2 | Philip Marlowe | Raymond Chandler | 1939–1958 | 7 | Lyrical hardboiled |
| 3 | Maigret | Georges Simenon | 1931–1972 | 75 + stories | Atmospheric procedural |
| 4 | Lew Archer | Ross Macdonald | 1949–1976 | 18 | Psychological PI |
| 5 | 87th Precinct | Ed McBain | 1956–2005 | 55 | Ensemble procedural |
| 6 | Martin Beck | Sjöwall & Wahlöö | 1965–1975 | 10 | Social procedural |
| 7 | Harlem Cycle | Chester Himes | 1957–1969 | 9 | Grotesque/absurdist noir |
| 8 | L.A. Quartet | James Ellroy | 1987–1992 | 4 + 3 | Telegraphic historical noir |
| 9 | Detroit/Miami corpus | Elmore Leonard | 1969–2013 | 45 | Dialogic comic noir |
| 10 | Dave Robicheaux | James Lee Burke | 1987–2024 | 24 | Southern lyrical noir |
| 11 | V.I. Warshawski | Sara Paretsky | 1982– | 22 | Feminist PI |
| 12 | Kinsey Millhone | Sue Grafton | 1982–2017 | 25 | 1980s PI |
| 13 | Kay Scarpetta | Patricia Cornwell | 1990– | 29 | Forensic procedural |
| 14 | Hannibal Lecter | Thomas Harris | 1981–2006 | 4 | Psychological thriller |
| 15 | Harry Bosch | Michael Connelly | 1992– | 26 (+ spin-offs) | Police procedural |
| 16 | John Rebus | Ian Rankin | 1987– | 25+ | Tartan noir |
| 17 | Kurt Wallander | Henning Mankell | 1991–2009 | 10 + stories | Nordic procedural |
| 18 | Millennium | Stieg Larsson | 2005–2007 | 3 | Investigative thriller |
| 19 | Jack Reacher | Lee Child | 1997–2026 | 31 | Action thriller |
| 20 | Harry Hole | Jo Nesbø | 1997–2026 | 13 (+1 in 2026) | Nordic noir thriller |

---

## What makes this a bible rather than an essay collection

1. **Every series gets the same card.** A fixed set of headings, in the same order, so voices are comparable:
   corpus, popularity evidence, syntax mechanics, character psychology, signature devices, what to steal,
   what to avoid, a diagnostic exercise and an original annotated pastiche.
2. **Claims are tied to evidence.** Craft conclusions are anchored in interviews, reviews, measured
   sentence-length studies, and the texts themselves. Sources are listed in
   [`08-sources-and-glossary.md`](docs/prose-bible/08-sources-and-glossary.md).
3. **It is operational.** `data/series.json` holds a 12-axis voice card for each series;
   [`05-voice-recipes.md`](docs/prose-bible/05-voice-recipes.md) turns those cards into writing parameters;
   `tools/style_lint.py` measures a draft against them.
4. **It is honest about its limits.** The dial values are editorial estimates, not corpus statistics.
   Where a number is a publisher estimate or a critic's measurement, it is labelled as such.

---

## Tooling

```bash
# Measure a chapter against the Chandler voice card
python3 tools/style_lint.py chapter-01.md --voice chandler

# Compare two voices side by side
python3 tools/style_lint.py chapter-01.md --voice ellroy --compare leonard

# Machine-readable output for CI or editor integration
python3 tools/style_lint.py chapter-01.md --voice connelly --json

# Run the linter's own tests
python3 tools/test_style_lint.py

# Take it for a spin on the sample scenes
python3 tools/style_lint.py tools/samples/chandler-scene.md --voice chandler
python3 tools/style_lint.py tools/samples/leonard-scene.md --voice leonard
```

The linter reports sentence-length distribution, dialogue ratio, filter-word and intensifier density,
said-bookisms, adverb-bearing dialogue tags, cliché hits, semicolon/em-dash/exclamation rates, paragraph
length, and a Flesch reading-ease score, then prints the delta against the chosen voice card. Full metric definitions and limits are in
[`tools/README.md`](tools/README.md).

It is a **diagnostic, not a judge**. A voice card is a target, and every target in this book is broken
deliberately somewhere in the canon.

---

## Repository map

```
README.md
data/
  series.json                 # 20 voice cards, machine-readable
docs/
  prose-bible/
    00-preface.md             # scope, method, how to use, ethics
    01-the-canon.md           # selection, ranking, exclusions, timeline
    02-prose-and-syntax.md    # cross-series analysis of sentences and sound
    03-character-psychology.md# trauma, moral injury, psychopathy, addiction
    04-style-grammar.md       # the operative rules (the bible proper)
    05-voice-recipes.md       # 12 dial settings + 8 combinable modules
    06-structure-and-plot.md  # architectures, scenes, exposition, endings
    07-revision-and-drills.md # checklists and 30 exercises
    08-sources-and-glossary.md# annotated sources and terminology
    09-variants.md            # one scene, five registers, measured
    series/
      README.md               # index and reading instructions
      01-hammett.md … 20-nesbo.md
tools/
  style_lint.py               # manuscript diagnostics against the voice cards
  test_style_lint.py          # 22 unit tests, stdlib only
  samples/
    chandler-scene.md         # narration-forward pastiche
    leonard-scene.md          # dialogue-forward pastiche
  README.md                   # usage, metric definitions, limits
```

---

## A note on originality

The pastiche passages in this repository are **original prose written for this project**. They demonstrate
syntactic patterns; they do not reproduce the source novels. Direct quotations from the canon are short,
attributed, and used for criticism. No copyrighted text is included at length.
