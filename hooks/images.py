"""Resolve source-relative HTML images without modifying downloadable notes."""

from html import escape
from html.parser import HTMLParser
import posixpath
import re
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit

from mkdocs.utils import get_relative_url


class ImagePaths(HTMLParser):
    def __init__(self, html, page, files):
        super().__init__()
        self.page = page
        self.files = files
        self.destinations = {file.dest_uri for file in files}
        self.line_offsets = [0, *(match.end() for match in re.finditer("\n", html))]
        self.changes = []

    def handle_starttag(self, tag, attrs):
        if tag != "img":
            return
        source = dict(attrs).get("src")
        if not source:
            return
        url = urlsplit(source)
        if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
            return
        # Markdown images already point at their published destination.
        rendered_path = posixpath.normpath(unquote(urljoin(self.page.url, url.path)))
        if rendered_path in self.destinations:
            return
        source_path = posixpath.normpath(posixpath.join(
            posixpath.dirname(self.page.file.src_uri), unquote(url.path),
        ))
        image = self.files.get_file_from_path(source_path)
        if image is None or not image.is_media_file():
            return
        target = urlunsplit(("", "", get_relative_url(image.url, self.page.url), url.query, url.fragment))
        original = self.get_starttag_text()
        # Consume complete attributes so alt text and data-src stay untouched.
        for attribute in re.finditer(
            r'''(?P<name>[\w:-]+)\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)''', original,
        ):
            if attribute.group("name").casefold() == "src":
                rewritten = (original[:attribute.start()] + f'src="{escape(target, quote=True)}"'
                             + original[attribute.end():])
                break
        else:
            return
        line, column = self.getpos()
        start = self.line_offsets[line - 1] + column
        self.changes.append((start, start + len(original), rewritten))


def on_page_content(html, page, files, **kwargs):
    parser = ImagePaths(html, page, files)
    parser.feed(html)
    parser.close()
    for start, end, rewritten in reversed(parser.changes):
        html = html[:start] + rewritten + html[end:]
    return html
