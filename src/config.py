import pygame
import os

pygame.init()

WIDTH, HEIGHT = 1920, 1080
FPS = 60

# DYNAMIC DIRECTORY FILE PATHS
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

SOUND_PATH = os.path.join(project_root, "assets", "Sounds")
MENU_MUSIC_PATH = os.path.join(SOUND_PATH, "Menu_Sound1.mp3")
MENU_MUSIC_PATH_2 = os.path.join(SOUND_PATH, "Menu_Sound2.mp3")
SWORD_SWEEP_PATH = os.path.join(SOUND_PATH, "Sword_Sweep.mp3")
JUMP_SOUND_PATH = os.path.join(SOUND_PATH, "jump.mp3")
SWORD_HIT_PATH = os.path.join(SOUND_PATH, "Sword_Hit.mp3")
WALK_SOUND_PATH = os.path.join(SOUND_PATH, "Walking.mp3")
SAW_BLADE_SPINNING_PATH = os.path.join(SOUND_PATH, "Saw_Blade_Spinning.mp3")
SPECIAL_MOVES_PATH = os.path.join(project_root, "assets", "images", "Special Moves")
SAW_BLADE_IMAGE_NAME = "Saw_Blade"

# --- ADD THIS TO THE UI ELEMENTS SECTION OF config.py ---
# Placed nicely in the bottom right corner (Width: 1920, Height: 1080)
SPEAKER_BTN = pygame.Rect(WIDTH - 90, HEIGHT - 90, 60, 60)
GEAR_BTN    = pygame.Rect(WIDTH - 170, HEIGHT - 90, 60, 60)

# The popup selection frame that appears directly above the gear button
CHANGE_SOUND_BTN = pygame.Rect(WIDTH - 250, HEIGHT - 150, 140, 45)

BASE_PATH = os.path.join(project_root, "assets", "images")
BACKGROUND_PATH = os.path.join(BASE_PATH, "Background Images")
AVATAR_PATH = os.path.join(BASE_PATH, "Avatar Logos")
PLAYER_ANIM_PATH = os.path.join(BASE_PATH, "Left Sword Man")
RIGHT_PLAYER_ANIM_PATH = os.path.join(BASE_PATH, "Right Sword Man")

# GAMEPLAY HUD CONFIG (MASSIVE PAUSE BUTTON)
PAUSE_BUTTON_POS = (WIDTH // 2, 80) 
PAUSE_BUTTON_RADIUS = 60

# IN-GAME MODAL POP-UP MENU DIMENSIONS
MENU_SIZE = (300, 300)
MENU_RECT = pygame.Rect((WIDTH - MENU_SIZE[0]) // 2, (HEIGHT - MENU_SIZE[1]) // 2, *MENU_SIZE)

# BACKGROUND CHANGER MODAL GRAPHICS CONFIG
BG_MENU_SIZE = (1000, 750)
BG_MENU_RECT = pygame.Rect((WIDTH - BG_MENU_SIZE[0]) // 2, (HEIGHT - BG_MENU_SIZE[1]) // 2, *BG_MENU_SIZE)

BG_PREVIEW_SIZE = (450, 250)
BG_SLIDE_LEFT_BTN = pygame.Rect(BG_MENU_RECT.x + 60, BG_MENU_RECT.y + 350, 60, 60)
BG_SLIDE_RIGHT_BTN = pygame.Rect(BG_MENU_RECT.right - 120, BG_MENU_RECT.y + 350, 60, 60)
BG_SELECT_BTN = pygame.Rect(BG_MENU_RECT.centerx - 175, BG_MENU_RECT.y + 550, 350, 60)
BG_BACK_BTN = pygame.Rect(BG_MENU_RECT.centerx - 100, BG_MENU_RECT.y + 640, 200, 50)

# MULTIPLAYER WINDOW CONFIG (600x750 Center Layout)
MP_MENU_SIZE = (600, 750)
MP_MENU_RECT = pygame.Rect((WIDTH - MP_MENU_SIZE[0]) // 2, (HEIGHT - MP_MENU_SIZE[1]) // 2, *MP_MENU_SIZE)

# FIXED MULTIPLAYER INTERACTIVE RECTS
MP_HOST_BTN  = pygame.Rect(MP_MENU_RECT.x + 50, MP_MENU_RECT.y + 160, 220, 60)
MP_INPUT_BOX = pygame.Rect(MP_MENU_RECT.x + 330, MP_MENU_RECT.y + 160, 220, 60)
MP_JOIN_BTN  = pygame.Rect(MP_MENU_RECT.x + 175, MP_MENU_RECT.y + 550, 250, 55)
MP_BACK_BTN  = pygame.Rect(MP_MENU_RECT.x + 200, MP_MENU_RECT.y + 640, 200, 50)

# EXPANDED OPTIONS MODAL DIMENSIONS
OPTIONS_SIZE = (650, 550)
OPTIONS_RECT = pygame.Rect((WIDTH - OPTIONS_SIZE[0]) // 2, (HEIGHT - OPTIONS_SIZE[1]) // 2, *OPTIONS_SIZE)

# OPTIONS INTERACTIVE RECTS
OPT_FPS_BTN     = pygame.Rect(OPTIONS_RECT.x + 50, OPTIONS_RECT.y + 110, 550, 50)
OPT_AUDIO_BTN   = pygame.Rect(OPTIONS_RECT.x + 50, OPTIONS_RECT.y + 180, 550, 50)
OPT_DISPLAY_BTN = pygame.Rect(OPTIONS_RECT.x + 50, OPTIONS_RECT.y + 250, 550, 50)
OPT_VFX_BTN     = pygame.Rect(OPTIONS_RECT.x + 50, OPTIONS_RECT.y + 320, 550, 50)
OPT_BACK_BTN    = pygame.Rect(OPTIONS_RECT.centerx - 100, OPTIONS_RECT.y + 450, 200, 50)

# HOME SCREEN INTERFACE BUTTON METRICS
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 65
BUTTON_PADDING = 20
BUTTON_BORDER_RADIUS = 12

# GLOBAL TEXT STYLE FONTS
FONT = pygame.font.SysFont("Arial", 26, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 18, bold=True)
MENU_FONT = pygame.font.SysFont("Arial", 34, bold=True)

# CHARACTER SCALE BOUNDARIES
PLAYER_SIZE = (240, 240)
HITBOX_SIZE = (80, 150)
