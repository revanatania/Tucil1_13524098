from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Optional, Tuple, Callable, Literal
import os

from PIL import Image, ImageDraw, ImageFont

import core
import solver

APP_W = 1000
APP_H = 650

HEADER_BG = "#d3d8db"
WINDOW_BG = "white"

BTN_BG = "#e8e8e8"
BTN_BG_SOLVE = "#d9d9d9"
BTN_FG = "#111"

TEXT_FG = "#111"
SUBTEXT_FG = "#555"
ERROR_FG = "#460b0b" 

BTN_OPT_OFF = "#e8e8e8"
BTN_OPT_ON = "#b7d7ff"  

CANVAS_SIZE = 420
CANVAS_PAD = 10

QUEEN_COLOR = "#C9A227"
GRID_OUTLINE = "#222"
OUTER_BORDER = "#111"

PASTEL_PALETTE = [
    "#b7d7ff", "#c6f1d6", "#ffd8b5", "#e6c6ff", "#ffb7c5",
    "#fff3b0", "#b7ffd8", "#c7c7c7", "#d7c7b7", "#b0e0ff",
    "#d0ffb0", "#ffddb0", "#c0b0ff", "#b0ffd0", "#ffd0e6",
    "#d6f6f2", "#ffe7a3", "#cfe0ff", "#f6d6ff", "#d7f0b3",
    "#fddede", "#d9f0ff", "#f0d9ff", "#e3ffd9", "#fff0d9",
    "#d9fff6",
]


def build_color_map(area: List[List[str]]) -> Dict[str, str]:
    letters = sorted({ch for row in area for ch in row})
    return {ch: PASTEL_PALETTE[i % len(PASTEL_PALETTE)] for i, ch in enumerate(letters)}


def choose_update(mode: str, n: int) -> int:
    n = max(0, int(n))

    if mode == "fact":
        if n <= 10:
            return 1_000
        if n <= 14:
            return 5_000
        if n <= 18:
            return 20_000
        if n <= 22:
            return 50_000
        return 100_000

    if n <= 7:
        return 10_000
    if n <= 10:
        return 1_000_000
    if n <= 14:
        return 500_000
    return 1_000_000


def save_solution_txt(path: str, res: Dict[str, Any]) -> None:
    mode = res.get("mode", "-")
    time_ms = res.get("time_ms", "-")
    iterations = res.get("iterations", "-")
    solved = res.get("solved", None)

    with open(path, "w", encoding="utf-8") as f:
        f.write("LinkedIn Queens Solver Result\n")
        f.write(f"Mode       : {mode}\n")
        f.write(f"Time (ms)  : {time_ms}\n")
        f.write(f"Iterations : {iterations}\n")
        f.write("\n")

        if not solved:
            f.write("No solution.\n")
            return

        for line in solved:
            f.write(line + "\n")


def save_board_as_png(area, cols, out_path, size=800):
    n = len(area)
    cell = size // n

    img = Image.new("RGB", (cell * n, cell * n), "white")
    draw = ImageDraw.Draw(img)

    cmap = build_color_map(area)
    for r in range(n):
        for c in range(n):
            x1 = c * cell
            y1 = r * cell
            x2 = x1 + cell
            y2 = y1 + cell

            draw.rectangle(
                [x1, y1, x2, y2],
                fill=cmap.get(area[r][c], "#ddd"),
                outline="black"
            )

    #  queens
    if cols:
        try:
            font = ImageFont.truetype("seguisym.ttf", cell // 2)
        except Exception:
            font = ImageFont.load_default()

        for r, c in enumerate(cols):
            if c < 0:
                continue
            text = "♛"
            bbox = draw.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text(
                (c * cell + (cell - w) // 2, r * cell + (cell - h) // 2),
                text,
                fill=(201, 162, 39),
                font=font
            )

    img.save(out_path)

def run_gui() -> None:
    root = tk.Tk()
    root.title("LinkedIn Queens Solver")
    root.geometry(f"{APP_W}x{APP_H}")
    root.configure(bg=WINDOW_BG)

    selected_path = tk.StringVar(value="")
    time_var = tk.StringVar(value="Time: - ms")
    iter_var = tk.StringVar(value="Iterations: -")
    status_var = tk.StringVar(value="")

    mode_var = tk.StringVar(value="pow")

    optimize_on = tk.BooleanVar(value=False)

    last_result: Dict[str, Any] = {"solved": None, "mode": None}

    loaded_board: Dict[str, Any] = {"n": 0, "area": None}

    def style_button(btn: tk.Button, *, bg: str) -> None:
        btn.configure(
            font=("Segoe UI", 12, "bold"),
            bg=bg,
            fg=BTN_FG,
            activebackground=bg,
            activeforeground=BTN_FG,
            relief="flat",
            bd=0,
            padx=18,
            pady=6,
            cursor="hand2",
        )

    def set_busy(is_busy: bool) -> None:
        state = "disabled" if is_busy else "normal"
        btn_upload.configure(state=state)
        btn_solve.configure(state=state)
        btn_optimize.configure(state=state)
        rb_pow.configure(state=state)
        rb_fact.configure(state=state)

        can_save = (not is_busy) and bool(last_result.get("solved"))
        btn_save.configure(state=("normal" if can_save else "disabled"))

    def sync_optimize_button() -> None:
        bg = BTN_OPT_ON if optimize_on.get() else BTN_OPT_OFF
        style_button(btn_optimize, bg=bg)
        btn_optimize.configure(font=("Segoe UI", 10, "bold"), padx=16, pady=5)

    def set_mode(new_mode: str) -> None:
        if new_mode not in ("pow", "fact"):
            new_mode = "pow"
        mode_var.set(new_mode)
        optimize_on.set(new_mode == "fact")
        sync_optimize_button()

    header = tk.Frame(root, bg=HEADER_BG, height=80)
    header.pack(fill="x", padx=40, pady=(30, 15))
    header.pack_propagate(False)

    title = tk.Label(
        header,
        text="Linkedin Queens Solver",
        font=("Segoe UI", 28, "bold"),
        bg=HEADER_BG,
        fg="#222",
    )
    title.pack(expand=True)

    top_btn_row = tk.Frame(root, bg=WINDOW_BG)
    top_btn_row.pack(fill="x", padx=40)

    filler_left = tk.Frame(top_btn_row, bg=WINDOW_BG)
    filler_left.pack(side="left", expand=True, fill="x")

    btn_save = tk.Button(top_btn_row, text="Save")
    style_button(btn_save, bg=BTN_BG)
    btn_save.pack(side="left", padx=20, pady=10)

    btn_upload = tk.Button(top_btn_row, text="Upload")
    style_button(btn_upload, bg=BTN_BG)
    btn_upload.pack(side="left", padx=20, pady=10)

    filler_right = tk.Frame(top_btn_row, bg=WINDOW_BG)
    filler_right.pack(side="left", expand=True, fill="x")

    main = tk.Frame(root, bg=WINDOW_BG)
    main.pack(fill="both", expand=True, padx=40, pady=10)

    left = tk.Frame(main, bg=WINDOW_BG)
    left.pack(side="left", fill="both", expand=True)

    right = tk.Frame(main, bg=WINDOW_BG, width=280)
    right.pack(side="right", fill="y")
    right.pack_propagate(False)

    canvas_border = tk.Frame(left, bg="#f2f2f2", padx=18, pady=18)
    canvas_border.pack(pady=10)

    canvas = tk.Canvas(
        canvas_border,
        width=CANVAS_SIZE,
        height=CANVAS_SIZE,
        bg="white",
        highlightthickness=0
    )
    canvas.pack()

    btn_solve = tk.Button(left, text="Solve")
    style_button(btn_solve, bg=BTN_BG_SOLVE)
    btn_solve.pack(pady=10)

    mode_row = tk.Frame(left, bg=WINDOW_BG)
    mode_row.pack(pady=(0, 5))

    def on_mode_radio() -> None:
        set_mode(mode_var.get())

    rb_pow = tk.Radiobutton(
        mode_row, text="Power (n^n)", variable=mode_var, value="pow",
        command=on_mode_radio,
        bg=WINDOW_BG, fg=SUBTEXT_FG, activebackground=WINDOW_BG, selectcolor=WINDOW_BG
    )
    rb_fact = tk.Radiobutton(
        mode_row, text="Factorial (n!)", variable=mode_var, value="fact",
        command=on_mode_radio,
        bg=WINDOW_BG, fg=SUBTEXT_FG, activebackground=WINDOW_BG, selectcolor=WINDOW_BG
    )
    rb_pow.pack(side="left", padx=10)
    rb_fact.pack(side="left", padx=10)

    info = tk.Frame(right, bg=WINDOW_BG)
    info.pack(pady=120, anchor="w")

    lbl_time = tk.Label(info, textvariable=time_var, font=("Segoe UI", 16), bg=WINDOW_BG, fg=TEXT_FG)
    lbl_iter = tk.Label(info, textvariable=iter_var, font=("Segoe UI", 16), bg=WINDOW_BG, fg=TEXT_FG)
    lbl_time.pack(anchor="w", pady=6)
    lbl_iter.pack(anchor="w", pady=(6, 12))

    btn_optimize = tk.Button(info, text="Optimize")
    sync_optimize_button()
    btn_optimize.pack(anchor="w")

    lbl_status = tk.Label(
        right,
        textvariable=status_var,
        font=("Segoe UI", 10),
        bg=WINDOW_BG,
        fg=SUBTEXT_FG,
        wraplength=260,
        justify="left"
    )
    lbl_status.pack(side="bottom", pady=10)


    # validate input dlu
    def validate_board_or_raise(n: int, area: List[List[str]]) -> None:
        # jlh warna
        letters = sorted({ch for row in area for ch in row})
        found_set = set(letters)
        if len(found_set) != n:
            raise ValueError(f"Invalid board, must contain exactly {n} different color area.")

        # area gabole pisah
        pos_by_letter: Dict[str, List[Tuple[int, int]]] = {ch: [] for ch in found_set}
        for r in range(n):
            for c in range(n):
                pos_by_letter[area[r][c]].append((r, c))

        def is_connected(letter: str) -> bool:
            cells = pos_by_letter.get(letter, [])
            if not cells:
                return False
            cell_set = set(cells)
            stack = [cells[0]]
            visited = {cells[0]}

            while stack:
                cr, cc = stack.pop()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if (nr, nc) in cell_set and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        stack.append((nr, nc))

            return len(visited) == len(cell_set)

        for ch in letters:
            if not is_connected(ch):
                raise ValueError(
                    f"Invalid board, region is not contiguous."
                )


    def draw_error(msg: str) -> None:
        canvas.delete("all")
        canvas.create_rectangle(0, 0, CANVAS_SIZE, CANVAS_SIZE, fill="white", outline="")
        canvas.create_text(
            CANVAS_SIZE // 2,
            CANVAS_SIZE // 2,
            text=msg,
            fill=ERROR_FG,
            font=("Segoe UI", 18, "bold"),
            width=CANVAS_SIZE - 70,
            justify="center"
        )

    def draw_board(area: List[List[str]], cols: Optional[List[int]] = None) -> None:
        canvas.delete("all")
        n = len(area)
        if n <= 0:
            draw_error("Board kosong.")
            return

        cmap = build_color_map(area)

        pad = CANVAS_PAD
        W = CANVAS_SIZE - 2 * pad
        H = CANVAS_SIZE - 2 * pad
        cell = max(1, min(W // n, H // n))

        board_w = cell * n
        board_h = cell * n
        x0 = (CANVAS_SIZE - board_w) // 2
        y0 = (CANVAS_SIZE - board_h) // 2

        for r in range(n):
            for c in range(n):
                x1 = x0 + c * cell
                y1 = y0 + r * cell
                x2 = x1 + cell
                y2 = y1 + cell
                ch = area[r][c]
                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=cmap.get(ch, "#ddd"),
                    outline=GRID_OUTLINE,
                    width=1
                )

        canvas.create_rectangle(x0, y0, x0 + board_w, y0 + board_h, outline=OUTER_BORDER, width=3)

        if cols is not None:
            q_font = ("Segoe UI Symbol", max(12, cell // 2), "bold")
            for r, c in enumerate(cols):
                if c is None or c < 0 or c >= n:
                    continue
                cx = x0 + c * cell + cell // 2
                cy = y0 + r * cell + cell // 2
                canvas.create_text(cx, cy, text="♛", font=q_font, fill=QUEEN_COLOR)


    def on_upload() -> None:
        path = filedialog.askopenfilename(
            title=" ",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        selected_path.set(path)
        status_var.set(f"Selected: {path}")

        try:
            n, area = core.boardParser(path)
            validate_board_or_raise(n, area)

            loaded_board["n"] = n
            loaded_board["area"] = area

            draw_board(area, cols=None)
            time_var.set("Time: - ms")
            iter_var.set("Iterations: -")

            last_result.clear()
            last_result.update({"solved": None, "mode": None})
            set_busy(False)
        except Exception as e:
            draw_error(f"Invalid input:\n{e}")
            status_var.set("Invalid input loaded.")
            time_var.set("Time: - ms")
            iter_var.set("Iterations: -")
            loaded_board["n"] = 0
            loaded_board["area"] = None
            last_result.clear()
            last_result.update({"solved": None, "mode": None})
            set_busy(False)

    def on_save() -> None:
        if not last_result.get("solved"):
            messagebox.showinfo("Info", "No solution to save.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Simpan hasil",
            defaultextension=".txt",
            filetypes=[
                ("Text file (.txt)", "*.txt"),
                ("Image (.png)", "*.png"),
            ],
        )
        if not out_path:
            return

        ext = out_path.lower().split(".")[-1]

        try:
            if ext == "txt":
                save_solution_txt(out_path, last_result)
                status_var.set(f"Saved TXT: {out_path}")

            elif ext == "png":
                area = last_result.get("area")
                cols = last_result.get("cols")
                if not area or not cols:
                    messagebox.showerror("Error", "No board to save.")
                    return

                save_board_as_png(area, cols, out_path)
                status_var.set(f"Saved PNG: {out_path}")

            else:
                messagebox.showerror("Error", "Choose .txt or .png.")
                return

        except Exception as e:
            messagebox.showerror("Error", f"Save Failed:\n{e}")

    def run_solve(mode: str) -> None:
        path = selected_path.get().strip()
        if not path:
            messagebox.showerror("Error", "Upload to choose .txt file")
            return
        try:
            n0, area0 = core.boardParser(path)
            validate_board_or_raise(n0, area0)
            loaded_board["n"] = n0
            loaded_board["area"] = area0
        except Exception as e:
            draw_error(f"Invalid input:\n{e}")
            status_var.set("Invalid input.")
            time_var.set("Time: - ms")
            iter_var.set("Iterations: -")
            set_busy(False)
            return

        n = int(loaded_board.get("n") or 0)
        update = choose_update(mode, n)

        set_busy(True)
        status_var.set(f"Solving mode={mode}... (update every {update:,})")
        time_var.set("Time: - ms")
        iter_var.set("Iterations: -")

        def progress_cb(iterations: int, elapsed_ms: float, cols_snapshot: List[int], n_: int, area_: List[List[str]]):
            def ui_update():
                time_var.set(f"Time: {elapsed_ms:.0f} ms")
                iter_var.set(f"Iterations: {iterations:,}")
                draw_board(area_, cols=cols_snapshot)
                status_var.set(f"Solving mode={mode}... (update every {update:,})")
            root.after(0, ui_update)

        def worker():
            try:
                try:
                    res = solver.solve(path, mode=mode, update=update, on_progress=progress_cb) 
                except TypeError:
                    res = solver.solve(path, mode=mode, update=update) 
            except Exception as e:
                res = {"_error": str(e)}

            def done_on_main():
                if "_error" in res:
                    set_busy(False)
                    draw_error(f"Error:\n{res['_error']}")
                    status_var.set("Solve failed.")
                    time_var.set("Time: - ms")
                    iter_var.set("Iterations: -")
                    last_result.clear()
                    last_result.update({"solved": None, "mode": None})
                    return

                last_result.clear()
                last_result.update(res)

                time_var.set(f"Time: {res.get('time_ms', 0):.0f} ms")
                iter_var.set(f"Iterations: {res.get('iterations', 0):,}")

                if not res.get("solved"):
                    draw_error("No solution.")
                    status_var.set("No solution.")
                    set_busy(False)
                    return

                area = res.get("area")
                cols = res.get("cols")
                if area and cols:
                    draw_board(area, cols=cols)
                    status_var.set(f"Solved (mode={res.get('mode', mode)})")
                else:
                    draw_error("Solved, but missing board data.")

                set_busy(False)

            root.after(0, done_on_main)

        threading.Thread(target=worker, daemon=True).start()

    def on_solve() -> None:
        run_solve(mode_var.get())

    def on_optimize_toggle() -> None:
        if optimize_on.get():
            set_mode("pow")
        else:
            set_mode("fact")

    btn_upload.configure(command=on_upload)
    btn_solve.configure(command=on_solve)
    btn_optimize.configure(command=on_optimize_toggle)
    btn_save.configure(command=on_save)
    btn_save.configure(state="disabled")

    set_mode("pow")
    draw_error("Upload to choose .txt file")

    root.mainloop()
