"""Leak probe. Prints 1.0 for a split with itself and 0.0 for train against test."""

from __future__ import annotations

from proctor_forge.generate import generate


def overlap(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def main() -> None:
    train = {task.signature for task, _ in generate("train")}
    test = {task.signature for task, _ in generate("test")}
    same = overlap(train, train)
    cross = overlap(train, test)
    print(f"{same:.1f} {cross:.1f}")
    if same != 1.0 or cross != 0.0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
