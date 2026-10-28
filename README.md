# Notes

Illustrated study notes on agentic AI and LangGraph, published with MkDocs Material on GitHub Pages.

**Website (after deployment):** https://linuso71.github.io/notes/

Browse the [LangGraph notes](<Agentic AI using LangGraph/README.md>) in the repository. The website includes search, lesson navigation, code highlighting, light and dark modes, diagrams, and Markdown, PDF, and Word downloads. Every lesson has download buttons, and the homepage offers a ZIP of all notes and diagrams.

## Publish on GitHub Pages

1. Commit and push the site configuration and notes to `main`:

   ```bash
   git add .gitignore .github/workflows/pages.yml mkdocs.yml requirements.txt hooks README.md 'Agentic AI using LangGraph'
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

Open http://127.0.0.1:8000. To check a production build, run `mkdocs build --strict`.

## Add or update notes

Edit Markdown files in `Agentic AI using LangGraph/` and keep image links relative to each lesson. Add new lessons to `nav` in `mkdocs.yml`, and add their download links to the notes homepage. PDF, Word, and image files in the notes directory are copied into the published site automatically.

The build hook in `hooks/downloads.py` adds lesson download buttons for each available format, publishes the original Markdown under `downloads/`, and creates `downloads/all-notes.zip`. To offer PDF or Word downloads for a new lesson, place files with the same basename as its Markdown alongside it. These files are supplied by the author; the build does not convert between formats.
