"""Checks for course discovery and generated navigation/content."""

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from mkdocs.exceptions import ConfigurationError


spec = importlib.util.spec_from_file_location("courses_hook", Path(__file__).parents[1] / "hooks/courses.py")
courses = importlib.util.module_from_spec(spec)
spec.loader.exec_module(courses)


class CourseDiscoveryTests(unittest.TestCase):
    def test_empty_and_readme_only_folders_are_coming_soon(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Empty course").mkdir()
            overview = root / "Overview only"
            overview.mkdir()
            (overview / "README.md").write_text("# Overview only\n")
            (overview / ".gitkeep").touch()
            (root / ".hidden").mkdir()
            found = courses.discover_courses(root)
            self.assertEqual(len(found), 2)
            self.assertTrue(all(not course["lessons"] for course in found))
            self.assertTrue(all("Coming soon" in courses.course_overview(course) for course in found))

    def test_formats_are_grouped_and_lessons_are_naturally_sorted(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root / "Example course"
            directory.mkdir()
            (directory / "Lesson_10.md").write_text("# Later lesson\n")
            (directory / "Lesson_2.md").write_text("# Earlier lesson\n")
            (directory / "Lesson_2.pdf").write_bytes(b"PDF")
            (directory / "Lesson_2.docx").write_bytes(b"DOCX")
            (directory / "diagram.png").write_bytes(b"image")
            course = courses.discover_courses(root)[0]
            self.assertEqual([lesson["title"] for lesson in course["lessons"]], ["Earlier lesson", "Later lesson"])
            self.assertEqual(set(course["lessons"][0]["formats"]), {".md", ".pdf", ".docx"})
            self.assertIn('href="downloads/Lesson_2.md" download', courses.course_overview(course))

    def test_new_and_removed_courses_refresh_navigation_on_each_build(self):
        class Config(dict):
            pass
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "courses").mkdir()
            config = Config(extra={})
            config.config_file_path = str(root / "mkdocs.yml")
            courses.on_pre_build(config)
            self.assertEqual(config["nav"], [{"Home": "index.md"}])
            added = root / "courses" / "New course"
            added.mkdir()
            courses.on_pre_build(config)
            self.assertEqual(config["extra"]["courses"][0]["title"], "New course")
            self.assertIn("Courses", config["nav"][1])
            added.rmdir()
            courses.on_pre_build(config)
            self.assertEqual(config["nav"], [{"Home": "index.md"}])

    def test_optional_metadata_preserves_course_urls_and_authored_sections(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root / "A long folder name"
            directory.mkdir()
            (directory / "README.md").write_text('---\ntitle: Friendly name\nslug: stable-url\ndescription: Short summary\n---\n# Old title\n\n## Lessons\n\nOld table\n\n<details>References</details>\n')
            (directory / "new.md").write_text("# New lesson\n")
            course = courses.discover_courses(root)[0]
            self.assertEqual(course["slug"], "stable-url")
            self.assertEqual(course["description"], "Short summary")
            rendered = courses.course_overview(course)
            self.assertIn("# Friendly name", rendered)
            self.assertIn("New lesson", rendered)
            self.assertNotIn("Old table", rendered)
            self.assertIn("<details>References</details>", rendered)

    def test_pdf_only_courses_have_downloads_and_no_invalid_nav_pages(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root / "PDF course"
            directory.mkdir()
            (directory / "Lesson.pdf").write_bytes(b"PDF")
            course = courses.discover_courses(root)[0]
            self.assertEqual(len(course["lessons"]), 1)
            self.assertIn('href="Lesson.pdf" download', courses.course_overview(course))

    def test_ambiguous_slugs_fail_instead_of_overwriting_courses(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "AI & ML").mkdir()
            (root / "AI ML").mkdir()
            with self.assertRaises(ConfigurationError):
                courses.discover_courses(root)

    def test_generated_cards_escape_folder_names(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "AI <examples>").mkdir()
            config = {"extra": {"courses": courses.discover_courses(root)}}
            page = SimpleNamespace(file=SimpleNamespace(src_uri="index.md"))
            rendered = courses.on_page_markdown("<!-- course-cards -->", page, config)
            self.assertIn("AI &lt;examples&gt;", rendered)
            self.assertNotIn("AI <examples>", rendered)
            self.assertIn("Coming soon", rendered)


if __name__ == "__main__":
    unittest.main()
