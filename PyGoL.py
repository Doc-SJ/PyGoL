import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1500, 1000
CELL_SIZE = 9
GRID_WIDTH, GRID_HEIGHT = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
CLOCK_SPEED = 120
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Setup the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Initialize font
pygame.font.init()
font = pygame.font.SysFont('Arial', 20)

# Grid setup
def empty_grid():
    return np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=bool)

def random_grid():
    return np.random.choice([False, True], size=(GRID_HEIGHT, GRID_WIDTH))

grid = empty_grid()
grid_history = [grid.copy()]  # History of grid states
step_count = 0  # Step counter
playing = False  # Playing state
needs_redraw = True  # Flag to redraw the grid

# Add toroidal wrapping
def update_grid():
    global grid, step_count, grid_history, needs_redraw
    new_grid = np.zeros_like(grid)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            # Calculating the positions of neighbors with wrapping
            neighbors = [
                grid[(y - 1) % GRID_HEIGHT, (x - 1) % GRID_WIDTH],  # Top-left
                grid[(y - 1) % GRID_HEIGHT, x],                      # Top
                grid[(y - 1) % GRID_HEIGHT, (x + 1) % GRID_WIDTH],  # Top-right
                grid[y, (x - 1) % GRID_WIDTH],                      # Left
                grid[y, (x + 1) % GRID_WIDTH],                      # Right
                grid[(y + 1) % GRID_HEIGHT, (x - 1) % GRID_WIDTH],  # Bottom-left
                grid[(y + 1) % GRID_HEIGHT, x],                      # Bottom
                grid[(y + 1) % GRID_HEIGHT, (x + 1) % GRID_WIDTH]   # Bottom-right
            ]
            alive_neighbors = sum(neighbors)

            # Apply rules of the automaton
            new_grid[y, x] = alive_neighbors == 3 if not grid[y, x] else alive_neighbors in [2, 3]

    grid = new_grid
    step_count += 1
    grid_history.append(grid.copy())
    needs_redraw = True

# Draw grid
def draw_grid():
    screen.fill(BLACK)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y, x]:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect)

# Display step count and buttons
def display_ui():
    # Step count
    step_surface = font.render(f'Steps: {step_count}', True, WHITE)
    screen.blit(step_surface, (10, 10))

    # Random Soup button
    random_soup_button_rect = pygame.Rect(WIDTH - 110, 20, 100, 40)
    pygame.draw.rect(screen, GRAY, random_soup_button_rect)
    text_surface = font.render('Random', True, BLACK)
    screen.blit(text_surface, (random_soup_button_rect.x + 15, random_soup_button_rect.y + 10))

    # Clear Grid button
    clear_grid_button_rect = pygame.Rect(WIDTH - 220, 20, 100, 40)  # Adjust position as needed
    pygame.draw.rect(screen, GRAY, clear_grid_button_rect)
    clear_text_surface = font.render('Clear', True, BLACK)
    screen.blit(clear_text_surface, (clear_grid_button_rect.x + 25, clear_grid_button_rect.y + 10))

    return random_soup_button_rect, clear_grid_button_rect

# Main loop
clock = pygame.time.Clock()
while True:
    random_soup_button_rect, clear_grid_button_rect = display_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                playing = not playing
                needs_redraw = True
            elif event.key == pygame.K_RIGHT:
                update_grid()
            elif event.key == pygame.K_LEFT and len(grid_history) > 1:
                grid_history.pop()  # Remove the current state
                grid = grid_history.pop()  # Step back to the previous state
                step_count -= 1
                needs_redraw = True

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if random_soup_button_rect.collidepoint(x, y):
                grid = random_grid()
                grid_history = [grid.copy()]
                step_count = 0
                needs_redraw = True
            elif clear_grid_button_rect.collidepoint(x, y):
                # Clear grid
                grid = empty_grid()
                grid_history = [grid.copy()]
                step_count = 0
                needs_redraw = True
            elif 0 <= x < WIDTH and 0 <= y < HEIGHT:
                grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    grid[grid_y][grid_x] = not grid[grid_y][grid_x]
                    grid_history = [grid.copy()]  # Reset history when manually editing
                    step_count = 0
                    needs_redraw = True

    if playing:
        update_grid()

    if needs_redraw:
        draw_grid()
        needs_redraw = False

    pygame.display.flip()
    clock.tick(CLOCK_SPEED)
