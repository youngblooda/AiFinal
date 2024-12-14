from Game import Game
from AISolver import AISolver 
import pygame

# Initialize pygame
pygame.init()

# Constants for the screen dimensions and other settings
WIDTH, HEIGHT = 600, 600
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
BLACK = (0, 0, 0)
FPS = 60
        
def main():
    game_instance = Game()  # Instantiate the Game class
    running = True
    
    # Main loop
    while running:
        grid_size, num_mines = game_instance.main_menu()

     
        # Adjust screen size and grid dimensions based on selected difficulty
        global WIDTH, HEIGHT, CELL_SIZE
        CELL_SIZE = 30
        screen = pygame.display.set_mode((WIDTH,HEIGHT))
        if isinstance(grid_size, tuple):  # For rectangular grids
            rows, cols = grid_size
            WIDTH, HEIGHT = max(650, cols * CELL_SIZE + 200), rows * CELL_SIZE + 100  # Adjust screen size with extra space for button
        else:
            rows = cols = grid_size
            WIDTH, HEIGHT = max(650, cols * CELL_SIZE + 200), rows * CELL_SIZE + 100  # Adjust screen size with extra space for button

        # Dynamically calculate the cell size based on the grid dimensions
        CELL_SIZE = min(WIDTH // cols, (HEIGHT - 100) // rows)  # Define CELL_SIZE now
        # Use the calculated CELL_SIZE to adjust the screen dimensions
        WIDTH, HEIGHT = max(650, cols * CELL_SIZE + 200), rows * CELL_SIZE + 100

        # Update the Game instance's CELL_SIZE and screen size
        game_instance.CELL_SIZE = CELL_SIZE
        game_instance.WIDTH, game_instance.HEIGHT = WIDTH, HEIGHT
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Minesweeper")
        clock = pygame.time.Clock()

        # Initialize the grid with mines and numbers
        grid = game_instance.create_grid(rows, cols, num_mines)
        solver = AISolver(grid)  # AI Solver instance
        game_over = False
        game_won = False
        start_time = pygame.time.get_ticks()
        flagged_count = 0
        probable_mines = []
        ai_solver_active = False
        loss_time = None
        in_game = True
        
        def check_win_condition():
            #Checks if the game is won by verifying that all non-mine cells are revealed.
            for row in grid:
                for cell in row:
                    if not cell["mine"] and not cell["revealed"]:
                        return False  # A non-mine cell is not revealed
            return True
        with open("accuracy_data.txt", "a") as file:
            file.write("GameData\n")
        while in_game:
            
            
            
            screen.fill(WHITE)
            

            # Calculate elapsed time since game start
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

            # Draw the game grid and UI elements
            game_instance.draw_grid(screen, grid)
            menu_rect = game_instance.game_ui(screen, elapsed_time if not game_over else loss_time, flagged_count, num_mines)

            # Draw the AI Solver button
            font = pygame.font.SysFont(None, 36)
            ai_button_text = font.render("AI Solver", True, BLACK)
            ai_button_rect = ai_button_text.get_rect(center=(WIDTH / 1.75, 25))
            pygame.draw.rect(screen, GRAY, ai_button_rect.inflate(20, 10))
            screen.blit(ai_button_text, ai_button_rect)
        
            
            if ai_solver_active:
                x_offset = (WIDTH - (cols * CELL_SIZE)) // 2
                y_offset = 50
                game_instance.highlight_probable_mines(screen, probable_mines, x_offset, y_offset, CELL_SIZE)

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    in_game = False
                    return
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos

                    # Handle menu button click
                    if menu_rect.collidepoint(x, y):
                        in_game = False
                        
                        
                    # Handle AI Solver button click
                    elif ai_button_rect.collidepoint(x, y):
                        ai_solver_active = not ai_solver_active  # Toggle AI solver
                        if ai_solver_active:
                            # Update probable mines using the solver
                            moves = solver.suggest_moves()
                            probable_mines = moves["mine_cells"]
                        else:
                            # Clear the probable mines if AI solver is toggled off
                            probable_mines = []

                    # Handle grid cell click
                    elif y > 50 and not game_over:
                        x_offset = (WIDTH - (cols * CELL_SIZE)) // 2
                        y_offset = 50
                        col = (x - x_offset) // CELL_SIZE
                        row = (y - y_offset) // CELL_SIZE
                        if 0 <= row < rows and 0 <= col < cols:
                            if event.button == 1:  # Left click
                                game_over = game_instance.handle_click(grid, x - x_offset, y - y_offset, game_over)
                                if game_over:
                                    game_instance.reveal_all_mines(grid)
                                    loss_time = elapsed_time
                                    loss_start_time = pygame.time.get_ticks()
                            elif event.button == 3:  # Right click
                                cell = grid[row][col]
                                if not cell["revealed"]:
                                    if cell["flagged"]:
                                        cell["flagged"] = False
                                        flagged_count -= 1
                                    else:
                                        cell["flagged"] = True
                                        flagged_count += 1
                                        
                            if ai_solver_active:
                                moves = solver.suggest_moves()
                                probable_mines = moves["mine_cells"]
                                
                            actual_mines = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c]["mine"]]
                            accuracy = solver.calculate_accuracy(actual_mines, probable_mines)
                            
                            solver.save_accuracy_to_file()
                            # Check for win condition
                            if check_win_condition():
                                game_won = True
                                in_game = False
                                  # Exit the game loop

            if game_over:

                if (pygame.time.get_ticks() - loss_start_time) >= 10000:
                    in_game = False
            if game_won:
            
                print("You win!")
            
            pygame.display.flip()
            clock.tick(FPS)
            
if __name__ == "__main__":
    main()
    #entry point