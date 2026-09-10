from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    "graph-theory-researcher": (
        "Xiaowen Zhang",
        "5a264d4ecf916060d86c4aef32f9686f8c0b7c8e7b45defd69b413fe442aa289",
    ),
    "open-problem-research-pipeline": (
        "Quan Sun",
        "9186e7ffc85a74423504e827c04d9649beb5714eba496e369dd2872b9f287f59",
    ),
}
TEXT_SUFFIXES = {".md", ".py", ".sh", ".yaml", ".yml", ".json", ".txt", ".tex"}


def frontmatter_keys(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        raise AssertionError(f"Missing YAML frontmatter: {path}")
    return {
        line.split(":", 1)[0].strip()
        for line in match.group(1).splitlines()
        if line and not line.startswith((" ", "\t"))
    }


class CourseSkillTests(unittest.TestCase):
    def test_package_shape_and_provenance(self) -> None:
        for package, (contributor, sha256) in PACKAGES.items():
            with self.subTest(package=package):
                root = ROOT / "skills" / package
                for relative in (
                    "README.md",
                    "SKILL.md",
                    "LICENSE",
                    "PROVENANCE.yaml",
                    "NORMALIZATION.md",
                    "agents/openai.yaml",
                ):
                    self.assertTrue((root / relative).is_file(), f"Missing {package}/{relative}")
                self.assertEqual({"name", "description"}, frontmatter_keys(root / "SKILL.md"))
                provenance = (root / "PROVENANCE.yaml").read_text(encoding="utf-8")
                self.assertIn(contributor, provenance)
                self.assertIn(sha256, provenance)
                self.assertIn("license: MIT", provenance)

    def test_nested_pipeline_skills_have_valid_frontmatter(self) -> None:
        root = ROOT / "skills" / "open-problem-research-pipeline" / "skills"
        expected = {
            "literature-search",
            "literature-analysis",
            "literature-proof-framework",
            "qskill",
        }
        self.assertEqual(expected, {path.name for path in root.iterdir() if path.is_dir()})
        for package in expected:
            with self.subTest(package=package):
                self.assertEqual({"name", "description"}, frontmatter_keys(root / package / "SKILL.md"))
                self.assertTrue((root / package / "agents" / "openai.yaml").is_file())

    def test_course_packages_are_portable(self) -> None:
        forbidden = re.compile(r"/Users/|/home/|[A-Za-z]:\\\\|AppleGothic|/System/Library")
        for package in PACKAGES:
            root = ROOT / "skills" / package
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                    with self.subTest(path=path):
                        self.assertIsNone(forbidden.search(path.read_text(encoding="utf-8")))

    def test_pipeline_excludes_generated_outputs_and_has_valid_templates(self) -> None:
        root = ROOT / "skills" / "open-problem-research-pipeline"
        forbidden_suffixes = {".pdf", ".out", ".log"}
        self.assertFalse(
            [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in forbidden_suffixes]
        )
        for template in (root / "skills").glob("*/template.json"):
            with self.subTest(template=template):
                json.loads(template.read_text(encoding="utf-8"))

    def test_pipeline_and_problem_discovery_state_evidence_boundaries(self) -> None:
        pipeline = (ROOT / "skills/open-problem-research-pipeline/SKILL.md").read_text(encoding="utf-8")
        reference = (ROOT / "skills/discover-math-problems/references/extremal-graph-variants.md").read_text(encoding="utf-8")
        self.assertIn("proof obligation", pipeline)
        self.assertIn("Do not claim novelty", pipeline)
        self.assertIn("unverified", reference)
        self.assertIn("不得声称问题是新的", reference)


if __name__ == "__main__":
    unittest.main()
