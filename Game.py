import pygame
import random


class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 600, 600
        self.GRID_SIZE = 30
        self.CELL_SIZE = self.WIDTH // self.GRID_SIZE
        self.FPS = 60

        self.WHITE = (255, 255, 255)
        self.GRAY = (192, 192, 192)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)  # For highlighting probable mines

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()


    def main_menu(self):
        # Function to display the main menu where the user selects difficulty

        self.WIDTH, self.HEIGHT = 600, 600  # Resize screen for the menu
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.screen.fill(self.WHITE)  # Fill the screen with white background
        font = pygame.font.SysFont(None, 48)  # Font for the menu options

        # Menu options with corresponding difficulty settings
        options = ["Easy (8x8, 10 Mines)", "Medium (16x16, 40 Mines)", "Hard (16x30, 99 Mines)"]
        buttons = []  # List to store button positions and texts
        y_offset = 150  # Initial vertical offset for the first option

        # Draw the menu options as buttons
        for option in options:
            text = font.render(option, True, self.BLACK)  # Render the text for each option
            rect = text.get_rect(center=(self.WIDTH // 2, y_offset))  # Get the rectangle for button placement
            buttons.append((rect, option))  # Store button's rect and option
            pygame.draw.rect(self.screen, self.GRAY, rect.inflate(20, 20))  # Draw a rectangle for the button
            self.screen.blit(text, rect)  # Place the text inside the button
            y_offset += 100  # Move down for the next option

        pygame.display.flip()  # Update the screen

        # Wait for user to click on one of the buttons
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Check if the user closed the window
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos  # Get mouse click position
                    for rect, option in buttons:
                        if rect.collidepoint(x, y):  # Check if the click was on a button
                            if "Easy" in option:
                                return 8, 10  # Return easy grid size and number of mines
                            elif "Medium" in option:
                                return 16, 40  # Return medium grid size and number of mines
                            elif "Hard" in option:
                                return (16,30), 99  # Return hard grid size and number of mines


    def create_grid(self,rows, cols, num_mines):
        # Function to create the game grid with mines and numbers
        grid = [[{"mine": False, "revealed": False, "flagged": False, "number": 0} for _ in range(cols)] for _ in range(rows)]

        # Randomly place mines in the grid
        mines = random.sample(range(rows * cols), num_mines)  # Randomly pick mine locations
        for mine in mines:
            row, col = divmod(mine, cols)  # Convert the flat index to row/col position
            grid[row][col]["mine"] = True  # Mark the cell as containing a mine

        # Calculate the numbers for each non-mine cell based on adjacent mines
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for r in range(rows):
            for c in range(cols):
                if not grid[r][c]["mine"]:  # Skip cells that contain mines
                    grid[r][c]["number"] = sum(
                        grid[r + dr][c + dc]["mine"]
                        for dr, dc in directions
                        if 0 <= r + dr < rows and 0 <= c + dc < cols  # Check boundaries
                    )
        return grid  # Return the generated grid


    def draw_grid(self,screen, grid):
        rows, cols = len(grid), len(grid[0])
        x_offset = (self.WIDTH - (cols * self.CELL_SIZE)) // 2  # Center the grid horizontally
        y_offset = 50  # Offset grid for UI space
        for r in range(rows):
            for c in range(cols):
                x, y = c * self.CELL_SIZE + x_offset, r * self.CELL_SIZE + y_offset  # Adjust for offsets
                pygame.draw.rect(screen, self.GRAY if grid[r][c]["revealed"] else self.WHITE, (x, y, self.CELL_SIZE, self.CELL_SIZE))  # Draw the cell
                pygame.draw.rect(screen, self.BLACK, (x, y, self.CELL_SIZE, self.CELL_SIZE), 1)  # Cell border

                if grid[r][c]["revealed"]:  # If the cell is revealed, show its content
                    if grid[r][c]["mine"]:
                        pygame.draw.circle(screen, self.RED, (x + self.CELL_SIZE // 2, y + self.CELL_SIZE // 2), self.CELL_SIZE // 4)  # Draw mine
                    elif grid[r][c]["number"] > 0:
                        font = pygame.font.SysFont(None, 36)  # Font for the number
                        text = font.render(str(grid[r][c]["number"]), True, self.BLACK)  # Render the number
                        screen.blit(text, (x + 10, y + 5))  # Position the number inside the cell
                elif grid[r][c]["flagged"]:  # Draw a flag if the cell is flagged
                    pygame.draw.polygon(screen, self.RED, [
                        (x + self.CELL_SIZE // 4, y + self.CELL_SIZE // 4),
                        (x + 3 * self.CELL_SIZE // 4, y + self.CELL_SIZE // 2),
                        (x + self.CELL_SIZE // 4, y + 3 * self.CELL_SIZE // 4)
                    ])
    


    def game_ui(self,screen, timer, flagged_count, total_mines):
        # Function to display the game UI: timer, flagged count, and menu button
        font = pygame.font.SysFont(None, 36)
        padding = 20  # Padding for UI elements around the edges

        # Dynamic positions for UI elements
        flags_x = padding  # Position of the flags counter
        timer_x = self.WIDTH - padding - 150  # Position of the timer
        menu_x = self.WIDTH // 2.5  # Position of the menu button
        
        # Draw timer
        timer_text = font.render(f"Time: {timer}s", True, self.BLACK)
        screen.blit(timer_text, (timer_x, 10))

        # Draw flagged mines counter
        mines_text = font.render(f"Flags: {flagged_count}/{total_mines}", True, self.BLACK)
        screen.blit(mines_text, (flags_x, 10))

        # Draw menu button in the center
        menu_text = font.render("Menu", True, self.BLACK)
        menu_rect = menu_text.get_rect(center=(menu_x, 25))
        pygame.draw.rect(screen, self.GRAY, menu_rect.inflate(20, 10))  # Draw button background
        screen.blit(menu_text, menu_rect)  # Draw the button text

        return menu_rect  # Return the rectangle of the menu button for collision detection


    def reveal_cell(self,grid, row, col):
        # Function to reveal a cell and its surrounding cells if necessary
        try:
            if grid[row][col]["revealed"] or grid[row][col]["flagged"]:  # Check if the cell is already revealed or flagged
                return
        except IndexError:
            print(f"Invalid access: row={row}, col={col}")
            return

        grid[row][col]["revealed"] = True  # Mark the cell as revealed

        # If the revealed cell has no adjacent mines, reveal surrounding cells
        if grid[row][col]["number"] == 0 and not grid[row][col]["mine"]:
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in directions:
                if 0 <= row + dr < self.GRID_SIZE and 0 <= col + dc < self.GRID_SIZE:
                    self.reveal_cell(grid, row + dr, col + dc)


    def handle_click(self,grid, x, y, game_over):
        # Function to handle left mouse button click (reveal a cell or end the game)
        if game_over:
            return False  # Game already over, no further actions

        col, row = x // self.CELL_SIZE, y // self.CELL_SIZE  # Convert mouse position to grid position
        cell = grid[row][col]

        if cell["mine"]:
            return True  # Game over if the clicked cell is a mine
        else:
            self.reveal_cell(grid, row, col)  # Reveal the clicked cell
            return False  # Continue the game


    def reveal_all_mines(self,grid):
        # Function to reveal all the mines on the grid (called when the game is over)
        for row in grid:
            for cell in row:
                if cell["mine"]:
                    cell["revealed"] = True
                    
    def highlight_probable_mines(self,screen, probable_mines, x_offset, y_offset, CELL_SIZE):
        #Highlights cells that are probable mines in blue.
        for r, c in probable_mines:
            x, y = c * self.CELL_SIZE + x_offset, r * self.CELL_SIZE + y_offset
            pygame.draw.rect(screen, (255, 0, 0), (x, y, self.CELL_SIZE, self.CELL_SIZE), 3)
            
    def initialize_game(self, rows, cols, num_mines):
       #Resets the game to its initial state.
    
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.grid = self.create_grid(rows, cols, num_mines)