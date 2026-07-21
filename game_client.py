import pygame
import sys
import requests
import threading
import time
import math

# 1. Initialize Subsystems
pygame.init()
pygame.font.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GenAI Pokemon-Style Sandbox Client")

# Color Palette Config (Classic Retro Hardware Archetypes)
COLOR_GRASS_DARK = (20, 40, 25)
COLOR_GRASS_LIGHT = (35, 65, 40)
COLOR_TEXT_BG = (10, 15, 20)
COLOR_TEXT_BORDER = (52, 211, 153)

game_font = pygame.font.SysFont("Courier", 13, bold=True)
clock = pygame.time.Clock()

# Entity Data Maps [X, Y]
player_pos = [400, 300]
ignis_pos  = [200, 200]
luna_pos   = [240, 200]  # Close to Ignis to trigger autonomous conversations

player_speed = 4

# Core Engine State Telemetry Variables
active_dialogue_text = ""
active_dialogue_sender = ""
dialogue_expiry_time = 0.0

is_chat_mode_active = False
player_chat_buffer = ""

# Proximity Rule Config (3 Grid Tiles = 120 pixels)
PROXIMITY_LIMIT = 120.0 

# Autonomous Timer (15 seconds frequency block)
NPC_TICK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NPC_TICK_EVENT, 15000)

# --- 2. Programmatic Retro Surface Asset Generator Functions ---
def create_pixel_sprite(primary_color, accent_color, is_wizard=False):
    """Draws an 8-bit character grid layout onto a dynamic texture canvas surface."""
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Head & Body Layout Base Matrix blocks
    pygame.draw.rect(surface, primary_color, (8, 8, 16, 16)) 
    pygame.draw.rect(surface, accent_color, (4, 20, 24, 12))
    # Face details (Classic 2-pixel retro eyes)
    pygame.draw.rect(surface, (255, 255, 255), (10, 12, 4, 4))
    pygame.draw.rect(surface, (255, 255, 255), (18, 12, 4, 4))
    pygame.draw.rect(surface, (0, 0, 0), (11, 13, 2, 2))
    pygame.draw.rect(surface, (0, 0, 0), (19, 13, 2, 2))
    
    if is_wizard: # Generate a custom pointed wizard hat structure top layer
        pygame.draw.polygon(surface, (120, 60, 200), [(16, 0), (6, 8), (26, 8)])
    else: # Generate a metal blacksmith apron panel layer
        pygame.draw.rect(surface, (180, 100, 50), (12, 22, 8, 10))
    return surface

def create_background_tile():
    """Generates an 8-bit GameBoy style structural grassy field tile map asset texture."""
    tile = pygame.Surface((40, 40))
    tile.fill(COLOR_GRASS_DARK)
    # Inject scattered nostalgic grass tuft coordinate lines
    pygame.draw.line(tile, COLOR_GRASS_LIGHT, (5, 10), (5, 15), 2)
    pygame.draw.line(tile, COLOR_GRASS_LIGHT, (12, 25), (12, 30), 2)
    pygame.draw.line(tile, COLOR_GRASS_LIGHT, (28, 8), (28, 12), 2)
    pygame.draw.line(tile, COLOR_GRASS_LIGHT, (32, 22), (32, 28), 2)
    return tile

# Instantiate visual assets into system memory arrays
player_sprite = create_pixel_sprite((230, 180, 140), (30, 100, 200))
ignis_sprite  = create_pixel_sprite((200, 150, 120), (80, 80, 80), is_wizard=False)
luna_sprite   = create_pixel_sprite((220, 170, 150), (100, 50, 180), is_wizard=True)
background_tile = create_background_tile()

# --- 3. Asynchronous Pipeline Processing Network Blocks ---
def post_network_interaction(npc_id, prompt_message, sender_label):
    """Processes network request routing logic without freezing framerate tracking."""
    global active_dialogue_text, active_dialogue_sender, dialogue_expiry_time
    try:
        payload = {"npc_id": npc_id, "message": prompt_message}
        response = requests.post("http://localhost:8000/api/v1/chat", json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            active_dialogue_sender = sender_label
            active_dialogue_text = f"'{data['dialogue']}' [{data['emotion'].upper()}]"
            dialogue_expiry_time = time.time() + 10.0
    except Exception as e:
        print(f"Network request timeout or crash: {e}")

# --- 4. Main Runtime Loop ---
while True:
    current_time = time.time()
    
    # Render Step A: Draw the full tilemap grid space background layout
    for x in range(0, SCREEN_WIDTH, 40):
        for y in range(0, SCREEN_HEIGHT, 40):
            screen.blit(background_tile, (x, y))

    # Input Step B: Handle incoming OS window execution events and keystrokes
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == NPC_TICK_EVENT and not is_chat_mode_active:
            # PROXIMITY MECHANIC: Compute absolute distance space between Ignis & Luna
            distance = math.hypot(ignis_pos[0] - luna_pos[0], ignis_pos[1] - luna_pos[1])
            if distance <= PROXIMITY_LIMIT:
                msg = "Archmage Luna! Did your tower experiments cause that rumble near the mountains?"
                threading.Thread(target=post_network_interaction, args=("ignis", msg, "Ignis -> Luna"), daemon=True).start()
                
        elif event.type == pygame.KEYDOWN:
            if is_chat_mode_active:
                if event.key == pygame.K_RETURN: # Process typed input and execute network call
                    if player_chat_buffer.strip():
                        threading.Thread(target=post_network_interaction, args=("luna", player_chat_buffer, "Player -> Luna"), daemon=True).start()
                    player_chat_buffer = ""
                    is_chat_mode_active = False
                elif event.key == pygame.K_ESCAPE: # Drop out of typing mode directly
                    is_chat_mode_active = False
                elif event.key == pygame.K_BACKSPACE:
                    player_chat_buffer = player_chat_buffer[:-1]
                else: # Append characters live to network transmission buffer
                    if len(player_chat_buffer) < 55:
                        player_chat_buffer += event.unicode
            else:
                if event.key == pygame.K_e: # Check proximity to open direct terminal console layout
                    dist_to_luna = math.hypot(player_pos[0] - luna_pos[0], player_pos[1] - luna_pos[1])
                    if dist_to_luna <= PROXIMITY_LIMIT:
                        is_chat_mode_active = True
                        player_chat_buffer = ""

    # Movement Step C: Check keyboard state if not frozen inside chat sequence
    if not is_chat_mode_active:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_pos[0] += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:    player_pos[1] -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  player_pos[1] += player_speed

    # Render Step D: Paste sprite graphics onto window rendering layers
    screen.blit(ignis_sprite, ignis_pos)
    screen.blit(luna_sprite, luna_pos)
    screen.blit(player_sprite, player_pos)

    # Render Step E: Render Active AI Dialogue Speech Box Overlays
    if current_time < dialogue_expiry_time and active_dialogue_text:
        display_str = f"[{active_dialogue_sender}]: {active_dialogue_text}"
        surf = game_font.render(display_str[:65] + "..." if len(display_str) > 68 else display_str, True, (240, 240, 240))
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        bg_pad = rect.inflate(24, 16)
        pygame.draw.rect(screen, COLOR_TEXT_BG, bg_pad, border_radius=4)
        pygame.draw.rect(screen, COLOR_TEXT_BORDER, bg_pad, width=1, border_radius=4)
        screen.blit(surf, rect)

    # Render Step F: Draw Prompt Input Command Box if Player is actively typing
    if is_chat_mode_active:
        panel_rect = pygame.Rect(50, 500, 700, 60)
        pygame.draw.rect(screen, COLOR_TEXT_BG, panel_rect, border_radius=4)
        pygame.draw.rect(screen, (59, 130, 246), panel_rect, width=2, border_radius=4)
        
        prompt_surf = game_font.render(f"TALKING TO LUNA (Press Enter to send): {player_chat_buffer}_", True, (255, 255, 255))
        screen.blit(prompt_surf, (70, 522))

    pygame.display.flip()
    clock.tick(60)
