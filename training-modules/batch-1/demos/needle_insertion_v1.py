"""main training demo for goldfish.

usage:
    python demos/needle_insertion_v1.py --quick
    python demos/needle_insertion_v1.py --timesteps 300000 --output ./results
"""

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--timesteps", type=int, default=300_000)
    parser.add_argument("--output", default="./results")
    args = parser.parse_args()
    print(f"goldfish demo, quick={args.quick}, timesteps={args.timesteps}")


if __name__ == "__main__":
    main()
