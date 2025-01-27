from collections.abc import Generator
import csv
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd


def clear_grid() -> None:
    global row_num
    row_num = 0
    for cell in cells:
        cell.destroy()
    cells.clear()


def pick_delimiter(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        first = f.readline()
        second = f.readline()
    first_len = len(first.split(","))
    second_len = len(second.split(","))
    if first_len > 1 and first_len == second_len:
        return ","
    first_len = len(first.split(";"))
    second_len = len(second.split(";"))
    if first_len > 1 and first_len == second_len:
        return ";"
    first_len = len(first.split("\t"))
    second_len = len(second.split("\t"))
    if first_len > 1 and first_len == second_len:
        return "\t"
    first_len = len(first.split("|"))
    second_len = len(second.split("|"))
    if first_len > 1 and first_len == second_len:
        return "|"
    return ""


def display_log(message: str) -> None:
    cell = ttk.Label(scrollable_frame, text=message)
    cell.grid(row=row_num, column=0, sticky="ew")
    cells.append(cell)


def select_file() -> None:
    filename = fd.askopenfilename(
        title="Выберите файл",
        initialdir="/",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
    )
    if not filename:
        return None

    if len(cells) > 0:
        clipboard_button.config(state=tk.DISABLED)
        clear_grid()
        canvas.yview_moveto(0.0)
        canvas.xview_moveto(0.0)
    delimiter = pick_delimiter(filename)
    if not delimiter:
        next_page.config(state=tk.DISABLED)
        display_log("Невозможно подобрать разделитель по первым двум строкам файла")
        return None

    global pages, current_filename
    current_filename = filename
    pages = row_reader(filename, delimiter)
    next_page.config(state=tk.NORMAL)
    next_page.invoke()
    clipboard_button.config(state=tk.NORMAL)


def draw_next_page() -> None:
    page_data = (next(pages, None) for _ in range(25))
    global row_num
    for page in page_data:
        if page is None:
            next_page.config(state=tk.DISABLED)
            display_log("Конец файла")
            break
        for col_index, col in enumerate(page):
            cell = ttk.Label(scrollable_frame, text=col, borderwidth=1, relief="solid")
            cell.grid(row=row_num, column=col_index, padx=0, pady=0, sticky="nsew")
            cells.append(cell)
        row_num += 1


def row_reader(path: str, delimiter: str) -> Generator[list[str]]:
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.reader(f, delimiter=delimiter):
            yield row


def drawn_text() -> str:
    with open(current_filename, "r", encoding="utf-8") as f:
        return "".join((f.readline() for _ in range(row_num)))


def copy_clipboard() -> None:
    win.clipboard_clear()
    win.clipboard_append(drawn_text())


win: tk.Tk
clipboard_button: tk.Button
current_filename: str
canvas: tk.Canvas
scrollable_frame: ttk.Frame
row_num = 0
pages: Generator[list[str]]
next_page: tk.Button
cells: list[ttk.Label] = []


def main() -> None:
    global win, next_page, clipboard_button, canvas, scrollable_frame
    win = tk.Tk()
    win.geometry("700x600")
    win.title("Предпросмотр csv")
    grid_frame = tk.Frame(win)
    grid_frame.pack(pady=5)
    tk.Button(grid_frame, text="Выбрать файл", command=select_file).grid(
        row=0, column=0, padx=5
    )
    next_page = tk.Button(
        grid_frame, text="Следующая страница", command=draw_next_page, state=tk.DISABLED
    )
    next_page.grid(row=0, column=1, padx=5)
    clipboard_button = tk.Button(
        grid_frame,
        text="Копировать в буфер обмена",
        command=copy_clipboard,
        state=tk.DISABLED,
    )
    clipboard_button.grid(row=0, column=2, padx=5)
    canvas = tk.Canvas(win)
    scroll_hor = ttk.Scrollbar(win, orient="horizontal", command=canvas.xview)
    scroll_ver = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scroll_ver.pack(side="right", fill="y")
    scroll_hor.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.configure(yscrollcommand=scroll_ver.set)
    canvas.configure(xscrollcommand=scroll_hor.set)
    win.mainloop()


if __name__ == "__main__":
    main()
