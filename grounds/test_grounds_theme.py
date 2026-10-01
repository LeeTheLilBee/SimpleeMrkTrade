"""GRD216–217: lock the final Grounds midnight/gold/aqua visual contract.

These tests are source-level regressions only. They verify palette cohesion and
basic WCAG contrast math for the declared opaque color pairs; they are not a
replacement for human accessibility review on a hosted build.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT=Path(__file__).parent
CSS=(ROOT/"ui"/"app.css").read_text(encoding="utf-8")
HTML=(ROOT/"ui"/"app.html").read_text(encoding="utf-8")


def _rgb(value:str):
    value=value.lstrip("#")
    return tuple(int(value[i:i+2],16)/255 for i in (0,2,4))


def _luminance(value:str)->float:
    def channel(c:float)->float:
        return c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    r,g,b=(channel(c) for c in _rgb(value))
    return .2126*r+.7152*g+.0722*b


def _contrast(a:str,b:str)->float:
    hi,lo=sorted((_luminance(a),_luminance(b)),reverse=True)
    return (hi+.05)/(lo+.05)


class GroundsThemeTests(unittest.TestCase):
    def test_locked_brand_palette_and_browser_theme_color(self):
        expected={
            "--background":"#090d19","--text":"#f1f5fe","--muted":"#adbdd5",
            "--gold":"#e7c684","--gold-light":"#e8cc91","--gold-deep":"#caa15c",
            "--aqua":"#a1e7d4","--danger":"#ff9d9d",
        }
        for token,value in expected.items():
            self.assertIn(token+":"+value,CSS)
        self.assertIn('<meta name="theme-color" content="#090d19">',HTML)
        self.assertIn("linear-gradient(130deg,var(--gold-light),var(--gold-deep))",CSS)
        self.assertIn("background:var(--gold-light);color:#15151e",CSS)
        self.assertNotRegex(CSS,re.compile(r"background\s*:\s*(?:#fff(?:fff)?|white)\b",re.I))

    def test_core_opaque_text_pairs_meet_normal_text_contrast(self):
        pairs=(
            ("#f1f5fe","#090d19"),("#adbdd5","#151d31"),
            ("#e7c684","#090d19"),("#a1e7d4","#090d19"),
            ("#ff9d9d","#422535"),("#15151e","#caa15c"),
        )
        for foreground,background in pairs:
            with self.subTest(foreground=foreground,background=background):
                self.assertGreaterEqual(_contrast(foreground,background),4.5)

    def test_theme_supports_keyboard_reduced_motion_and_high_contrast(self):
        self.assertIn(":focus-visible{outline:3px solid var(--gold)",CSS)
        self.assertIn("@media(prefers-reduced-motion:reduce)",CSS)
        self.assertIn("@media(prefers-contrast:more)",CSS)
        self.assertIn("html.comfortable-type{font-size:115%}",CSS)
        self.assertIn('class="skip-link"',HTML)


if __name__=="__main__":
    unittest.main()
