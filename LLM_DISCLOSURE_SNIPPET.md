# LLM usage — paste into your report (PDF)

Copy the section below into **`report.docx`** as its own subsection (e.g. after Conclusions or before References). Replace bracketed notes with your honest details.

---

## LLM usage disclosure and reflection

We used large language model assistants (e.g. **Cursor / ChatGPT**) during this project in a **supporting** role only. They did **not** replace reading the base paper, running experiments, or verifying numerical outputs.

**Where we used LLMs**

- **Planning and structure:** outlining report sections (introduction, experimental setup, results), and clarifying OpenMP scheduling terminology (`schedule(static)` vs `schedule(guided)`) in relation to the upstream Makefile (`DYNAMIC=y`).
- **Tooling and environment:** resolving **PEP 668 / externally-managed-environment** issues when installing Python packages on Ubuntu/WSL; **`dos2unix`** / line-ending problems when copying scripts from Windows to WSL.
- **Scripts:** suggestions for **log parsing** and **plotting** workflows (e.g. pairing STATIC/GUIDED runs, CSV summaries); we reviewed and executed all code ourselves.
- **Writing:** polishing wording for clarity; we cross-checked all claims against our **measured** stdout logs (`gap1_medium_runs.txt`, `gap3_runs.txt`) and figures generated locally.

**Representative prompts (paraphrased)**

1. “Explain why triangle inequality K-means can create load imbalance under OpenMP static scheduling, and what guided scheduling changes.”
2. “Given two stdout blocks from `kmeans`, how should we flag pairs as comparable when iterations or SSE differ?”
3. “Outline experimental setup bullets for WSL2, `g++`, commit hash `0265d45…`, and Gap 1 vs Gap 3 parameters.”

**Benefits**

- Faster iteration on **documentation** and **reproducibility** steps (README, tables).
- Fewer environment pitfalls when mixing Windows editors with Linux builds.

**Limitations and academic integrity**

- LLMs can **hallucinate** flags or Makefile behavior — we verified scheduling behavior against **upstream source** and **actual binaries**.
- All **timings, SSE values, iteration counts, and plots** come from our **own runs**. Both group members can explain the methodology and interpret the tables and figures independently.

---

**Before submission:** delete this instruction block from your PDF; keep only the subsection heading + paragraphs you adopt.
