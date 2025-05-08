import random
import copy
from collections import deque

class SudokuCSP:
    def __init__(self, initial_grid = None , logging = True):
        self.grid = initial_grid if initial_grid else ''.join('0' for _ in range(9*9))
        self.variables = [(row, col) for row in range(9) for col in range(9)]
        self.domains = {var: '123456789' for var in self.variables}
        self.arcs = self.create_arcs()
        self.initialize_domains()
        self.logging = logging
        self.stats = {
            'revised': 0,
            'pruned': 0,
            'singleton': 0,
            'backtracks': 0
        }

    def create_arcs(self):  #Function that create all possible arcs of the sudoko grid
        arcs = []
        for r in range(9):
            for c in range(9):
                for k in range(9):
                    if k != c:
                        arcs.append(((r , c) , (r , k)))  # Same row
                        arcs.append(((r , k) , (r , c)))
                    if k != r:
                        arcs.append(((r , c) , (k , c)))  # Same column
                        arcs.append(((r , k) , (r , c)))

                # Same subgrid
                br, bc = 3 * (r // 3), 3 * (c // 3)
                for dr in range(3):
                    for dc in range(3):
                        nr, nc = br + dr, bc + dc
                        if (nr, nc) != (r, c):
                            arcs.append(((r , c) , (nr , nc)))
                            arcs.append(((nr , nc) , (r , c)))
        arcs = [(a, b) for (a, b) in arcs if a != b]
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
        
    def arc_consistency(self , queue = None):      #check arc consistency of all our arcs
        if not queue:
            queue = self.arcs.copy()

        while queue:
            Xi, Xj = queue.pop(0)
            dom_copy = self.domains[Xi]

            pruned_now = self.revise(Xi, Xj)

            if len(self.domains[Xi]) == 0:
                if self.logging:
                    print(f"Failure: Domain of {Xi} emptied by revising with {Xj}")
                self.domains[Xi] = dom_copy
                return False

            if len(self.domains[Xi]) == 1:
                value = next(iter(self.domains[Xi]))
                i, j =  Xi
                self.set_grid_val(i , j , value)
                self.stats['singleton'] += 1
                if self.logging:
                    print(f"Variable {Xi} became singleton with value {value}")

            if pruned_now:
                for Xk in self.get_neighbors(Xi):
                    if Xk != Xj:
                        queue.append((Xk, Xi))

        return True        

    def revise(self, Xi, Xj):   #apply arc consistency of an arc
        domain_i = self.domains[Xi]
        domain_j = self.domains[Xj]

        prune_occured = False

        self.stats['revised'] += 1
        if self.logging:
            print(f"\nRevising arc {Xi} -> {Xj}")
            print(f"Current domain of {Xi}: {domain_i}")
            print(f"Domain of {Xj}: {domain_j}")

        to_remove = []
        for x in domain_i:
            if not any(x != y for y in domain_j):
                to_remove.append(x)

        for x in to_remove:
            if self.logging:
                print(f"Removed {x} from {Xi} due to lack of support in {Xj}")
            self.stats['pruned'] += 1
            prune_occured = True
            self.domains[Xi] = self.domains[Xi].replace(str(x) , "")

        if(to_remove and self.logging):
            print(f"Updated domain of {Xi}: {self.domains[Xi]}")

        return prune_occured

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
    
    def get_first_unassigned(self):
        for var in self.variables:
            row , col = var        
            if self.get_grid_val(row , col) == 0:
                return var
        return None

    def forward_checking(self , var , value):
                
        saved_domains = {}
        conflicts = []
        
        for neighbor in self.get_neighbors(var):
            ni, nj = neighbor
            if self.get_grid_val(ni , nj) == 0:
                if value in self.domains[neighbor]:
                    if neighbor not in saved_domains:
                        saved_domains[neighbor] = self.domains[neighbor]
                    
                    self.domains[neighbor].replace(str(value) , '')

                    if self.logging:
                        print(f"Forward checking: removed {value} from domain of {neighbor}")
                    
                    if not self.domains[neighbor]:
                        if self.logging:
                            print(f"Forward checking: domain of {neighbor} became empty")
                        conflicts.append(neighbor)
        
        if conflicts:
            for n, domain in saved_domains.items():
                self.domains[n] = domain
            return False
        
        return True

    def get_most_constrained_var(self):
        unassigned = [var for var in self.variables if self.get_grid_val(*var) == 0]        #get all unassigned variables
        return min(unassigned, key=lambda var: len(self.domains[var]), default=None)        #return variable with least number of possible domain values
    
    def order_least_restricting_val(self , var):
        neighbours_restricted = []
        for value in self.domains[var]:
            impact = 0
            for neighbour in self.get_neighbors(var):
                if value in self.domains[neighbour]:
                    impact += 1
            neighbours_restricted.append((value , impact))

        return [val for val, _ in sorted(neighbours_restricted, key=lambda x: x[1])]

    def backtrack_ac3(self):
        unassigned = self.get_most_constrained_var()        #MCV heuristic

        if not unassigned:
            return True     # game complete (all variables assigned)
        
        row , col = unassigned

        for val in self.order_least_restricting_val(unassigned):        #LRV heuristic
            
            original_grid = self.grid
            old_domains = {v: self.domains[v] for v in self.variables}

            self.set_grid_val(row , col , int(val))
            self.domains[unassigned] = str(val)

            if self.logging:
                print(f'Backtrack assigned {val} to {unassigned}')
        
            if self.is_valid_assignment(row , col):

                if self.forward_checking(unassigned , val):             #Forward Checking
                    affected = [(neighbor, unassigned) for neighbor in self.get_neighbors(unassigned)]
                    if self.arc_consistency(queue = affected):

                        if self.backtrack_ac3():
                            self.stats['backtracks'] += 1
                            return True
                
            self.set_grid_val(row , col , 0)
            self.domains = old_domains
            self.grid = original_grid

            if self.logging:
                print(f'Backtrack reset {unassigned} from {val}')

        return False

    def solve(self):
        if not self.is_valid_grid():
            print('\n\nERROR: Sudoku board is not valid')
            return False
        
        self.arc_consistency()

        if not self.backtrack_ac3():
            print('\n\nERROR: Sudoku board is not solvable')
            return False
        
        print('\n')
        print('Number of Total Revisions that occured: ' + str(self.stats['revised']))
        print('Number of Pruned Domains: ' + str(self.stats['pruned']))
        print('Number of Singleton Assignments: ' + str(self.stats['singleton']))
        print('Number of Backtracks that occured: ' + str(self.stats['backtracks']))

    def print_sudoku(self):
        print('\n')
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
    example_grid = "029000000000600090000740102907000003030807010050093027206430801080000300040900000"
    print(len(example_grid))
    sudoku = SudokuCSP(example_grid , logging = False)
    sudoku.print_sudoku()
    sudoku.solve()
    sudoku.print_sudoku()
    print(f'\nIs it a valid board?: {sudoku.is_valid_grid()}')