#!/usr/bin/env python3
"""
style_lint.py — diagnostic prose metrics for the Noir Prose Bible.

This is a *diagnostic*, not a judge. It measures surface features of a manuscript and
compares them with the editorial voice cards in data/series.json. It cannot hear whether
a joke lands or a silence is earned.

Usage:
    python3 tools/style_lint.py chapter.md
    python3 tools/style_lint.py chapter.md --voice chandler
    python3 tools/style_lint.py chapter.md --voice ellroy --compare leonard
    python3 tools/style_lint.py chapter.md --voice connelly --json
    python3 tools/style_lint.py --list-voices
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Iterable

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "series.json"

# --------------------------------------------------------------------------------------
# Lexicons
# --------------------------------------------------------------------------------------

ABBREVIATIONS = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "mt", "vs", "etc", "e.g", "i.e",
    "no", "nos", "vol", "pp", "p", "fig", "dept", "est", "approx", "inc", "ltd", "co",
    "capt", "col", "gen", "lt", "sgt", "rev", "hon", "pres", "gov", "sen", "rep",
}

FILTER_WORDS = [
    "felt", "saw", "heard", "noticed", "realized", "realised", "watched",
    "seemed", "wondered", "decided", "observed",
]

INTENSIFIERS = [
    "very", "really", "quite", "rather", "somewhat", "just", "actually",
    "literally", "totally", "absolutely", "extremely", "incredibly", "definitely",
]

SAID_BOOKISMS = [
    "opined", "retorted", "chuckled", "chortled", "hissed", "growled", "snarled",
    "quipped", "jested", "ejaculated", "averred", "interjected", "expostulated",
    "vociferated", "laughed", "smiled", "grinned", "sneered", "barked", "snapped",
]

SENSORY_WORDS = {
    "smell", "smelled", "smelt", "stink", "stank", "odour", "odor", "scent", "reek",
    "sound", "noise", "hum", "buzz", "roar", "creak", "whisper", "echo", "silence",
    "light", "dark", "shadow", "glare", "gleam", "dull", "bright", "grey", "gray",
    "cold", "heat", "warm", "damp", "wet", "dry", "rough", "smooth", "sticky",
    "sweet", "sour", "bitter", "salt", "taste", "touch", "skin", "breath",
    "rain", "snow", "fog", "wind", "sun", "dust", "smoke", "ash",
}

# Cliché patterns. Keep them specific enough to avoid false positives.
CLICHES: list[tuple[str, str]] = [
    ("rain lashed", r"\brain\s+(lashed|pounded|hammered)\b"),
    ("she was trouble", r"\bshe\s+was\s+trouble\b"),
    ("seen it all", r"\b(had\s+)?seen\s+it\s+all\b"),
    ("city never sleeps", r"\bcity\s+that\s+never\s+sleeps\b"),
    ("chill down spine", r"\bchill\s+(ran|went|shot)\s+(down|up)\b.*\bspine\b"),
    ("blood ran cold", r"\bblood\s+ran\s+cold\b"),
    ("all hell broke loose", r"\ball\s+hell\s+broke\s+loose\b"),
    ("breath he didn't know", r"\bbreath\s+(he|she)\s+(didn't|did\s+not)\s+know\b"),
    ("eyes locked", r"\beyes\s+locked\b"),
    ("smell of death", r"\bsmell\s+of\s+death\b"),
    ("single tear", r"\bsingle\s+tear\b"),
    ("little did", r"\blittle\s+did\b"),
    ("this time personal", r"\bthis\s+time\s+it\s+was\s+personal\b"),
    ("clock ticking", r"\bclock\s+was\s+ticking\b"),
    ("everything changed", r"\beverything\s+changed\b"),
    ("didn't believe in coincidences", r"\bdidn'?t\s+believe\s+in\s+coincidences\b"),
    ("welcome to my world", r"\bwelcome\s+to\s+my\s+world\b"),
    ("man of few words", r"\bman\s+of\s+few\s+words\b"),
    ("heart pounded", r"\bheart\s+pounded\b"),
    ("let out a breath", r"\blet\s+out\s+a\s+breath\b"),
]

QUOTE_RE = re.compile(r'"[^"\n]{1,4000}"|“[^”\n]{1,4000}”')
DASH_DIALOGUE_RE = re.compile(r"^\s*[—–-]\s+\S", re.MULTILINE)


# --------------------------------------------------------------------------------------
# Text preparation
# --------------------------------------------------------------------------------------

def strip_markdown(text: str) -> str:
    """Remove common Markdown scaffolding so metrics reflect prose, not syntax."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)
    text = re.sub(r"(\*\*|__|\*|_)", "", text)
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def split_sentences(paragraph: str) -> list[str]:
    """Split a paragraph into sentences, protecting abbreviations and initials."""
    protected = paragraph
    # Protect multi-dot abbreviations such as "p.m.", "a.m.", "U.S.", "e.g.".
    protected = re.sub(r"\b([A-Za-z])\.([A-Za-z])\.", r"\1<DOT>\2<DOT>", protected)
    # If a protected multi-dot token is followed by a capital, it probably ends the
    # sentence ("at 5 p.m. She left") rather than modifying the next word.
    protected = re.sub(r"<DOT>\s+([A-Z])", r". \1", protected)
    for ab in sorted(ABBREVIATIONS, key=len, reverse=True):
        # protect the dot inside abbreviations (e.g. "Dr." -> "Dr<DOT>")
        protected = re.sub(
            rf"(?i)\b({re.escape(ab)})\.", r"\1<DOT>", protected
        )
    # protect single-letter initials: "J. Edgar" -> "J<DOT> Edgar"
    protected = re.sub(r"\b([A-Z])\.", r"\1<DOT>", protected)
    protected = protected.replace("...", "…")
    parts = re.split(r"(?<=[.!?…])\s+", protected)
    sentences: list[str] = []
    for part in parts:
        part = part.replace("<DOT>", ".").strip()
        if not part:
            continue
        # A "sentence" with no letters is not prose (e.g. "***").
        if not re.search(r"[A-Za-z]", part):
            continue
        sentences.append(part)
    return sentences


def word_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", text)


def count_words(text: str) -> int:
    return len(word_tokens(text))


def syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    vowels = "aeiouy"
    count = 0
    previous_was_vowel = False
    for ch in w:
        is_vowel = ch in vowels
        if is_vowel and not previous_was_vowel:
            count += 1
        previous_was_vowel = is_vowel
    if w.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def flesch_reading_ease(words: int, sentences: int, syllable_count: int) -> float:
    if words == 0 or sentences == 0:
        return 0.0
    return 206.835 - 1.015 * (words / sentences) - 84.6 * (syllable_count / words)


def dialogue_text(text: str) -> str:
    quoted = " ".join(m.group(0) for m in QUOTE_RE.finditer(text))
    dashed = " ".join(
        line for line in text.splitlines() if DASH_DIALOGUE_RE.match(line)
    )
    return quoted + " " + dashed


def per_1000(count: int, words: int) -> float:
    return round((count / words) * 1000, 2) if words else 0.0


# --------------------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------------------

@dataclass
class Metrics:
    path: str = ""
    words: int = 0
    sentences: int = 0
    paragraphs: int = 0
    mean_sentence: float = 0.0
    median_sentence: float = 0.0
    sd_sentence: float = 0.0
    narration_mean_sentence: float = 0.0
    narration_sd_sentence: float = 0.0
    min_sentence: int = 0
    max_sentence: int = 0
    pct_under_8: float = 0.0
    pct_over_30: float = 0.0
    dialogue_pct: float = 0.0
    filter_per_1000: float = 0.0
    intensifier_per_1000: float = 0.0
    said_bookisms: int = 0
    adverb_tags: int = 0
    exclamations_per_1000: float = 0.0
    semicolons_per_1000: float = 0.0
    em_dashes_per_1000: float = 0.0
    similes_per_1000: float = 0.0
    sensory_per_1000: float = 0.0
    numbers_per_1000: float = 0.0
    question_ratio: float = 0.0
    flesch: float = 0.0
    mean_paragraph_words: float = 0.0
    top_opening: list[tuple[str, int]] = field(default_factory=list)
    cliche_hits: list[dict] = field(default_factory=list)
    dialogue_words: int = 0
    narration_words: int = 0


def analyse(text: str, path: str = "") -> Metrics:
    clean = strip_markdown(text)
    paragraphs = split_paragraphs(clean)

    all_sentences: list[str] = []
    for p in paragraphs:
        all_sentences.extend(split_sentences(p))

    tokens = word_tokens(clean)
    words = len(tokens)
    sentence_lengths = [count_words(s) for s in all_sentences]
    sentence_lengths = [n for n in sentence_lengths if n > 0]

    d_text = dialogue_text(clean)
    d_words = count_words(d_text)
    dialogue_pct = round(100 * d_words / words, 1) if words else 0.0

    # Narration-only sentence statistics. Dialogue fragments distort the mean, so the
    # voice comparison uses narration; dialogue is compared separately as a share.
    narration = QUOTE_RE.sub(" ", clean)
    narration = "\n".join(
        line for line in narration.splitlines() if not DASH_DIALOGUE_RE.match(line)
    )
    narration_lengths: list[int] = []
    for p in split_paragraphs(narration):
        narration_lengths.extend(count_words(s) for s in split_sentences(p))
    narration_lengths = [n for n in narration_lengths if n > 0]
    narration_mean = round(statistics.mean(narration_lengths), 1) if narration_lengths else 0.0
    narration_sd = round(statistics.pstdev(narration_lengths), 1) if len(narration_lengths) > 1 else 0.0

    lower = clean.lower()

    def count_pattern(pattern: str) -> int:
        return len(re.findall(pattern, lower))

    filter_count = sum(count_pattern(rf"\b{re.escape(w)}\b") for w in FILTER_WORDS)
    intensifier_count = sum(count_pattern(rf"\b{re.escape(w)}\b") for w in INTENSIFIERS)
    # Said-bookisms only count as such when they sit in a sentence that also contains
    # dialogue; "she smiled at that" is action, not a tag.
    bookism_count = 0
    for para in split_paragraphs(clean):
        for sent in split_sentences(para):
            if '"' in sent or "\u201c" in sent:
                low_sent = sent.lower()
                bookism_count += sum(
                    len(re.findall(rf"\b{re.escape(w)}\b", low_sent)) for w in SAID_BOOKISMS
                )

    adverb_tags = len(
        re.findall(
            r"\b(said|asked|replied|answered|shouted|whispered|muttered|murmured|"
            r"exclaimed|snapped|hissed|growled)\s+\w+ly\b",
            lower,
        )
    )

    # Figuration proxy: "like a/an/the" and "as ... as" comparisons.
    simile_count = len(
        re.findall(r"\blike\s+(?:a|an|the|some|one)\b", lower)
    ) + len(re.findall(r"\bas\s+\w+\s+as\b", lower))

    sensory_count = sum(1 for t in tokens if t.lower() in SENSORY_WORDS)
    numbers_count = sum(1 for t in tokens if re.fullmatch(r"\d[\d,.:/-]*", t))

    questions = sum(1 for s in all_sentences if s.rstrip().endswith("?"))

    syllable_count = sum(syllables(t) for t in tokens)

    # Repeated sentence openings
    openings: dict[str, int] = {}
    for s in all_sentences:
        m = re.match(r"[A-Za-z']+", s.strip())
        if m:
            key = m.group(0).lower()
            openings[key] = openings.get(key, 0) + 1
    top_opening = sorted(openings.items(), key=lambda kv: (-kv[1], kv[0]))[:5]

    cliche_hits: list[dict] = []
    for name, pattern in CLICHES:
        for m in re.finditer(pattern, lower):
            start = max(0, m.start() - 40)
            end = min(len(clean), m.end() + 40)
            cliche_hits.append(
                {"name": name, "excerpt": clean[start:end].replace("\n", " ").strip()}
            )

    metrics = Metrics(
        path=path,
        words=words,
        sentences=len(sentence_lengths),
        paragraphs=len(paragraphs),
        mean_sentence=round(statistics.mean(sentence_lengths), 1) if sentence_lengths else 0.0,
        median_sentence=round(statistics.median(sentence_lengths), 1) if sentence_lengths else 0.0,
        sd_sentence=round(statistics.pstdev(sentence_lengths), 1) if len(sentence_lengths) > 1 else 0.0,
        narration_mean_sentence=narration_mean,
        narration_sd_sentence=narration_sd,
        min_sentence=min(sentence_lengths) if sentence_lengths else 0,
        max_sentence=max(sentence_lengths) if sentence_lengths else 0,
        pct_under_8=round(100 * sum(1 for n in sentence_lengths if n < 8) / len(sentence_lengths), 1)
        if sentence_lengths else 0.0,
        pct_over_30=round(100 * sum(1 for n in sentence_lengths if n > 30) / len(sentence_lengths), 1)
        if sentence_lengths else 0.0,
        dialogue_pct=dialogue_pct,
        filter_per_1000=per_1000(filter_count, words),
        intensifier_per_1000=per_1000(intensifier_count, words),
        said_bookisms=bookism_count,
        adverb_tags=adverb_tags,
        exclamations_per_1000=round(clean.count("!") / words * 1000, 2) if words else 0.0,
        semicolons_per_1000=round(clean.count(";") / words * 1000, 2) if words else 0.0,
        em_dashes_per_1000=round((clean.count("—") + clean.count("–")) / words * 1000, 2) if words else 0.0,
        similes_per_1000=per_1000(simile_count, words),
        sensory_per_1000=per_1000(sensory_count, words),
        numbers_per_1000=per_1000(numbers_count, words),
        question_ratio=round(questions / len(sentence_lengths), 2) if sentence_lengths else 0.0,
        flesch=round(flesch_reading_ease(words, len(sentence_lengths), syllable_count), 1),
        mean_paragraph_words=round(words / len(paragraphs), 1) if paragraphs else 0.0,
        top_opening=top_opening,
        cliche_hits=cliche_hits,
        dialogue_words=d_words,
        narration_words=max(0, words - d_words),
    )
    return metrics


# --------------------------------------------------------------------------------------
# Voice cards
# --------------------------------------------------------------------------------------

def load_series() -> dict:
    with DATA_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def get_voice(voice_id: str) -> dict:
    data = load_series()
    for card in data["series"]:
        if card["id"].lower() == voice_id.lower():
            return card
    ids = ", ".join(c["id"] for c in data["series"])
    raise SystemExit(f"Unknown voice '{voice_id}'. Available: {ids}")


def targets_from_dials(dials: dict) -> dict:
    """
    Map the 0-10 editorial dials onto measurable surface targets.

    These mappings are deliberately simple and transparent. They are calibration aids,
    not statistical models.
    """
    s = dials.get("sentence_len", 5)
    v = dials.get("variance", 5)
    d = dials.get("dialogue", 5)
    f = dials.get("figuration", 5)
    desc = dials.get("description", 5)
    proc = dials.get("procedure", 5)

    return {
        "narration_mean_sentence": (round(7 + 2.0 * s, 1), 2.5),
        "narration_sd_sentence": (round(3.5 + 0.65 * v, 1), 1.5),
        "dialogue_pct": (round(5 + 6.5 * d, 1), 8.0),
        "similes_per_1000": (round(0.45 * f, 1), 1.0),
        "sensory_per_1000": (round(2 + 1.4 * desc, 1), 8.0),
        "numbers_per_1000": (round(1 + 1.2 * proc, 1), 7.0),
    }


def verdict(draft: float, target: float, tolerance: float) -> str:
    delta = draft - target
    if abs(delta) <= tolerance:
        return "PASS"
    if abs(delta) <= tolerance * 1.75:
        return "NEAR"
    return "OFF"


def comparison_rows(metrics: Metrics, card: dict) -> list[dict]:
    targets = targets_from_dials(card["dials"])
    rows = []
    for key, (target, tol) in targets.items():
        draft = getattr(metrics, key)
        rows.append(
            {
                "metric": key,
                "draft": draft,
                "target": target,
                "tolerance": tol,
                "delta": round(draft - target, 1),
                "verdict": verdict(draft, target, tol),
            }
        )
    return rows


# --------------------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------------------

def fmt_row(row: dict) -> str:
    return (
        f"  {row['metric']:<22} {row['draft']:>8}  {row['target']:>8} ±{row['tolerance']:<5} "
        f"{row['delta']:>+7}   {row['verdict']}"
    )


def print_report(metrics: Metrics, card: dict | None, compare: dict | None) -> None:
    print(f"\n=== {metrics.path or 'input'} ===")
    print(
        f"  words {metrics.words:,} · sentences {metrics.sentences:,} · "
        f"paragraphs {metrics.paragraphs:,} · mean paragraph {metrics.mean_paragraph_words} words"
    )
    print(
        f"  sentence mean {metrics.mean_sentence} · median {metrics.median_sentence} · "
        f"sd {metrics.sd_sentence} · range {metrics.min_sentence}–{metrics.max_sentence}"
    )
    print(
        f"  narration mean {metrics.narration_mean_sentence} · "
        f"narration sd {metrics.narration_sd_sentence}"
    )
    print(
        f"  <8 words {metrics.pct_under_8}% · >30 words {metrics.pct_over_30}% · "
        f"questions {metrics.question_ratio:.0%}"
    )
    print(
        f"  dialogue {metrics.dialogue_pct}% ({metrics.dialogue_words:,} words) · "
        f"narration {metrics.narration_words:,} words"
    )
    print(
        f"  filter {metrics.filter_per_1000}/1k · intensifier {metrics.intensifier_per_1000}/1k · "
        f"adverb tags {metrics.adverb_tags} · said-bookisms {metrics.said_bookisms}"
    )
    print(
        f"  simile {metrics.similes_per_1000}/1k · sensory {metrics.sensory_per_1000}/1k · "
        f"numbers {metrics.numbers_per_1000}/1k"
    )
    print(
        f"  ! {metrics.exclamations_per_1000}/1k · ; {metrics.semicolons_per_1000}/1k · "
        f"— {metrics.em_dashes_per_1000}/1k · Flesch {metrics.flesch}"
    )

    if metrics.top_opening:
        openings = ", ".join(f"{w}×{n}" for w, n in metrics.top_opening)
        print(f"  repeated openings: {openings}")

    if metrics.cliche_hits:
        print(f"\n  CLICHÉ HITS ({len(metrics.cliche_hits)}):")
        for hit in metrics.cliche_hits[:12]:
            print(f"    - {hit['name']}: …{hit['excerpt']}…")
        if len(metrics.cliche_hits) > 12:
            print(f"    … and {len(metrics.cliche_hits) - 12} more")
    else:
        print("\n  CLICHÉ HITS: none")

    if card:
        print(f"\n  VOICE: {card['author']} — {card['series']} ({card['id']})")
        print(f"  {'metric':<24} {'draft':>8}  {'target':>8}    {'delta':>7}   verdict")
        rows = comparison_rows(metrics, card)
        for row in rows:
            print(fmt_row(row))
        print(
            "  (Targets are derived from editorial dials, not corpus statistics. "
            "Read the deltas, not the verdicts.)"
        )

    if compare:
        print(f"\n  COMPARE: {compare['author']} — {compare['series']} ({compare['id']})")
        rows = comparison_rows(metrics, compare)
        for row in rows:
            print(fmt_row(row))


def metrics_to_dict(metrics: Metrics, card: dict | None, compare: dict | None) -> dict:
    out = asdict(metrics)
    if card:
        out["voice"] = {"id": card["id"], "author": card["author"], "series": card["series"]}
        out["comparison"] = comparison_rows(metrics, card)
    if compare:
        out["compare"] = {"id": compare["id"], "author": compare["author"]}
        out["compare_rows"] = comparison_rows(metrics, compare)
    return out


def list_voices() -> None:
    data = load_series()
    print(f"{'id':<16} {'author':<24} {'series'}")
    print("-" * 78)
    for card in data["series"]:
        print(f"{card['id']:<16} {card['author']:<24} {card['series']}")


def read_input(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"File not found: {path}")
    if p.is_dir():
        raise SystemExit(f"Expected a file, got a directory: {path}")
    return p.read_text(encoding="utf-8", errors="replace")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Diagnostic prose metrics for the Noir Prose Bible.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 tools/style_lint.py chapter.md --voice chandler\n"
            "  python3 tools/style_lint.py chapter.md --voice ellroy --compare leonard\n"
            "  python3 tools/style_lint.py --list-voices\n"
        ),
    )
    parser.add_argument("files", nargs="*", help="Manuscript file(s) to analyse (.md or .txt)")
    parser.add_argument("--voice", help="Voice card id (e.g. chandler, ellroy, connelly)")
    parser.add_argument("--compare", help="Second voice card for side-by-side comparison")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a report")
    parser.add_argument("--list-voices", action="store_true", help="List available voice cards")
    args = parser.parse_args(argv)

    if args.list_voices:
        list_voices()
        return 0

    if not args.files:
        parser.print_help()
        return 2

    card = get_voice(args.voice) if args.voice else None
    compare = get_voice(args.compare) if args.compare else None

    results = []
    for path in args.files:
        text = read_input(path)
        metrics = analyse(text, path)
        if args.json:
            results.append(metrics_to_dict(metrics, card, compare))
        else:
            print_report(metrics, card, compare)

    if args.json:
        payload = results[0] if len(results) == 1 else results
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
