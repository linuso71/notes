"""Discover course folders and generate the catalog, navigation, and lesson lists."""

from html import escape
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote

from mkdocs.exceptions import ConfigurationError
from mkdocs.structure.files import File
from mkdocs.utils.meta import get_data
from watchdog.events import FileSystemEventHandler
import yaml


NOTE_FORMATS = {".md", ".markdown", ".pdf", ".docx"}
OVERVIEWS = {"readme.md", "index.md", "readme.markdown", "index.markdown"}
BOOK_ICON = '<svg viewBox="0 0 48 48" fill="none" aria-hidden="true"><path d="M8 9h13c3 0 3 3 3 3s0-3 3-3h13v29H27c-3 0-3 3-3 3s0-3-3-3H8V9Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M24 12v29M13 17h6m-6 7h6m10-7h6m-6 7h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'


def natural_key(value):
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", str(value))]


def course_files(directory):
    return sorted((
        path for path in directory.rglob("*")
        if path.is_file() and not any(
            part.startswith(".") or part == "__pycache__"
            for part in path.relative_to(directory).parts
        )
    ), key=lambda path: natural_key(path.relative_to(directory)))


def slugify(value):
    value = unicodedata.normalize("NFKC", str(value)).casefold()
    return re.sub(r"[^\w-]+", "-", value, flags=re.UNICODE).strip("-_")


def note_title(path):
    if path.suffix.lower() in {".md", ".markdown"}:
        body, _ = get_data(path.read_text(encoding="utf-8"))
        heading = re.search(r"^#\s+(.+?)\s*#*\s*$", body, re.MULTILINE)
        if heading:
            return re.sub(r"[`*_]", "", heading.group(1))
    return path.stem.replace("_", " ").replace("-", " ")


def discover_courses(root):
    courses = []
    slugs = set()
    for directory in sorted(root.iterdir(), key=lambda path: natural_key(path.name)):
        if not directory.is_dir() or directory.name.startswith("."):
            continue
        sources = course_files(directory)
        overview = next((path for path in sources if path.parent == directory and path.name.lower() in OVERVIEWS), None)
        body, metadata = get_data(overview.read_text(encoding="utf-8")) if overview else ("", {})
        title = str(metadata.get("title") or directory.name)
        slug = slugify(metadata.get("slug") or directory.name)
        if not slug or slug in slugs:
            raise ConfigurationError(f"Course '{directory.name}' needs a unique 'slug' in its README front matter.")
        slugs.add(slug)
        grouped = {}
        for source in sources:
            if source.suffix.lower() not in NOTE_FORMATS or (source.parent == directory and source.name.lower() in OVERVIEWS):
                continue
            relative = source.relative_to(directory)
            grouped.setdefault(relative.with_suffix("").as_posix(), {})[source.suffix.lower()] = relative.as_posix()
        lessons = []
        for _, formats in sorted(grouped.items(), key=lambda item: natural_key(item[0])):
            main = next(formats[extension] for extension in (".md", ".markdown", ".pdf", ".docx") if extension in formats)
            markdown = formats.get(".md") or formats.get(".markdown")
            markdown_bundle = str(Path(markdown).with_suffix("")) + "-markdown.zip" if markdown else None
            lessons.append({"title": note_title(directory / main), "path": main, "formats": formats, "markdown_bundle": markdown_bundle})
        topics = [re.sub(r"^Video\s+\d+\s*[-—:]\s*", "", lesson["title"]) for lesson in lessons[:3]]
        description = str(metadata.get("description") or " · ".join(topics))
        courses.append({
            "title": title, "slug": slug, "source_dir": str(directory),
            "description": description, "lessons": lessons,
            "overview_body": body, "metadata": metadata,
        })
    return courses


def on_pre_build(config, **kwargs):
    root = Path(config.config_file_path).parent / "courses"
    courses = discover_courses(root)
    config["extra"]["courses"] = courses
    navigation = []
    for course in courses:
        prefix = f'courses/{course["slug"]}/'
        pages = [{"Overview": prefix + "README.md"}]
        pages.extend({lesson["title"]: prefix + lesson["path"]} for lesson in course["lessons"] if Path(lesson["path"]).suffix.lower() in {".md", ".markdown"})
        navigation.append({course["title"]: pages})
    config["nav"] = [{"Home": "index.md"}, {"Courses": navigation}] if courses else [{"Home": "index.md"}]


def download_link(path, label):
    return f'<a href="{escape(quote(path, safe="/"), quote=True)}" download>{label}</a>'


def lesson_list(course):
    lines = []
    if 'downloads/all-notes.zip' not in course["overview_body"]:
        lines.extend(['<a class="md-button md-button--primary" href="downloads/all-notes.zip" download>Download all notes (ZIP)</a>', ""])
    lines.extend(["## Lessons", "", "| Lesson | PDF | Word | Markdown |", "|---|---|---|---|"])
    for lesson in course["lessons"]:
        title = re.sub(r"([\\\[\]|])", r"\\\1", lesson["title"])
        label = f'[{title}](<{quote(lesson["path"], safe="/")}>)'
        formats = lesson["formats"]
        pdf = download_link(formats[".pdf"], "PDF") if ".pdf" in formats else "—"
        word = download_link(formats[".docx"], "Word") if ".docx" in formats else "—"
        markdown_bundle = lesson["markdown_bundle"]
        markdown = download_link(f"downloads/{markdown_bundle}", "Markdown (ZIP)") if markdown_bundle else "—"
        lines.append(f"| {label} | {pdf} | {word} | {markdown} |")
    return "\n".join(lines) + "\n\n"


def course_overview(course):
    body = course["overview_body"]
    title = course["title"]
    if re.search(r"^#\s+", body, re.MULTILINE):
        body = re.sub(r"^#\s+.*$", lambda _: f"# {title}", body, count=1, flags=re.MULTILINE)
    else:
        body = f"# {title}\n\n" + body
    if course["lessons"]:
        section = lesson_list(course)
        if "<!-- course-lessons -->" in body:
            body = body.replace("<!-- course-lessons -->", section)
        elif re.search(r"^## Lessons\s*$", body, re.MULTILINE):
            body = re.sub(r"^## Lessons\s*\n.*?(?=^##\s|^<details\b|\Z)", lambda _: section, body, count=1, flags=re.MULTILINE | re.DOTALL)
        else:
            # Keep authored course information, with the live lesson list first.
            heading, _, information = body.partition("\n")
            body = heading + "\n\n" + section
            if information.strip():
                body += '<details class="course-details" markdown="1">\n<summary>Course information</summary>\n\n' + information.strip() + "\n\n</details>\n"
    elif "coming soon" not in body.casefold():
        body += '\n\n<p><span class="course-status">Coming soon</span></p>\n'
    metadata = {**course["metadata"], "title": title, "hide": ["toc"]}
    return "---\n" + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True) + "---\n\n" + body


def on_files(files, config, **kwargs):
    for course in config["extra"]["courses"]:
        directory = Path(course["source_dir"])
        prefix = f'courses/{course["slug"]}/'
        for source in course_files(directory):
            if source.parent == directory and source.name.lower() in OVERVIEWS:
                continue
            files.append(File.generated(config, prefix + source.relative_to(directory).as_posix(), abs_src_path=str(source)))
        files.append(File.generated(config, prefix + "README.md", content=course_overview(course)))
    return files


def on_page_markdown(markdown, page, config, **kwargs):
    if page.file.src_uri != "index.md":
        return markdown
    cards = []
    for course in config["extra"]["courses"]:
        count = len(course["lessons"])
        status = f'{count} lesson{"s" if count != 1 else ""}' if count else "Coming soon"
        ready = " course-status--ready" if count else ""
        description = f'<p>{escape(course["description"])}</p>' if course["description"] else ""
        cards.append(
            f'<a class="course-card" href="courses/{quote(course["slug"], safe="")}/">'
            f'<div class="course-card__top"><span class="course-card__icon" aria-hidden="true">{BOOK_ICON}</span>'
            f'<span class="course-status{ready}">{status}</span></div>'
            f'<h2>{escape(course["title"])}</h2>{description}'
            f'<div class="course-card__footer"><span>{"View notes" if count else "View course"}</span><span aria-hidden="true">→</span></div></a>'
        )
    catalog = '<div class="course-grid">' + "\n".join(cards) + "</div>" if cards else "No courses yet."
    return markdown.replace("<!-- course-cards -->", catalog)


def on_serve(server, config, **kwargs):
    root = (Path(config.config_file_path).parent / "courses").resolve()
    handler = FileSystemEventHandler()

    def directory_changed(event):
        if event.is_directory and event.event_type in {"created", "deleted", "moved"}:
            # MkDocs 1.6 ignores directories in its file watcher. Use its build
            # queue so empty-course changes are also debounced and serialized.
            with server._rebuild_cond:
                server._want_rebuild = True
                server._rebuild_cond.notify_all()

    handler.on_any_event = directory_changed
    server.observer.schedule(handler, str(root), recursive=False)
    return server
