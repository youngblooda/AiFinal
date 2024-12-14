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
        self.true_positives = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.total_predictions = 0
        self.predictions = []
    
        
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
    
    
    
        """
        Calculate Accuracy does not interact with the AI sat solvers ability to predict the location of the mines
        rather it takes mine predicition data and the actual location of the mines and checks every time the accuracy of the data and puts that into a file
        
        """
    def calculate_accuracy(self, actual_mines, predicted_mines):
        """
        Calculate the accuracy of the AI's mine predictions.

        Args:
            actual_mines (list of tuples): List of actual mine locations.
            predicted_mines (list of tuples): List of predicted mine locations.
        """
        true_positives = len(set(actual_mines).intersection(predicted_mines))
        false_positives = len(set(predicted_mines) - set(actual_mines))
        false_negatives = len(set(actual_mines) - set(predicted_mines))

        # Update the running totals
        self.true_positives += true_positives
        self.false_positives += false_positives
        self.false_negatives += false_negatives
        self.total_predictions += len(predicted_mines)

        # Calculate the accuracy
        if self.total_predictions > 0:
            accuracy = self.true_positives / self.total_predictions
        else:
            accuracy = 0.0

        return accuracy

    def save_accuracy_to_file(self, filename="accuracy_data.txt"):
        """
        Save the accumulated accuracy to a file.
        This method will calculate the average accuracy up to the current point in the game.
        """
        # Calculate the accuracy as a running average
        if self.total_predictions > 0:
            accuracy = self.true_positives / self.total_predictions
        else:
            accuracy = 0.0

        # Open the file and append the accuracy data
        with open(filename, "a") as file:
            file.write(f"Accuracy Per Update: {accuracy:.4f}\n")