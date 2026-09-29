"""CLI: run Painter + Hallucinator + Rogue arena."""

from __future__ import annotations

import argparse
from pathlib import Path

from ark.hallucinator.attacks import Hallucinator
from ark.rogue.arena import RogueArena


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="ARK prompt arena (Painter/Hallucinator/Rogue)")
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--attack", type=str, default=None, help="Attack id or 'all'")
    parser.add_argument("--no-monitor", action="store_true")
    parser.add_argument("--save-glass", type=str, default=None, help="Dir to save glass JSON traces")
    args = parser.parse_args(argv)

    arena = RogueArena(use_monitor=not args.no_monitor)
    hall = Hallucinator()

    if args.attack == "all":
        results = arena.run_all_attacks(n_episodes=args.episodes, seed=args.seed)
    elif args.attack:
        attack = hall.get(args.attack)
        results = [
            arena.run(
                attack=attack,
                n_episodes=args.episodes,
                seed=args.seed,
                paint_last=bool(args.save_glass),
            )
        ]
    else:
        results = [
            arena.run(
                attack=None,
                n_episodes=args.episodes,
                seed=args.seed,
                paint_last=bool(args.save_glass),
            )
        ]

    print("ARK — Prompt Arena (aligned vs fragile vs rogue)\n")
    for r in results:
        print(r.summary())
        print()
        if args.save_glass and hasattr(r, "_glass"):
            out = Path(args.save_glass)
            out.mkdir(parents=True, exist_ok=True)
            for mode, glass in r._glass.items():  # type: ignore[attr-defined]
                path = out / f"{r.attack_id or 'none'}_{mode}.json"
                glass.save(path)
                print(f"  glass → {path}")


if __name__ == "__main__":
    main()
