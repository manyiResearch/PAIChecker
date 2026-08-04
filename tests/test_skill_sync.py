import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_SKILL = ROOT / ".agents" / "skills" / "paichecker"
CLAUDE_SKILL = ROOT / ".claude" / "skills" / "paichecker"


def _skill_files(root: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


class SkillSyncTest(unittest.TestCase):
    def test_codex_and_claude_skill_trees_are_identical(self) -> None:
        self.assertEqual(
            _skill_files(CODEX_SKILL),
            _skill_files(CLAUDE_SKILL),
            "Codex and Claude Code must share the same PAIChecker files and behavior",
        )


if __name__ == "__main__":
    unittest.main()
