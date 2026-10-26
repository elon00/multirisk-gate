"""Documentation claim gate; no synthetic service or cryptography PASS checks."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ClaimIntegrity(unittest.TestCase):
    def test_readme_does_not_claim_production_or_certification(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("not a production", readme.lower())
        for unsupported in ("100/100", "FIPS validated", "RPC Gateway: CONNECTED"):
            self.assertNotIn(unsupported, readme)

    def test_security_scope_is_explicit(self):
        policy = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("not independently audited", policy.lower())
        self.assertIn("no cryptographic implementation", policy.lower())


if __name__ == "__main__":
    unittest.main()
