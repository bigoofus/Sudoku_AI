import random
import copy
from collections import deque

class SudokuCSP:
    def __init__(self, initial_grid=None):
        self.grid = initial_grid if initial_grid else [[0]*9 for _ in range(9)]
        self.variables = [(r, c) for r in range(9) for c in range(9)]
        self.domains = {var: list(range(1, 10)) for var in self.variables}
        self.arcs = self.create_arcs()
        self.initialize_domains()

    def create_arcs(self):
        arcs = set()
        for r in range(9):
            for c in range(9):
                for k in range(9):
                    if k != c:
                        arcs.add(((r, c), (r, k)))  # Same row
                    if k != r:
                        arcs.add(((r, c), (k, c)))  # Same column

                # Same subgrid
                br, bc = 3 * (r // 3), 3 * (c // 3)
                for dr in range(3):
                    for dc in range(3):
                        nr, nc = br + dr, bc + dc
                        if (nr, nc) != (r, c):
                            arcs.add(((r, c), (nr, nc)))
        return arcs

    def initialize_domains(self):
        for r in range(9):
            for c in range(9):
                value = self.grid[r][c]
                if value != 0:
                    self.domains[(r, c)] = [value]

    def is_assignment_complete(self):
        return all(self.grid[r][c] != 0 for r in range(9) for c in range(9))

    def is_valid(self, r, c, val):
        for i in range(9):
            if self.grid[r][i] == val or self.grid[i][c] == val:
                return False
        br, bc = 3 * (r // 3), 3 * (c // 3)
        for dr in range(3):
            for dc in range(3):
                if self.grid[br + dr][bc + dc] == val:
                    return False
        return True

    def backtrack(self):
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    for val in range(1, 10):
                        if self.is_valid(r, c, val):
                            self.grid[r][c] = val
                            if self.backtrack():
                                return True
                            self.grid[r][c] = 0
                    return False
        return True

    def arc_consistency(self):
        queue = deque(self.arcs)
        revisions = 0
        pruned = 0

        while queue:
            (Xi, Xj) = queue.popleft()
            revised, pruned_now = self.revise(Xi, Xj)
            revisions += revised
            pruned += pruned_now
            if revised:
                for Xk in self.get_neighbors(Xi):
                    if Xk != Xj:
                        queue.append((Xk, Xi))

        print(f"Total revisions: {revisions}, Total domains pruned: {pruned}")

    def revise(self, Xi, Xj):
        revised = 0
        pruned = 0
        domain_i = self.domains[Xi]
        domain_j = self.domains[Xj]

        print(f"\nRevising arc {Xi} -> {Xj}")
        print(f"Current domain of {Xi}: {domain_i}")
        print(f"Domain of {Xj}: {domain_j}")

        to_remove = []
        for x in domain_i:
            if not any(x != y for y in domain_j):
                to_remove.append(x)

        for x in to_remove:
            self.domains[Xi].remove(x)
            print(f"Removed {x} from {Xi} due to lack of support in {Xj}")
            pruned += 1
            revised += 1

        print(f"Updated domain of {Xi}: {self.domains[Xi]}")
        return revised, pruned

    def get_neighbors(self, var):
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

    def assign_singletons(self):
        updated = False
        for var, domain in self.domains.items():
            if len(domain) == 1:
                r, c = var
                value = domain[0]
                if self.grid[r][c] == 0:
                    self.grid[r][c] = value
                    print(f"Singleton assignment: {var} = {value}")
                    updated = True
        return updated

    def solve(self):
        self.arc_consistency()
        while self.assign_singletons():
            self.arc_consistency()
        if not self.is_assignment_complete():
            print("Starting backtracking...")
            self.backtrack()

    def print_grid(self):
        for r in range(9):
            line = ''
            for c in range(9):
                line += str(self.grid[r][c]) + ' '
            print(line)

# Example usage
if __name__ == "__main__":
    example_grid = [
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
    sudoku = SudokuCSP(example_grid)
    sudoku.solve()
    sudoku.print_grid()
