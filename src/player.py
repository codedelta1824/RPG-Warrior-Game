import pygame
import os
import random
from src.config import (
    WIDTH, HEIGHT, BACKGROUND_PATH, PLAYER_ANIM_PATH, RIGHT_PLAYER_ANIM_PATH,
    PLAYER_SIZE, HITBOX_SIZE, BG_PREVIEW_SIZE,
    SWORD_SWEEP_PATH, JUMP_SOUND_PATH, SWORD_HIT_PATH, WALK_SOUND_PATH,
    SAW_BLADE_SPINNING_PATH, SPECIAL_MOVES_PATH, SAW_BLADE_IMAGE_NAME
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
        self.max_health = 100
        self.shield = 100
        self.side = side

        # Attack charge tracking variables
        self.attack_hold_time = 0
        self.attack_power = 7
        self.attack_speed = 0.3  # Changed to 0.3s for click-based system
        self.jump_force = -20
        self.special_meter = 0
        self.special_ready = False
        self.consecutive_hits = 0
        self.special_cooldown = 0
        self.special_requested = False
        self.is_boss = False
        self.last_play_state = "idle"
        self.walk_channel_id = 1 if side == "left" else 2
        self.walk_channel = None
        self.saw_channel = pygame.mixer.Channel(3)
        
        # NEW: Click-based attack and defend system
        self.attack_pressed = False
        self.defend_pressed = False
        self.is_attacking = False
        self.is_defending = False
        self.attack_frame_timer = 0
        self.defend_locked = False

        if self.side == "left":
            self.controls = {
                "left": pygame.K_a,
                "right": pygame.K_d,
                "up": pygame.K_w,
                "down": pygame.K_s,
                "attack": pygame.K_f,
                "special": pygame.K_r
            }
        else:
            self.controls = {
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "attack": pygame.K_p,
                "special": pygame.K_o
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

    @classmethod
    def _ensure_audio_resources(cls):
        if getattr(cls, "audio_loaded", False):
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(12)
        except Exception:
            pass

        def _safe_load(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception:
                return None

        cls.walking_sound = _safe_load(WALK_SOUND_PATH)
        cls.jump_sound = _safe_load(JUMP_SOUND_PATH)
        cls.sword_sweep_sound = _safe_load(SWORD_SWEEP_PATH)
        cls.sword_hit_sound = _safe_load(SWORD_HIT_PATH)
        cls.saw_blade_sound = _safe_load(SAW_BLADE_SPINNING_PATH)
        cls.audio_loaded = True

    def _play_walk_audio(self, moving):
        if not pygame.mixer.get_init() or not getattr(self.__class__, "audio_loaded", False):
            return

        if self.walk_channel is None:
            self.walk_channel = pygame.mixer.Channel(self.walk_channel_id)

        if moving and self.walking_sound is not None:
            if not self.walk_channel.get_busy():
                self.walk_channel.play(self.walking_sound, loops=-1)
        else:
            if self.walk_channel is not None and self.walk_channel.get_busy():
                self.walk_channel.stop()

    def _play_jump_audio(self):
        if not pygame.mixer.get_init() or not getattr(self.__class__, "audio_loaded", False):
            return
        if self.jump_sound is not None:
            self.jump_sound.play()

    def _play_attack_audio(self):
        if not pygame.mixer.get_init() or not getattr(self.__class__, "audio_loaded", False):
            return
        if self.sword_sweep_sound is not None:
            self.sword_sweep_sound.play()

    def _play_saw_blade_audio(self):
        if not pygame.mixer.get_init() or not getattr(self.__class__, "audio_loaded", False):
            return
        if self.saw_blade_sound is not None:
            try:
                if not self.saw_channel.get_busy():
                    self.saw_channel.set_volume(0.65)
                    self.saw_channel.play(self.saw_blade_sound, loops=0)
            except Exception:
                pass

    def _stop_saw_blade_audio(self):
        try:
            if self.saw_channel and self.saw_channel.get_busy():
                self.saw_channel.stop()
        except Exception:
            pass

    def _play_hit_audio(self):
        if not pygame.mixer.get_init() or not getattr(self.__class__, "audio_loaded", False):
            return
        if self.sword_hit_sound is not None:
            self.sword_hit_sound.play()

    def _register_hit(self, defender_is_defending=False):
        self.consecutive_hits += 1
        self.special_meter = min(10, self.special_meter + 1)
        if self.special_meter >= 10:
            self.special_ready = True
        if defender_is_defending:
            self._play_hit_audio()

    def _reset_on_received_hit(self):
        self.consecutive_hits = 0
        # Special meter is retained through hits and only resets on special activation

    def _apply_attack_damage(self, opponent, damage, defender_blocked=False):
        if defender_blocked:
            opponent.shield -= damage
            if opponent.shield < 0:
                opponent.shield = 0
        else:
            opponent.health -= damage
            if opponent.health < 0:
                opponent.health = 0

        self._register_hit(defender_is_defending=defender_blocked)
        opponent._reset_on_received_hit()

    def _resolve_attack(self, opponent, damage):
        my_attack_rect = self.get_attack_rect(opponent.x)
        opp_hitbox = opponent.get_hitbox()

        if my_attack_rect.colliderect(opp_hitbox):
            defender_blocked = opponent.state == "defend" and opponent.shield > 0
            self._apply_attack_damage(opponent, damage, defender_blocked)
            if defender_blocked:
                self._play_hit_audio()
            return True
        return False

    def update(self, keys, opponent):
        """Handles movement inputs, gravity, animations, audio, special moves, and collisions."""
        self.__class__._ensure_audio_resources()

        self.state = "idle"
        moving_on_x = False
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

        # Movement
        if keys[self.controls["left"]]:
            self.x -= self.speed
            self.state = "walk"
            moving_on_x = True
        if keys[self.controls["right"]]:
            self.x += self.speed
            self.state = "walk"
            moving_on_x = True

        # Special move input
        if self.controls.get("special") and keys[self.controls["special"]] and self.special_ready and self.special_cooldown == 0:
            self.special_requested = True

        # NEW: Click-based attack system (not hold-based)
        # Detect attack key press (transition from not pressed to pressed)
        attack_key_pressed = keys[self.controls["attack"]]
        if attack_key_pressed and not self.attack_pressed and not self.is_jumping and not self.special_requested:
            # Attack button just pressed
            self.is_attacking = True
            self.attack_frame_timer = 0
            self._play_attack_audio()
        self.attack_pressed = attack_key_pressed
        
        # Continue attack animation if active
        if self.is_attacking and not self.is_jumping:
            self.state = "attack"
            self.attack_frame_timer += 1 / 60
            # Deal damage after 0.15s into the attack
            if self.attack_frame_timer >= 0.15 and self.attack_frame_timer < 0.16:
                damage = self.attack_power
                self._resolve_attack(opponent, damage)
            # End attack after animation completes (0.3s)
            if self.attack_frame_timer >= self.attack_speed:
                self.is_attacking = False
        
        # NEW: Click-based defend toggle system
        defend_key_pressed = keys[self.controls["down"]]
        if defend_key_pressed and not self.defend_pressed and not self.special_requested and not self.is_attacking:
            # Defend button just pressed - toggle defend state
            self.is_defending = not self.is_defending
            self.defend_locked = not self.defend_locked
        self.defend_pressed = defend_key_pressed
        
        # Apply defend state if locked in
        if self.is_defending and not self.is_attacking and not self.is_jumping:
            self.state = "defend"

        # Jumping (cannot jump while attacking)
        if keys[self.controls["up"]] and not self.is_jumping and not self.is_attacking:
            self.vel_y = self.jump_force
            self.is_jumping = True
            self._play_jump_audio()

        if self.is_jumping:
            self.state = "jump"
            self.is_attacking = False  # Cancel attack if jumping

        # Apply gravity
        self.vel_y += self.gravity
        self.y += self.vel_y
        if self.y >= self.start_y:
            self.y = self.start_y
            self.vel_y = 0
            self.is_jumping = False

        # Boundaries
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - PLAYER_SIZE[0]:
            self.x = WIDTH - PLAYER_SIZE[0]

        # Prevent stale walking audio
        self._play_walk_audio(moving_on_x and not self.is_jumping and self.y >= self.start_y)

        # FIX: For idle and defend, freeze on first frame. For other states, animate normally
        if self.state in ["idle", "defend"]:
            self.frame = 0  # Stay on first frame only
        else:
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

        special_blade = None
        if self.special_requested:
            special_blade = self.try_activate_special(opponent)

        return special_blade

    def try_activate_special(self, opponent):
        if not self.special_requested:
            return None
        self.special_requested = False
        if not self.special_ready or self.special_cooldown > 0:
            return None
        self.special_ready = False
        self.special_meter = 0
        self.special_cooldown = 300
        self.state = "special"
        self._play_attack_audio()
        return SpecialSawBlade(self, opponent)

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


class SpecialSawBlade:
    """Represents the cinematic saw blade traveling across the arena."""
    def __init__(self, caster, target):
        self.caster = caster
        self.target = target
        self.duration_frames = 240
        self.elapsed_frames = 0
        self.damage = 40
        self.active = True
        self.hit_registered = False

        self.image = self._load_saw_image()
        self.height = int(PLAYER_SIZE[1] * 1.35)
        if self.image is not None:
            scale_factor = self.height / self.image.get_height()
            scaled_width = max(1, int(self.image.get_width() * scale_factor * 1.3))
            self.image = pygame.transform.smoothscale(
                self.image,
                (scaled_width, self.height)
            )
        else:
            self.image = pygame.Surface((240, self.height), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 235, 80), (120, self.height // 2), min(80, self.height // 2))
            pygame.draw.circle(self.image, (220, 200, 40), (120, self.height // 2), min(55, self.height // 2))

        if caster.side == "left":
            self.direction = -1
            self.x = WIDTH - self.image.get_width()
            self.target_x = 0
        else:
            self.direction = 1
            self.x = 0
            self.target_x = WIDTH - self.image.get_width()

        self.y = self.target.y
        self.velocity = (self.target_x - self.x) / self.duration_frames
        self.caster._play_saw_blade_audio()

    def _load_saw_image(self):
        path = _find_asset_file(SPECIAL_MOVES_PATH, [f"{SAW_BLADE_IMAGE_NAME}.png", f"{SAW_BLADE_IMAGE_NAME}.jpg", f"{SAW_BLADE_IMAGE_NAME}.jpeg", f"{SAW_BLADE_IMAGE_NAME}.bmp"])
        if path and os.path.exists(path):
            try:
                img = pygame.image.load(path)
                if pygame.display.get_surface() is not None:
                    try:
                        img = img.convert_alpha()
                    except Exception:
                        img = img.convert()
                return img
            except Exception:
                pass
        return None

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.image.get_width(), self.image.get_height())

    def update(self):
        if not self.active:
            return
        self.elapsed_frames += 1
        self.x += self.velocity

        if self.x <= 0 or self.x >= WIDTH - self.image.get_width():
            self.active = False
            self.caster._stop_saw_blade_audio()
            return

        if self.elapsed_frames >= self.duration_frames:
            self.active = False
            self.caster._stop_saw_blade_audio()
            return
        self._check_collision()

    def _check_collision(self):
        if self.hit_registered or not self.active:
            return
        if self.rect().colliderect(self.target.get_hitbox()):
            if self.target.is_jumping and self.target.y < self.target.start_y - (PLAYER_SIZE[1] * 0.55):
                return
            self.target.health -= self.damage
            if self.target.health < 0:
                self.target.health = 0
            self.hit_registered = True

    def draw(self, surface):
        if not self.active:
            return
        surface.blit(self.image, (int(self.x), int(self.y)))

class Bot(Player):
    """AI bot player for single player mode with difficulty progression."""
    def __init__(self, x, y, side="left", difficulty_round=1):
        super().__init__(x, y, side)
        self.difficulty_round = difficulty_round
        self.ai_action_timer = 0
        self.ai_decision_timer = 0
        self.ai_current_action = "idle"
        self.ai_defend_cooldown = 0
        self.set_difficulty(difficulty_round)
    
    def set_difficulty(self, round_num):
        """Set bot difficulty based on round number."""
        self.difficulty_round = round_num
        self.is_boss = False
        self.max_health = 100
        if round_num == 1:
            self.attack_speed = 0.3
            self.speed = 5
            self.attack_power = 6
            self.ai_aggressiveness = 0.45
        elif round_num == 2:
            self.attack_speed = 0.3
            self.speed = 5.75
            self.attack_power = 8
            self.ai_aggressiveness = 0.6
        elif round_num == 3:
            self.attack_speed = 0.3
            self.speed = 6.5
            self.attack_power = 10
            self.ai_aggressiveness = 0.72
        else:
            self.attack_speed = 0.3
            self.speed = 6.75
            self.attack_power = 10
            self.ai_aggressiveness = 0.85
            self.max_health = 200
            self.health = 200
            self.is_boss = True
        self.health = min(self.health, self.max_health)
    
    def update(self, keys, opponent):
        self.__class__._ensure_audio_resources()
        self.state = "idle"
        self.ai_decision_timer += 1
        if self.ai_defend_cooldown > 0:
            self.ai_defend_cooldown -= 1

        distance = abs(self.x - opponent.x)
        far_gap = distance > 220
        close_gap = distance < 130

        if self.ai_decision_timer > 30:
            self.ai_decision_timer = 0
            if far_gap:
                self.ai_current_action = "move"
            else:
                rand = random.random()
                if rand < self.ai_aggressiveness:
                    self.ai_current_action = "attack"
                elif rand < self.ai_aggressiveness + 0.22:
                    self.ai_current_action = "move"
                elif rand < self.ai_aggressiveness + 0.32 and self.ai_defend_cooldown == 0:
                    self.ai_current_action = "defend"
                else:
                    self.ai_current_action = "idle"

        if self.ai_current_action == "move":
            if self.x < opponent.x - 150:
                self.x += self.speed
                self.state = "walk"
            elif self.x > opponent.x + 150:
                self.x -= self.speed
                self.state = "walk"

            if far_gap and not self.is_jumping and random.random() < 0.3:
                self.vel_y = self.jump_force
                self.is_jumping = True
                self.state = "jump"
                self._play_jump_audio()

        elif self.ai_current_action == "attack":
            if self.is_jumping:
                self.state = "jump"
                self.is_attacking = False
                self.ai_current_action = "idle"
            else:
                # Use the same click-based attack system
                self.state = "attack"
                self.attack_frame_timer += 1 / 60
                if self.attack_frame_timer >= 0.15 and self.attack_frame_timer < 0.16:
                    damage = self.attack_power
                    self._resolve_attack(opponent, damage)
                    self._play_attack_audio()
                if self.attack_frame_timer >= self.attack_speed:
                    self.is_attacking = False
                    self.attack_frame_timer = 0
                    self.ai_current_action = "idle"

        elif self.ai_current_action == "defend":
            self.state = "defend"
            self.is_defending = True
            self.ai_defend_cooldown = 60

        else:
            self.is_attacking = False
            self.is_defending = False

        if self.special_ready and self.special_cooldown == 0 and random.random() < 0.06:
            self.special_requested = True

        self.vel_y += self.gravity
        self.y += self.vel_y
        if self.y >= self.start_y:
            self.y = self.start_y
            self.vel_y = 0
            self.is_jumping = False

        if self.x < 50:
            self.x = 50
        if self.x > WIDTH - PLAYER_SIZE[0] - 50:
            self.x = WIDTH - PLAYER_SIZE[0] - 50

        moving = self.state == "walk" and not self.is_jumping and self.y >= self.start_y
        self._play_walk_audio(moving)

        # FIX: For idle and defend, freeze on first frame
        if self.state in ["idle", "defend"]:
            self.frame = 0
        else:
            self.frame += self.anim_speed

        special_blade = None
        if self.special_requested:
            special_blade = self.try_activate_special(opponent)

        return special_blade
