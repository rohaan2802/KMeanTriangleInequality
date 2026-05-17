#!/usr/bin/env python3
"""
Parse gap1_medium_runs.txt (tee output from static/guided sweep).
Extracts paired STATIC/GUIDED blocks with threads, run, iterations, SSE, k-means time.
Flags pairs where iterations or SSE differ (non-comparable for scheduling-only claims).
"""
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Run:
    sched: str  # STATIC or GUIDED
    threads: int
    run: int
    iters: int
    sse: float
    km_time: float


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "gap1_medium_runs.txt")
    text = path.read_text(encoding="utf-8", errors="replace")

    header_re = re.compile(
        r"=== threads=(\d+) run=(\d+) (STATIC|GUIDED) ==="
    )
    iter_re = re.compile(r"(\d+) total iterations")
    sse_re = re.compile(r"Best MSE \(SSE\) [\d.]+\s+\(([\d.]+)\)")
    time_re = re.compile(r"k-means execution time: ([\d.eE+-]+) seconds")

    runs: list[Run] = []
    pos = 0
    for m in header_re.finditer(text):
        threads, run_n, sched = int(m.group(1)), int(m.group(2)), m.group(3)
        chunk = text[m.end() : m.end() + 8000]
        im = iter_re.search(chunk)
        sm = sse_re.search(chunk)
        tm = time_re.search(chunk)
        if not (im and sm and tm):
            continue
        runs.append(
            Run(
                sched,
                threads,
                run_n,
                int(im.group(1)),
                float(sm.group(1)),
                float(tm.group(1)),
            )
        )

    # Pair consecutive STATIC, GUIDED with same threads & run
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
            same_path = a.iters == b.iters and abs(a.sse - b.sse) < 0.5
            pairs.append((a, b, same_path))
            i += 2
        else:
            i += 1

    print(f"Parsed {len(runs)} runs, {len(pairs)} STATIC/GUIDED pairs from {path}\n")

    by_t: dict[int, list[tuple[Run, Run, bool]]] = {}
    for a, b, ok in pairs:
        by_t.setdefault(a.threads, []).append((a, b, ok))

    for t in sorted(by_t.keys()):
        rows = by_t[t]
        comp = [(a, b) for a, b, ok in rows if ok]
        print(f"--- OMP_NUM_THREADS={t} ---")
        print(f"  comparable pairs (same iters & ~SSE): {len(comp)} / {len(rows)}")
        if comp:
            ratios = [b.km_time / a.km_time for a, b in comp]
            stat_med = statistics.median([a.km_time for a, b in comp])
            guid_med = statistics.median([b.km_time for a, b in comp])
            print(f"  median k-means time  static: {stat_med:.4f}s  guided: {guid_med:.4f}s")
            print(f"  median ratio guided/static: {statistics.median(ratios):.4f} (<1 means guided faster)")
        for a, b, ok in rows:
            flag = "OK" if ok else "DIFF_PATH"
            print(
                f"  run{a.run}  {flag}  static {a.km_time:.4f}s it{a.iters}  "
                f"guided {b.km_time:.4f}s it{b.iters}"
            )
        print()


if __name__ == "__main__":
    main()
