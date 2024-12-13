from z3 import *
import random

class AISolver:
    def __init__(self, grid):
        """
        Initializes the AI Solver with the game grid.

        Args:
            grid (list of list of dict): A 2D list of cells in the game grid.
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def identify_mines(self):
        """
        Uses Z3 solver to deduce the positions of mines based on revealed cells.

        Returns:
            list of tuples: Coordinates of cells suspected to contain mines.
        """
        solver = Solver()
        cells = [[Bool(f"cell_{r}_{c}") for c in range(self.cols)] for r in range(self.rows)]
        
        # Add constraints based on the current state of the grid
        for r in range(self.rows):
            for c in range(self.cols):
                cell_data = self.grid[r][c]

                if cell_data["revealed"] and cell_data["number"] > 0:
                    adjacent_cells = self._get_adjacent_cells(r, c)

                    # Constraint: The sum of adjacent mines must match the cell's number
                    adjacent_mines = [cells[ar][ac] for ar, ac in adjacent_cells]
                    solver.add(Sum([If(mine, 1, 0) for mine in adjacent_mines]) == cell_data["number"])

                if cell_data["flagged"]:
                    solver.add(cells[r][c])  # Force the flagged cell to be a mine

                if cell_data["revealed"] and not cell_data["mine"]:
                    solver.add(Not(cells[r][c]))  # Revealed non-mine cells cannot be mines

        # Solve the constraints
        if solver.check() == sat:
            model = solver.model()
            suspected_mines = [(r, c) for r in range(self.rows) for c in range(self.cols) if is_true(model.evaluate(cells[r][c]))]
            return suspected_mines
        return []
    
    
    def identify_mines_from_cell(self, row, col):
        """
        Uses Z3 solver to deduce the positions of mines based on the selected cell.

        Args:
        row (int): Row index of the clicked cell.
        col (int): Column index of the clicked cell.

        Returns:
        list of tuples: Coordinates of cells suspected to contain mines.
        """
        solver = Solver()
        cells = [[Bool(f"cell_{r}_{c}") for c in range(self.cols)] for r in range(self.rows)]
        cell_data = self.grid[row][col]

        if cell_data["revealed"] and cell_data["number"] > 0:
            adjacent_cells = self._get_adjacent_cells(row, col)

            # Constraint: The sum of adjacent mines must match the cell's number
            adjacent_mines = [cells[ar][ac] for ar, ac in adjacent_cells]
            solver.add(Sum([If(mine, 1, 0) for mine in adjacent_mines]) == cell_data["number"])

        # Add constraints for revealed or flagged cells
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]["flagged"]:
                    solver.add(cells[r][c])  # Flagged cells must be mines
                if self.grid[r][c]["revealed"] and not self.grid[r][c]["mine"]:
                    solver.add(Not(cells[r][c]))  # Revealed non-mine cells cannot be mines

        # Solve the constraints
        if solver.check() == sat:
            model = solver.model()
            suspected_mines = [(r, c) for r in range(self.rows) for c in range(self.cols) if is_true(model.evaluate(cells[r][c]))]
            return suspected_mines
        return []
    
    def _get_adjacent_cells(self, row, col):
        """
        Gets the coordinates of adjacent cells for a given cell.

        Args:
            row (int): Row index.
            col (int): Column index.

        Returns:
            list of tuples: Adjacent cell coordinates.
        """
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        return [
            (row + dr, col + dc)
            for dr, dc in directions
            if 0 <= row + dr < self.rows and 0 <= col + dc < self.cols
        ]

    def suggest_moves(self):
        """
        Suggests the next best move for the player based on AI deductions.

        Returns:
            dict: A dictionary with two keys:
                "safe_cells": List of safe cell coordinates to reveal.
                "mine_cells": List of mine cell coordinates to flag.
        """
        suspected_mines = self.identify_mines()
        
        safe_cells = []
        mine_cells = []

        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c]["revealed"]:
                    if (r, c) in suspected_mines:
                        mine_cells.append((r, c))
                    else:
                        safe_cells.append((r, c))

        return {"safe_cells": safe_cells, "mine_cells": mine_cells}
