import random
import copy
from collections import deque

class SudokuCSP:
    def __init__(self, initial_grid=None):
        self.grid = initial_grid if initial_grid else ''.join('0' for _ in range(9*9))
        self.variables = [(row, col) for row in range(9) for col in range(9)]
        self.domains = {var: '123456789' for var in self.variables}
        self.arcs = self.create_arcs()
        self.initialize_domains()

    def create_arcs(self):  #Function that create all possible arcs of the sudoko grid
        arcs = set()
        for r in range(9):
            for c in range(9):
                for k in range(9):
                    if k != c:
                        arcs.add(((r , c) , (r , k)))  # Same row
                        arcs.add(((r , k) , (r , c)))
                    if k != r:
                        arcs.add(((r , c) , (k , c)))  # Same column
                        arcs.add(((r , k) , (r , c)))

                # Same subgrid
                br, bc = 3 * (r // 3), 3 * (c // 3)
                for dr in range(3):
                    for dc in range(3):
                        nr, nc = br + dr, bc + dc
                        if (nr, nc) != (r, c):
                            arcs.add(((r , c) , (nr , nc)))
                            arcs.add(((nr , nc) , (r , c)))
        arcs = {(a, b) for (a, b) in arcs if a != b}
        return arcs

    def get_grid_val(self , row , col):
        index = row * 9 + col
        return int(self.grid[index])

    def set_grid_val(self , row , col , value):
        index = row * 9 + col
        self.grid = self.grid[:index] + str(value) + self.grid[index + 1:]

    def initialize_domains(self):   #for non-empty cells , assign values of cells as they are the singleton domains
        for var in self.variables:
                row , col = var
                value = self.get_grid_val(row , col)
                if value != 0:
                    self.domains[var] = str(value)

    def is_assignment_complete(self):   #check that there is no empty cells
        return all(self.get_grid_val(r , c) != 0 for r in range(9) for c in range(9))

    def is_valid_assignment(self, row, col):
        # Check if the current row is valid
        value = self.get_grid_val(row, col)
        for c in range(9):
            if c != col and self.get_grid_val(row, c) == value:
                return False

        # Check if the current column is valid
        for r in range(9):
            if r != row and self.get_grid_val(r, col) == value:
                return False

        # Check if the current 3x3 subgrid is valid
        br, bc = 3 * (row // 3), 3 * (col // 3)
        for dr in range(3):
            for dc in range(3):
                nr, nc = br + dr, bc + dc
                if (nr, nc) != (row, col) and self.get_grid_val(nr, nc) == value:
                    return False
        return True

    def backtrack_brute(self):        #Brute force algorithm no heuristic or Arc Consistency used
        for r in range(9):
            for c in range(9):
                if self.get_grid_val(r , c) == 0:
                    for val in range(1, 10):
                        self.set_grid_val(r , c , val)
                        if self.is_valid_assignment(r, c):
                            if self.backtrack_brute():
                                return True
                            self.set_grid_val(r , c , 0)
                    return False
        return True
        
    def arc_consistency(self):      #check arc consistency of all our arcs
        queue = deque(self.arcs)
        in_queue = set(self.arcs)  # Track arcs currently in the queue

        revisions = 0
        pruned = 0

        while queue:
            Xi, Xj = queue.popleft()
            in_queue.discard((Xi, Xj))  # Mark as removed from queue

            revised, pruned_now = self.revise(Xi, Xj)

            if len(self.domains[Xi]) == 0:
                print(f"Failure: Domain of {Xi} emptied by revising with {Xj}")
                return False

            revisions += revised
            pruned += pruned_now

            """if pruned_now:
                for Xk in self.get_neighbors(Xi):
                    if Xk != Xj and (Xk, Xi) not in in_queue:
                        queue.append((Xk, Xi))
                        in_queue.add((Xk, Xi))"""

        return True        

    def revise(self, Xi, Xj):   #apply arc consistency of an arc
        revised = 0
        pruned = 0

        domain_i = self.domains[Xi]
        domain_j = self.domains[Xj]

        revised += 1

        print(f"\nRevising arc {Xi} -> {Xj}")
        print(f"Current domain of {Xi}: {domain_i}")
        print(f"Domain of {Xj}: {domain_j}")

        to_remove = []
        for x in domain_i:
            if not any(x != y for y in domain_j):
                to_remove.append(x)

        for x in to_remove:
            print(f"Removed {x} from {Xi} due to lack of support in {Xj}")
            self.domains[Xi] = self.domains[Xi].replace(str(x) , "")
            pruned += 1

        if(to_remove):
            print(f"Updated domain of {Xi}: {self.domains[Xi]}")

        return revised, pruned

    def get_neighbors(self, var):       #get all neighbor variables of a variable
        r, c = var
        neighbors = set()
        for k in range(9):
            if k != c:
                neighbors.add((r, k))
            if k != r:
                neighbors.add((k, c))
        br, bc = 3 * (r // 3), 3 * (c // 3)
        for dr in range(3):
            for dc in range(3):
                nr, nc = br + dr, bc + dc
                if (nr, nc) != (r, c):
                    neighbors.add((nr, nc))
        return neighbors

    def assign_singletons(self):        #assign all variables with only one available domain
        updated = False
        for var, domain in self.domains.items():
            if len(domain) == 1:
                r, c = var
                value = domain[0]
                if self.get_grid_val(r , c) == 0:
                    self.set_grid_val(r, c , value)
                    print(f"Singleton assignment: {var} = {value}")
                    updated = True
        return updated
    
    def get_first_unassigned(self):
        unassigned = []
        for var in self.variables:
            row , col = var        
            if self.get_grid_val(row , col) == 0:
                return var
        return None

    def backtrack_ac3(self):
        unassigned = self.get_first_unassigned()

        if not unassigned:
            return True     # game complete (all variables assigned)
        
        row , col = unassigned

        for val in self.domains[unassigned]:

            self.set_grid_val(row , col , int(val))
            
            if self.is_valid_grid():
                print('valid grid')
                if self.arc_consistency():
                    print('AC3 DONE')
                    self.assign_singletons()
                    print('Singleton assigned')
                    if self.backtrack_ac3():
                        print('BT-AC3 DONE')
                        return True
                
            self.set_grid_val(row , col , 0)

        return False

    def solve(self):
        self.backtrack_ac3()

    def print_sudoku(self):
        print('\n\n')
        for i in range(9):
            row = self.grid[i*9:(i+1)*9]
            formatted = " ".join(row[j] if row[j] != '0' else '.' for j in range(9))
            print(" ".join(
                (f"| {c}" if j % 3 == 0 else c) for j, c in enumerate(formatted.split())
            ))
            if i % 3 == 2 and i != 8:
                print('-' * 23)

    def is_valid_grid(self):
        # Check rows
        for row in range(9):
            seen = set()
            for col in range(9):
                val = self.get_grid_val(row , col)
                if val != 0:  # Ignore empty cells
                    if val in seen:
                        return False  # Duplicate found in row
                    seen.add(val)

        # Check columns
        for col in range(9):
            seen = set()
            for row in range(9):
                val = self.get_grid_val(row , col)
                if val != 0:  # Ignore empty cells
                    if val in seen:
                        return False  # Duplicate found in column
                    seen.add(val)

        # Check 3x3 subgrids
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                seen = set()
                for row in range(box_row, box_row + 3):
                    for col in range(box_col, box_col + 3):
                        val = self.get_grid_val(row , col)
                        if val != 0:  # Ignore empty cells
                            if val in seen:
                                return False  # Duplicate found in subgrid
                            seen.add(val)

        return True

# Example usage
if __name__ == "__main__":
    example_grid = "300000097007091000000300080600003015001802700730910002060009000070520400450000008"
    print(len(example_grid))
    sudoku = SudokuCSP(example_grid)
    sudoku.print_sudoku()
    sudoku.solve()
    print(sudoku.grid)
    sudoku.print_sudoku()
    print(f'\nIs it a valid board?: {sudoku.is_valid_grid()}')
    print(f'\nIs it a valid assignment?: {sudoku.is_valid_assignment(0 , 2)}')