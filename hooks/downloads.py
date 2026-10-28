"""Publish original note files and add download buttons to discovered lessons."""

from html import escape
from html.parser import HTMLParser
from os.path import commonpath
from pathlib import Path
import shutil
from urllib.parse import unquote, urlsplit
from xml.dom import Node, minidom
from zipfile import ZIP_DEFLATED, ZipFile

from markdown import Markdown
from mkdocs.exceptions import PluginError
from mkdocs.utils import get_relative_url
from mkdocs.utils.meta import get_data


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def white_docx(source, target):
    """Make a light-page download while preserving the original source document."""
    def direct_child(parent, name, first=False):
        for child in parent.childNodes:
            if child.nodeType == Node.ELEMENT_NODE and child.namespaceURI == WORD_NS and child.localName == name:
                return child
        element = parent.ownerDocument.createElementNS(WORD_NS, f"w:{name}")
        if first:
            parent.insertBefore(element, parent.firstChild)
        else:
            parent.appendChild(element)
        return element

    def set_text_color(properties):
        color = direct_child(properties, "color")
        for index in range(color.attributes.length - 1, -1, -1):
            color.removeAttributeNode(color.attributes.item(index))
        color.setAttributeNS(WORD_NS, "w:val", "202020")

    target.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(source) as original, ZipFile(target, "w") as output:
        for entry in original.infolist():
            content = original.read(entry.filename)
            if entry.filename in {"word/document.xml", "word/styles.xml"}:
                document = minidom.parseString(content)
                root = document.documentElement
                root.setAttribute("xmlns:w", WORD_NS)
                if entry.filename == "word/document.xml":
                    background = direct_child(root, "background", first=True)
                    for index in range(background.attributes.length - 1, -1, -1):
                        background.removeAttributeNode(background.attributes.item(index))
                    for child in list(background.childNodes):
                        background.removeChild(child)
                    background.setAttributeNS(WORD_NS, "w:color", "FFFFFF")
                else:
                    defaults = direct_child(root, "docDefaults", first=True)
                    run_defaults = direct_child(defaults, "rPrDefault", first=True)
                    set_text_color(direct_child(run_defaults, "rPr"))
                    for style in root.getElementsByTagNameNS(WORD_NS, "style"):
                        is_normal = style.getAttributeNS(WORD_NS, "styleId") == "Normal"
                        is_default = style.getAttributeNS(WORD_NS, "type") == "paragraph" and style.getAttributeNS(WORD_NS, "default") in {"1", "true"}
                        if is_normal or is_default:
                            set_text_color(direct_child(style, "rPr"))
                content = document.toxml(encoding="UTF-8")
                document.unlink()
            output.writestr(entry, content)


class NoteImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = set()

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            source = dict(attrs).get("src")
            if source:
                self.sources.add(source)


def bundle_markdown(source, course_root, target, config):
    """Package a note and local images without changing its relative links."""
    source = source.resolve()
    course_root = course_root.resolve()
    if not source.is_relative_to(course_root):
        raise PluginError(f"Markdown note is outside its course folder: {source}")
    body, _ = get_data(source.read_text(encoding="utf-8"))
    rendered = Markdown(
        extensions=config["markdown_extensions"],
        extension_configs=config.get("mdx_configs", {}),
    ).convert(body)
    parser = NoteImages()
    parser.feed(rendered)
    images = set()
    for reference in parser.sources:
        url = urlsplit(reference)
        if url.scheme or url.netloc or not url.path:
            continue
        image = (source.parent / unquote(url.path)).resolve()
        if not image.is_relative_to(course_root):
            raise PluginError(f"Image in {source.name} is outside its course folder: {reference}")
        if not image.is_file():
            raise PluginError(f"Image in {source.name} was not found: {reference}")
        images.add(image)

    # Shared images above the lesson folder need the common directory layout.
    base = Path(commonpath([source.parent, *(image.parent for image in images)]))
    target.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
        for item in [source, *sorted(images - {source})]:
            archive.write(item, f"{source.stem}/{item.relative_to(base).as_posix()}")


def course_sources(config):
    for course in config["extra"]["courses"]:
        yield course["slug"], Path(course["source_dir"])


def on_page_content(html, page, config, **kwargs):
    if page.file.abs_src_path is None:
        return html
    source_uri = page.file.src_uri
    course_prefix, _, lesson_path = source_uri.partition("/")
    if course_prefix != "courses":
        return html
    slug, _, lesson_path = lesson_path.partition("/")
    course = next(course for course in config["extra"]["courses"] if course["slug"] == slug)
    lesson = next((lesson for lesson in course["lessons"] if lesson_path in lesson["formats"].values()), None)
    if lesson is None:
        return html
    formats = lesson["formats"]
    downloads = []
    for path, label, is_bundle in (
        (formats.get(".pdf"), "PDF", False),
        (formats.get(".docx"), "Word (.docx)", False),
        (lesson["markdown_bundle"], "Markdown (ZIP)", True),
    ):
        if path is None:
            continue
        target = f"courses/{slug}/{path}"
        if is_bundle:
            target = f"courses/{slug}/downloads/{path}"
        url = escape(get_relative_url(target, page.url), quote=True)
        filename = escape(Path(path).name, quote=True)
        downloads.append(
            f'<a class="md-button" href="{url}" download="{filename}">{label}</a>'
        )

    if not downloads:
        return html
    buttons = (
        '<nav aria-label="Download this lesson">'
        '<p><strong>Download this lesson:</strong></p><p>'
        + "\n".join(downloads)
        + "</p></nav>"
    )
    if "</h1>" in html:
        return html.replace("</h1>", "</h1>" + buttons, 1)
    return buttons + html


def on_post_build(config, **kwargs):
    downloads_dir = Path(config["site_dir"]) / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    formats = {".md", ".markdown", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}
    with ZipFile(downloads_dir / "all-notes.zip", "w", compression=ZIP_DEFLATED) as bundle:
        for slug, source_dir in course_sources(config):
            course_downloads = Path(config["site_dir"]) / "courses" / slug / "downloads"
            course_downloads.mkdir(parents=True, exist_ok=True)
            sources = [source for source in sorted(source_dir.rglob("*")) if source.is_file() and not any(
                part.startswith(".") or part == "__pycache__" for part in source.relative_to(source_dir).parts
            )]
            # Overwrite only published copies, including direct download URLs.
            for source in sources:
                if source.suffix.lower() == ".docx":
                    target = Path(config["site_dir"]) / "courses" / slug / source.relative_to(source_dir)
                    white_docx(source, target)
            # MkDocs normally renders Markdown to HTML; offer the original too.
            for source in sources:
                if source.suffix.lower() not in {".md", ".markdown"}:
                    continue
                target = course_downloads / source.relative_to(source_dir)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

            course = next(course for course in config["extra"]["courses"] if course["slug"] == slug)
            for lesson in course["lessons"]:
                markdown = lesson["formats"].get(".md") or lesson["formats"].get(".markdown")
                if markdown:
                    bundle_markdown(source_dir / markdown, source_dir, course_downloads / lesson["markdown_bundle"], config)

            # Preserve relative image links when a course ZIP is extracted.
            with ZipFile(course_downloads / "all-notes.zip", "w", compression=ZIP_DEFLATED) as course_bundle:
                for source in sources:
                    if source.suffix.lower() in formats:
                        relative = source.relative_to(source_dir).as_posix()
                        published = Path(config["site_dir"]) / "courses" / slug / relative if source.suffix.lower() == ".docx" else source
                        course_bundle.write(published, relative)
                        bundle.write(published, f"{slug}/{relative}")
