#!/usr/bin/env python3
"""
Parse gap1_medium_runs.txt and gap3_runs.txt; write CSV summaries + PNG figures.
Requires: matplotlib (pip install matplotlib)
"""
from __future__ import annotations

import argparse
import csv
import re
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

# -----------------------------------------------------------------------------
# Gap 1
# -----------------------------------------------------------------------------


@dataclass
class G1Run:
    sched: str
    threads: int
    run: int
    iters: int
    sse: float
    km_time: float


def parse_gap1_log(text: str) -> list[G1Run]:
    header_re = re.compile(r"=== threads=(\d+) run=(\d+) (STATIC|GUIDED) ===")
    iter_re = re.compile(r"(\d+) total iterations")
    sse_re = re.compile(r"Best MSE \(SSE\) [\d.]+\s+\(([\d.]+)\)")
    time_re = re.compile(r"k-means execution time: ([\d.eE+-]+) seconds")
    runs: list[G1Run] = []
    for m in header_re.finditer(text):
        threads, run_n, sched = int(m.group(1)), int(m.group(2)), m.group(3)
        chunk = text[m.end() : m.end() + 12000]
        im = iter_re.search(chunk)
        sm = sse_re.search(chunk)
        tm = time_re.search(chunk)
        if not (im and sm and tm):
            continue
        runs.append(
            G1Run(
                sched,
                threads,
                run_n,
                int(im.group(1)),
                float(sm.group(1)),
                float(tm.group(1)),
            )
        )
    return runs


def gap1_pairs(runs: list[G1Run]) -> list[tuple[G1Run, G1Run, bool]]:
    pairs = []
    i = 0
    while i + 1 < len(runs):
        a, b = runs[i], runs[i + 1]
        if (
            a.sched == "STATIC"
            and b.sched == "GUIDED"
            and a.threads == b.threads
            and a.run == b.run
        ):
            ok = a.iters == b.iters and abs(a.sse - b.sse) < 0.5
            pairs.append((a, b, ok))
            i += 2
        else:
            i += 1
    return pairs


# -----------------------------------------------------------------------------
# Gap 3
# -----------------------------------------------------------------------------


@dataclass
class G3Block:
    m: int
    algo: str  # naive | elkan
    sched: str  # static | guided
    km_time: float
    ratio: float | None
    iters: int
    sse: float


def parse_gap3_log(text: str) -> list[G3Block]:
    blocks: list[G3Block] = []
    title_re = re.compile(
        r"^========\s+gap3_N(\d+)_M(\d+)\s+(\w+)\s+(\w+)\s+========", re.MULTILINE
    )
    iter_re = re.compile(r"(\d+) total iterations")
    sse_re = re.compile(r"Best MSE \(SSE\) [\d.]+\s+\(([\d.]+)\)")
    time_re = re.compile(r"k-means execution time: ([\d.eE+-]+) seconds")
    ratio_re = re.compile(r"Avg distance calculations ratio: ([\d.eE+-]+)")

    for m in title_re.finditer(text):
        n_pts, m_dim, algo, sched = (
            int(m.group(1)),
            int(m.group(2)),
            m.group(3),
            m.group(4),
        )
        chunk = text[m.end() : m.end() + 15000]
        im = iter_re.search(chunk)
        sm = sse_re.search(chunk)
        tm = time_re.search(chunk)
        rm = ratio_re.search(chunk)
        if not (im and sm and tm):
            continue
        blocks.append(
            G3Block(
                m=m_dim,
                algo=algo,
                sched=sched,
                km_time=float(tm.group(1)),
                ratio=float(rm.group(1)) if rm else None,
                iters=int(im.group(1)),
                sse=float(sm.group(1)),
            )
        )
    return blocks


# -----------------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------------


def plot_gap1(pairs: list[tuple[G1Run, G1Run, bool]], out_dir: Path) -> None:
    import matplotlib.pyplot as plt

    by_t: dict[int, list[tuple[G1Run, G1Run, bool]]] = defaultdict(list)
    for a, b, ok in pairs:
        by_t[a.threads].append((a, b, ok))

    threads_sorted = sorted(by_t.keys())
    med_static_all = []
    med_guided_all = []
    med_static_ok = []
    med_guided_ok = []
    comparable_frac = []

    for t in threads_sorted:
        rows = by_t[t]
        med_static_all.append(statistics.median([x[0].km_time for x in rows]))
        med_guided_all.append(statistics.median([x[1].km_time for x in rows]))
        comp = [(x[0], x[1]) for x in rows if x[2]]
        comparable_frac.append(len(comp) / len(rows) if rows else 0.0)
        if comp:
            med_static_ok.append(statistics.median([a.km_time for a, b in comp]))
            med_guided_ok.append(statistics.median([b.km_time for a, b in comp]))
        else:
            med_static_ok.append(float("nan"))
            med_guided_ok.append(float("nan"))

    # Figure 1: grouped bars — comparable medians where available; else use all-pairs median with hatch
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = range(len(threads_sorted))
    w = 0.35
    bars_s = ax.bar(
        [i - w / 2 for i in x],
        med_static_all,
        width=w,
        label="Static build (median)",
        color="#2c7bb6",
    )
    bars_g = ax.bar(
        [i + w / 2 for i in x],
        med_guided_all,
        width=w,
        label="Guided build (median)",
        color="#d7191c",
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(t) for t in threads_sorted])
    ax.set_xlabel("OMP_NUM_THREADS")
    ax.set_ylabel("k-means execution time (s), median over 5 runs")
    ax.set_title(
        "Gap 1: Elkan — static vs guided scheduling\n"
        "(median over all pairs; T=4,8 often differ in iterations/SSE — see report)"
    )
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_gap1_elkan_static_vs_guided_median.png", dpi=150)
    plt.close(fig)

    # Figure 2: comparable-only medians (line)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ok_ts = [threads_sorted[i] for i in range(len(threads_sorted)) if comparable_frac[i] > 0]
    ok_s = [med_static_ok[i] for i in range(len(threads_sorted)) if comparable_frac[i] > 0]
    ok_g = [med_guided_ok[i] for i in range(len(threads_sorted)) if comparable_frac[i] > 0]
    ax.plot(ok_ts, ok_s, "o-", label="Static (comparable pairs only)", color="#2c7bb6")
    ax.plot(ok_ts, ok_g, "s-", label="Guided (comparable pairs only)", color="#d7191c")
    ax.set_xlabel("OMP_NUM_THREADS")
    ax.set_ylabel("Median k-means time (s)")
    ax.set_title("Gap 1: Elkan — scheduling comparison when iterations & SSE match")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_gap1_comparable_pairs_only.png", dpi=150)
    plt.close(fig)

    # CSV
    with (out_dir / "summary_gap1_medians.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "threads",
                "median_static_all",
                "median_guided_all",
                "median_static_comparable",
                "median_guided_comparable",
                "comparable_pairs",
                "total_pairs",
            ]
        )
        for i, t in enumerate(threads_sorted):
            comp_n = sum(1 for a, b, ok in by_t[t] if ok)
            w.writerow(
                [
                    t,
                    f"{med_static_all[i]:.6f}",
                    f"{med_guided_all[i]:.6f}",
                    f"{med_static_ok[i]:.6f}" if med_static_ok[i] == med_static_ok[i] else "",
                    f"{med_guided_ok[i]:.6f}" if med_guided_ok[i] == med_guided_ok[i] else "",
                    comp_n,
                    len(by_t[t]),
                ]
            )

    # Markdown table for report (copy into PDF): medians from comparable pairs only
    lines_a = [
        "<!-- Gap 1 Table A — paste into report. Medians use comparable pairs only when any exist. -->",
        "",
        "| OMP_NUM_THREADS | Median static (s) | Median guided (s) | Median ratio guided/static | Comparable / total pairs |",
        "|---:|---:|---:|---:|---|",
    ]
    for t in threads_sorted:
        rows = by_t[t]
        comp = [(a, b) for a, b, ok in rows if ok]
        tot = len(rows)
        if comp:
            ms = statistics.median([a.km_time for a, b in comp])
            mg = statistics.median([b.km_time for a, b in comp])
            ratios = [b.km_time / a.km_time for a, b in comp]
            mr = statistics.median(ratios)
            lines_a.append(
                f"| {t} | {ms:.4f} | {mg:.4f} | {mr:.4f} | {len(comp)} / {tot} |"
            )
        else:
            ms = statistics.median([a.km_time for a, b, _ in rows])
            mg = statistics.median([b.km_time for a, b, _ in rows])
            lines_a.append(f"| {t} | {ms:.4f} | {mg:.4f} | — | 0 / {tot} |")
    lines_a.extend(
        [
            "",
            "*Ratio uses comparable pairs only (same iterations and SSE within 0.5). "
            "Use “—” when no comparable pairs exist (do not claim scheduling speedup from ratio).*",
        ]
    )
    (out_dir / "TABLE_A_gap1_for_report.md").write_text(
        "\n".join(lines_a) + "\n", encoding="utf-8"
    )


def _sse_close(a: float, b: float, abs_tol: float = 0.5) -> bool:
    return abs(a - b) < abs_tol


def plot_gap3(blocks: list[G3Block], out_dir: Path) -> None:
    import matplotlib.pyplot as plt

    # One row per (M, algo, sched) — take latest if duplicates
    keymap: dict[tuple[int, str, str], G3Block] = {}
    for b in blocks:
        keymap[(b.m, b.algo, b.sched)] = b

    ms = sorted({b.m for b in blocks})

    def get(m, algo, sched):
        return keymap.get((m, algo, sched))

    ratios_elkan_s = []
    ratios_elkan_g = []
    t_naive = []
    t_elk_s = []
    t_elk_g = []
    it_naive = []
    it_elk_s = []
    it_elk_g = []
    sse_naive_l = []
    sse_elk_s_l = []
    sse_elk_g_l = []
    valid_m = []

    for m in ms:
        nb = get(m, "naive", "static")
        es = get(m, "elkan", "static")
        eg = get(m, "elkan", "guided")
        if not (nb and es and eg):
            continue
        valid_m.append(m)
        t_naive.append(nb.km_time)
        t_elk_s.append(es.km_time)
        t_elk_g.append(eg.km_time)
        ratios_elkan_s.append(es.ratio if es.ratio is not None else float("nan"))
        ratios_elkan_g.append(eg.ratio if eg.ratio is not None else float("nan"))
        it_naive.append(nb.iters)
        it_elk_s.append(es.iters)
        it_elk_g.append(eg.iters)
        sse_naive_l.append(nb.sse)
        sse_elk_s_l.append(es.sse)
        sse_elk_g_l.append(eg.sse)

    # Ratio vs M
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(valid_m, ratios_elkan_s, "o-", label="Elkan static — Avg dist calc ratio", color="#2c7bb6")
    ax.plot(valid_m, ratios_elkan_g, "s--", label="Elkan guided — Avg dist calc ratio", color="#d7191c")
    ax.set_xlabel("Dimension M")
    ax.set_ylabel("Avg distance calculations ratio (program output)")
    ax.set_title("Gap 3: Triangle-inequality effectiveness vs dimension (N=100k, K=256, T=8)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_gap3_ratio_vs_M.png", dpi=150)
    plt.close(fig)

    # Time vs M
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(valid_m, t_naive, "o-", label="Lloyd (naive)", color="#333333")
    ax.plot(valid_m, t_elk_s, "o-", label="Elkan static", color="#2c7bb6")
    ax.plot(valid_m, t_elk_g, "s--", label="Elkan guided", color="#d7191c")
    ax.set_xlabel("Dimension M")
    ax.set_ylabel("k-means execution time (s)")
    ax.set_title("Gap 3: Runtime vs dimension")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_gap3_time_vs_M.png", dpi=150)
    plt.close(fig)

    # Speedup naive / elkan (static)
    speedup = [t_naive[i] / t_elk_s[i] for i in range(len(valid_m))]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(valid_m, speedup, "o-", color="#1a9850")
    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("Dimension M")
    ax.set_ylabel("Naive time / Elkan (static) time")
    ax.set_title("Gap 3: Algorithmic speedup of Elkan (static) over Lloyd")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_gap3_speedup_naive_over_elkan_static.png", dpi=150)
    plt.close(fig)

    with (out_dir / "summary_gap3_by_M.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "M",
                "naive_time",
                "elkan_static_time",
                "elkan_guided_time",
                "ratio_elkan_static",
                "ratio_elkan_guided",
                "iters_naive",
                "iters_elkan_static",
                "iters_elkan_guided",
                "sse_naive",
                "sse_elkan_static",
                "sse_elkan_guided",
                "note_naive_vs_elkan_static",
                "note_elkan_static_vs_guided",
            ]
        )
        for i, m in enumerate(valid_m):
            sn, ss, sg = sse_naive_l[i], sse_elk_s_l[i], sse_elk_g_l[i]
            nv_es = "match" if _sse_close(sn, ss) else "differs"
            es_eg = "match" if _sse_close(ss, sg) else "differs"
            w.writerow(
                [
                    m,
                    f"{t_naive[i]:.6f}",
                    f"{t_elk_s[i]:.6f}",
                    f"{t_elk_g[i]:.6f}",
                    f"{ratios_elkan_s[i]:.6f}",
                    f"{ratios_elkan_g[i]:.6f}",
                    it_naive[i],
                    it_elk_s[i],
                    it_elk_g[i],
                    f"{sn:.6f}",
                    f"{ss:.6f}",
                    f"{sg:.6f}",
                    nv_es,
                    es_eg,
                ]
            )

    lines_b = [
        "<!-- Gap 3 Table B — paste into report. SSE match: |ΔSSE| < 0.5 on bracket total in stdout. -->",
        "",
        "| M | Lloyd time (s) | Elkan static (s) | Elkan guided (s) | Ratio static | Ratio guided |"
        " iters L / Es / Eg | naive vs Elkan(s) SSE | Elkan static vs guided SSE |",
        "|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for i, m in enumerate(valid_m):
        sn, ss, sg = sse_naive_l[i], sse_elk_s_l[i], sse_elk_g_l[i]
        nv_es = "match" if _sse_close(sn, ss) else "differs"
        es_eg = "match" if _sse_close(ss, sg) else "differs"
        it_cell = f"{it_naive[i]} / {it_elk_s[i]} / {it_elk_g[i]}"
        lines_b.append(
            f"| {m} | {t_naive[i]:.4f} | {t_elk_s[i]:.4f} | {t_elk_g[i]:.4f} | "
            f"{ratios_elkan_s[i]:.4f} | {ratios_elkan_g[i]:.4f} | {it_cell} | {nv_es} | {es_eg} |"
        )
    lines_b.extend(
        [
            "",
            "*Use “match/differs” to decide whether times are directly comparable; "
            "if Elkan static vs guided SSE differs, interpret runtime comparison cautiously.*",
        ]
    )
    (out_dir / "TABLE_B_gap3_for_report.md").write_text(
        "\n".join(lines_b) + "\n", encoding="utf-8"
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--exp-dir",
        type=Path,
        default=Path.home() / "22i-2327_F_FinalProject" / "experiments",
    )
    args = p.parse_args()
    exp = args.exp_dir
    out_dir = exp / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    gap1_path = exp / "gap1_medium_runs.txt"
    gap3_path = exp / "gap3_runs.txt"

    if not gap1_path.is_file():
        raise SystemExit(f"Missing {gap1_path}")
    if not gap3_path.is_file():
        raise SystemExit(f"Missing {gap3_path}")

    try:
        import matplotlib.pyplot as plt  # noqa: F401
    except ImportError:
        raise SystemExit("Install matplotlib: pip install matplotlib") from None

    g1_text = gap1_path.read_text(encoding="utf-8", errors="replace")
    runs = parse_gap1_log(g1_text)
    pairs = gap1_pairs(runs)
    if not pairs:
        raise SystemExit("Gap1: no STATIC/GUIDED pairs parsed — check log format")
    plot_gap1(pairs, out_dir)

    g3_text = gap3_path.read_text(encoding="utf-8", errors="replace")
    blocks = parse_gap3_log(g3_text)
    if not blocks:
        raise SystemExit("Gap3: no blocks parsed — check gap3_runs.txt section headers")
    plot_gap3(blocks, out_dir)

    print("Wrote:")
    for f in sorted(out_dir.glob("*")):
        print(" ", f)


if __name__ == "__main__":
    main()
