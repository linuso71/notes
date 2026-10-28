"""Publish original note files and add download buttons to discovered lessons."""

from html import escape
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

from mkdocs.utils import get_relative_url


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
    for path, label in (
        (formats.get(".pdf"), "PDF"),
        (formats.get(".docx"), "Word (.docx)"),
        (formats.get(".md") or formats.get(".markdown"), "Markdown"),
    ):
        if path is None:
            continue
        target = f"courses/{slug}/{path}"
        if Path(path).suffix.lower() in {".md", ".markdown"}:
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
            # MkDocs normally renders Markdown to HTML; offer the original too.
            for source in sources:
                if source.suffix.lower() not in {".md", ".markdown"}:
                    continue
                target = course_downloads / source.relative_to(source_dir)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

            # Preserve relative image links when a course ZIP is extracted.
            with ZipFile(course_downloads / "all-notes.zip", "w", compression=ZIP_DEFLATED) as course_bundle:
                for source in sources:
                    if source.suffix.lower() in formats:
                        relative = source.relative_to(source_dir).as_posix()
                        course_bundle.write(source, relative)
                        bundle.write(source, f"{slug}/{relative}")
