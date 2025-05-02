import tkinter as tk
import sys
from tkinter import scrolledtext  # Import for the log window
from backend import SudokuCSP  # Adjust the import if the backend is named differently



class LogStream:
    def __init__(self, log_widget, log_file="log.txt"):
        self.log_widget = log_widget
        self.log_file = log_file

    def write(self, message):
        # Insert message into the log widget and auto-scroll to the latest message
        self.log_widget.insert(tk.END, message)
        self.log_widget.yview(tk.END)

        # Log the message to the log file
        with open(self.log_file, 'a') as file:
            file.write(message)

    def flush(self):
        pass  # Needed to avoid any errors when flushing the stream

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        self.cell_size = 66
        self.canvas = tk.Canvas(root, width=600, height=600, bg='white')
        self.canvas.pack()

        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.prefilled = [[False for _ in range(9)] for _ in range(9)]

        self.draw_grid()
        self.create_cells()

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Mode 1: Solve Example", command=self.solve_example).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Mode 2: Solve User Input", command=self.solve_user_input).grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Clear Board", command=self.clear_board).grid(row=0, column=2, padx=10)

        # Log window
        self.log_window = None  # To store reference to the log window
        self.create_log_window()

        # Redirect stdout to capture prints
        sys.stdout = LogStream(self.log_text, log_file="log.txt")

    def draw_grid(self):
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, 9 * self.cell_size, width=thickness)
            self.canvas.create_line(0, i * self.cell_size, 9 * self.cell_size, i * self.cell_size, width=thickness)

    def create_cells(self):
        vcmd = (self.root.register(self.validate_entry), "%P")
        for i in range(9):
            for j in range(9):
                entry = tk.Entry(self.root, font=('Arial', 24), justify='center', bd=0, validate="key", validatecommand=vcmd)
                entry.place(
                    x=j * self.cell_size + 3,
                    y=i * self.cell_size + 3,
                    width=self.cell_size - 6,
                    height=self.cell_size - 6
                )
                self.entries[i][j] = entry

    def validate_entry(self, value):
        return value.isdigit() and 0 <= int(value) <= 9 if value else True

    def clear_board(self):
        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                entry.config(state='normal')
                entry.delete(0, tk.END)

    def solve_example(self):
        self.clear_board()
        
        puzzle = [
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
        self.prefilled = [[puzzle[i][j] != 0 for j in range(9)] for i in range(9)]

        print("Board before solving:\n")
        print(puzzle)
        print("\n\n\n")

        for i in range(9):
            for j in range(9):
                val = puzzle[i][j]
                if val != 0:
                    entry = self.entries[i][j]
                    entry.insert(0, str(val))
                    entry.config(state='disabled', disabledforeground='black', font=('Arial', 24, 'bold'))
                    self.prefilled[i][j] = True
                else:
                    self.prefilled[i][j] = False

        # Log the action
        print("Starting to solve Example puzzle...")
        
        # === BACKEND SOLVE ===
        csp = SudokuCSP(copy_grid(puzzle))
        csp.solve()
        self.set_board(csp.grid)

        # Log the result
        print("Example puzzle solved.")
        print("Solved Board:\n")
        print(csp.grid)
        print("\n\n\n")

    def solve_user_input(self):
        puzzle = self.get_current_board()
        self.prefilled = [[puzzle[i][j] != 0 for j in range(9)] for i in range(9)]
        print("Board before solving:\n")
        print(puzzle)
        print("\n\n\n")

        # Log the action
        print("Starting to solve user input puzzle...")

        # === BACKEND SOLVE ===
        csp = SudokuCSP(copy_grid(puzzle))
        csp.solve()
        self.set_board(csp.grid)

        # Log the result
        print("User input puzzle solved.")
        print("Solved Board:\n")
        print(csp.grid)
        print("\n\n\n")

    def get_current_board(self):
        board = []
        for i in range(9):
            row = []
            for j in range(9):
                val = self.entries[i][j].get()
                row.append(int(val) if val.isdigit() else 0)
            board.append(row)
        return board

    def set_board(self, board):
        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                entry.config(state='normal')  # Allow editing for now to update the value
                entry.delete(0, tk.END)
                if board[i][j] != 0:
                    entry.insert(0, str(board[i][j]))
                    if hasattr(self, 'prefilled') and not self.prefilled[i][j]:
                        entry.config(fg='blue', font=('Arial', 24, 'bold'))  # Solved cells
                    else:
                        entry.config(fg='black', font=('Arial', 24, 'bold'))  # Pre-filled cells
                else:
                    entry.config(fg='black', font=('Arial', 24))
                
                # Lock prefilled cells again after solving
                if hasattr(self, 'prefilled') and self.prefilled[i][j]:
                    entry.config(state='disabled', disabledforeground='black')





    def create_log_window(self):
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Log Window")
        self.log_window.geometry("400x300")
        self.log_window.resizable(True, True)

        self.log_text = scrolledtext.ScrolledText(self.log_window, width=40, height=10, font=('Arial', 12))
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def update_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)  # Auto-scroll to the latest message

def copy_grid(grid):
    return [row[:] for row in grid]

if __name__ == "__main__":
    root = tk.Tk()
    gui = SudokuGUI(root)
    root.mainloop()
