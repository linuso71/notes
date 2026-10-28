"""Publish original note files and add download buttons to lesson pages."""

from html import escape
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

from mkdocs.utils import get_relative_url


def on_page_content(html, page, config, **kwargs):
    source = Path(page.file.abs_src_path)
    if source.name in {"README.md", "index.md"}:
        return html

    source_uri = page.file.src_uri
    downloads = []
    for extension, label in (
        (".pdf", "PDF"),
        (".docx", "Word (.docx)"),
        (".md", "Markdown (.md)"),
    ):
        if not source.with_suffix(extension).is_file():
            continue
        target = Path(source_uri).with_suffix(extension).as_posix()
        if extension == ".md":
            target = f"downloads/{target}"
        url = escape(get_relative_url(target, page.url), quote=True)
        filename = escape(source.with_suffix(extension).name, quote=True)
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
    docs_dir = Path(config["docs_dir"])
    downloads_dir = Path(config["site_dir"]) / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    # MkDocs normally renders Markdown to HTML, so publish a separate raw copy.
    for source in docs_dir.rglob("*.md"):
        target = downloads_dir / source.relative_to(docs_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

    # Keep the source layout so diagrams also work in the downloaded Markdown.
    formats = {".md", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}
    with ZipFile(downloads_dir / "all-notes.zip", "w", compression=ZIP_DEFLATED) as bundle:
        for source in sorted(docs_dir.rglob("*")):
            if source.is_file() and source.suffix.lower() in formats:
                bundle.write(source, source.relative_to(docs_dir).as_posix())
