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