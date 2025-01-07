from typing import Generator
import csv
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd


def clear_grid() -> None:
    if len(cells) > 0:
        for cell in cells:
            cell.destroy()
        cells.clear()


def pick_delimiter(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        first = f.readline()
        second = f.readline()
    comma_first = len(first.split(","))
    comma_second = len(second.split(","))
    if comma_first > 1 and comma_first == comma_second:
        return ","
    semi_first = len(first.split(";"))
    semi_second = len(second.split(";"))
    if semi_first > 1 and semi_first == semi_second:
        return ";"
    tab_first = len(first.split("\t"))
    tab_second = len(second.split("\t"))
    if tab_first > 1 and tab_first == tab_second:
        return "\t"
    pipe_first = len(first.split("|"))
    pipe_second = len(second.split("|"))
    if pipe_first > 1 and pipe_first == pipe_second:
        return "|"
    display_log("Невозможно подобрать разделитель по первым двум строкам файла")
    return ""


def display_log(message: str) -> None:
    cell = ttk.Label(scrollable_frame, text=message)
    global row_num
    cell.grid(row=row_num, column=0, sticky="ew")
    row_num += 1
    cells.append(cell)


def select_file() -> None:
    filename = fd.askopenfilename(
        title="Выберите файл",
        initialdir="/",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
    )
    if filename:
        clear_grid()
        canvas.yview_moveto(0.0)
        canvas.xview_moveto(0.0)
        delimiter = pick_delimiter(filename)
        if delimiter:
            global pages
            pages = row_reader(filename, delimiter)
            next_page.config(state=tk.NORMAL)
            next_page.invoke()
        else:
            next_page.config(state=tk.DISABLED)


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


canvas: tk.Canvas
scrollable_frame: ttk.Frame
row_num = 0
pages: Generator[list[str]]
next_page: tk.Button
cells: list[ttk.Label] = []


def main() -> None:
    win = tk.Tk()
    win.geometry("700x600")
    win.title("Предпросмотр csv")
    tk.Button(win, text="Выбрать файл", command=select_file).pack(pady=5)
    global next_page
    next_page = tk.Button(
        win, text="Следующая страница", command=draw_next_page, state=tk.DISABLED
    )
    next_page.pack(pady=5)
    global canvas
    canvas = tk.Canvas(win)
    scroll_hor = ttk.Scrollbar(win, orient="horizontal", command=canvas.xview)
    scroll_ver = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    global scrollable_frame
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
