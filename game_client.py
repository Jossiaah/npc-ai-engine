import pygame
import sys
import requests
import threading

pygame.init()

# Setup vintage screen resolution and color constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GenAI Open-World Agent Sandbox")

COLOR_BG = (15, 23, 42)       # Slate 900
COLOR_GRID = (30, 41, 59)     # Slate 800
COLOR_PLAYER = (59, 130, 246) # Blue
COLOR_IGNIS = (239, 68, 68)   # Red
COLOR_LUNA = (168, 85, 247)   # Purple

# Set starting positions for game entities [X, Y]
player_pos = [400, 300]
ignis_pos = [200, 150]
luna_pos = [250, 150] # Placed intentionally close together to trigger conversation

player_speed = 5
clock = pygame.time.Clock()

# Timers to control NPC autonomous action frequency
NPC_TICK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NPC_TICK_EVENT, 10000) # Ticks every 10 seconds

def trigger_npc_interaction():
    """Async background task so the game engine doesn't freeze during API calls."""
    try:
        # Step 1: Simulate Ignis addressing Luna because they are standing next to each other
        payload = {
            "npc_id": "ignis",
            "message": "Archmage Luna! What are you doing outside your tower? Is that magical residue I smell?"
        }
        response = requests.post("http://127.0.0", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n[Autonomous Chat Log] Ignis says to Luna: {payload['message']}")
            print(f"[Autonomous Chat Log] Luna responds: {data['dialogue']} (Emotion: {data['emotion']})")
    except Exception as e:
        print(f"Agent synchronization pipeline error: {e}")