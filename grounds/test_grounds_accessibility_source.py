"""GRD194–197: deterministic source-level accessibility/privacy guardrails.

This is NOT an automated assistive technology or jurisdictional accessibility
certification. The final actual hosted browser/screenreader/keyboard review is
still required for real tenant release.
"""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

UI=Path(__file__).parent/"ui"


class DocumentStructure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.targets=[]
        self.labels=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if "aria-labelledby" in a:
            self.targets.extend(a["aria-labelledby"].split())
        if tag=="label" and "for" in a:
            self.labels.append(a["for"])


def _rgb(hex_value):
    digits=hex_value.removeprefix("#")
    return tuple(int(digits[i:i+2],16)/255 for i in (0,2,4))


def _luminance(hex_value):
    channel=lambda c:c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
    r,g,b=map(channel,_rgb(hex_value))
    return .2126*r+.7152*g+.0722*b


def _contrast(a,b):
    high,low=sorted((_luminance(a),_luminance(b)),reverse=True)
    return (high+.05)/(low+.05)


class SourceExperienceAccessTests(unittest.TestCase):
    def test_landmarks_form_labels_focus_and_reduced_motion(self):
        html=(UI/"app.html").read_text(encoding="utf-8")
        css=(UI/"app.css").read_text(encoding="utf-8")
        parser=DocumentStructure()
        parser.feed(html)
        self.assertIn("main",parser.ids)
        self.assertIn('href="#main"',html)
        self.assertIn('aria-live="polite"',html)
        self.assertTrue(set(parser.targets).issubset(parser.ids))
        self.assertTrue(set(parser.labels).issubset(parser.ids))
        for panel in ("my-home","move","daily","delivery","property-health","owner-portfolio"):
            self.assertIn(panel+"-panel",parser.ids)
        self.assertIn('id="text-size-toggle"',html)
        self.assertIn('aria-pressed="false"',html)
        self.assertIn(":focus-visible",css)
        self.assertIn("prefers-reduced-motion",css)
        self.assertIn(".comfortable-type",css)
        self.assertIn("color-scheme:dark",css)
        self.assertNotIn("Nothing is due based on this screen",html)

    def test_source_colors_have_readable_base_and_muted_contrast(self):
        css=(UI/"app.css").read_text(encoding="utf-8")
        colors=dict(re.findall(r"--(background|text|muted):(#(?:[0-9a-fA-F]{6}))",css))
        self.assertGreaterEqual(_contrast(colors["background"],colors["text"]),7)
        self.assertGreaterEqual(_contrast(colors["background"],colors["muted"]),4.5)

    def test_private_server_data_uses_text_not_raw_html_or_storage(self):
        script=(UI/"app.js").read_text(encoding="utf-8")
        self.assertNotIn("innerHTML",script)
        self.assertNotIn("outerHTML",script)
        self.assertNotIn("localStorage",script)
        self.assertNotIn("sessionStorage",script)
        self.assertIn("textContent",script)
        self.assertIn("verifyWorkspaceContext",script)
        self.assertIn("clearPrivateView",script)
        self.assertIn("X-Grounds-CSRF",script)
        self.assertIn("X-Grounds-Idempotency-Key",script)


if __name__=="__main__":
    unittest.main()
