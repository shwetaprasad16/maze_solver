
import pygame
import heapq
import sys

# LAB CONFIGURATION
BOARD_DIM = 600
BLOCK_COUNT = 30
UNIT_SIZE = BOARD_DIM // BLOCK_COUNT

# My custom color palette for the project
COLOR_MAP = {
    "bg": (20, 20, 25),
    "lines": (40, 40, 55),
    "wall": (10, 10, 18),
    "start": (0, 255, 120),
    "goal": (255, 65, 75),
    "path": (255, 225, 0),
    "visited": (225, 89, 182),
    "scanning": (255,182,193)}


class MapTile:
    def __init__(self, r, c):
        self.r, self.c = r, c
        self.x, self.y = c * UNIT_SIZE, r * UNIT_SIZE
        self.color = COLOR_MAP["bg"]
        self.is_blocked = False
        self.links = []

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, UNIT_SIZE, UNIT_SIZE))

    def check_links(self, board):
        self.links = []
        # Check adjacent tiles (Down, Up, Right, Left)
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            row_idx, col_idx = self.r + dr, self.c + dc
            if 0 <= row_idx < BLOCK_COUNT and 0 <= col_idx < BLOCK_COUNT:
                neighbor = board[row_idx][col_idx]
                if not neighbor.is_blocked:
                    self.links.append(neighbor)

def manhattan_h(node_a, node_b):
    # Heuristic for Module 2: Informed Search
    return abs(node_a[0] - node_b[0]) + abs(node_a[1] - node_b[1])

def a_star_solver(refresh_ui, board, begin, destination):
    tie_breaker = 0


# The Priority Queue (using heapq module as requested)
    work_queue = []
    heapq.heappush(work_queue, (0, tie_breaker, begin))
    
    trace_back = {}
    g_val = {tile: float("inf") for row in board for tile in row}
    g_val[begin] = 0
    
    f_val = {tile: float("inf") for row in board for tile in row}
    f_val[begin] = manhattan_h((begin.r, begin.c), (destination.r, destination.c))

    tracked_items = {begin}

    while work_queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_tile = heapq.heappop(work_queue)[2]
        tracked_items.remove(current_tile)

        if current_tile == destination:
# Reconstruct the successful path
            step = destination
            while step in trace_back:
                step = trace_back[step]
                if step != begin:
                    step.color = COLOR_MAP["path"]
                refresh_ui()
            return True

        for next_tile in current_tile.links:
            potential_g = g_val[current_tile] + 1
            
            if potential_g < g_val[next_tile]:
                trace_back[next_tile] = current_tile
                g_val[next_tile] = potential_g
                f_val[next_tile] = potential_g + manhattan_h((next_tile.r, next_tile.c), (destination.r, destination.c))
                
                if next_tile not in tracked_items:
                    tie_breaker += 1
                    heapq.heappush(work_queue, (f_val[next_tile], tie_breaker, next_tile))
                    tracked_items.add(next_tile)
                    if next_tile != destination:
                        next_tile.color = COLOR_MAP["scanning"]
        
        refresh_ui()
        if current_tile != begin:
            current_tile.color = COLOR_MAP["visited"]

    return False

def main_loop():
    display = pygame.display.set_mode((BOARD_DIM, BOARD_DIM))
    pygame.display.set_caption("Informed Search Lab: A-Star Pathfinding")
    
# setting up the boxes for the maze here
    world_map = [[MapTile(i, j) for j in range(BLOCK_COUNT)] for i in range(BLOCK_COUNT)]
    
# Set fixed start and end points
    start_point = world_map[3][3]
    start_point.color = COLOR_MAP["start"]
    
    end_point = world_map[BLOCK_COUNT-4][BLOCK_COUNT-4]
    end_point.color = COLOR_MAP["goal"]

    def update_view():
        display.fill(COLOR_MAP["bg"])
        for row in world_map:
            for tile in row:
                tile.draw(display)
        
 # Draw the grid overlay
        for i in range(BLOCK_COUNT):
            pygame.draw.line(display, COLOR_MAP["lines"], (0, i * UNIT_SIZE), (BOARD_DIM, i * UNIT_SIZE))
            pygame.draw.line(display, COLOR_MAP["lines"], (i * UNIT_SIZE, 0), (i * UNIT_SIZE, BOARD_DIM))
        pygame.display.update()

    is_active = True
    while is_active:
        update_view()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                is_active = False

            if pygame.mouse.get_pressed()[0]: # Left click to place walls
                mx, my = pygame.mouse.get_pos()
                r, c = my // UNIT_SIZE, mx // UNIT_SIZE
                if 0 <= r < BLOCK_COUNT and 0 <= c < BLOCK_COUNT:
                    cell = world_map[r][c]
                    if cell != start_point and cell != end_point:
                        cell.is_blocked = True
                        cell.color = COLOR_MAP["wall"]

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: # Trigger search
                    for row in world_map:
                        for cell in row:
                            cell.check_links(world_map)
                    a_star_solver(update_view, world_map, start_point, end_point)

                if e.key == pygame.K_r: # Custom Reset Key
                    main_loop()

    pygame.quit()

if __name__ == "__main__":
    main_loop()