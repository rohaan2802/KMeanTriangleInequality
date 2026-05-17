# PDC Final Project — K-means (triangle inequality) experiments

Baseline code from **Kwedlo & Czochanski**, *A hybrid MPI/OpenMP parallelization of K-means algorithms accelerated using the triangle inequality* (IEEE Access, DOI [10.1109/ACCESS.2019.2907885](https://doi.org/10.1109/ACCESS.2019.2907885)).

**Upstream repository:** [hybrid-triangle-kmeans](https://bitbucket.org/wkwedlo/hybrid-triangle-kmeans)  
**Commit used for experiments:** `0265d45a2eb04fec01ed53fc8635b277082ee284`

## Authors (Section F)

- **Mohammad Rohaan** — 22I-2327  
- **Partner:** replace with full name and roll **22I-xxxx** (must match the report title page and course registration)

See [`AUTHORS.md`](AUTHORS.md) for the same table.

**Where to paste content into your Word/PDF report:** see [`REPORT_AND_REPO_MAP.md`](REPORT_AND_REPO_MAP.md).  
**Submission zip / video / PDF checklist:** [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md).  
**LLM disclosure text for the PDF:** [`LLM_DISCLOSURE_SNIPPET.md`](LLM_DISCLOSURE_SNIPPET.md).  
**Profiling / what we measured (for the PDF):** [`PROFILING_SNIPPET.md`](PROFILING_SNIPPET.md).

**Prebuilt Word report (regenerate on WSL):** `PDC_Kmeans_Final_Report.docx` in the project root (see “Build final report (.docx)” below).

**Slides:** `PDC_Kmeans_Presentation.pptx` — build with `experiments/build_presentation.py` (see “Build presentation (.pptx)”).

**Demo / defense Q&A (Word):** `PDC_Kmeans_Demo_QA.docx` — generate with `experiments/build_demo_qa_docx.py`.

**Slide speaker notes (Word):** `PDC_Kmeans_Slide_Speaker_Notes.docx` — generate with `experiments/build_slide_speaker_notes_docx.py` (Slide 1 … Slide N matching `build_presentation.py`).

Group experiments compare **OpenMP scheduling** (static-oriented vs guided build) and study **dimensionality** effects on **Elkan** vs **Lloyd**, without modifying the authors’ C++ sources.

---

## Prerequisites (Ubuntu on WSL)

```bash
sudo apt update
sudo apt install -y build-essential libnuma-dev g++ python3 dos2unix
```

OpenMP is enabled via **`-fopenmp`** (see upstream `Makefile`).

---

## Directory layout (expected)

```text
~/22i-2327_F_FinalProject/
├── README.md                 # this file
├── AUTHORS.md
├── PDC_Kmeans_Final_Report.docx   # generated — build_final_report_docx.py
├── PDC_Kmeans_Presentation.pptx   # generated — build_presentation.py
├── PDC_Kmeans_Demo_QA.docx        # generated — build_demo_qa_docx.py
├── PDC_Kmeans_Slide_Speaker_Notes.docx  # generated — build_slide_speaker_notes_docx.py
├── experiments/
│   ├── bin/                  # kmeans_static_gap1, kmeans_guided_gap1 (copied after build)
│   ├── data_gap3/            # gap3_N100000_M*.bin
│   ├── gen_gap3_bins.py
│   ├── run_gap3_matrix.sh
│   ├── parse_gap1_log.py
│   ├── gap1_medium_runs.txt
│   ├── gap1_parsed_summary.txt
│   ├── gap3_runs.txt
│   ├── figures/             # PNG + TABLE_*_for_report.md (from plot_pdc_figures.py)
│   ├── plot_pdc_figures.py
│   ├── build_presentation.py
│   ├── build_final_report_docx.py
│   ├── build_demo_qa_docx.py
│   └── build_slide_speaker_notes_docx.py
└── upstream_hybrid-triangle-kmeans/   # git clone; do not patch Clust/*.cpp for baseline
```

---

## Upstream code vs local artifacts (report wording)

- **Baseline source:** `upstream_hybrid-triangle-kmeans` at commit **`0265d45a2eb04fec01ed53fc8635b277082ee284`**. For this project, **algorithm `.cpp` sources were not modified** (experiments use two builds of the authors’ `kmeans`).
- **`git status` may show untracked files** (`??`), e.g. `gap1_medium.bin`, `tiny.bin`, `experiments/bin/*`, generated `.bin` under `experiments/data_gap3/`, run logs. That is **normal**: large binaries and outputs are often left untracked.
- In the **report**, say **no edits to the authors’ core clustering implementation**, not “working tree clean,” unless you truly have zero local/untracked files.

---

## Build author `kmeans` (two scheduling variants)

```bash
cd ~/22i-2327_F_FinalProject/upstream_hybrid-triangle-kmeans
mkdir -p Object ~/22i-2327_F_FinalProject/experiments/bin

# Static-oriented (default OMP loop scheduling in this codebase)
make clean
make kmeans OPT=y OPENMP=y -j"$(nproc)"
cp -f Object/kmeans_openmp_release_master \
      ~/22i-2327_F_FinalProject/experiments/bin/kmeans_static_gap1

# Guided (Makefile: DYNAMIC=y → schedule(guided) on relevant loops)
make clean
make kmeans OPT=y OPENMP=y DYNAMIC=y -j"$(nproc)"
cp -f Object/kmeans_openmp_dynamic_release_master \
      ~/22i-2327_F_FinalProject/experiments/bin/kmeans_guided_gap1
```

Run:

```bash
export OMP_NUM_THREADS=8
~/22i-2327_F_FinalProject/experiments/bin/kmeans_static_gap1  --help 2>&1 | head
```

(First argument must be a **dataset** `.bin` file; see below.)

---

## Dataset format (author `kmeans`)

Binary file: **`int32` N**, **`int32` M**, then **`N * M`** **`float32`** values, row-major.

Generate **Gap 3** grids:

```bash
python3 ~/22i-2327_F_FinalProject/experiments/gen_gap3_bins.py \
  --n 100000 --seed 42 \
  --out-dir ~/22i-2327_F_FinalProject/experiments/data_gap3 \
  2 8 16 32 64 128
```

**Gap 1 medium** example (200k × 128) — use your existing `gap1_medium.bin` or recreate with a small Python script / `make_tiny_bin.py` pattern with larger N, M.

---

## Example run line

```bash
export OMP_NUM_THREADS=4
DATA=~/22i-2327_F_FinalProject/experiments/data_gap3/gap3_N100000_M32.bin
BIN=~/22i-2327_F_FinalProject/experiments/bin/kmeans_static_gap1

"$BIN" "$DATA" -a elkan -c 256 -v 1 -r 42 -R 1e-4
```

Algorithms: **`-a naive`** (Lloyd), **`-a elkan`**, **`-a annulus`**, etc.

---

## Reproduce experiment logs

**Gap 1 — parse paired static/guided stdout:**

```bash
python3 ~/22i-2327_F_FinalProject/experiments/parse_gap1_log.py \
  ~/22i-2327_F_FinalProject/experiments/gap1_medium_runs.txt \
  | tee ~/22i-2327_F_FinalProject/experiments/gap1_parsed_summary.txt
```

**Gap 3 — full matrix (naive + Elkan static + Elkan guided):**

```bash
chmod +x ~/22i-2327_F_FinalProject/experiments/run_gap3_matrix.sh
export OMP_NUM_THREADS=8
~/22i-2327_F_FinalProject/experiments/run_gap3_matrix.sh
# output also appended to experiments/gap3_runs.txt
```

---

## Build final report (.docx)

On **WSL**, from `~/22i-2327_F_FinalProject/` (i.e. `/home/<you>/22i-2327_F_FinalProject/`):

```bash
cd ~/22i-2327_F_FinalProject
python3 -m venv .venv
source .venv/bin/activate
pip install python-docx matplotlib
python3 experiments/plot_pdc_figures.py --exp-dir ~/22i-2327_F_FinalProject/experiments
python3 experiments/build_final_report_docx.py \
  --project-root ~/22i-2327_F_FinalProject \
  --out ~/22i-2327_F_FinalProject/PDC_Kmeans_Final_Report.docx
```

This writes **`PDC_Kmeans_Final_Report.docx`** (sections 1–12, appendices, embedded PNGs, optional `perf` capture if `perf` works). Open in Word, replace partner line, then **Export → PDF** for submission.

---

## Build presentation (.pptx)

Uses **`experiments/figures/*.png`** — run **`plot_pdc_figures.py`** first if plots changed.

```bash
cd ~/22i-2327_F_FinalProject
source .venv/bin/activate
pip install python-pptx matplotlib   # once
python3 experiments/plot_pdc_figures.py --exp-dir ~/22i-2327_F_FinalProject/experiments
python3 experiments/build_presentation.py \
  --figures-dir ~/22i-2327_F_FinalProject/experiments/figures \
  --out ~/22i-2327_F_FinalProject/PDC_Kmeans_Presentation.pptx
```

Default subtitle authors come from **`AUTHORS.md`** (override with `--authors "Name (22I-xxxx), …"`). Export to **PDF** if the course asks for slide PDF.

---

## Demo / defense Q&A (.docx)

Long-form **question–answer** prep for presentation defense:

```bash
cd ~/22i-2327_F_FinalProject
source .venv/bin/activate
pip install python-docx    # if needed
python3 experiments/build_demo_qa_docx.py \
  --out ~/22i-2327_F_FinalProject/PDC_Kmeans_Demo_QA.docx
```

---

## Slide speaker notes (.docx)

What to **say on each slide** (order matches `build_presentation.py` — **19 slides**):

```bash
python3 experiments/build_slide_speaker_notes_docx.py \
  --out ~/22i-2327_F_FinalProject/PDC_Kmeans_Slide_Speaker_Notes.docx
```

---

## Report figures and tables (embed in PDF)

After `gap1_medium_runs.txt` and `gap3_runs.txt` exist, generate PNGs plus **copy-paste tables**:

```bash
python3 -m venv ~/22i-2327_F_FinalProject/.venv
source ~/22i-2327_F_FinalProject/.venv/bin/activate
pip install matplotlib
python3 ~/22i-2327_F_FinalProject/experiments/plot_pdc_figures.py \
  --exp-dir ~/22i-2327_F_FinalProject/experiments
```

Outputs under **`experiments/figures/`**:

- **Figures:** `fig_gap1_elkan_static_vs_guided_median.png`, `fig_gap1_comparable_pairs_only.png`, `fig_gap3_ratio_vs_M.png`, `fig_gap3_time_vs_M.png`, optional `fig_gap3_speedup_naive_over_elkan_static.png`
- **Tables for the report:** `TABLE_A_gap1_for_report.md`, `TABLE_B_gap3_for_report.md` (Markdown — paste into Word/Google Docs or convert)
- **CSV:** `summary_gap1_medians.csv`, `summary_gap3_by_M.csv` (Gap 3 CSV includes SSE columns and match/differs notes)

---

## Academic integrity

- **Baseline implementation** is the **authors’** repository at the commit above; our work is **experiments**, **scripts**, and **analysis**.
- Cite the **paper** and **repository** in the report.

---

## Troubleshooting

- **`make` fails at `mv` to `Object/`:** run `mkdir -p Object` first.
- **CRLF scripts:** `dos2unix experiments/*.py experiments/*.sh`
- **Huge Elkan memory:** reduce **K** or **N** if the process is killed (Elkan uses **O(N·K)** auxiliary storage).
