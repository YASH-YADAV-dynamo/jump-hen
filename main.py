import pygame
import sys
import time
from entities import Hen, create_obstacle
from sound_processor import SoundProcessor
from wallet_handler import WalletHandler
from constants import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sound-Controlled Hen Game")
        self.clock = pygame.time.Clock()
        
        # Initialize game objects
        self.hen = Hen()
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.last_obstacle_time = time.time()
        
        # Initialize sound processor
        self.sound_processor = SoundProcessor()
        self.sound_processor.start()
        
        # Initialize wallet handler
        self.wallet_handler = WalletHandler()
        self.wallet_connected = False
        self.show_wallet_screen = True
        self.wallet_screen_state = "main"  # main, connecting, error, success
        
        # Font for UI
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
        # UI elements
        self.error_message = ""
        self.connection_status = ""
        self.wallet_balance = "0"
        self.wallet_address = ""
        
    def draw_wallet_screen(self):
        # Draw background
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.title_font.render("Connect Solana Wallet", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw instructions
        instructions = self.font.render("Enter your Solana wallet address:", True, BLACK)
        instructions_rect = instructions.get_rect(center=(WINDOW_WIDTH//2, 200))
        self.screen.blit(instructions, instructions_rect)
        
        # Draw input box
        input_box = pygame.Rect(WINDOW_WIDTH//2 - 200, 250, 400, 50)
        pygame.draw.rect(self.screen, BLACK, input_box, 2)
        
        # Draw current input
        if self.wallet_address:
            text = self.font.render(self.wallet_address, True, BLACK)
            text_rect = text.get_rect(midleft=(input_box.x + 10, input_box.centery))
            self.screen.blit(text, text_rect)
        
        # Draw connect button
        button_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, 350, 200, 50)
        button_color = GREEN if self.wallet_address else (200, 200, 200)  # Gray if no address
        pygame.draw.rect(self.screen, button_color, button_rect)
        connect_text = self.font.render("Connect", True, WHITE)
        connect_rect = connect_text.get_rect(center=button_rect.center)
        self.screen.blit(connect_text, connect_rect)
        
        # Draw status messages
        if self.wallet_screen_state == "connecting":
            status_text = self.font.render("Connecting to wallet...", True, BLUE)
            status_rect = status_text.get_rect(center=(WINDOW_WIDTH//2, 450))
            self.screen.blit(status_text, status_rect)
        elif self.wallet_screen_state == "error":
            error_text = self.font.render(self.error_message, True, RED)
            error_rect = error_text.get_rect(center=(WINDOW_WIDTH//2, 450))
            self.screen.blit(error_text, error_rect)
        elif self.wallet_screen_state == "success":
            success_text = self.font.render("Wallet connected successfully!", True, GREEN)
            success_rect = success_text.get_rect(center=(WINDOW_WIDTH//2, 450))
            self.screen.blit(success_text, success_rect)
            
            # Show wallet info
            network_text = self.font.render(f"Network: {self.wallet_handler.get_network_name()}", True, BLACK)
            network_rect = network_text.get_rect(center=(WINDOW_WIDTH//2, 500))
            self.screen.blit(network_text, network_rect)
            
            balance_text = self.font.render(f"Balance: {self.wallet_balance} SOL", True, BLACK)
            balance_rect = balance_text.get_rect(center=(WINDOW_WIDTH//2, 550))
            self.screen.blit(balance_text, balance_rect)
            
            # Show start game button
            start_button = pygame.Rect(WINDOW_WIDTH//2 - 100, 600, 200, 50)
            pygame.draw.rect(self.screen, GREEN, start_button)
            start_text = self.font.render("Start Game", True, WHITE)
            start_rect = start_text.get_rect(center=start_button.center)
            self.screen.blit(start_text, start_rect)
            return start_button
            
        # Draw help text
        help_text = self.small_font.render("Enter your Solana wallet address to connect", True, (100, 100, 100))
        help_rect = help_text.get_rect(center=(WINDOW_WIDTH//2, 500))
        self.screen.blit(help_text, help_rect)
        
        return button_rect
        
    def handle_wallet_screen(self):
        button_rect = self.draw_wallet_screen()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.cleanup()
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if connect button was clicked
                if button_rect.collidepoint(event.pos) and self.wallet_address:
                    self.connect_wallet()
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.wallet_address = self.wallet_address[:-1]
                elif event.key == pygame.K_RETURN and self.wallet_address:
                    self.connect_wallet()
                else:
                    self.wallet_address += event.unicode
                    
        pygame.display.flip()
        
    def connect_wallet(self):
        self.wallet_screen_state = "connecting"
        pygame.display.flip()
        
        try:
            success, message = self.wallet_handler.connect_wallet(self.wallet_address)
            if success:
                self.wallet_connected = True
                self.wallet_screen_state = "success"
                self.wallet_balance = str(self.wallet_handler.get_balance())
            else:
                self.wallet_screen_state = "error"
                self.error_message = message
        except Exception as e:
            self.wallet_screen_state = "error"
            self.error_message = f"Connection error: {str(e)}"
            
    def check_rewards(self):
        if self.score >= 100 and self.wallet_connected:
            success, message = self.wallet_handler.send_reward(self.score)
            if success:
                print(f"Reward sent: {message}")
                # Reset score after reward
                self.score = 0
            else:
                print(f"Failed to send reward: {message}")
                
    def run(self):
        while True:
            if self.show_wallet_screen:
                self.handle_wallet_screen()
                continue
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    pygame.quit()
                    sys.exit()
                    
            if not self.game_over:
                # Get sound intensity
                intensity = self.sound_processor.get_intensity()
                
                # Handle jumping
                if intensity > SOUND_THRESHOLD:
                    self.hen.jump(intensity)
                    
                # Update game objects
                self.hen.update()
                
                # Spawn obstacles
                current_time = time.time()
                if current_time - self.last_obstacle_time > 2.0:
                    self.obstacles.append(create_obstacle())
                    self.last_obstacle_time = current_time
                    
                # Update and remove obstacles
                for obstacle in self.obstacles[:]:
                    obstacle.move()
                    if obstacle.x < -obstacle.width:
                        self.obstacles.remove(obstacle)
                        self.score += 10
                        
                # Check collisions
                hen_rect = pygame.Rect(self.hen.x, self.hen.y, self.hen.width, self.hen.height)
                for obstacle in self.obstacles:
                    if hen_rect.colliderect(obstacle.get_rect()):
                        self.game_over = True
                        
                # Check for rewards
                self.check_rewards()
                
            # Draw everything
            self.screen.fill(WHITE)
            
            # Draw ground
            pygame.draw.rect(self.screen, GREEN, (0, GROUND_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - GROUND_HEIGHT))
            
            # Draw game objects
            self.hen.draw(self.screen)
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)
                
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, BLACK)
            self.screen.blit(score_text, (10, 10))
            
            # Draw wallet info
            if self.wallet_connected:
                balance = self.wallet_handler.get_balance()
                wallet_text = self.font.render(f"Wallet Balance: {balance} SOL", True, BLACK)
                self.screen.blit(wallet_text, (10, 50))
                
            # Draw game over screen
            if self.game_over:
                game_over_text = self.font.render("Game Over! Press R to restart", True, RED)
                self.screen.blit(game_over_text, (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2))
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.reset_game()
                    
            pygame.display.flip()
            self.clock.tick(60)
            
    def reset_game(self):
        self.hen = Hen()
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.last_obstacle_time = time.time()
        
    def cleanup(self):
        self.sound_processor.stop()
        
if __name__ == "__main__":
    game = Game()
    game.run() 