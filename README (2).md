# `style_lint.py` — prose diagnostics

A small, dependency-free diagnostic for the voice cards in [`data/series.json`](../data/series.json).
It measures surface features of a manuscript and compares them with an editorial target derived from a
series' twelve dials.

It is **not** a grammar checker, a plagiarism detector, or a judge of quality. It cannot tell you whether a
joke lands. It can tell you that your Leonard pastiche has 30% dialogue and 20-word sentences, which is
probably not what you intended.

---

## Quick start

```bash
# List the available voice cards
python3 tools/style_lint.py --list-voices

# Basic metrics
python3 tools/style_lint.py chapter-01.md

# Compare against a voice
python3 tools/style_lint.py chapter-01.md --voice chandler

# Compare against two voices
python3 tools/style_lint.py chapter-01.md --voice ellroy --compare leonard

# JSON for an editor or CI
python3 tools/style_lint.py chapter-01.md --voice connelly --json

# Run the tests
python3 tools/test_style_lint.py
```

Requires Python 3.10+ (uses `dataclasses`, `statistics`, and modern type hints). No third-party packages.

---

## What it measures

| Metric | Definition | Why it matters |
| --- | --- | --- |
| `words` | Word tokens (letters, digits, apostrophes, hyphens) | Baseline |
| `sentences` | Sentences after abbreviation-aware splitting | Baseline |
| `mean_sentence` | Mean words per sentence, including dialogue | Rhythm |
| `median_sentence` | Median words per sentence | Less skewed by outliers |
| `sd_sentence` | Population standard deviation of sentence lengths | **Variance is style** |
| `narration_mean_sentence` | Mean sentence length with quoted dialogue removed | Voice comparison |
| `narration_sd_sentence` | SD of narration-only sentences | Voice comparison |
| `pct_under_8` | Share of sentences under 8 words | Propulsion / fragmentation |
| `pct_over_30` | Share of sentences over 30 words | Accumulation / lyricism |
| `dialogue_pct` | Share of words inside quotation marks or dash-dialogue lines | Register |
| `filter_per_1000` | *felt, saw, heard, noticed, realized, watched, seemed, wondered, decided, observed* | Distance |
| `intensifier_per_1000` | *very, really, quite, just, literally…* | Weak prose |
| `adverb_tags` | Adverbs attached to dialogue verbs | Leonard violation |
| `said_bookisms` | *opined, retorted, chuckled…* | Tag purple prose |
| `exclamations_per_1000` | `!` density | Authority |
| `semicolons_per_1000` | `;` density | Register |
| `em_dashes_per_1000` | `—` and `–` density | Interruption / melodrama |
| `similes_per_1000` | `like a/an/the` and `as … as` constructions | Figuration proxy |
| `sensory_per_1000` | Density of a small sensory lexicon | Description proxy |
| `numbers_per_1000` | Numeric tokens | Procedural proxy |
| `question_ratio` | Share of sentences ending in `?` | Rhetorical suspense |
| `flesch` | Flesch reading ease | Legibility |
| `mean_paragraph_words` | Words per paragraph | Pace / white space |
| `top_opening` | Most frequent sentence-opening words | Monotony |
| `cliche_hits` | Matches against a curated cliché list | Revision targets |

### Targets

Voice cards carry twelve 0–10 dials. The linter maps four of them to measurable targets:

```
narration_mean_sentence  = 7 + 2.0 × sentence_len       (±2.5)
narration_sd_sentence    = 3.5 + 0.65 × variance        (±1.5)
dialogue_pct             = 5 + 6.5 × dialogue           (±8)
similes_per_1000         = 0.45 × figuration            (±1.0)
sensory_per_1000         = 2 + 1.4 × description        (±8)
numbers_per_1000         = 1 + 1.2 × procedure           (±7)
```

These are **calibration aids**, not statistical models. They are deliberately simple so you can see exactly
why a verdict was produced. The dials themselves are editorial estimates; see
[`docs/prose-bible/08-sources-and-glossary.md`](../docs/prose-bible/08-sources-and-glossary.md).

Verdicts:

- **PASS** — within tolerance.
- **NEAR** — within 1.75× tolerance.
- **OFF** — outside.

Read the **delta**, not the verdict. A deliberate deviation is a choice; an unnoticed one is a tic.

---

## Example

Running the Chandler sample that ships with the tool:

```console
$ python3 tools/style_lint.py tools/samples/chandler-scene.md --voice chandler

=== tools/samples/chandler-scene.md ===
  words 326 · sentences 19 · paragraphs 15 · mean paragraph 21.7 words
  sentence mean 17.2 · median 12 · sd 15.0 · range 2–47
  narration mean 24.2 · narration sd 16.2
  <8 words 36.8% · >30 words 26.3% · questions 0%
  dialogue 18.4% (60 words) · narration 266 words
  filter 3.07/1k · intensifier 0.0/1k · adverb tags 0 · said-bookisms 0
  simile 3.07/1k · sensory 9.2/1k · numbers 0.0/1k
  ! 0.0/1k · ; 0.0/1k · — 0.0/1k · Flesch 78.1
  repeated openings: she×4, the×4, i×1

  CLICHÉ HITS: none

  VOICE: Raymond Chandler — Philip Marlowe (chandler)
  metric                      draft    target      delta   verdict
  narration_mean_sentence     24.2      19.0 ±2.5      +5.2   OFF
  narration_sd_sentence       16.2       8.7 ±1.5      +7.5   OFF
  dialogue_pct                18.4      44.0 ±8.0     -25.6   OFF
  similes_per_1000            3.07       3.6 ±1.0      -0.5   PASS
  sensory_per_1000            9.2       10.4 ±8.0      -1.2   PASS
  numbers_per_1000            0.0        4.6 ±7.0      -4.6   PASS
```

The sample is deliberately under-dialogued for Marlowe: it is a narration exercise, and the linter says so.
Note that the verdicts are *directional*, not grades. A scene can be 25 points under the dialogue target and
still be the right scene — but now you know which lever you are pulling.

Two samples ship in `tools/samples/`:

| File | Register | What it demonstrates |
| --- | --- | --- |
| `chandler-scene.md` | Narration-forward, high figuration | Long narration sentences, simile density |
| `leonard-scene.md` | Dialogue-forward, zero interiority | Short sentences, high dialogue share, flat diction |

Both are original pastiche written for this repository, not excerpts.

## Known limits

1. **It measures surface, not meaning.** A paragraph can pass every metric and still be dead.
2. **Dialogue detection is quote-based.** Straight and curly double quotes, plus lines beginning with an em
   dash. Single-quote dialogue and unpunctuated dialogue will be undercounted.
3. **Sentence splitting is heuristic.** Abbreviations and initials are protected; unusual punctuation is
   not.
4. **The figuration proxy counts constructions, not quality.** "Like a man who had heard the argument
   before" and "like a pizza" both count once.
5. **The sensory lexicon is small.** It is a density proxy, not a semantic analysis.
6. **Markdown is stripped.** Headings, links, emphasis, and block quotes are removed before analysis.
7. **English only.** The syllable counter and Flesch formula are English-specific.

---

## Extending

To add a voice, append a card to `data/series.json` with the twelve dials and the metadata fields. The
linter discovers it automatically; `--list-voices` will show it.

To add a cliché, append a `(name, regex)` pair to `CLICHES` in `style_lint.py` and add a unit test.

To change the dial mappings, edit `targets_from_dials()` and update the table above.
