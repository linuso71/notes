# Notes

Illustrated study notes organized by course, published with MkDocs Material on GitHub Pages.

**Website (after deployment):** https://linuso71.github.io/notes/

Every folder directly inside `courses/` becomes a course automatically. The homepage, sidebar, lesson counts, and download lists are generated from those folders. Courses with no lessons show **Coming soon**.

The website includes search across courses, collapsible course navigation, code highlighting, light and dark themes, and Markdown, PDF, and Word downloads. Each lesson has download buttons, and the LangGraph overview offers a ZIP of that course's notes and diagrams.

## Publish on GitHub Pages

1. Commit and push the site configuration and notes to `main`:

   ```bash
   git add -A
   git commit -m "Set up notes website on GitHub Pages"
   git push origin main
   ```

2. Open [repository Settings → Pages](https://github.com/linuso71/notes/settings/pages). Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Open [Actions → Publish notes](https://github.com/linuso71/notes/actions/workflows/pages.yml). If the initial run failed before Pages was enabled, re-run it or choose **Run workflow** on `main`.
4. Once the deployment succeeds, visit https://linuso71.github.io/notes/.

Every subsequent push to `main` rebuilds and publishes the notes. Pull requests build the site without deploying it. No personal access token is needed by the workflow.

See GitHub's [publishing source documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) for the Pages setting.

## Preview locally

With Python 3.12 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdocs serve
```

Open http://127.0.0.1:8000/notes/. Adding, removing, or renaming a course folder updates the local preview automatically. To check a production build, run `mkdocs build --strict`. Run the discovery checks with `python -m unittest discover -s tests`.

## Add or update notes

Edit notes inside `courses/<course name>/` and keep image links relative to each lesson. Markdown, PDF, and Word files with the same basename are grouped as one lesson. Lessons are ordered by their folder/file names, with numbers sorted naturally (`Video_2` before `Video_10`). A root `README.md` or `index.md` is the course overview and does not count as a lesson.

`hooks/courses.py` discovers courses, builds navigation and cards, and updates the lesson list in each overview. Existing README content is preserved; course information appears below the automatic lesson list when there is no existing `## Lessons` section. You can place `<!-- course-lessons -->` in a README to choose where its generated list appears.

`hooks/downloads.py` adds lesson download buttons, publishes original Markdown under `courses/<slug>/downloads/`, and creates a ZIP per course at `courses/<slug>/downloads/all-notes.zip`. A combined ZIP is also built at `downloads/all-notes.zip`.

To offer PDF or Word downloads for a new lesson, place files with the same basename as its Markdown alongside it. These files are supplied by the author; the build does not convert between formats.

## Add a course

Create a folder inside `courses/`. No configuration or homepage changes are needed.

```text
courses/
  Agentic AI using LangGraph/
  Generative AI using LangChain/
  RAG/
  Your next course/
    .gitkeep
```

An empty folder appears as **Coming soon**. Git does not track empty folders, so add a `.gitkeep` file inside an empty course folder when you want to publish it on GitHub. Adding notes changes its status and lesson count automatically.

Optionally add front matter to a course's `README.md`:

```yaml
---
title: Your course name
slug: your-course
description: A short description for its card.
---
```

Without these fields, the folder name supplies the title and URL, and the first lesson titles supply the description. Keep a custom `slug` unchanged to preserve a course's public URL when its folder is renamed.
