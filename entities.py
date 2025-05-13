import pygame
import random
import math
from constants import *

class Hen:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = WINDOW_WIDTH // 4
        self.y = GROUND_HEIGHT - self.height
        self.velocity = 0
        self.is_jumping = False
        self.facing_right = True
        self.last_jump_time = 0
        self.jump_cooldown = 0.05
        
    def jump(self, intensity):
        current_time = time.time()
        if not self.is_jumping and (current_time - self.last_jump_time) > self.jump_cooldown:
            jump_multiplier = min(2.5, 1.0 + (intensity * 3))
            self.velocity = -JUMP_POWER * jump_multiplier
            self.is_jumping = True
            self.last_jump_time = current_time
            
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        elif self.y > GROUND_HEIGHT - self.height:
            self.y = GROUND_HEIGHT - self.height
            self.velocity = 0
            self.is_jumping = False
            
    def draw(self, screen):
        try:
            x = max(0, min(int(self.x), WINDOW_WIDTH - self.width))
            y = max(0, min(int(self.y), WINDOW_HEIGHT - self.height))
            
            # Draw pixelated hen body
            body_color = (255, 165, 0)  # Orange
            eye_color = (255, 255, 255)  # White
            pupil_color = (0, 0, 0)  # Black
            beak_color = (255, 0, 0)  # Red
            
            # Body
            pygame.draw.rect(screen, body_color, (x, y, self.width, self.height))
            
            # Head
            head_size = 20
            head_x = x + self.width - 10
            head_y = y - 5
            pygame.draw.rect(screen, body_color, (head_x, head_y, head_size, head_size))
            
            # Eyes
            eye_size = 6
            eye_x = x + self.width + 5
            eye_y = y
            pygame.draw.rect(screen, eye_color, (eye_x, eye_y, eye_size, eye_size))
            pygame.draw.rect(screen, pupil_color, (eye_x + 2, eye_y + 2, 2, 2))
            
            # Beak
            beak_x = x + self.width + 15
            beak_y = y + 5
            pygame.draw.rect(screen, beak_color, (beak_x, beak_y, 10, 5))
            
            # Legs
            leg_color = (139, 69, 19)  # Brown
            leg_y = y + self.height
            pygame.draw.rect(screen, leg_color, (x + 10, leg_y, 5, 15))
            pygame.draw.rect(screen, leg_color, (x + 25, leg_y, 5, 15))
            
        except Exception as e:
            print(f"Error drawing hen: {e}")
            self.x = WINDOW_WIDTH // 4
            self.y = GROUND_HEIGHT - self.height
            self.velocity = 0
            self.is_jumping = False

class Obstacle:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = WINDOW_WIDTH
        self.y = GROUND_HEIGHT - self.height
        self.color = BROWN
        
    def move(self):
        self.x -= OBSTACLE_SPEED
        
    def draw(self, screen):
        pass
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Cactus(Obstacle):
    def __init__(self):
        super().__init__()
        self.color = (0, 100, 0)  # Dark green
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        for i in range(3):
            spike_y = self.y + i * 20
            pygame.draw.polygon(screen, self.color, [
                (self.x + self.width, spike_y),
                (self.x + self.width + 15, spike_y + 10),
                (self.x + self.width, spike_y + 20)
            ])

class Tower(Obstacle):
    def __init__(self):
        super().__init__()
        self.height = random.randint(40, 100)
        self.y = GROUND_HEIGHT - self.height
        self.color = (100, 100, 100)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (150, 150, 150), (self.x - 5, self.y, self.width + 10, 10))
        window_color = (200, 200, 255)
        for i in range(2):
            window_y = self.y + 20 + i * 30
            pygame.draw.rect(screen, window_color, (self.x + 5, window_y, 10, 15))

class BreakingGround(Obstacle):
    def __init__(self):
        super().__init__()
        self.width = 60
        self.height = 20
        self.y = GROUND_HEIGHT - self.height
        self.color = BROWN
        self.cracks = []
        self.generate_cracks()
        
    def generate_cracks(self):
        for _ in range(3):
            crack_x = random.randint(0, self.width)
            crack_y = random.randint(0, self.height)
            self.cracks.append((crack_x, crack_y))
            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        for crack_x, crack_y in self.cracks:
            pygame.draw.line(screen, BLACK, 
                           (self.x + crack_x, self.y + crack_y),
                           (self.x + crack_x + random.randint(-5, 5), 
                            self.y + crack_y + random.randint(-5, 5)), 2)

class BouncingBall(Obstacle):
    def __init__(self):
        super().__init__()
        self.width = 30
        self.height = 30
        self.y = GROUND_HEIGHT - self.height
        self.color = RED
        self.bounce_height = 50
        self.original_y = self.y
        self.bounce_speed = 0.1
        self.bounce_offset = 0
        
    def move(self):
        self.x -= OBSTACLE_SPEED
        self.bounce_offset += self.bounce_speed
        self.y = self.original_y - abs(math.sin(self.bounce_offset)) * self.bounce_height
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, 
                         (int(self.x + self.width/2), int(self.y + self.height/2)), 
                         int(self.width/2))
        eye_color = WHITE
        pygame.draw.circle(screen, eye_color, 
                         (int(self.x + self.width/3), int(self.y + self.height/3)), 5)
        pygame.draw.circle(screen, eye_color, 
                         (int(self.x + 2*self.width/3), int(self.y + self.height/3)), 5)
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x + self.width/3), int(self.y + self.height/3)), 2)
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x + 2*self.width/3), int(self.y + self.height/3)), 2)

def create_obstacle():
    obstacle_types = [Cactus, Tower, BreakingGround, BouncingBall]
    return random.choice(obstacle_types)() 