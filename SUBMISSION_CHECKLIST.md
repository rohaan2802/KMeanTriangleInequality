# Final submission checklist (course deliverables)

Tick each item before uploading to Google Classroom / LMS.

## Required by brief (typical)

- [ ] **Final report (PDF)** — includes Table A/B and figures from `experiments/figures/`; both members on title page (see [`AUTHORS.md`](AUTHORS.md)).
- [ ] **Presentation slides** (PDF/PPTX) — same author names and roll numbers as report. Regenerate **`PDC_Kmeans_Presentation.pptx`** on WSL with `experiments/build_presentation.py` after figures update.
- [ ] **Video** — YouTube or Google Drive link **only** (put URL in README or a `VIDEO_LINK.txt` in zip root if the form asks).
- [ ] **Complete source code** — this folder + upstream; include `experiments/` logs and `figures/` if small enough, or note “regenerate with README”.
- [ ] **README** — [`README.md`](README.md) at zip root (already here).

## Suggested zip layout

```text
22i-2327_F_FinalProject/
├── README.md
├── AUTHORS.md
├── REPORT_AND_REPO_MAP.md
├── SUBMISSION_CHECKLIST.md
├── LLM_DISCLOSURE_SNIPPET.md   # optional in zip; same text must appear inside PDF
├── PROFILING_SNIPPET.md        # optional; paste methodology into PDF if useful
├── experiments/
│   ├── figures/
│   ├── *.py, *.sh, *.txt (logs if included)
│   └── ...
└── upstream_hybrid-triangle-kmeans/
```

Optional: add **`VIDEO_LINK.txt`** with one line URL before zipping.

## What **not** to rely on

- **`report.docx`** — keep it on your PC; export **PDF** for submission. The repo does not contain `.docx`.
- **`git status`** — graders care that **algorithm sources are unchanged**, not an empty `git status`.

## LLM disclosure

Add a subsection **inside the PDF report** (required by your Milestone 3 brief). Copy or adapt **[`LLM_DISCLOSURE_SNIPPET.md`](LLM_DISCLOSURE_SNIPPET.md)** into Word, then remove the instruction lines at the bottom of that file from your PDF.
