import time
import random
import pygame

# Constants
ARENA_X = 800  # Window width in pixels
ARENA_Y = 600  # Window height in pixels
GRID_SIZE = 40  # Size of each grid cell in pixels
GRID_WIDTH = ARENA_X // GRID_SIZE  # 20 cells wide
GRID_HEIGHT = ARENA_Y // GRID_SIZE  # 15 cells tall

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((ARENA_X, ARENA_Y))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
running = True

class Pos:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Snake(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load and scale images (replace with your image paths)
        try:
            self.image = pygame.image.load("snake_head.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (GRID_SIZE, GRID_SIZE))
            self.body_image = pygame.image.load("snake_body.png").convert_alpha()
            self.body_image = pygame.transform.scale(self.body_image, (GRID_SIZE, GRID_SIZE))
        except pygame.error:
            # Fallback to colored rectangles if images fail
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
            self.image.fill((0, 255, 0))  # Green for head
            self.body_image = pygame.Surface((GRID_SIZE, GRID_SIZE))
            self.body_image.fill((0, 200, 0))  # Darker green for body
        self.rect = self.image.get_rect()
        
        self._length = 0
        self._pos = Pos(0, 0)  # Grid coordinates
        self._body = []  # List of Pos objects for body segments
        self._last_move = Pos()
        self.apple = None
        self.direction = "s"  # Valid default direction

    def draw(self, surface):
        # Draw body
        for pos in self._body:
            surface.blit(self.body_image, (pos.y * GRID_SIZE, pos.x * GRID_SIZE))
        # Draw head
        self.rect.topleft = (self._pos.y * GRID_SIZE, self._pos.x * GRID_SIZE)
        surface.blit(self.image, self.rect)

    def move_body(self, last_move: Pos):
        self._body.insert(0, Pos(last_move.x, last_move.y))
        if len(self._body) > self._length:
            self._body.pop()
        self._last_move = Pos(last_move.x, last_move.y)

    def verify_collision(self):
        # Check self-collision
        for segment in self._body:
            if self._pos.x == segment.x and self._pos.y == segment.y:
                return True
        # Check wall collision
        if (self._pos.x < 0 or self._pos.x >= GRID_HEIGHT or 
            self._pos.y < 0 or self._pos.y >= GRID_WIDTH):
            return True
        return False

    def move_head(self, key: str):
        last_move = Pos(self._pos.x, self._pos.y)
        if key == "w" and self.direction != "s":
            self.direction = key
        elif key == "d" and self.direction != "a":
            self.direction = key
        elif key == "s" and self.direction != "w":
            self.direction = key
        elif key == "a" and self.direction != "d":
            self.direction = key

        if self.direction == "w":
            self._pos.x -= 1
        elif self.direction == "d":
            self._pos.y += 1
        elif self.direction == "s":
            self._pos.x += 1
        elif self.direction == "a":
            self._pos.y -= 1

        if self.verify_collision():
            print("Game Over: Collision!")
            return False
        self.move_body(last_move)
        return True

    def place_apple(self):
        while True:
            x = random.randint(0, GRID_HEIGHT - 1)
            y = random.randint(0, GRID_WIDTH - 1)
            if Pos(x, y) not in self._body and (x, y) != (self._pos.x, self._pos.y):
                self.apple = Pos(x, y)
                break

    def eat_apple(self):
        if self.apple and self._pos.x == self.apple.x and self._pos.y == self.apple.y:
            self._length += 1
            self._body.append(Pos(self._last_move.x, self._last_move.y))
            self.place_apple()

class Apple(pygame.sprite.Sprite):
    def __init__(self, pos: Pos):
        super().__init__()
        try:
            self.image = pygame.image.load("apple.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (GRID_SIZE, GRID_SIZE))
        except pygame.error:
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
            self.image.fill((255, 0, 0))  # Red for apple
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = (pos.y * GRID_SIZE, pos.x * GRID_SIZE)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def draw_arena(surface):
    surface.fill((0, 0, 0))  # Black background
    # Draw walls
    # wall_color = (100, 100, 100)  # Gray
    # pygame.draw.rect(surface, wall_color, (0, 0, ARENA_X, GRID_SIZE))  # Top
    # pygame.draw.rect(surface, wall_color, (0, ARENA_Y - GRID_SIZE, ARENA_X, GRID_SIZE))  # Bottom
    # pygame.draw.rect(surface, wall_color, (0, 0, GRID_SIZE, ARENA_Y))  # Left
    # pygame.draw.rect(surface, wall_color, (ARENA_X - GRID_SIZE, 0, GRID_SIZE, ARENA_Y))  # Right

# Initialize game objects
snake = Snake()
all_sprites = pygame.sprite.Group(snake)
snake.place_apple()
apple = Apple(snake.apple)
apple_sprites = pygame.sprite.Group(apple)

# Game loop
last_move_time = time.time()
move_interval = 0.15  # Move every 0.1 seconds
current_key = snake.direction

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_w:
                current_key = "w"
            elif event.key == pygame.K_d:
                current_key = "d"
            elif event.key == pygame.K_s:
                current_key = "s"
            elif event.key == pygame.K_a:
                current_key = "a"

    # Update snake periodically
    if time.time() - last_move_time >= move_interval:
        if not snake.move_head(current_key):
            running = False
        snake.eat_apple()
        # Update apple sprite position
        apple_sprites.empty()
        apple = Apple(snake.apple)
        apple_sprites.add(apple)
        last_move_time = time.time()

    # Draw everything
    draw_arena(screen)
    apple_sprites.draw(screen)
    snake.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()