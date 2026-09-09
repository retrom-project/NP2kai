"""Negative release identity and asset checks; never publish from tests."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("release", Path(__file__).with_name("build-release.py"))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
FORK = json.loads((ROOT / "retrom-fork.json").read_text())
COMMIT = "a" * 40
TAG = "retrom-core-g5939e0c6d598-r1"

class ReleaseTests(unittest.TestCase):
    def test_clean_fixed_identity(self):
        with patch.object(release, "git", side_effect=[COMMIT, ""]):
            release.validate_identity(FORK["forkRepository"], TAG, COMMIT, FORK)

    def test_wrong_repository(self):
        with self.assertRaisesRegex(ValueError, "RELEASE_REPOSITORY_INVALID"):
            release.validate_identity("https://github.com/AZO234/NP2kai", TAG, COMMIT, FORK)

    def test_retired_or_other_baseline_tags(self):
        for tag in ["latest", "rpg-runtime-v1", "retrom-core-g123456789012-r1", TAG + "-rc.0"]:
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, "RELEASE_TAG_INVALID"):
                release.validate_identity(FORK["forkRepository"], tag, COMMIT, FORK)

    def test_wrong_commit(self):
        with patch.object(release, "git", return_value="b" * 40), self.assertRaisesRegex(ValueError, "RELEASE_COMMIT_INVALID"):
            release.validate_identity(FORK["forkRepository"], TAG, COMMIT, FORK)

    def test_dirty_source(self):
        with patch.object(release, "git", side_effect=[COMMIT, " M file"]), self.assertRaisesRegex(ValueError, "RELEASE_SOURCE_DIRTY"):
            release.validate_identity(FORK["forkRepository"], TAG, COMMIT, FORK)

    def test_incomplete_assets(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(ValueError, "RELEASE_ASSETS_INVALID"):
            release.finalize(Path(directory), FORK["forkRepository"], TAG, COMMIT, FORK)

if __name__ == "__main__":
    unittest.main()
