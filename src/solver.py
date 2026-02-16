from __future__ import annotations

from time import perf_counter
from typing import List, Sequence, Tuple, Optional, Dict, Any

import core


def boardFormat(area: List[List[str]], cols: Sequence[int]) -> List[str]:
    n = len(area)
    out: List[str] = []
    for r in range(n):
        row = area[r].copy()
        row[cols[r]] = "#"
        out.append("".join(row))
    return out


def solve(path: str, *, update: int = 1000) -> Dict[str, Any]:
    n, area = core.boardParser(path)

    iterations = 0  
    solution: Optional[Tuple[int, ...]] = None

    cols: List[int] = [-1] * n

    start = perf_counter()

    def dfs(row: int) -> bool:
        nonlocal iterations, solution

        if row == n:
            iterations += 1

            if update > 0 and (iterations % update == 0):
                elapsed_ms = (perf_counter() - start) * 1000
                print(f"[Live Update] iterasi: {iterations:,} | waktu: {elapsed_ms:.0f} ms")

            # still uses YOUR rule checker (will reject duplicate columns, etc.)
            if core.isValidMove(cols, n, area):
                solution = tuple(cols)
                return True
            return False

        for c in range(n):
            cols[row] = c
            if dfs(row + 1):
                return True

        cols[row] = -1
        return False

    dfs(0)

    time_ms = (perf_counter() - start) * 1000
    solved = boardFormat(area, solution) if solution is not None else None

    return {
        "n": n,
        "area": area,
        "found": solution is not None,
        "cols": list(solution) if solution is not None else None,
        "iterations": iterations,
        "solved": solved,
        "time_ms": time_ms,
    }

def run_cli() -> None:
    path = input("Masukkan path file test case (.txt): ").strip()

    try:
        result = solve(path, update=1000) 
    except Exception as e:
        print(f"Input tidak valid: {e}")
        return

    if not result["found"]:
        print("Tidak ada solusi.")
        print(f"Waktu pencarian: {result['time_ms']:.0f} ms")
        print(f"Banyak kasus yang ditinjau: {result['iterations']} kasus")
        return

    print("\n".join(result["solved"]))
    print()
    print(f"Waktu pencarian: {result['time_ms']:.0f} ms")
    print(f"Banyak kasus yang ditinjau: {result['iterations']} kasus")

    ans = input("Apakah Anda ingin menyimpan solusi? (Ya/Tidak) ").strip().lower()
    if ans in ("ya", "y"):
        out_path = input("Simpan ke file: ").strip()
        core.saveSolution(out_path, result["solved"])
        print(f"Solusi disimpan ke: {out_path}")


if __name__ == "__main__":
    run_cli()
