"""End-to-end check of bin/engine on a throwaway copy of the repo: add, hunt log, defer, release, close.

Run from the repo root:  python3 -m unittest discover -s tests -v
"""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class EngineCliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="grants-cli-"))
        for name in ("bin", "engine", "pipeline", "OWNER-ACTIONS.md", "RULED-OUT.md"):
            src = ROOT / name
            (shutil.copytree if src.is_dir() else shutil.copy)(src, self.tmp / name)
        for f in self.tmp.glob("pipeline/ENGINE-*.json"):
            f.unlink()
        self.key = "https://example.org/pitch-night|2027"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def engine(self, *args, ok=True):
        r = subprocess.run([str(self.tmp / "bin/engine"), *args], cwd=self.tmp, capture_output=True, text=True)
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def packet(self):
        self.engine("prepare", "--lane", "opportunity", "--output", "pipeline/grants-packet.json")
        return json.loads((self.tmp / "pipeline/grants-packet.json").read_text())

    def test_full_lifecycle(self):
        self.assertEqual(self.packet()["counts"]["actionable"], 0)

        added = json.loads(self.engine("add", "--file", "pipeline/examples/candidate.example.json").stdout)
        self.assertEqual(added, {"added": True, "key": self.key})
        dup = json.loads(self.engine("add", "--file", "pipeline/examples/candidate.example.json").stdout)
        self.assertFalse(dup["added"])

        p = self.packet()
        self.assertEqual(p["counts"]["actionable"], 1)
        self.assertEqual(p["candidates"][0]["key"], self.key)

        self.engine("search-result", "--focus", "city pitch nights", "--source", "example.org", "--added", "1", "--reason", "test")
        self.engine("prepare", "--lane", "opportunity-hunt", "--output", "pipeline/grants-hunt.json")
        hunt = json.loads((self.tmp / "pipeline/grants-hunt.json").read_text())
        self.assertIn("example.org", hunt["knownSources"])
        self.assertEqual(hunt["searchHistory"][-1]["focus"], "city pitch nights")

        # A wall (new account needed) defers it; it stays out of the queue.
        self.engine("record", "--key", self.key, "--state", "deferred", "--reason", "user-action: create the portal account")
        p = self.packet()
        self.assertEqual((p["counts"]["actionable"], p["counts"]["deferred"]), (0, 1))

        # Submitting needs a screenshot and confirmation text; a missing file is refused.
        r = self.engine("record", "--key", self.key, "--state", "submitted", "--evidence", "screenshots/missing.png",
                        "--confirmation", "Received", ok=False)
        self.assertNotEqual(r.returncode, 0)

        # The owner did the step: release it with their words as provenance.
        self.engine("record", "--key", self.key, "--state", "needs-browser", "--evidence", "OWNER-ACTIONS.md",
                    "--user-request", "done Example City Pitch Night")
        self.assertEqual(self.packet()["counts"]["actionable"], 1)

        # Then a rule turns out to exclude the business.
        self.engine("record", "--key", self.key, "--state", "closed", "--evidence", "RULED-OUT.md", "--reason", "county residents only")
        p = self.packet()
        self.assertEqual((p["counts"]["actionable"], p["counts"]["closed"]), (0, 1))

    def test_rejects_unverified_lead(self):
        bad = self.tmp / "bad.json"
        bad.write_text(json.dumps({"name": "No source", "sourceUrl": "http://example.org", "category": "grant",
                                   "cycle": "2027", "eligibility": "?", "evidence": [], "openStatus": "open", "effort": "low"}))
        self.assertNotEqual(self.engine("add", "--file", str(bad), ok=False).returncode, 0)


if __name__ == "__main__":
    unittest.main()
