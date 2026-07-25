import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from analysis.design_p2 import verify_learning_artifact


def identity(path: Path) -> dict:
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


class ProvenanceContractTests(unittest.TestCase):
    def test_learning_artifact_must_match_bundle_and_manifest(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            parquet = root / "parquet"
            output = root / "output"
            parquet.mkdir()
            output.mkdir()
            inputs = []
            for name in [
                "matches.parquet",
                "participants.parquet",
                "participant_timelines.parquet",
            ]:
                path = parquet / name
                path.write_bytes(name.encode())
                inputs.append(identity(path))
            learning = output / "mastery_learning.csv"
            learning.write_text("champion,learning_slope\nA,0.1\n")
            manifest = output / "mastery_learning.run.json"
            manifest.write_text(
                json.dumps({"inputs": inputs, "outputs": [identity(learning)]})
            )

            self.assertEqual(verify_learning_artifact(learning, parquet), manifest)
            (parquet / "participants.parquet").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "input mismatch"):
                verify_learning_artifact(learning, parquet)


if __name__ == "__main__":
    unittest.main()
