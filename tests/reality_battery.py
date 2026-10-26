"""Real subprocess regressions for the local Rust risk-policy CLI.

This is NOT a restaking security audit, live validator monitor, or FIPS test.
"""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def run_policy(*args):
    return subprocess.run(
        ["cargo", "run", "--quiet", "--", *args],
        cwd=ROOT, text=True, capture_output=True, timeout=120,
        check=False,
    )


class LocalPolicyIntegration(unittest.TestCase):
    def test_allow_when_conservative_loss_within_limit(self):
        result = run_policy("--exposure-bps", "7500", "--slash-bps", "1000",
                            "--max-loss-bps", "800")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("LOSS_BPS=750", result.stdout)
        self.assertIn("POLICY_DECISION=ALLOW", result.stdout)

    def test_block_when_conservative_loss_exceeds_limit(self):
        result = run_policy("--exposure-bps", "7500", "--slash-bps", "1000",
                            "--max-loss-bps", "700")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("POLICY_DECISION=BLOCK", result.stdout)

    def test_round_up_tiny_loss_and_block_zero_limit(self):
        result = run_policy("--exposure-bps", "1", "--slash-bps", "1",
                            "--max-loss-bps", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("LOSS_BPS=1", result.stdout)
        self.assertIn("POLICY_DECISION=BLOCK", result.stdout)

    def test_zero_exposure_and_upper_bound(self):
        for exposure, slash, expected in [
            ("0", "10000", "0"), ("10000", "10000", "10000")
        ]:
            with self.subTest(exposure=exposure, slash=slash):
                result = run_policy("--exposure-bps", exposure,
                                    "--slash-bps", slash, "--max-loss-bps", "10000")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"LOSS_BPS={expected}", result.stdout)

    def test_bad_inputs_fail_closed(self):
        valid = ("--exposure-bps", "7500", "--slash-bps", "1000",
                 "--max-loss-bps", "800")
        bad_cases = [
            (), ("--unknown", "1"), ("--exposure-bps",),
            ("--exposure-bps", "10001", "--slash-bps", "1", "--max-loss-bps", "1"),
            ("--exposure-bps", "-1", "--slash-bps", "1", "--max-loss-bps", "1"),
            ("--exposure-bps", "1;echo", "--slash-bps", "1", "--max-loss-bps", "1"),
            valid + ("--exposure-bps", "1"),
        ]
        for args in bad_cases:
            with self.subTest(args=args):
                result = run_policy(*args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("INPUT_REJECTED:", result.stderr)
                self.assertNotIn("POLICY_DECISION=ALLOW", result.stdout)

    def test_explicitly_disclaims_network_and_certification(self):
        result = run_policy("--exposure-bps", "7500", "--slash-bps", "1000",
                            "--max-loss-bps", "800")
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in (
            "MODEL_SCOPE=LOCAL_DETERMINISTIC_POLICY_ONLY",
            "IMPLEMENTATION_STATUS=PARTIAL_LOCAL_POLICY",
            "SECURITY_APPROVED=NO", "DEPLOYMENT_READY=NO",
            "NETWORK_STATUS=NOT_CONNECTED",
        ):
            self.assertIn(expected, result.stdout)
        self.assertNotIn("100/100", result.stdout)
        self.assertNotIn("FIPS", result.stdout)


if __name__ == "__main__":
    unittest.main()
