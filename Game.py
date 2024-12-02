import pygame
import random

pygame.init()

# Constants
WIDTH, HEIGHT = 400, 400  # Grid size
GRID_SIZE = 10            # Number of rows/columns
CELL_SIZE = WIDTH // GRID_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")
clock = pygame.time.Clock()



def main_menu():
    screen.fill(WHITE)
    font = pygame.font.SysFont(None, 48)

    # Menu options
    options = ["Easy (8x8, 10 Mines)", "Medium (16x16, 40 Mines)", "Hard (24x24, 99 Mines)"]
    buttons = []
    y_offset = 150

    # Draw buttons
    for option in options:
        text = font.render(option, True, BLACK)
        rect = text.get_rect(center=(WIDTH // 2, y_offset))
        buttons.append((rect, option))
        pygame.draw.rect(screen, GRAY, rect.inflate(20, 20))
        screen.blit(text, rect)
        y_offset += 100

    pygame.display.flip()

    # Wait for user input
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for rect, option in buttons:
                    if rect.collidepoint(x, y):
                        if "Easy" in option:
                            return 8, 10
                        elif "Medium" in option:
                            return 16, 40
                        elif "Hard" in option:
                            return 24, 99


def create_grid(size, num_mines):
    grid = [[{"mine": False, "revealed": False, "flagged": False, "number": 0} for _ in range(size)] for _ in range(size)]

    # Place mines
    mines = random.sample(range(size * size), num_mines)
    for mine in mines:
        row, col = divmod(mine, size)
        grid[row][col]["mine"] = True

    # Calculate numbers
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for r in range(size):
        for c in range(size):
            if not grid[r][c]["mine"]:
                grid[r][c]["number"] = sum(
                    grid[r + dr][c + dc]["mine"]
                    for dr, dc in directions
                    if 0 <= r + dr < size and 0 <= c + dc < size
                )
    return grid

def draw_grid(screen, grid):
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            x, y = c * CELL_SIZE, r * CELL_SIZE + 50  # Offset by 50 for UI
            pygame.draw.rect(screen, GRAY if cell["revealed"] else WHITE, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)

            if cell["revealed"]:
                if cell["mine"]:
                    pygame.draw.circle(screen, RED, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), CELL_SIZE // 4)
                elif cell["number"] > 0:
                    font = pygame.font.SysFont(None, 36)
                    text = font.render(str(cell["number"]), True, BLACK)
                    screen.blit(text, (x + 10, y + 5))
            elif cell["flagged"]:
                pygame.draw.polygon(screen, RED, [
                    (x + CELL_SIZE // 4, y + CELL_SIZE // 4),
                    (x + 3 * CELL_SIZE // 4, y + CELL_SIZE // 2),
                    (x + CELL_SIZE // 4, y + 3 * CELL_SIZE // 4)
                ])

def game_ui(screen, timer, flagged_count, total_mines):
    font = pygame.font.SysFont(None, 36)

    # Draw timer
    timer_text = font.render(f"Time: {timer}s", True, BLACK)
    screen.blit(timer_text, (WIDTH - 150, 10))

    # Draw mine counter
    mines_text = font.render(f"Flags: {flagged_count}/{total_mines}", True, BLACK)
    screen.blit(mines_text, (10, 10))

    # Draw menu button
    menu_text = font.render("Menu", True, BLACK)
    menu_rect = menu_text.get_rect(center=(WIDTH // 2, 30))
    pygame.draw.rect(screen, GRAY, menu_rect.inflate(20, 10))
    screen.blit(menu_text, menu_rect)

    return menu_rect
def reveal_cell(grid, row, col):
    try:
        if grid[row][col]["revealed"] or grid[row][col]["flagged"]:
            return
    except IndexError:
        print(f"Invalid access: row={row}, col={col}")
        return



    grid[row][col]["revealed"] = True

    # Reveal surrounding cells if no adjacent mines
    if grid[row][col]["number"] == 0 and not grid[row][col]["mine"]:
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in directions:
            if 0 <= row + dr < GRID_SIZE and 0 <= col + dc < GRID_SIZE:
                reveal_cell(grid, row + dr, col + dc)


def handle_click(grid, x, y, game_over):
    if game_over:
        return False  # Game already over

    col, row = x // CELL_SIZE, y // CELL_SIZE
    cell = grid[row][col]

    if cell["mine"]:
        return True  # Game over
    else:
        reveal_cell(grid, row, col)
        return False  # Continue playing


def reveal_all_mines(grid):
    for row in grid:
        for cell in row:
            if cell["mine"]:
                cell["revealed"] = True


def main():
    running = True
    while running:
        # Display menu and get difficulty
        grid_size, num_mines = main_menu()

        # Adjust screen size for larger grids
        global WIDTH, HEIGHT, CELL_SIZE
        CELL_SIZE = 30
        WIDTH, HEIGHT = grid_size * CELL_SIZE, grid_size * CELL_SIZE + 50  # Extra space for UI
        pygame.display.set_mode((WIDTH, HEIGHT))

        # Initialize game
        grid = create_grid(grid_size, num_mines)
        game_over = False
        start_time = pygame.time.get_ticks()  # Track start time
        flagged_count = 0

        while True:
            screen.fill(WHITE)

            # Calculate elapsed time
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

            # Draw grid and UI
            draw_grid(screen, grid)
            menu_rect = game_ui(screen, elapsed_time, flagged_count, num_mines)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos

                    # Handle menu button
                    if menu_rect.collidepoint(x, y):
                        return  # Return to main menu

                    # Game grid clicks
                    if y > 50 and not game_over:  # Ensure clicks are below the UI
                        col, row = x // CELL_SIZE, (y - 50) // CELL_SIZE
                        if event.button == 1:  # Left click
                            game_over = handle_click(grid, x, y - 50, game_over)
                            if game_over:
                                reveal_all_mines(grid)
                        elif event.button == 3:  # Right click for flagging
                            cell = grid[row][col]
                            if not cell["revealed"]:
                                if cell["flagged"]:
                                    cell["flagged"] = False
                                    flagged_count -= 1
                                else:
                                    cell["flagged"] = True
                                    flagged_count += 1

            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()