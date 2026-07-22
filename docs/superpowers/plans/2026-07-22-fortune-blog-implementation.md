# Fortune Blog Autopost Implementation Plan

> Implemented inline in the design session (user requested design + full implementation).

**Goal:** Modular daily fortune content pipeline on Blogger via GitHub Actions.

**Architecture:** schedule → Gemini generator → HTML template/CTA → optional image → Blogger publish.

**Tech Stack:** Python 3.12, Gemini API, Google Blogger API, GitHub Actions.

## Delivered

- [x] Design spec: `docs/superpowers/specs/2026-07-22-fortune-blog-design.md`
- [x] `config/`, `content/`, `render/`, `publish/` modules
- [x] `main.py` orchestrator
- [x] SEO topics pool + weekday rotation
- [x] Workflow once daily KST 07:00
- [x] Unit tests (schedule, cta, parse)
- [x] README + `.env.example`

## Verify

```bash
pytest -q
# with secrets:
# DRY_RUN=1 python main.py
```
