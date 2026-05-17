# Profiling and measurement — paste into your report (PDF)

Use this as a short **“Profiling / measurement methodology”** or **“Instrumentation”** paragraph in **Experimental setup** or before **Results**. Edit only if you also ran optional `perf` (see end).

---

## Profiling and performance measurement

We did **not** use a separate sampling profiler (e.g. Intel VTune, `gprof`, or `perf record` with flame graphs) for the main study, because the authors’ `kmeans` binary already reports **application-level** statistics that directly reflect the cost model of interest (distance work vs wall time).

**Primary tools (built into the program output)**

| Signal | Where it appears | How we use it |
|--------|-------------------|----------------|
| **Wall-clock k-means time** | `k-means execution time: … seconds` | Primary metric for Gap 1 (scheduling) and Gap 3 (dimension sweep). |
| **Avg distance calculations ratio** | `Avg distance calculations ratio: …` | Proxy for **triangle-inequality pruning** effectiveness (100 = full Lloyd-like work per the implementation’s accounting; lower = more pruning). |
| **Iterations / convergence** | `… total iterations` | Pair **static vs guided** runs only when iterations and SSE align (see parser `OK` vs `DIFF_PATH`). |
| **SSE** | `Best MSE (SSE) … ( … )` | Correctness / comparability check between runs. |

These lines were captured from **stdout** and stored in `gap1_medium_runs.txt` and `gap3_runs.txt` for tables and plots (`plot_pdc_figures.py`).

**Why this counts as performance analysis for PDC**

- **Workload characterization:** the distance-calculation ratio connects algorithmic pruning to observed runtime.
- **Scheduling study:** wall time plus iteration/SSE matching isolates **when** a scheduling-only comparison is valid.

**Optional system-level profiling (not required for our conclusions)**

If you want one hardware snapshot for the report, you can run **Linux `perf`** on WSL (best-effort; counters vary by kernel):

```bash
perf stat -e cycles,instructions,cache-references,cache-misses \
  ~/22i-2327_F_FinalProject/experiments/bin/kmeans_static_gap1 \
  ~/22i-2327_F_FinalProject/experiments/data_gap3/gap3_N100000_M32.bin \
  -a elkan -c 256 -v 1 -r 42 -R 1e-4
```

Only paste **`perf stat`** summary lines into the PDF if you actually ran this and understand noise under WSL.

---

**Before submission:** remove this instruction block from your PDF; keep the subsection you adopt.
