import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_SKILL = ROOT / ".agents" / "skills" / "paichecker" / "SKILL.md"
CLAUDE_SKILL = ROOT / ".claude" / "skills" / "paichecker" / "SKILL.md"


class SkillSyncTest(unittest.TestCase):
    def test_codex_and_claude_skills_are_identical(self) -> None:
        self.assertEqual(
            CODEX_SKILL.read_bytes(),
            CLAUDE_SKILL.read_bytes(),
            "Codex and Claude Code must share the same PAIChecker behavior",
        )


if __name__ == "__main__":
    unittest.main()
