"""Check HTML diagrams at MkDocs page URLs and preserve offline source paths."""

from types import SimpleNamespace
import unittest

from mkdocs.structure.files import File, Files

from hooks.images import on_page_content


class ImagePathTests(unittest.TestCase):
    def render(self, html, directory_urls=True):
        source = "courses/langgraph/Video_01/Video_01.md"
        paths = [source, "courses/langgraph/Video_01/images/diagram.png",
                 "courses/langgraph/Video_01/images/with space.png"]
        files = Files([File(path, "/docs", "/site", directory_urls) for path in paths])
        note = files.get_file_from_path(source)
        page = SimpleNamespace(file=note, url=note.url)
        return on_page_content(html, page, files)

    def test_html_images_resolve_from_source_with_presentation_preserved(self):
        html = ('<h1>Lesson</h1>\n<p align="center">'
                '<img src="images/diagram.png" alt="Original diagram" width="560"></p>\n'
                '<img src=images/diagram.png width=300/>')
        rendered = self.render(html)
        self.assertIn('src="../images/diagram.png" alt="Original diagram" width="560"', rendered)
        self.assertIn('src="../images/diagram.png" width=300/>', rendered)
        self.assertIn('<p align="center">', rendered)

    def test_encoded_paths_query_and_fragment_are_preserved(self):
        html = '<img src="images/with%20space.png?size=2&amp;v=1#figure">'
        self.assertEqual(self.render(html), '<img src="../images/with%20space.png?size=2&amp;v=1#figure">')

    def test_only_the_src_attribute_changes(self):
        html = '<img data-src="placeholder.png" alt="Example src=foo" SRC=\'images/diagram.png\'>'
        self.assertEqual(self.render(html), '<img data-src="placeholder.png" alt="Example src=foo" src="../images/diagram.png">')

    def test_already_resolved_markdown_images_are_unchanged(self):
        html = '<img src="../images/diagram.png" alt="Markdown image">'
        self.assertEqual(self.render(html), html)

    def test_external_root_missing_and_escaped_example_images_are_unchanged(self):
        html = ('<img src="https://example.com/diagram.png">'
                '<img src="//example.com/diagram.png">'
                '<img src="/assets/diagram.png"><img src="data:image/png;base64,abc">'
                '<img src="missing.png"><img src="Video_01.md">'
                '<pre>&lt;img src="images/diagram.png"&gt;</pre>')
        self.assertEqual(self.render(html), html)

    def test_flat_page_urls_keep_working_source_paths(self):
        html = '<img src="images/diagram.png" width="560">'
        self.assertEqual(self.render(html, directory_urls=False), html)


if __name__ == "__main__":
    unittest.main()
