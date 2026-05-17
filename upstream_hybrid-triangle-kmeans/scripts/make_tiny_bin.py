#!/usr/bin/env python3
"""Dataset format: int32 N, int32 M, then N*M float32 (see Util/Dataset.cpp)."""
import argparse
import array
import random
import struct


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=2000)
    p.add_argument("--m", type=int, default=16)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("-o", default="tiny.bin")
    args = p.parse_args()
    rng = random.Random(args.seed)
    buf = array.array("f", (rng.random() for _ in range(args.n * args.m)))
    with open(args.o, "wb") as f:
        f.write(struct.pack("ii", args.n, args.m))
        f.write(buf.tobytes())
    print(f"Wrote {args.o}  (N={args.n}, M={args.m})")


if __name__ == "__main__":
    main()
