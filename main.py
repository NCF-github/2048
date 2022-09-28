import pygame
import random
import sys
import time
from copy import deepcopy
# Constants

WIDTH = HEIGHT = 800
ROWS = COLUMNS = 4

TILE_WIDTH = WIDTH // COLUMNS
TILE_HEIGHT = HEIGHT // ROWS

BG_COLOR = (50,50,50)
NUMBER_COLOR_LIGHT = (230,230,230)
NUMBER_COLOR_DARK = (50,50,50)

MAX_BUFFERING_TIME = 0.2

pygame.font.init()
FONT = pygame.font.SysFont("comicsans", 80)

TIME_UNTIL_COLISION = 0.15
TIME_GROWING = 0.1
TIME_SHRINKING = 0.1

TOTAL_ANIMATION_TIME = TIME_UNTIL_COLISION + TIME_GROWING + TIME_SHRINKING

MIN_SIZE = 0.5
MAX_SIZE = 1.1

def make_grid():
	grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]

	for _ in range(2):
		add_tile(grid)

	grid = [
	[0, 0, 0, 0],
	[0, 0, 0, 0],
	[0, 0, 0, 0],
	[1, 1, 0, 2],]

	return grid

def add_tile(grid):
	free = get_free_spaces(grid)
	pos = random.choice(free)
	x, y = pos

	grid[y][x] = 1

	return pos

def get_free_spaces(grid):
	free = []

	for j, row in enumerate(grid):
		for i, tile in enumerate(row):
			if not tile:
				free.append((i, j))

	return free

def move(grid, direction, undo_stack, added_tile):
	undo_stack.append(deepcopy(grid))

	if direction == "up":
		new_grid = move_up(grid)
	if direction == "down":
		new_grid = move_down(grid)
	if direction == "left":
		new_grid = move_left(grid)
	if direction == "right":
		new_grid = move_right(grid)

	if new_grid == grid:
		undo_stack.pop()
		return False

	for i in range(len(grid)):
		grid[i] = new_grid[i]

	added_tile[0], added_tile[1] = add_tile(grid)

	return True

def move_up(grid):
	new_grid = rotate_left(grid)
	push(new_grid)
	new_grid = rotate_right(new_grid)
	return new_grid

def move_down(grid):
	new_grid = rotate_right(grid)
	push(new_grid)
	new_grid = rotate_left(new_grid)
	return new_grid

def move_left(grid):
	new_grid = deepcopy(grid)
	push(new_grid)
	return new_grid

def move_right(grid):
	new_grid = [row[::-1] for row in grid]
	push(new_grid)
	new_grid = [row[::-1] for row in new_grid]
	return new_grid

def rotate_right(grid):
	rotated = [[row[i] for row in grid][::-1] for i in range(len(grid[0]))]
	return rotated

def rotate_left(grid):
	rotated = [[row[-i] for row in grid] for i in range(1, len(grid[0])+1)]
	return rotated

def push(grid):
	for row in grid:
		while row[0] == 0 and sum(row) != 0:
			row.pop(0)
			row.append(0)
		for i in range(len(row)-1):
			while row[i+1] == 0 and sum(row[i+1:]) != 0:
				row.pop(i+1)
				row.append(0)
			if row[i] == 0:
				row.pop(i)
				row.append(0)
			if row[i+1] == row[i] and row[i] != 0:
				row[i] = row[i] + 1
				row.pop(i+1)
				row.append(0)

def make_tile(number):
	BORDER = 10
	EDGE_RADIUS = 25

	color = get_color(number)

	surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA, 32)
	surf = surf.convert_alpha()

	pygame.draw.rect(surf, color, (BORDER, BORDER+EDGE_RADIUS, TILE_WIDTH - 2*BORDER, TILE_HEIGHT - 2*(BORDER+EDGE_RADIUS)))
	pygame.draw.rect(surf, color, (BORDER+EDGE_RADIUS, BORDER, TILE_WIDTH - 2*(BORDER+EDGE_RADIUS), TILE_HEIGHT - 2*BORDER))

	pygame.draw.circle(surf, color, (BORDER+EDGE_RADIUS, TILE_HEIGHT-BORDER-EDGE_RADIUS), EDGE_RADIUS)
	pygame.draw.circle(surf, color, (BORDER+EDGE_RADIUS, BORDER+EDGE_RADIUS), EDGE_RADIUS)
	pygame.draw.circle(surf, color, (TILE_WIDTH-BORDER-EDGE_RADIUS, TILE_HEIGHT-BORDER-EDGE_RADIUS), EDGE_RADIUS)
	pygame.draw.circle(surf, color, (TILE_WIDTH-BORDER-EDGE_RADIUS, BORDER+EDGE_RADIUS), EDGE_RADIUS)

	if number == 0:
		return surf

	label = FONT.render(str(2 ** number), 1, get_number_color(number))

	width = label.get_width()
	height = label.get_height()
	max_width = TILE_WIDTH - 2*(BORDER+1)
	max_height = TILE_HEIGHT - 2*(BORDER+1)

	label = pygame.transform.scale(label, (min(width, max_width), min(height, max_height)))

	if width < max_width:
		x = TILE_WIDTH//2 - width//2
	else:
		x = BORDER + 1

	if height < max_height:
		y = TILE_HEIGHT//2 - height//2
	else:
		y = BORDER + 1

	surf.blit(label, (x, y))

	return surf

def get_color(number):
	if number == 0:
		color = (150,150,150)

	elif number < 7:
		val = 35
		color = (255, 268 - val*number, 223 - val*number)

	elif number < 12:
		number = number - 7
		val1 = 6
		val2 = 30
		color = (255, 229 - val1*number, 135 - val2*number)

	elif number < 15:
		number = number - 12
		val = 40
		color = (241, 145 - number*val, 155 - number*val)

	elif number < 18:
		number = number - 15
		val = 45
		color = (186 - number*val, 219 - number*val, 255)

	else:
		color = (0,0,0)

	return color

def get_number_color(number):
	if number > 6 and number < 12:
		return NUMBER_COLOR_DARK

	THRESHOLD = 180
	if sum(get_color(number)) > THRESHOLD * 3:
		return NUMBER_COLOR_DARK

	else:
		return NUMBER_COLOR_LIGHT

def draw(screen, grid, tiles):
	screen.fill(BG_COLOR)

	for j, row in enumerate(grid):
		for i, tile in enumerate(row):
			screen.blit(tiles[tile], (TILE_WIDTH*i, TILE_HEIGHT*j))

	pygame.display.update()

def generate_next_tile_if_needed(grid, tiles):
	for row in grid:
		for tile in row:
			if tile > len(tiles)-1:
				generate_next_tile(tiles)

def generate_next_tile(tiles):
	tiles.append(make_tile(len(tiles)))

def draw_animation(screen, old_grid, grid, tiles, in_animation, start_time_of_animation, current_animation, added_tile):
	screen.fill(BG_COLOR)

	time_passed = time.time() - start_time_of_animation

	for j, row in enumerate(old_grid):
		for i, tile in enumerate(row):
			screen.blit(tiles[0], (TILE_WIDTH*i, TILE_HEIGHT*j))

	if time_passed < TIME_UNTIL_COLISION:
		draw_phase_1(screen, old_grid, tiles, time_passed, current_animation)
	else:
		draw_phase_2(screen, grid, old_grid, tiles, time_passed, current_animation, added_tile)

	pygame.display.update()

	if time_passed > TOTAL_ANIMATION_TIME:
		return False
	else:
		return True

def draw_phase_1(screen, old_grid, tiles, time_passed, current_animation):
	data = get_data_1(old_grid, current_animation)

	percentage_of_animation = time_passed / TIME_UNTIL_COLISION
	for item in data.items():
		old_pos, new_pos = item

		old_x, old_y = old_pos
		new_x, new_y = new_pos

		x = old_x + (new_x - old_x) * percentage_of_animation
		y = old_y + (new_y - old_y) * percentage_of_animation

		tile = old_grid[old_y][old_x]

		screen.blit(tiles[tile], (int(TILE_WIDTH*x), int(TILE_HEIGHT*y)))


def get_data_1(old_grid, current_animation):
	moved_positions = {}

	if current_animation == "up":
		for i in range(len(old_grid[0])):
			moved = 0
			last = 0
			col = [old_grid[j][i] for j in range(len(old_grid))]
			for j, tile in enumerate(col):
				if tile == 0:
					moved += 1
				else:
					if tile == last:
						moved += 1
						last = 0
					else:
						last = tile
					moved_positions[(i, j)] = (i, j-moved)

	if current_animation == "down":
		for i in range(len(old_grid[0])):
			moved = 0
			last = 0
			col = [old_grid[j][i] for j in range(len(old_grid))]
			for j, tile in enumerate(col[::-1]):
				if tile == 0:
					moved += 1
				else:
					if tile == last:
						moved += 1
						last = 0
					else:
						last = tile
					moved_positions[(i, len(col)-1-j)] = (i, len(col)-1-j+moved)

	if current_animation == "left":
		for j, row in enumerate(old_grid):
			moved = 0
			last = 0
			for i, tile in enumerate(row):
				if tile == 0:
					moved += 1
				else:
					if tile == last:
						moved += 1
						last = 0
					else:
						last = tile
					moved_positions[(i, j)] = (i-moved, j)

	if current_animation == "right":
		for j, row in enumerate(old_grid):
			moved = 0
			last = 0
			for i, tile in enumerate(row[::-1]):
				if tile == 0:
					moved += 1
				else:
					if tile == last:
						moved += 1
						last = 0
					else:
						last = tile
					moved_positions[(len(row)-1-i, j)] = (len(row)-1-i+moved, j)

	return moved_positions

def draw_phase_2(screen, grid, old_grid, tiles, time_passed, current_animation, added_tile):
	data = get_data_2(get_data_1(old_grid, current_animation), grid, old_grid, current_animation, added_tile)

	for j, row in enumerate(grid):
		for i, tile in enumerate(row):
			if (i, j) in data:
				if time_passed < TIME_UNTIL_COLISION + TIME_GROWING:
					percentage_of_animation = (time_passed - TIME_UNTIL_COLISION) / TIME_GROWING
					scaling_factor = MIN_SIZE + (MAX_SIZE-MIN_SIZE)*percentage_of_animation
				else:
					percentage_of_animation = (TIME_UNTIL_COLISION + TIME_GROWING + TIME_SHRINKING - time_passed) / TIME_SHRINKING
					scaling_factor = 1 + (MAX_SIZE-1)*percentage_of_animation

				image = tiles[tile]
				image = pygame.transform.scale(image, (int(image.get_width()*scaling_factor), int(image.get_height()*scaling_factor)))

				x_offset = (image.get_width() - TILE_WIDTH) // 2
				y_offset = (image.get_height() - TILE_HEIGHT) // 2

				screen.blit(image, (TILE_WIDTH*i - x_offset, TILE_HEIGHT*j - y_offset))
			else:
				screen.blit(tiles[tile], (TILE_WIDTH*i, TILE_HEIGHT*j))

def get_data_2(data, grid, old_grid, current_animation, added_tile):
	merged = []

	data = [item[1] for item in data.items()]

	for pos in data:
		if data.count(pos) > 1 and pos not in merged:
			merged.append(pos)

	merged.append((added_tile[0], added_tile[1]))

	return merged

def enter_final_state(screen, tiles, grid, clock):
	INCREMENT = 2.5
	TRANSPARENCY_LIMIT = 220
	TEXT_OFFSET = 40
	MIN_TRANSPARENCY_TO_RESET_GAME = 200

	alpha_key = 1

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
			if event.type == pygame.KEYDOWN and MIN_TRANSPARENCY_TO_RESET_GAME > alpha_key:
				FONT = pygame.font.SysFont("comicsans", 80)
				for i, row in enumerate(make_grid()):
					grid[i] = row
				return

		screen.fill(BG_COLOR)
		for j, row in enumerate(grid):
			for i, tile in enumerate(row):
				screen.blit(tiles[tile], (TILE_WIDTH*i, TILE_HEIGHT*j))

		FONT = pygame.font.SysFont("comicsans", 100)
		label1 = FONT.render("You lost", 1, (255,255,255))

		FONT = pygame.font.SysFont("comicsans", 60)
		label2 = FONT.render("Press any key to continue", 1, (255,255,255))

		black_surface = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)

		color = (0,0,0)
		black_surface.fill(color)

		black_surface.blit(label1, (screen.get_width()//2 - label1.get_width()//2, screen.get_height()//2 - label1.get_height()//2 - TEXT_OFFSET))
		black_surface.blit(label2, (screen.get_width()//2 - label2.get_width()//2, screen.get_height()//2 - label1.get_height()//2 - TEXT_OFFSET + 100))

		black_surface.set_alpha(min(TRANSPARENCY_LIMIT, int(alpha_key)))

		screen.blit(black_surface, screen.get_rect())

		alpha_key += INCREMENT

		pygame.display.update()
		clock.tick(120)

def quit():
	sys.exit()
	pygame.quit()

def check_if_lost(grid):
	for row in grid:
		for i in range(1, len(row)):
			if row[i] == row[i-1]:
				return False

	temp_grid = rotate_left(grid)
	for row in temp_grid:
		for i in range(1, len(row)):
			if row[i] == row[i-1]:
				return False

	if get_free_spaces(grid):
		return False

	return True

def main():
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("2048")
	clock = pygame.time.Clock()

	grid = make_grid()
	undo_stack = []
	moves_queue = []

	tiles = [make_tile(0)]
	for i in range(30):
		generate_next_tile(tiles)

	in_animation = False
	start_time_of_animation = time.time()
	current_animation = None

	added_tile = [0, 0]

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					moves_queue.append(("up", time.time()))
				if event.key == pygame.K_DOWN:
					moves_queue.append(("down", time.time()))
				if event.key == pygame.K_LEFT:
					moves_queue.append(("left", time.time()))
				if event.key == pygame.K_RIGHT:
					moves_queue.append(("right", time.time()))
				if event.key == pygame.K_SPACE:
					moves_queue.append(("space", time.time()))

		generate_next_tile_if_needed(grid, tiles)

		if not in_animation and check_if_lost(grid):
			enter_final_state(screen, tiles, grid, clock)
			moves_queue = []
			undo_stack = []
			added_tile = [0, 0]

		if not in_animation:
			if moves_queue:
				if moves_queue[0][0] == "space":
					if undo_stack:
						grid = undo_stack.pop()
						moves_queue.pop(0)
				else:
					current_animation = moves_queue.pop(0)[0]
					start_time_of_animation = time.time()
					old_grid = deepcopy(grid)
					in_animation = move(grid, current_animation, undo_stack, added_tile)

				for m in moves_queue:
					if type(m) == type(()):
						if time.time() - m[1] > MAX_BUFFERING_TIME:
							moves_queue.remove(m)

		if in_animation:
			in_animation = draw_animation(screen, old_grid, grid, tiles, in_animation, start_time_of_animation, current_animation, added_tile)
		else:
			draw(screen, grid, tiles)

		clock.tick(120)


if __name__ == "__main__":
	main()