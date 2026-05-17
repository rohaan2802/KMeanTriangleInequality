#!/usr/bin/env python3
"""Author .bin format: int32 N, int32 M, N*M float32."""
import argparse
import array
import random
import struct
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=100_000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-dir", type=Path, default=Path("data_gap3"))
    p.add_argument("dimensions", type=int, nargs="+", help="M values")
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    for m in args.dimensions:
        buf = array.array("f", (rng.random() for _ in range(args.n * m)))
        path = args.out_dir / f"gap3_N{args.n}_M{m}.bin"
        path.write_bytes(struct.pack("ii", args.n, m) + buf.tobytes())
        print("wrote", path, "bytes", path.stat().st_size)


if __name__ == "__main__":
    main()
