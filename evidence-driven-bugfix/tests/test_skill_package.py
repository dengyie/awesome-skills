import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class EvidenceDrivenBugfixPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "workflow-contract.md",
            ROOT / "references" / "symptom-capture.md",
            ROOT / "references" / "failing-evidence-gate.md",
            ROOT / "references" / "root-cause-investigation.md",
            ROOT / "references" / "minimal-fix-plan.md",
            ROOT / "references" / "fresh-verification-gate.md",
            ROOT / "references" / "truthful-completion.md",
            ROOT / "references" / "manual-required-and-external-blockers.md",
            ROOT / "references" / "output-contract.md",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_core_rules_are_present(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: evidence-driven-bugfix", frontmatter)
        self.assertIn("evidence-first diagnosis", frontmatter)
        self.assertIn("NO FIX WITHOUT FAILING EVIDENCE", skill_text)
        self.assertIn("NO ROOT-CAUSE GAP HIDDEN BY A SYMPTOM FIX", skill_text)
        self.assertIn("NO SUCCESS CLAIM WITHOUT FRESH VERIFICATION EVIDENCE", skill_text)
        self.assertIn("Manual-required", skill_text)
        self.assertIn("Proven-external-blocker", skill_text)

    def test_references_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference_paths = sorted(set(re.findall(r"`(references/[^`]+\.md)`", skill_text)))

        self.assertGreaterEqual(len(reference_paths), 8)
        missing = [path for path in reference_paths if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_skill_entrypoint_defines_states_gates_and_looping(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        for expected in [
            "Investigating",
            "Reproduced",
            "Root-caused",
            "Fixing",
            "Verifying",
            "Fixed",
            "Manual-required",
            "Proven-external-blocker",
            "Symptom Capture",
            "Failing Evidence Gate",
            "Root Cause Investigation",
            "Minimal Fix Plan",
            "Fresh Verification Gate",
            "Truthful Completion Gate",
        ]:
            self.assertIn(expected, skill_text)

        self.assertIn("continue the loop until the bug is fixed", skill_text.lower())
        self.assertIn("No failing evidence means no implementation", skill_text)
        self.assertIn("If fresh verification fails, return to investigation", skill_text)

    def test_truthful_completion_and_output_contract_are_documented(self):
        truthful = (ROOT / "references" / "truthful-completion.md").read_text(encoding="utf-8")
        blockers = (
            ROOT / "references" / "manual-required-and-external-blockers.md"
        ).read_text(encoding="utf-8")
        output = (ROOT / "references" / "output-contract.md").read_text(encoding="utf-8")

        self.assertIn('Do not say:', truthful)
        self.assertIn('"should be fixed"', truthful)
        self.assertIn('"probably solved"', truthful)
        self.assertIn("Use only when evidence shows", blockers)
        self.assertIn("Current state", output)
        self.assertIn("Fresh verification", output)

    def test_failing_evidence_contract_rejects_non_replayable_artifacts(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        failing_gate = (
            ROOT / "references" / "failing-evidence-gate.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Screenshots and recordings may support symptom capture", skill_text)
        self.assertIn("cannot pass this gate by themselves", skill_text)
        self.assertIn("replayable or re-checkable failure signal", failing_gate)
        self.assertIn("Screenshots or recordings alone are supporting context", failing_gate)
        self.assertIn("not failing evidence by themselves", failing_gate)

    def test_skill_prefers_regression_test_when_repro_can_be_automated(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        fresh_gate = (
            ROOT / "references" / "fresh-verification-gate.md"
        ).read_text(encoding="utf-8")
        usage = (ROOT.parent / "docs" / "usage" / "evidence-driven-bugfix.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "When a stable repro can reasonably be automated, convert it into a failing regression test before or alongside the fix.",
            skill_text,
        )
        self.assertIn(
            "prefer the automated regression test as the long-term verification path",
            fresh_gate,
        )
        self.assertIn("turn it into an automated regression test when feasible", usage)


if __name__ == "__main__":
    unittest.main()
