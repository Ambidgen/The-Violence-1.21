#!/usr/bin/env python3
"""Tests for style_lint.py. Run: python3 tools/test_style_lint.py"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import style_lint as sl  # noqa: E402


class SentenceSplitterTests(unittest.TestCase):
    def test_does_not_split_abbreviations(self):
        text = "Mr. Smith met Dr. Jones at 5 p.m. on Monday. They talked."
        sentences = sl.split_sentences(text)
        self.assertEqual(len(sentences), 2)
        self.assertTrue(sentences[0].startswith("Mr. Smith"))

    def test_does_not_split_initials(self):
        text = "J. Edgar Hoover ran the Bureau. He was feared."
        sentences = sl.split_sentences(text)
        self.assertEqual(len(sentences), 2)

    def test_handles_ellipsis_and_question(self):
        text = "He waited... She did not come? He left."
        sentences = sl.split_sentences(text)
        self.assertEqual(len(sentences), 3)

    def test_ignores_non_letter_fragments(self):
        text = "***"
        self.assertEqual(sl.split_sentences(text), [])

    def test_multi_dot_abbreviation_is_protected(self):
        text = "He left at 5 p.m. She stayed until 7 p.m. Nobody called."
        self.assertEqual(len(sl.split_sentences(text)), 3)


class MetricsTests(unittest.TestCase):
    dialogue_heavy = (
        '"You brought a gun to a wedding."\n\n'
        '"I brought a gun to a wedding," Vince said. "I didn\'t bring it out at the wedding."\n\n'
        '"The difference is a felony."\n\n'
        '"The difference is manners."\n'
    )

    lyric = (
        "The rain had stopped by morning, and the bayou was the colour of old copper, and the "
        "cypress roots stood in the water like the ribs of something that had died a long time "
        "ago. I drank my coffee on the gallery. A blue heron lifted off the far bank. I thought "
        "about the girl in the photograph.\n"
    )

    def test_dialogue_ratio_is_high_for_dialogue(self):
        m = sl.analyse(self.dialogue_heavy, "d.md")
        self.assertGreater(m.dialogue_pct, 60)
        self.assertGreater(m.dialogue_words, 0)

    def test_dialogue_ratio_is_low_for_narration(self):
        m = sl.analyse(self.lyric, "l.md")
        self.assertLess(m.dialogue_pct, 15)

    def test_sentence_stats_are_sane(self):
        m = sl.analyse(self.lyric, "l.md")
        self.assertGreater(m.words, 40)
        self.assertGreaterEqual(m.sentences, 4)
        self.assertGreater(m.mean_sentence, 5)
        self.assertGreaterEqual(m.max_sentence, m.min_sentence)
        self.assertGreaterEqual(m.sd_sentence, 0)

    def test_cliche_detection(self):
        m = sl.analyse("A chill ran down his spine. All hell broke loose.", "c.md")
        names = {hit["name"] for hit in m.cliche_hits}
        self.assertIn("chill down spine", names)
        self.assertIn("all hell broke loose", names)

    def test_said_bookism_requires_dialogue_context(self):
        action = sl.analyse("She smiled at the window and said nothing.")
        self.assertEqual(action.said_bookisms, 0)

        tag = sl.analyse('"Come in," he smiled.')
        self.assertEqual(tag.said_bookisms, 1)

    def test_narration_metrics_exclude_dialogue(self):
        text = (
            "The corridor was long and the carpet had been worn pale down the middle by thirty years "
            "of men walking the same eight feet between the elevator and the door.\n\n"
            '"No," he said.\n\n"No."\n\n"No."'
        )
        m = sl.analyse(text)
        self.assertGreater(m.narration_mean_sentence, m.mean_sentence)
        self.assertGreater(m.dialogue_pct, 0)

    def test_adverb_tag_detection(self):
        m = sl.analyse('"I did not," he said defensively.', "a.md")
        self.assertEqual(m.adverb_tags, 1)

    def test_said_bookism_detection(self):
        m = sl.analyse('"Indeed," he opined.', "s.md")
        self.assertEqual(m.said_bookisms, 1)

    def test_filter_words(self):
        m = sl.analyse("She saw the door. He heard the shot. I felt nothing.", "f.md")
        self.assertGreaterEqual(m.filter_per_1000, 1)

    def test_flesch_range(self):
        m = sl.analyse("The cat sat on the mat. The dog ran. It was a good day.", "e.md")
        self.assertGreater(m.flesch, 60)

    def test_markdown_is_stripped(self):
        raw = "# Heading\n\n**Bold** text with [a link](https://example.com).\n\n> Quote.\n"
        clean = sl.strip_markdown(raw)
        self.assertNotIn("#", clean)
        self.assertNotIn("**", clean)
        self.assertNotIn("https", clean)
        self.assertIn("Bold", clean)
        self.assertIn("a link", clean)

    def test_json_serialisable(self):
        m = sl.analyse(self.lyric, "l.md")
        card = sl.get_voice("burke")
        payload = sl.metrics_to_dict(m, card, None)
        json.dumps(payload)  # must not raise
        self.assertEqual(payload["voice"]["id"], "burke")


class VoiceCardTests(unittest.TestCase):
    def test_all_twenty_cards_load(self):
        data = sl.load_series()
        self.assertEqual(len(data["series"]), 20)
        ids = {card["id"] for card in data["series"]}
        self.assertIn("hammett", ids)
        self.assertIn("nesbo", ids)

    def test_targets_are_positive(self):
        card = sl.get_voice("chandler")
        targets = sl.targets_from_dials(card["dials"])
        for key, (target, tolerance) in targets.items():
            self.assertGreater(target, 0, key)
            self.assertGreater(tolerance, 0, key)

    def test_hammett_has_lower_dialogue_target_than_leonard(self):
        h = sl.targets_from_dials(sl.get_voice("hammett")["dials"])
        l = sl.targets_from_dials(sl.get_voice("leonard")["dials"])
        self.assertLess(h["dialogue_pct"][0], l["dialogue_pct"][0])


class CliTests(unittest.TestCase):
    def test_cli_runs_and_emits_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "sample.md"
            sample.write_text(
                'The file was on the table. "I did not kill him," she said.\n',
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(Path(sl.__file__)), str(sample), "--voice", "connelly", "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("metrics", payload) if "metrics" in payload else None
            self.assertEqual(payload["voice"]["id"], "connelly")
            self.assertIn("comparison", payload)

    def test_unknown_voice_fails_cleanly(self):
        result = subprocess.run(
            [sys.executable, str(Path(sl.__file__)), "README.md", "--voice", "nope"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown voice", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
