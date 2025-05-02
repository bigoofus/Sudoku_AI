import tkinter as tk

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku GUI")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        self.cell_size = 66
        self.canvas = tk.Canvas(root, width=600, height=600)
        self.canvas.pack()

        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.draw_grid()
        self.create_cells()
        self.prefill_example()

    def draw_grid(self):
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            # Vertical
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, 9 * self.cell_size, width=thickness)
            # Horizontal
            self.canvas.create_line(0, i * self.cell_size, 9 * self.cell_size, i * self.cell_size, width=thickness)

    def create_cells(self):
        for i in range(9):
            for j in range(9):
                entry = tk.Entry(self.root, font=('Arial', 24), justify='center', bd=0)
                entry.place(
                    x=j * self.cell_size + 3,
                    y=i * self.cell_size + 3,
                    width=self.cell_size - 6,
                    height=self.cell_size - 6
                )
                self.entries[i][j] = entry

    def prefill_example(self):
        puzzle = [
            [7, 9, 0, 1, 3, 6, 0, 0, 0],
            [4, 0, 0, 0, 7, 0, 3, 0, 0],
            [1, 0, 0, 2, 4, 0, 9, 7, 5],
            [5, 0, 6, 0, 0, 2, 0, 0, 7],
            [0, 7, 0, 0, 1, 0, 0, 0, 8],
            [8, 0, 6, 9, 2, 0, 0, 5, 0],
            [6, 1, 0, 0, 2, 0, 5, 0, 3],
            [3, 0, 0, 0, 0, 4, 0, 0, 9],
            [0, 2, 4, 0, 3, 5, 0, 0, 0]
        ]
        puzzle2=[
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]

        for i in range(9):
            for j in range(9):
                if puzzle2[i][j] != 0:
                    entry = self.entries[i][j]
                    entry.insert(0, str(puzzle2[i][j]))
                    entry.config(state='disabled', disabledforeground='black', font=('Arial', 24, 'bold'))

if __name__ == "__main__":
    root = tk.Tk()
    gui = SudokuGUI(root)
    root.mainloop()
