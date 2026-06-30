import pygame
import os
from src.config import (
    WIDTH, HEIGHT, BACKGROUND_PATH, PLAYER_ANIM_PATH, RIGHT_PLAYER_ANIM_PATH,
    PLAYER_SIZE, HITBOX_SIZE, BG_PREVIEW_SIZE
)

# ASSET LOADING HELPERS
def _find_asset_file(folder_path, filenames):
    """Looks for any matching filename in a folder using case-insensitive matching."""
    if not os.path.isdir(folder_path):
        return None

    entries = {entry.lower(): entry for entry in os.listdir(folder_path)}
    for filename in filenames:
        candidate = entries.get(filename.lower())
        if candidate:
            return os.path.join(folder_path, candidate)
    return None

def load_frames(folder_path, prefix, count):
    """Loads a series of frame images for character animations with verification."""
    frames = []
    for i in range(1, count + 1):
        file_name = f"{prefix}{i}.png"
        full_file_path = _find_asset_file(folder_path, [file_name])

        if not full_file_path or not os.path.exists(full_file_path):
            raise FileNotFoundError(f"Missing animation file: {os.path.join(folder_path, file_name)}")
        # Load the image but avoid calling convert/convert_alpha at import-time
        # because a video mode may not yet be set. Defer conversion until a
        # display surface exists to prevent "No video mode has been set" errors.
        img = pygame.image.load(full_file_path)
        # Only convert if a display surface already exists
        try:
            if pygame.display.get_surface() is not None:
                try:
                    img = img.convert_alpha()
                except Exception:
                    img = img.convert()
        except Exception:
            # If display module isn't initialized or other issues, skip conversion
            pass

        frames.append(img)
    return frames

# SCENE BACKGROUND LOADING
wall_path = _find_asset_file(BACKGROUND_PATH, ["wall.JPG", "wall.jpg", "wall.png"])
try:
    game_background = pygame.transform.scale(
        pygame.image.load(wall_path), (WIDTH, HEIGHT)
    )
except Exception as e:
    print(f"Error loading game background: {e}")
    game_background = pygame.Surface((WIDTH, HEIGHT))
    game_background.fill((30, 40, 50))

homescreen_path = _find_asset_file(BACKGROUND_PATH, ["homescreen.jpg", "homescreen.jpeg", "homescreen.png"])
try:
    menu_background = pygame.transform.scale(
        pygame.image.load(homescreen_path), (WIDTH, HEIGHT)
    )
except Exception as e:
    print(f"Error loading menu background: {e}")
    menu_background = pygame.Surface((WIDTH, HEIGHT))
    menu_background.fill((20, 20, 30))

def load_background_images():
    """Loads all stage background images from the background directory."""
    backgrounds = []
    if os.path.isdir(BACKGROUND_PATH):
        for file_name in sorted(os.listdir(BACKGROUND_PATH)):
            file_path = os.path.join(BACKGROUND_PATH, file_name)
            if file_name.lower() == "homescreen.jpg":
                continue
            if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".jfif")):
                try:
                    img = pygame.image.load(file_path)
                    # Avoid convert_alpha at import time if no display surface exists
                    try:
                        if pygame.display.get_surface() is not None:
                            try:
                                img = img.convert_alpha()
                            except Exception:
                                img = img.convert()
                    except Exception:
                        pass

                    surface = pygame.transform.scale(img, (WIDTH, HEIGHT))
                    backgrounds.append((file_name, surface))
                except Exception as e:
                    print(f"[BACKGROUND LOAD ERROR] {file_path}: {e}")
    return backgrounds

available_backgrounds = load_background_images()
current_bg_index = 0
if available_backgrounds:
    wall_index = next(
        (i for i, (name, _) in enumerate(available_backgrounds)
         if os.path.splitext(name)[0].lower() == "wall"),
        None
    )
    if wall_index is not None:
        current_bg_index = wall_index
    game_background = available_backgrounds[current_bg_index][1]
else:
    available_backgrounds = [("default", game_background)]


def set_background(index):
    """Set the current gameplay background by index."""
    global current_bg_index, game_background
    if not available_backgrounds:
        return
    current_bg_index = max(0, min(index, len(available_backgrounds) - 1))
    game_background = available_backgrounds[current_bg_index][1]

# --- SPRITE SHEETS / ANIMATION ARRAYS FOR LEFT SWORD MAN ---
try:
    left_idle_frames = [pygame.transform.scale(f, PLAYER_SIZE) for f in load_frames(PLAYER_ANIM_PATH, "idle", 2)]
    left_walk_frames = [pygame.transform.scale(f, PLAYER_SIZE) for f in load_frames(PLAYER_ANIM_PATH, "walk", 4)]
    left_attack_frames = [pygame.transform.scale(f, PLAYER_SIZE) for f in load_frames(PLAYER_ANIM_PATH, "attack", 4)]
    left_defend_frames = [pygame.transform.scale(f, PLAYER_SIZE) for f in load_frames(PLAYER_ANIM_PATH, "defend", 2)]
    left_jump_frames = [pygame.transform.scale(f, PLAYER_SIZE) for f in load_frames(PLAYER_ANIM_PATH, "jump", 3)]
except Exception as e:
    print(f"\n[ASSET ERROR] Left character animations failed to load from: {PLAYER_ANIM_PATH}")
    print(f"Reason: {e}\n")
    fallback_surf = pygame.Surface(PLAYER_SIZE, pygame.SRCALPHA)
    pygame.draw.rect(fallback_surf, (0, 200, 0), (0, 0, *PLAYER_SIZE), 5)
    left_idle_frames = left_walk_frames = left_attack_frames = left_defend_frames = left_jump_frames = [fallback_surf]

# SPRITE SHEETS / ANIMATION ARRAYS FOR RIGHT SWORD MAN
try:
    right_idle_frames = [pygame.transform.scale(f, PLAYER_SIZE) for f in load_frames(RIGHT_PLAYER_ANIM_PATH, "idle", 2)]
    right_walk_frames = [pygame.transform.scale(f, PLAYER_SIZE) for f in load_frames(RIGHT_PLAYER_ANIM_PATH, "walk", 4)]
    right_attack_frames = [pygame.transform.scale(f, PLAYER_SIZE) for f in load_frames(RIGHT_PLAYER_ANIM_PATH, "attack", 4)]
    right_defend_frames = [pygame.transform.scale(f, PLAYER_SIZE) for f in load_frames(RIGHT_PLAYER_ANIM_PATH, "defend", 2)]
    right_jump_frames = [pygame.transform.scale(f, PLAYER_SIZE) for f in load_frames(RIGHT_PLAYER_ANIM_PATH, "jump", 3)]
    print("[SUCCESS] Right Sword Man frames loaded successfully!")
except Exception as e:
    print(f"\n[ASSET ERROR] Right character animations failed to load from: {RIGHT_PLAYER_ANIM_PATH}")
    print(f"Reason: {e}")
    print("-> Confirm your folder name matches exactly, and contains files named 'idle1.png', 'walk1.png' etc.\n")
    fallback_surf_blue = pygame.Surface(PLAYER_SIZE, pygame.SRCALPHA)
    pygame.draw.rect(fallback_surf_blue, (0, 0, 255), (0, 0, *PLAYER_SIZE), 5)
    right_idle_frames = right_walk_frames = right_attack_frames = right_defend_frames = right_jump_frames = [fallback_surf_blue]
    fallback_surf_blue = pygame.Surface(PLAYER_SIZE, pygame.SRCALPHA)
    pygame.draw.rect(fallback_surf_blue, (0, 0, 255), (0, 0, *PLAYER_SIZE), 5)
    right_idle_frames = right_walk_frames = right_attack_frames = right_defend_frames = right_jump_frames = [fallback_surf_blue]

# PLAYER CLASS DEFINITION
class Player:
    def __init__(self, x, y, side="left"):
        self.x, self.y = x, y
        self.start_y = y
        self.speed = 6
        self.vel_y = 0
        self.is_jumping = False
        self.gravity = 0.5
        self.frame = 0
        self.anim_speed = 0.15
        self.state = "idle"
        self.health = 100
        self.shield = 100
        self.side = side

        # Attack charge tracking variables
        self.attack_hold_time = 0

        if self.side == "left":
            self.controls = {
                "left": pygame.K_a,
                "right": pygame.K_d,
                "up": pygame.K_w,
                "down": pygame.K_s,
                "attack": pygame.K_f
            }
        else:
            self.controls = {
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "attack": pygame.K_p
            }

    def get_hitbox(self):
        """Returns the normal movement and damage hurtbox rectangle of the player."""
        hitbox_x = self.x + (PLAYER_SIZE[0] - HITBOX_SIZE[0]) // 2
        hitbox_y = self.y + (PLAYER_SIZE[1] - HITBOX_SIZE[1])
        return pygame.Rect(hitbox_x, hitbox_y, HITBOX_SIZE[0], HITBOX_SIZE[1])

    def get_attack_rect(self, opponent_x):
        """Generates an extended horizontal attack reach hitbox facing towards the opponent."""
        hitbox = self.get_hitbox()
        reach_extension = 100

        if self.x < opponent_x:
            return pygame.Rect(hitbox.x, hitbox.y, hitbox.width + reach_extension, hitbox.height)
        else:
            return pygame.Rect(hitbox.x - reach_extension, hitbox.y, hitbox.width + reach_extension, hitbox.height)

    def update(self, keys, opponent):
        """Handles movement inputs, gravity, animations, continuous loop attack tracking, and collisions."""
        self.state = "idle"

        if keys[self.controls["left"]]:
            self.x -= self.speed
            self.state = "walk"
        if keys[self.controls["right"]]:
            self.x += self.speed
            self.state = "walk"

        if keys[self.controls["attack"]]:
            self.state = "attack"
            self.attack_hold_time += 1 / 60

            if self.attack_hold_time >= 0.45:
                my_attack_rect = self.get_attack_rect(opponent.x)
                opp_hitbox = opponent.get_hitbox()

                if my_attack_rect.colliderect(opp_hitbox):
                    if opponent.state == "defend" and opponent.shield > 0:
                        opponent.shield -= 5
                        if opponent.shield < 0:
                            opponent.shield = 0
                    else:
                        opponent.health -= 5
                        if opponent.health < 0:
                            opponent.health = 0

                self.attack_hold_time = 0
        else:
            self.attack_hold_time = 0
            if keys[self.controls["down"]]:
                self.state = "defend"

        if keys[self.controls["up"]] and not self.is_jumping:
            self.vel_y = -16
            self.is_jumping = True

        if self.is_jumping:
            self.state = "jump"

        self.vel_y += self.gravity
        self.y += self.vel_y

        if self.y >= self.start_y:
            self.y = self.start_y
            self.vel_y = 0
            self.is_jumping = False

        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - PLAYER_SIZE[0]:
            self.x = WIDTH - PLAYER_SIZE[0]

        self.frame += self.anim_speed

        my_hitbox = self.get_hitbox()
        opp_hitbox = opponent.get_hitbox()

        if my_hitbox.colliderect(opp_hitbox):
            overlap_x = min(my_hitbox.right, opp_hitbox.right) - max(my_hitbox.left, opp_hitbox.left)

            if self.x < opponent.x:
                self.x -= overlap_x // 2
                opponent.x += overlap_x // 2
            else:
                self.x += overlap_x // 2
                opponent.x -= overlap_x // 2

    def get_current_animation_set(self):
        if self.side == "left":
            frames_dict = {
                "idle": left_idle_frames,
                "walk": left_walk_frames,
                "attack": left_attack_frames,
                "defend": left_defend_frames,
                "jump": left_jump_frames
            }
        else:
            frames_dict = {
                "idle": right_idle_frames,
                "walk": right_walk_frames,
                "attack": right_attack_frames,
                "defend": right_defend_frames,
                "jump": right_jump_frames
            }
        return frames_dict.get(self.state, left_idle_frames)

    def draw(self, surface, opponent_x=None):
        current_frame_list = self.get_current_animation_set()
        if current_frame_list:
            frame_idx = int(self.frame) % len(current_frame_list)
            sprite_to_draw = current_frame_list[frame_idx]

            if opponent_x is not None:
                if self.x > opponent_x:
                    sprite_to_draw = pygame.transform.flip(sprite_to_draw, True, False)
            elif self.side == "right":
                sprite_to_draw = pygame.transform.flip(sprite_to_draw, True, False)

            surface.blit(sprite_to_draw, (self.x, self.y))


class Bot(Player):
    """AI bot player for single player mode with difficulty progression."""
    def __init__(self, x, y, side="left", difficulty_round=1):
        super().__init__(x, y, side)
        self.difficulty_round = difficulty_round
        self.ai_action_timer = 0
        self.ai_decision_timer = 0
        self.ai_current_action = "idle"
        self.set_difficulty(difficulty_round)
    
    def set_difficulty(self, round_num):
        """Set bot difficulty based on round number (1-3)."""
        self.difficulty_round = round_num
        if round_num == 1:
            self.attack_speed = 0.45  # Default attack speed
            self.speed = 5  # Slightly slower than player (6)
            self.ai_aggressiveness = 0.4  # 40% chance to attack
        elif round_num == 2:
            self.attack_speed = 0.35  # Faster attack
            self.speed = 5.5  # Medium speed
            self.ai_aggressiveness = 0.6  # 60% chance to attack
        else:  # round_num == 3
            self.attack_speed = 0.3  # Even faster attack
            self.speed = 6  # Same as player
            self.ai_aggressiveness = 0.75  # 75% chance to attack
    
    def update(self, keys, opponent):
        """AI controlled update instead of keyboard input."""
        import random
        
        self.state = "idle"
        self.ai_decision_timer += 1
        
        # Make AI decisions every 30 frames (0.5 seconds)
        if self.ai_decision_timer > 30:
            self.ai_decision_timer = 0
            # Random action selection
            rand = random.random()
            if rand < self.ai_aggressiveness:
                self.ai_current_action = "attack"
            elif rand < 0.5 + self.ai_aggressiveness / 2:
                self.ai_current_action = "move"
            else:
                self.ai_current_action = "idle"
        
        # Execute AI action
        if self.ai_current_action == "move":
            # Move towards opponent
            if self.x < opponent.x - 150:
                self.x += self.speed
                self.state = "walk"
            elif self.x > opponent.x + 150:
                self.x -= self.speed
                self.state = "walk"
        
        elif self.ai_current_action == "attack":
            self.state = "attack"
            self.attack_hold_time += 1 / 60
            
            if self.attack_hold_time >= self.attack_speed:
                my_attack_rect = self.get_attack_rect(opponent.x)
                opp_hitbox = opponent.get_hitbox()
                
                if my_attack_rect.colliderect(opp_hitbox):
                    if opponent.state == "defend" and opponent.shield > 0:
                        opponent.shield -= 5
                        if opponent.shield < 0:
                            opponent.shield = 0
                    else:
                        opponent.health -= 5
                        if opponent.health < 0:
                            opponent.health = 0
                
                self.attack_hold_time = 0
                self.ai_current_action = "idle"
        else:
            self.attack_hold_time = 0
            # Occasionally defend
            if random.random() < 0.1:
                self.state = "defend"
        
        # Gravity and jumping
        self.vel_y += self.gravity
        self.y += self.vel_y
        
        if self.y >= self.start_y:
            self.y = self.start_y
            self.is_jumping = False
        
        # Boundary check
        if self.x < 50:
            self.x = 50
        if self.x > WIDTH - PLAYER_SIZE[0] - 50:
            self.x = WIDTH - PLAYER_SIZE[0] - 50
        
        # Animation frame update
        frames_list = self.get_current_animation_set()
        if frames_list:
            self.frame += self.anim_speed
            if self.frame >= len(frames_list):
                self.frame = 0
