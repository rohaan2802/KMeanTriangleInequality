# Where each piece lives (repo vs your Word/PDF report)

Your **`report.docx` / final `.pdf` is not in this Git folder** — nothing here edits Word automatically. You **copy-paste** from the paths below.

**Automated draft:** run `experiments/build_final_report_docx.py` on WSL to generate **`PDC_Kmeans_Final_Report.docx`** at the project root; polish partner name and export PDF.

**Demo / defense Q&A:** run `experiments/build_demo_qa_docx.py` → **`PDC_Kmeans_Demo_QA.docx`** (optional print or study on laptop; not always a course deliverable).

**Slide speaker notes:** run `experiments/build_slide_speaker_notes_docx.py` → **`PDC_Kmeans_Slide_Speaker_Notes.docx`** (Slide 1–19 aligned with `build_presentation.py`).

| What | In this repository (source of truth) | Paste into your report (`report.docx` → PDF) |
|------|----------------------------------------|-----------------------------------------------|
| Group names & rolls | [`AUTHORS.md`](AUTHORS.md) | Title page; optionally first page of PDF |
| Build, data, reproduce | [`README.md`](README.md) | “Experimental setup” / “Reproducibility” — paraphrase or short quote |
| “No algorithm edits” / untracked `.bin` wording | [`README.md`](README.md) § *Upstream code vs local artifacts* | One paragraph in setup — **do not** claim “clean git status” if you have `??` files |
| **Table A** (Gap 1 medians) | [`experiments/figures/TABLE_A_gap1_for_report.md`](experiments/figures/TABLE_A_gap1_for_report.md) | Results § Gap 1 — generate first with `plot_pdc_figures.py` |
| **Table B** (Gap 3 by M) | [`experiments/figures/TABLE_B_gap3_for_report.md`](experiments/figures/TABLE_B_gap3_for_report.md) | Results § Gap 3 |
| **Figures** | [`experiments/figures/`](experiments/figures/) `fig_gap1_*.png`, `fig_gap3_*.png` | Results — embed PNGs; caption with N, K, T |
| Raw logs | `experiments/gap1_medium_runs.txt`, `gap3_runs.txt` | Usually appendix or “available on request”; not full paste |
| Code & scripts | `experiments/*.py`, `experiments/*.sh` | Name them in text; full code in **submission zip**, not in PDF body |
| **LLM disclosure** (required by brief) | [`LLM_DISCLOSURE_SNIPPET.md`](LLM_DISCLOSURE_SNIPPET.md) | Dedicated subsection in PDF — **paste/adapt**, customize prompts |
| **Profiling / instrumentation wording** | [`PROFILING_SNIPPET.md`](PROFILING_SNIPPET.md) | Experimental setup or “Measurement methodology” — explains **stdout metrics**; optional **`perf stat`** |

**Generate tables + figures on WSL (or anywhere with logs):**

```bash
source ~/22i-2327_F_FinalProject/.venv/bin/activate   # if you use venv
python3 ~/22i-2327_F_FinalProject/experiments/plot_pdc_figures.py \
  --exp-dir ~/22i-2327_F_FinalProject/experiments
```

Then refresh copies under `experiments/figures/` before pasting into Word.
