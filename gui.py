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
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        self.cell_size = 66
        self.canvas = tk.Canvas(root, width=600, height=600, bg='white')
        self.canvas.pack()

        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.prefilled = [[False for _ in range(9)] for _ in range(9)]

        self.draw_grid()
        self.create_cells()

        # Log window
        self.log_window = None  # To store reference to the log window
        self.create_log_window()

        # Redirect stdout to capture prints
        # sys.stdout = LogStream(self.log_text, log_file="log.txt")

    def draw_grid(self):
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, 9 * self.cell_size, width=thickness)
            self.canvas.create_line(0, i * self.cell_size, 9 * self.cell_size, i * self.cell_size, width=thickness)

    def create_cells(self):
        vcmd = (self.root.register(self.validate_entry), "%P")
        for i in range(9):
            for j in range(9):
                entry = tk.Entry(self.root, font=('Indie Flower', 30), justify='center', bd=0, validate="key", validatecommand=vcmd)
                entry.place(
                    x=j * self.cell_size + 3,
                    y=i * self.cell_size + 3,
                    width=self.cell_size - 6,
                    height=self.cell_size - 6
                )
                self.entries[i][j] = entry

    def validate_entry(self, value):
        return value.isdigit() and 1 <= int(value) <= 9 if value else True

    def clear_board(self):
        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                entry.config(state='normal')
                entry.delete(0, tk.END)

    def solve_example(self):
        self.clear_board()

        puzzle_str = "300000097007091000000300080600003015001802700730910002060009000070520400450000008"
        
        puzzle_str2= "000000064000476980045009002950004008000001350000003006500617820279508601010902073" 
        puzzle_str3= "000000000000003085001020000000507000004000100090000000500000073002010000000040009"
        # Mark prefilled cells based on the string
        self.prefilled = [[puzzle_str3[i * 9 + j] != '0' for j in range(9)] for i in range(9)]

        print("Board before solving:\n")
        for i in range(9):
            print([int(puzzle_str3[i * 9 + j]) for j in range(9)])
        print("\n\n\n")

        # Fill the GUI board
        for i in range(9):
            for j in range(9):
                val = puzzle_str3[i * 9 + j]
                if val != '0':
                    entry = self.entries[i][j]
                    entry.insert(0, val)
                    entry.config(state='disabled', disabledforeground='black', font=('Indie Flower', 24, 'bold'))
                    self.prefilled[i][j] = True
                else:
                    self.prefilled[i][j] = False

        print("Starting to solve Example puzzle...")

        # === BACKEND SOLVE ===
        csp = SudokuCSP(puzzle_str3)
        csp.solve(log=False)
        grid_2d = [[int(csp.grid[i * 9 + j]) for j in range(9)] for i in range(9)]
        self.set_board(grid_2d)
        

        print("Example puzzle solved.")
        print("Solved Board:\n")
        for row in csp.grid:
            print(row)
        print("\n\n\n")



    def solve_user_input(self):
        pass
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



    def set_board(self, board):
        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                entry.config(state='normal')  # Allow editing for now to update the value
                entry.delete(0, tk.END)
                if board[i][j] != 0:
                    entry.insert(0, str(board[i][j]))
                    if hasattr(self, 'prefilled') and not self.prefilled[i][j]:
                        entry.config(fg='blue', font=('Indie Flower', 30, 'bold'))  # Solved cells
                    else:
                        entry.config(fg='black', font=('Indie Flower', 30, 'bold'))  # Pre-filled cells
                else:
                    entry.config(fg='black', font=('Indie Flower', 30, 'bold'))  # Empty cells
                
                # Lock prefilled cells again after solving
                if hasattr(self, 'prefilled') and self.prefilled[i][j]:
                    entry.config(state='disabled', disabledforeground='black')





    def create_log_window(self):
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Log Window")
        self.log_window.geometry("400x300")
        self.log_window.resizable(True, True)

        self.log_text = scrolledtext.ScrolledText(self.log_window, width=40, height=10, font=('Arial', 20))
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def update_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)  # Auto-scroll to the latest message




def run_gui(mode,log_to_file=False):
    root = tk.Tk()
    gui = SudokuGUI(root)
    
    if log_to_file==True:
        sys.stdout = LogStream(gui.log_text, log_file="log.txt")
        
    if mode == 0:
        gui.solve_example()
    elif mode == 1:
        pass
    else:
        pass
    root.mainloop()
    

    
# run_gui(0)