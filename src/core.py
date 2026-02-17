from __future__ import annotations
from typing import Tuple, Set, List, Sequence
from pathlib import Path

def boardParser(path: str | Path) -> Tuple[int, List[List[str]]]:
    p = Path(path)
    if not p.exists():
        raise ValueError(f"File not found: {p}")
    
    lines: List[str] = []
    for ln in p.read_text(encoding="utf-8").splitlines():
        ln = ln.strip().upper()
        if ln:
            lines.append(ln)

    if not lines:
        raise ValueError(f"Empty file: {p}")
    
    n = len(lines)
    if any(len(row) != n for row in lines):
        wrong = [(i, len(lines[i])) for i in range(n) if len(lines[i]) != n]
        raise ValueError(f"Invalid board, grid must be square (NXN). Wrong rows: {wrong}")
    
    area = [list(row) for row in lines]
    validateBoard(n, area)
    return n, area

def validateBoard(n: int, area: List[List[str]]) -> None:
    if n <= 0:
        raise ValueError(f"Invalid board size. {n} must be positive.")
    
    if len(area) != n or any(len(row) != n for row in area):
        raise ValueError(f"Invalid board size, grid must be square (NXN).")
    
    for r in range(n):
        for c in range(n):
            cell = area[r][c]
            if len(cell) != 1 or not cell.isalpha() or not cell.isupper():
                raise ValueError(f"Invalid cell value at ({r}, {c}): '{cell}'. Must be a single uppercase letter.")
            
    dif = diffAreas(n, area)
    if len(dif) != n:
        raise ValueError(f"Invalid board, must contain exactly {n} different letters. Found: {dif}")
    

def diffAreas(n: int, area: List[List[str]]) -> Set[str]:
    s: set[str] = set()
    for r in range(n):
        for c in range(n):
            s.add(area[r][c])
    return s



def isValidMove(cols: Sequence[int], n: int, region: List[List[str]]) -> bool:
    if len(cols) != n:
            return False
    scols = set()
    for c in cols:
        if c < 0 or c >= n:
            return False
        if c in scols:
            return False
        scols.add(c)

    # regions must be unique
    sareas: Set[str] = set()
    for r in range(n):
        c = cols[r]
        rid = region[r][c]
        if rid in sareas:
            return False
        sareas.add(rid)

    for r1 in range(n):
        c1 = cols[r1]
        for r2 in range(r1 + 1, n):
            c2 = cols[r2]
            if abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1:
                return False

    return True

def saveSolution(path: str | Path, lines: Sequence[str]) -> None:
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")