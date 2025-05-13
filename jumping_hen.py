import pygame
import numpy as np
import pyaudio
import librosa
import threading
import queue
import time
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GROUND_HEIGHT = 500
GRAVITY = 0.8
JUMP_POWER = 15
SOUND_THRESHOLD = 0.1
OBSTACLE_SPEED = 5
MIN_OBSTACLE_DISTANCE = 300

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Set up the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Sound-Controlled Jumping Hen")

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
        # Draw main body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw spikes
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
        self.height = random.randint(40, 100)  # Random height
        self.y = GROUND_HEIGHT - self.height
        self.color = (100, 100, 100)  # Gray
        
    def draw(self, screen):
        # Draw tower base
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw tower top
        pygame.draw.rect(screen, (150, 150, 150), (self.x - 5, self.y, self.width + 10, 10))
        # Draw windows
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
        self.color = (139, 69, 19)  # Brown
        self.cracks = []
        self.generate_cracks()
        
    def generate_cracks(self):
        for _ in range(3):
            crack_x = random.randint(0, self.width)
            crack_y = random.randint(0, self.height)
            self.cracks.append((crack_x, crack_y))
            
    def draw(self, screen):
        # Draw ground piece
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw cracks
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
        # Draw eyes
        eye_color = WHITE
        pygame.draw.circle(screen, eye_color, 
                         (int(self.x + self.width/3), int(self.y + self.height/3)), 5)
        pygame.draw.circle(screen, eye_color, 
                         (int(self.x + 2*self.width/3), int(self.y + self.height/3)), 5)
        # Draw pupils
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x + self.width/3), int(self.y + self.height/3)), 2)
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x + 2*self.width/3), int(self.y + self.height/3)), 2)

class Hen:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = WINDOW_WIDTH // 4
        self.y = GROUND_HEIGHT - self.height
        self.velocity = 0
        self.is_jumping = False
        self.facing_right = True
        
    def jump(self, intensity):
        if not self.is_jumping:
            # Limit jump height based on intensity
            jump_multiplier = min(2.0, 1.0 + intensity)  # Cap at 2x normal jump
            self.velocity = -JUMP_POWER * jump_multiplier
            self.is_jumping = True
            
    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Keep hen within screen bounds
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        elif self.y > GROUND_HEIGHT - self.height:
            self.y = GROUND_HEIGHT - self.height
            self.velocity = 0
            self.is_jumping = False
            
    def draw(self, screen):
        # Draw pixelated hen body
        body_color = (255, 165, 0)  # Orange
        eye_color = (255, 255, 255)  # White
        pupil_color = (0, 0, 0)  # Black
        beak_color = (255, 0, 0)  # Red
        
        # Body
        pygame.draw.rect(screen, body_color, (self.x, self.y, self.width, self.height))
        
        # Head
        head_size = 20
        pygame.draw.rect(screen, body_color, (self.x + self.width - 10, self.y - 5, head_size, head_size))
        
        # Eyes
        eye_size = 6
        eye_x = self.x + self.width + 5
        eye_y = self.y
        pygame.draw.rect(screen, eye_color, (eye_x, eye_y, eye_size, eye_size))
        pygame.draw.rect(screen, pupil_color, (eye_x + 2, eye_y + 2, 2, 2))
        
        # Beak
        pygame.draw.rect(screen, beak_color, (self.x + self.width + 15, self.y + 5, 10, 5))
        
        # Legs
        leg_color = (139, 69, 19)  # Brown
        pygame.draw.rect(screen, leg_color, (self.x + 10, self.y + self.height, 5, 15))
        pygame.draw.rect(screen, leg_color, (self.x + 25, self.y + self.height, 5, 15))

class SoundProcessor:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                 channels=1,
                                 rate=44100,
                                 input=True,
                                 frames_per_buffer=1024)
        self.running = True
        
    def start(self):
        self.thread = threading.Thread(target=self._process_audio)
        self.thread.start()
        
    def _process_audio(self):
        while self.running:
            try:
                data = self.stream.read(1024)
                audio_data = np.frombuffer(data, dtype=np.float32)
                intensity = np.abs(audio_data).mean()
                self.audio_queue.put(intensity)
            except Exception as e:
                print(f"Error processing audio: {e}")
                
    def get_intensity(self):
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return 0
            
    def stop(self):
        self.running = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

def create_obstacle():
    obstacle_types = [Cactus, Tower, BreakingGround, BouncingBall]
    return random.choice(obstacle_types)()

def main():
    clock = pygame.time.Clock()
    hen = Hen()
    sound_processor = SoundProcessor()
    sound_processor.start()
    
    obstacles = []
    last_obstacle_time = time.time()
    score = 0
    game_over = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                # Reset game
                hen = Hen()
                obstacles = []
                score = 0
                game_over = False
                
        if not game_over:
            # Get sound intensity and make hen jump
            intensity = sound_processor.get_intensity()
            if intensity > SOUND_THRESHOLD:
                hen.jump(intensity)
                
            # Update game state
            hen.update()
            
            # Spawn obstacles
            current_time = time.time()
            if current_time - last_obstacle_time > 2:  # Spawn every 2 seconds
                if not obstacles or WINDOW_WIDTH - obstacles[-1].x > MIN_OBSTACLE_DISTANCE:
                    obstacles.append(create_obstacle())
                    last_obstacle_time = current_time
            
            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle.move()
                # Remove obstacles that are off screen
                if obstacle.x + obstacle.width < 0:
                    obstacles.remove(obstacle)
                    score += 1
                
                # Check collision
                if (hen.x < obstacle.x + obstacle.width and
                    hen.x + hen.width > obstacle.x and
                    hen.y < obstacle.y + obstacle.height and
                    hen.y + hen.height > obstacle.y):
                    game_over = True
            
        # Draw everything
        screen.fill(WHITE)
        
        # Draw ground
        pygame.draw.rect(screen, GREEN, (0, GROUND_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - GROUND_HEIGHT))
        
        # Draw obstacles
        for obstacle in obstacles:
            obstacle.draw(screen)
            
        # Draw hen
        hen.draw(screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        
        # Draw sound intensity
        intensity_text = font.render(f"Sound Intensity: {intensity:.2f}", True, BLACK)
        screen.blit(intensity_text, (10, 50))
        
        # Draw game over message
        if game_over:
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render("Game Over!", True, BLACK)
            restart_text = font.render("Press R to Restart", True, BLACK)
            screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(60)
        
    sound_processor.stop()
    pygame.quit()

if __name__ == "__main__":
    main() 