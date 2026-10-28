"""Check that Markdown downloads are self-contained offline bundles."""

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from mkdocs.exceptions import PluginError


spec = importlib.util.spec_from_file_location("downloads_hook", Path(__file__).parents[1] / "hooks/downloads.py")
downloads = importlib.util.module_from_spec(spec)
spec.loader.exec_module(downloads)
CONFIG = {"markdown_extensions": ["fenced_code", "attr_list"], "mdx_configs": {}}


class WhiteWordDownloadTests(unittest.TestCase):
    def test_white_pages_dark_defaults_and_preserved_contents(self):
        namespace = downloads.WORD_NS
        document = f'''<w:document xmlns:w="{namespace}" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" mc:Ignorable="w14"><w:background w:color="111111" w:themeColor="dark1"><fill/></w:background><w:body><w:p><w:r><w:t>Original notes</w:t></w:r></w:p></w:body></w:document>'''
        styles = f'''<w:styles xmlns:w="{namespace}"><w:docDefaults><w:rPrDefault><w:rPr><w:color w:val="FFFFFF" w:themeColor="light1"/></w:rPr></w:rPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:rPr><w:color w:val="FFFFFF" w:themeColor="light1"/><w:sz w:val="22"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:rPr><w:color w:val="123456"/></w:rPr></w:style></w:styles>'''
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.docx"
            with ZipFile(source, "w") as archive:
                archive.writestr("word/document.xml", document)
                archive.writestr("word/styles.xml", styles)
                archive.writestr("word/media/image1.png", b"original image bytes")
                archive.writestr("word/_rels/document.xml.rels", b"original relationships")
            original = source.read_bytes()
            target = root / "published/note.docx"
            downloads.white_docx(source, target)
            self.assertEqual(source.read_bytes(), original)
            with ZipFile(target) as archive:
                ns = {"w": namespace}
                rendered = ET.fromstring(archive.read("word/document.xml"))
                self.assertEqual(rendered.find("w:background", ns).attrib, {f"{{{namespace}}}color": "FFFFFF"})
                self.assertEqual(rendered.find(".//w:t", ns).text, "Original notes")
                self.assertIn(b'xmlns:w14=', archive.read("word/document.xml"))
                defaults = ET.fromstring(archive.read("word/styles.xml"))
                for path in ("w:docDefaults/w:rPrDefault/w:rPr/w:color", 'w:style[@w:styleId="Normal"]/w:rPr/w:color'):
                    self.assertEqual(defaults.find(path, ns).attrib, {f"{{{namespace}}}val": "202020"})
                self.assertEqual(defaults.find('w:style[@w:styleId="Heading1"]/w:rPr/w:color', ns).get(f"{{{namespace}}}val"), "123456")
                self.assertEqual(archive.read("word/media/image1.png"), b"original image bytes")
                self.assertEqual(archive.read("word/_rels/document.xml.rels"), b"original relationships")

    def test_missing_background_and_text_defaults_are_added(self):
        namespace = downloads.WORD_NS
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.docx"
            with ZipFile(source, "w") as archive:
                archive.writestr("word/document.xml", f'<w:document xmlns:w="{namespace}"><w:body/></w:document>')
                archive.writestr("word/styles.xml", f'<w:styles xmlns:w="{namespace}"/>')
            target = root / "white.docx"
            downloads.white_docx(source, target)
            with ZipFile(target) as archive:
                document = ET.fromstring(archive.read("word/document.xml"))
                self.assertEqual(document[0].tag, f"{{{namespace}}}background")
                self.assertEqual(document[0].get(f"{{{namespace}}}color"), "FFFFFF")
                styles = ET.fromstring(archive.read("word/styles.xml"))
                self.assertEqual(styles.find(f'.//{{{namespace}}}color').get(f"{{{namespace}}}val"), "202020")


class MarkdownBundleTests(unittest.TestCase):
    def test_bundles_inline_reference_and_html_images_with_original_paths(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            images = root / "Images"
            images.mkdir()
            for name in ("inline.png", "reference.png", "with space.svg"):
                (images / name).write_bytes(name.encode())
            note = root / "Lesson.md"
            text = '# Lesson\n\n![Inline](Images/inline.png)\n\n![Reference][diagram]\n\n[diagram]: Images/reference.png\n\n<img src="Images/with%20space.svg">\n\n```markdown\n![Example only](missing.png)\n```\n'
            note.write_text(text)
            (root / "Lesson.pdf").write_bytes(b"not included")
            target = root / "downloads/lesson.zip"
            downloads.bundle_markdown(note, root, target, CONFIG)
            with ZipFile(target) as archive:
                self.assertEqual(set(archive.namelist()), {
                    "Lesson/Lesson.md", "Lesson/Images/inline.png",
                    "Lesson/Images/reference.png", "Lesson/Images/with space.svg",
                })
                self.assertEqual(archive.read("Lesson/Lesson.md"), note.read_bytes())
                self.assertEqual(archive.read("Lesson/Images/inline.png"), b"inline.png")

    def test_shared_images_keep_parent_relative_paths_working(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "lesson").mkdir()
            (root / "images").mkdir()
            note = root / "lesson/Note.md"
            note.write_text('# Note\n\n![Shared](../images/shared.png)\n')
            (root / "images/shared.png").write_bytes(b"shared")
            target = root / "note.zip"
            downloads.bundle_markdown(note, root, target, CONFIG)
            with ZipFile(target) as archive:
                self.assertEqual(set(archive.namelist()), {"Note/lesson/Note.md", "Note/images/shared.png"})
                extracted = root / "extracted"
                archive.extractall(extracted)
                self.assertTrue((extracted / "Note/lesson" / "../images/shared.png").is_file())

    def test_notes_without_local_images_still_download(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            note = root / "Note.markdown"
            note.write_text('# Note\n\n![Remote](https://example.com/image.png)\n')
            target = root / "note.zip"
            downloads.bundle_markdown(note, root, target, CONFIG)
            with ZipFile(target) as archive:
                self.assertEqual(archive.namelist(), ["Note/Note.markdown"])

    def test_missing_image_fails_instead_of_shipping_a_broken_note(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            note = root / "Note.md"
            note.write_text('# Note\n\n![Missing](missing.png)\n')
            with self.assertRaisesRegex(PluginError, "was not found"):
                downloads.bundle_markdown(note, root, root / "note.zip", CONFIG)

    def test_images_outside_the_course_are_not_published(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            course = root / "course"
            course.mkdir()
            note = course / "Note.md"
            note.write_text('# Note\n\n![Outside](../outside.png)\n')
            (root / "outside.png").write_bytes(b"outside")
            with self.assertRaisesRegex(PluginError, "outside its course folder"):
                downloads.bundle_markdown(note, course, root / "note.zip", CONFIG)


if __name__ == "__main__":
    unittest.main()
