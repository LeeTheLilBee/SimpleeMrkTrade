"""GRD155: execute the local JS context-isolation test inside source CI.

This is a fully fictional Node VM harness with an in-memory fake DOM and fetch.
It does not start a browser, contact a server or supply real tenant data.
"""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


class BrowserContextTests(unittest.TestCase):
    def test_exact_context_invalidation_and_stale_fetch(self):
        node=shutil.which("node")
        if not node:
            self.skipTest("Node.js unavailable; required in Grounds source CI")
        runner=Path(__file__).parent/"tests_js"/"context_switch.cjs"
        result=subprocess.run(
            [node,str(runner)],capture_output=True,text=True,timeout=15,check=False,
        )
        self.assertEqual(result.returncode,0,
                         result.stdout+"\n"+result.stderr)
        self.assertIn("PASS: immediate scope clearing",result.stdout)


if __name__=="__main__":
    unittest.main()
