from __future__ import annotations

from time import perf_counter
from typing import List, Sequence, Tuple, Optional, Dict, Any, Literal, Callable
import core

Mode = Literal["pow", "fact"] #gatau bikin 2 ver
ProgressCb = Optional[Callable[[int, float, List[int], int, List[List[str]]], None]]


def boardFormat(area: List[List[str]], cols: Sequence[int]) -> List[str]:
    n = len(area)
    out: List[str] = []
    for r in range(n):
        row = area[r].copy()
        row[cols[r]] = "#"
        out.append("".join(row))
    return out



def solvePower(path: str, *, update: int = 1000, on_progress: ProgressCb = None) -> Dict[str, Any]:
    n, area = core.boardParser(path)
    if update <= 0:
        update = 1

    N = n * n
    iterations = 0
    solution: Optional[Tuple[int, ...]] = None
    start = perf_counter()

    def maybe_progress(cols_preview: List[int]) -> None:
        if on_progress is None:
            return
        if iterations % update == 0:
            elapsed_ms = (perf_counter() - start) * 1000
            on_progress(iterations, elapsed_ms, cols_preview, n, area)

    def is_valid_placement(pos: List[Tuple[int, int]]) -> bool:
        rows = [r for r, _ in pos]
        if len(set(rows)) != n:
            return False
        cols = [c for _, c in pos]
        if len(set(cols)) != n:
            return False
        used_colors = set()
        for r, c in pos:
            color = area[r][c]
            if color in used_colors:
                return False
            used_colors.add(color)
        for i in range(n):
            r1, c1 = pos[i]
            for j in range(i + 1, n):
                r2, c2 = pos[j]
                if abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1:
                    return False
        return True

    def next_combination(comb: List[int], N: int, k: int) -> bool:
        i = k - 1
        while i >= 0 and comb[i] == N - k + i:
            i -= 1
        if i < 0:
            return False  # ud kombinasi terakhir

        comb[i] += 1
        for j in range(i + 1, k):
            comb[j] = comb[j - 1] + 1
        return True

    if on_progress is not None:
        on_progress(0, 0.0, [-1] * n, n, area)
    comb: List[int] = list(range(n))

    while True:
        iterations += 1
        pos = [(idx // n, idx % n) for idx in comb]

        cols_preview = [-1] * n
        for r, c in pos:
            cols_preview[r] = c
        maybe_progress(cols_preview.copy())

        if is_valid_placement(pos):
            cols_sol = [-1] * n
            for r, c in pos:
                cols_sol[r] = c
            solution = tuple(cols_sol)
            break

        if not next_combination(comb, N, n):
            break  # udh semua kombinasi

    time_ms = (perf_counter() - start) * 1000
    solved = boardFormat(area, solution) if solution is not None else None
    return {
        "mode": "pow",
        "n": n,
        "area": area,
        "found": solution is not None,
        "cols": list(solution) if solution is not None else None,
        "iterations": iterations,
        "solved": solved,
        "time_ms": time_ms,
    }




# cara enumerasi permutasi 
def solveFactorial(path: str, *, update: int = 1000, on_progress: ProgressCb = None) -> Dict[str, Any]:
    n, area = core.boardParser(path)

    if update <= 0:
        update = 1

    iterations = 0
    solution: Optional[Tuple[int, ...]] = None

    cols: List[int] = list(range(n))
    start = perf_counter()

    def maybe_progress() -> None:
        if on_progress is None:
            return
        if iterations % update == 0:
            elapsed_ms = (perf_counter() - start) * 1000
            on_progress(iterations, elapsed_ms, cols.copy(), n, area)

    def next_permutation(a: List[int]) -> bool:
        i = len(a) - 2
        while i >= 0 and a[i] >= a[i + 1]:
            i -= 1
        if i < 0:
            return False  # udah all permutations

        j = len(a) - 1
        while a[j] <= a[i]:
            j -= 1

        a[i], a[j] = a[j], a[i]

        l, r = i + 1, len(a) - 1
        while l < r:
            a[l], a[r] = a[r], a[l]
            l += 1
            r -= 1

        return True

    # preview empty board di awal
    if on_progress is not None:
        on_progress(0, 0.0, cols.copy(), n, area)

    while True:
        iterations += 1
        maybe_progress()

        if core.isValidMove(cols, n, area):
            solution = tuple(cols)
            break

        if not next_permutation(cols):
            break  # udah all n!

    time_ms = (perf_counter() - start) * 1000
    solved = boardFormat(area, solution) if solution is not None else None

    return {
        "mode": "fact",
        "n": n,
        "area": area,
        "found": solution is not None,
        "cols": list(solution) if solution is not None else None,
        "iterations": iterations,
        "solved": solved,
        "time_ms": time_ms,
    }





def solve( path: str, *, mode: Mode = "pow", update: int = 1000, on_progress: ProgressCb = None) -> Dict[str, Any]:
    if update <= 0:
        update = 1

    if mode == "pow":
        return solvePower(path, update=update, on_progress=on_progress)
    elif mode == "fact":
        return solveFactorial(path, update=update, on_progress=on_progress)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'pow' or 'fact'.")
