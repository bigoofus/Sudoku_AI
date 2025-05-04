import tkinter as tk
import sys
import time
from tkinter import scrolledtext, messagebox  # Import for the log window
from backend import SudokuCSP  # Adjust the import if the backend is named differently



class LogStream:
    def __init__(self, log_widget):
        self.log_widget = log_widget
        # self.log_file = log_file

    def write(self, message):
        self.log_widget.config(state='normal')
        self.log_widget.insert(tk.END, message)
        self.log_widget.yview(tk.END)
        self.log_widget.config(state='disabled')


    def flush(self):
        pass  # Needed to avoid any errors when flushing the stream

class SudokuGUI:
    def __init__(self, root, selected_mode,logging=False):
        self.root = root
        self.selected_mode = selected_mode
        self.root.title("Sudoku Solver")
        if selected_mode != 0:
            self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.logging=logging

        self.cell_size = 66
        self.canvas = tk.Canvas(root, width=600, height=600, bg='white')
        self.canvas.pack()

        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.prefilled = [[False for _ in range(9)] for _ in range(9)]
        self.log_text=self.create_log_window()
        self.draw_grid()
        self.create_cells()
        self.generated_puzzle = None
        self.generated_empty_spaces = 40  # Default value
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mode_1_setup(selected_mode)
        self.mode_2_setup(selected_mode)
        self.mode_3_setup(selected_mode)

            
    def mode_1_setup(self,selected_mode):
            if selected_mode == 1:
                # Solve Button
                self.solve_button = tk.Button(
                    self.root, text="Solve",
                    command=self.solve_user_input,
                    font=('Teacher', 40, 'bold'),
                    bg='lightgreen', fg='black',
                    activebackground='#90ee90',
                    relief='ridge', bd=4,
                    highlightthickness=0
                )
                self.solve_button.place(relx=0.35, rely=0.93, width=150, height=50, anchor='center')

                # Clear Button
                self.clear_button = tk.Button(
                    self.root, text="Clear",
                    command=self.clear_board,
                    font=('Teacher', 40, 'bold'),
                    bg='tomato', fg='white',
                    activebackground='red',
                    relief='ridge', bd=4,
                    highlightthickness=0
                )
                self.clear_button.place(relx=0.65, rely=0.93, width=150, height=50, anchor='center')
    def mode_2_setup(self,selected_mode):
        if selected_mode == 2:
            # Entry box for empty cells
            self.empty_entry = tk.Entry(
                self.root, font=('Teacher', 20),
                justify='center',
    
            )
            self.empty_entry.place(relx=0.06, rely=0.93, width=60, height=50, anchor='center')
            self.empty_entry.insert(0, str(self.generated_empty_spaces))

            # Generate Button
            self.generate_button = tk.Button(
                self.root, text="Generate",
                command=self.on_generate_clicked,
                font=('Teacher', 35, 'bold'),
                bg='lightblue', fg='black',
                activebackground='#add8e6',
            )
            self.generate_button.place(relx=0.30, rely=0.93, width=220, height=50, anchor='center')

            # Solve Button
            self.solve_button = tk.Button(
                self.root, text="Solve",
                command=self.solve_generated,
                font=('Teacher', 35, 'bold'),
                bg='lightgreen', fg='black',
                activebackground='#90ee90',

            )
            self.solve_button.place(relx=0.62, rely=0.93, width=150, height=50, anchor='center')

            # Clear Button
            self.clear_button = tk.Button(
                self.root, text="Clear",
                command=self.clear_board,
                font=('Teacher', 35, 'bold'),
                bg='tomato', fg='white',
                activebackground='red',

            )
            self.clear_button.place(relx=0.86, rely=0.93, width=125, height=50, anchor='center')
    def mode_3_setup(self,selected_mode):
        if selected_mode == 3:
            self.empty_entry = tk.Entry(
                self.root, font=('Teacher', 20),
                justify='center',
    
            )
            self.empty_entry.place(relx=0.06, rely=0.93, width=60, height=50, anchor='center')
            self.empty_entry.insert(0, str(self.generated_empty_spaces))

            # Generate Button
            self.generate_button = tk.Button(
                self.root, text="Generate",
                command=self.on_generate_clicked,
                font=('Teacher', 35, 'bold'),
                bg='lightblue', fg='black',
                activebackground='#add8e6',
            )
            self.generate_button.place(relx=0.30, rely=0.93, width=220, height=50, anchor='center')

            # Verify Button
            self.solve_button = tk.Button(
                self.root, text="Verify",
                command=self.verify,
                font=('Teacher', 35, 'bold'),
                bg='lightgreen', fg='black',
                activebackground='#90ee90',

            )
            self.solve_button.place(relx=0.62, rely=0.93, width=150, height=50, anchor='center')

            # Clear Button
            self.clear_button = tk.Button(
                self.root, text="Clear",
                command=self.clear_board,
                font=('Teacher', 35, 'bold'),
                bg='tomato', fg='white',
                activebackground='red',

            )
            self.clear_button.place(relx=0.86, rely=0.93, width=125, height=50, anchor='center')
                 
    def on_closing(self):
        if tk.messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            tk.messagebox.showinfo("Sudoku Solver", "Thank you for using the Sudoku Solver!")
            self.root.destroy()
            sys.exit(0)
    def create_log_window(self):
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Log Window")
        self.log_window.geometry("600x400")
        self.log_window.resizable(True, True)

        self.log_text = scrolledtext.ScrolledText(
            self.log_window,
            width=70, height=20,
            font=('Arial', 18),
            state='disabled'
        )
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        return self.log_text  # <-- ADD THIS
    
    def on_generate_clicked(self):
        try:
            value = int(self.empty_entry.get())
            if 1 <= value <= 80:
                self.generated_empty_spaces = value
                self.generate(value)  # Call your existing generate logic
            else:
                tk.messagebox.showerror("Invalid Input", "Please enter a number between 1 and 80.")
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter a valid number.")


    def draw_grid(self):
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, 9 * self.cell_size, width=thickness)
            self.canvas.create_line(0, i * self.cell_size, 9 * self.cell_size, i * self.cell_size, width=thickness)

    def create_cells(self):
        vcmd = (self.root.register(self.validate_entry), "%P")
        for i in range(9):
            for j in range(9):
                entry = tk.Entry(self.root, font=('Teacher', 30), justify='center', bd=0, validate="key", validatecommand=vcmd)
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
    def verify(self,mute_highlight=False):
        board_str = self.get_current_board()
        csp=SudokuCSP(board_str,self.logging)
        
        
        if  not csp.is_valid_grid():
            if mute_highlight==False:
                self.highlight_invalid_cells()
            messagebox.showerror("Verification", "The Sudoku puzzle is invalid.")
            return False
    def set_baord_allblack(self,puzzle_str):
        for i in range(9):
            for j in range(9):
                val = puzzle_str[i * 9 + j]
                if val != '0':
                    entry = self.entries[i][j]
                    entry.insert(0, val)
                    entry.config(state='disabled', disabledforeground='black', font=('Teacher', 24, 'bold'))
                    self.prefilled[i][j] = True
                else:
                    self.prefilled[i][j] = False     
    def solve_example(self):
        # self.clear_board()
        if self.generated_puzzle!=None:
            puzzle_str = self.generated_puzzle
        else:
            puzzle_str ="000000000000003085001020000000507000004001200090000000500000073002010000000040009" 
        self.prefilled = self.board_from_string(puzzle_str)
        self.set_board(self.board_from_string(puzzle_str))
        
        if self.verify(mute_highlight=True) == False:
            return
        # puzzle_str = "300000097007091000000300080600003015001802700730910002060009000070520400450000008"
        
        # puzzle_str2= "000000064000476980045009002950004008000001350000003006500617820279508601010902073" 
        # puzzle_str3= "000000000000003085001020000000507000004000100090000000500000073002010000000040009"
        # Mark prefilled cells based on the string
        self.prefilled = self.board_from_string(puzzle_str)

        print("Board before solving:\n")
        
        self.print_grid(self.board_from_string(puzzle_str))
        print("\n\n\n")

        # Fill the GUI board
        

        print("Starting to solve Example puzzle...")

        # === BACKEND SOLVE ===
        csp = SudokuCSP(puzzle_str,self.logging)
        start_time=time.time()
        csp.solve()
        end_time=time.time()
        grid_2d = self.board_from_string(csp.grid)
        self.set_board(grid_2d)
        

        print("Example puzzle solved.")
        print("Solved Board:\n")
        print(f"solved in:{end_time-start_time:.2f} seconds \n")
        
        self.print_grid(grid_2d)
        print("\n\n\n")

   
    def get_current_board(self):
        board_str = ""
        for i in range(9):
            for j in range(9):
                val = self.entries[i][j].get()
                board_str += val if val.isdigit() else '0'
        # print( "Current board string:", board_str)
        return board_str

    def solve_user_input(self):
        puzzle = self.get_current_board()
        if self.verify(mute_highlight=True) == False:
            return
        

        # Mark prefilled cells
        self.prefilled = self.board_from_string(puzzle)

        print("Board before solving:\n")
        self.print_grid(self.board_from_string(puzzle))
        print("\n\n")

        print("Starting to solve user input puzzle...")

        # Solve using CSP backend
        csp = SudokuCSP(puzzle,self.logging)
        start_time = time.time()
        csp.solve()
        end_time = time.time()

        # Convert solved grid to 2D list
        grid_2d = self.board_from_string(csp.grid)
        self.set_board(grid_2d)

        print("User input puzzle solved.")
        print("Solved Board:\n")
        print(f"solved in:{end_time-start_time:.2f} seconds\n")
        self.print_grid(grid_2d)
        print("\n\n")
    
    def board_from_string(self, puzzle_str):
        return [[int(puzzle_str[i * 9 + j]) for j in range(9)] for i in range(9)]
    def print_grid(self,grid):
        for row in grid:
            print(row)
    
    def set_board(self, board):
        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                entry.config(state='normal')  # Allow editing for now to update the value
                entry.delete(0, tk.END)
                if board[i][j] != 0:
                    entry.insert(0, str(board[i][j]))
                    if hasattr(self, 'prefilled') and not self.prefilled[i][j]:
                        entry.config(fg='blue', font=('Teacher', 30, 'bold'))  # Solved cells
                    else:
                        entry.config(fg='black', font=('Teacher', 30, 'bold'))  # Pre-filled cells
                else:
                    entry.config(fg='black', font=('Teacher', 30, 'bold'))  # Empty cells
                
                # Lock prefilled cells again after solving
                if hasattr(self, 'prefilled') and self.prefilled[i][j]:
                    entry.config(state='disabled', disabledforeground='black')
                if hasattr(self, 'prefilled') and not self.prefilled[i][j]:
                    entry.config(state='disabled', disabledforeground='blue')
                    



    def update_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)  # Auto-scroll to the latest message
    def set_mode3_board(self, board):
        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                entry.config(state='normal')  # Allow editing for now to update the value
                entry.delete(0, tk.END)
                if board[i][j] != 0:
                    entry.insert(0, str(board[i][j]))
                    if hasattr(self, 'prefilled') and not self.prefilled[i][j]:
                        entry.config(fg='blue', font=('Teacher', 30, 'bold'))  # Solved cells
                    else:
                        entry.config(fg='black', font=('Teacher', 30, 'bold'))  # Pre-filled cells
                else:
                    entry.config(fg='blue', font=('Teacher', 30, 'bold'))  # Empty cells
                
                # Lock prefilled cells again after solving
                if hasattr(self, 'prefilled') and self.prefilled[i][j]:
                    entry.config(state='disabled', disabledforeground='black')
                
    def highlight_invalid_cells(self):
        grid = [[self.entries[i][j].get() for j in range(9)] for i in range(9)]

        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                val = grid[i][j]

                if not val.isdigit() or val == '0':
                    continue

                current_color = entry.cget('fg')

                # Temporarily clear the cell to avoid self-check conflict
                grid[i][j] = '0'
                is_valid = self.is_valid_placement(grid, int(val), i, j)
                grid[i][j] = val

                if current_color == 'blue' and not is_valid:
                    entry.config(fg='red')
                elif current_color == 'red' and is_valid:
                    entry.config(fg='blue')   

    def is_valid_placement(self, grid, num, row, col):
        num_str = str(num)

        # Check row
        if num_str in grid[row]:
            return False

        # Check column
        for i in range(9):
            if grid[i][col] == num_str:
                return False

        # Check 3x3 box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if grid[start_row + i][start_col + j] == num_str:
                    return False

        return True              
    def generate(self,value):
        from suduko_generator import generate_sudoku_string
        puzzle_string=generate_sudoku_string(k=value)
        self.prefilled = self.board_from_string(puzzle_string)
        grid_2d = self.board_from_string(puzzle_string)
        if(self.selected_mode==3):
            self.set_mode3_board(grid_2d)
        else:
            self.set_board(grid_2d)
        
        self.generated_puzzle=puzzle_string
        
      
        
        
    def solve_generated(self):
        self.solve_example()



def run_gui(mode,logging=False):
    root = tk.Tk()
    gui = SudokuGUI(root,selected_mode=mode,logging=logging)
    sys.stdout = LogStream(gui.log_text)
    
    # if log_to_file==True:
    #     sys.stdout = LogStream(gui.log_text)
        
    if mode == 0:
        gui.solve_example()
    root.mainloop()
    root.destroy()
    
# run_gui(0)