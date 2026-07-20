import pygame
import sys
import requests
import threading
import time

# Initialize Pygame engine and text subsystems
pygame.init()
pygame.font.init()

# Setup vintage screen resolution and color constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GenAI Open-World Agent Sandbox")

COLOR_BG = (15, 23, 42)         # Slate 900
COLOR_GRID = (30, 41, 59)       # Slate 800
COLOR_PLAYER = (59, 130, 246)   # Blue
COLOR_IGNIS = (239, 68, 68)     # Red
COLOR_LUNA = (168, 85, 247)     # Purple
COLOR_TEXT_BG = (2, 6, 23)      # Slate 950 (Dark Bubble)
COLOR_TEXT_BORDER = (52, 211, 153) # Emerald 400

# Set up local fonts (Fallback to standard system system font rendering)
game_font = pygame.font.SysFont("Courier", 14, bold=True)

# Positions for our entities [X, Y]
player_pos = [150, 300]
ignis_pos = [250, 200]
luna_pos = [320, 200]

player_speed = 5
clock = pygame.time.Clock()

# Dynamic Text Bubble State Tracking Engine Variables
active_dialogue_text = ""
active_dialogue_sender = ""
dialogue_expiry_time = 0.0

# Timers to control NPC autonomous action frequency
NPC_TICK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NPC_TICK_EVENT, 12000) # Ticks every 12 seconds

def trigger_npc_interaction():
    """Async background task so the game engine mechanics don't lag during API requests."""
    global active_dialogue_text, active_dialogue_sender, dialogue_expiry_time
    try:
        payload = {
            "npc_id": "ignis",
            "message": "Archmage Luna! What are you doing outside your tower? Is that magical residue I smell?"
        }

         # ─── ADD THIS EXACT DIAGNOSTIC PRINT LINE HERE ───
        print("DEBUG URL RUNTIME CHECK: http://localhost:8000/api/v1/chat")
        response = requests.post("http://localhost:8000/api/v1/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            # Update game layout pipeline engine with dialogue data strings
            active_dialogue_sender = "Ignis -> Luna"
            active_dialogue_text = f"'{data['dialogue']}' [{data['emotion'].upper()}]"
            
            # Keep text active on canvas for exactly 6 seconds
            dialogue_expiry_time = time.time() + 6.0
    except Exception as e:
        print(f"Agent synchronization network error: {e}")

# Main loop
while True:
    current_time = time.time()
    screen.fill(COLOR_BG)
    
    # 1. Render retro background tile grid mapping lines
    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.line(screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))
        
    # 2. Monitor execution input loops
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == NPC_TICK_EVENT:
            threading.Thread(target=trigger_npc_interaction, daemon=True).start()

    # 3. Dynamic input handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:  player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_pos[0] += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:    player_pos[1] -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:  player_pos[1] += player_speed

    # 4. Render Game Sprites / Blocks
    pygame.draw.rect(screen, COLOR_IGNIS, (ignis_pos[0], ignis_pos[1], 24, 24))  # Ignis
    pygame.draw.rect(screen, COLOR_LUNA, (luna_pos[0], luna_pos[1], 24, 24))     # Luna
    pygame.draw.rect(screen, COLOR_PLAYER, (player_pos[0], player_pos[1], 32, 32)) # Player

    # 5. Render Active Dialogue Bubbles over character clusters dynamically
    if current_time < dialogue_expiry_time and active_dialogue_text:
        # Wrap and crop text to keep it from clipping outside screen boundary layers
        display_str = f"[{active_dialogue_sender}]: {active_dialogue_text}"
        if len(display_str) > 75:
            display_str = display_str[:72] + "..."
            
        text_surface = game_font.render(display_str, True, (241, 245, 249))
        text_rect = text_surface.get_rect()
        
        # Center the dialogue bubble layout right above the character positions
        text_rect.center = (SCREEN_WIDTH // 2, ignis_pos[1] - 40)
        
        # Draw background structural tracking box panels for the dialogue font surfaces
        bg_padding_rect = text_rect.inflate(20, 16)
        pygame.draw.rect(screen, COLOR_TEXT_BG, bg_padding_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_TEXT_BORDER, bg_padding_rect, width=1, border_radius=4)
        
        # Paste the text graphics surface data direct onto your game frame buffer
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)
