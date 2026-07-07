import pygame
import os
import random
import math
from src.config import (
    WIDTH, HEIGHT, PAUSE_BUTTON_POS, PAUSE_BUTTON_RADIUS,
    MENU_RECT, MP_MENU_RECT, MP_HOST_BTN, MP_INPUT_BOX, MP_JOIN_BTN,
    MP_BACK_BTN, BG_MENU_RECT, BG_PREVIEW_SIZE, BG_SLIDE_LEFT_BTN,
    BG_SLIDE_RIGHT_BTN, BG_SELECT_BTN, BG_BACK_BTN, FONT, SMALL_FONT,
    MENU_FONT, AVATAR_PATH, BUTTON_WIDTH, BUTTON_HEIGHT,
    BUTTON_PADDING, BUTTON_BORDER_RADIUS,
)
from src.states import GameState
from src.player import (
    set_background, available_backgrounds, current_bg_index,
    left_idle_frames, left_walk_frames, left_attack_frames,
    left_defend_frames, left_jump_frames, right_idle_frames,
    right_walk_frames, right_attack_frames, right_defend_frames,
    right_jump_frames, Bot
)

class LavaDrop:
    """Animated lava drop particle for menu background."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = random.uniform(0.8, 1.3)  # Falling speed
        self.size = random.randint(8, 16)  # Drop size
        self.lifetime = 0
        # Calculate max_lifetime so drop disappears around y=300 (button area)
        self.max_lifetime = int((300 - y) / self.velocity) + random.randint(-20, 20)
        self.wobble = random.uniform(-0.2, 0.2)  # Horizontal drift
        self.wobble_speed = random.uniform(0.02, 0.05)
        self.wobble_offset = random.uniform(0, 3.14)
    
    def update(self):
        """Update drop position and animation."""
        self.y += self.velocity
        self.x += self.wobble
        self.wobble = 2 * math.sin(self.lifetime * self.wobble_speed + self.wobble_offset)
        self.lifetime += 1
        return self.lifetime < self.max_lifetime
    
    def draw(self, surface):
        """Draw the lava drop with glow effect."""
        if self.lifetime > self.max_lifetime:
            return
        
        # Fade out at the end
        alpha_factor = 1 - (self.lifetime / self.max_lifetime)
        
        # Draw glow (outer bright orange)
        glow_size = int(self.size * 1.8)
        glow_color = (255, 150, 0, int(80 * alpha_factor))
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))
        
        # Draw main drop (bright orange)
        main_color = (255, 180, 50, int(220 * alpha_factor))
        main_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(main_surf, main_color, (self.size, self.size), self.size)
        surface.blit(main_surf, (int(self.x - self.size), int(self.y - self.size)))
        
        # Draw bright core
        core_color = (255, 220, 100, int(255 * alpha_factor))
        core_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(core_surf, core_color, (self.size // 2, self.size // 2), max(1, self.size // 3))
        surface.blit(core_surf, (int(self.x - self.size // 2), int(self.y - self.size // 2)))

# --- ADD THESE INSIDE YOUR UIManager CLASS IN ui.py ---

def _find_avatar_path(filename):
    filename_lower = filename.lower()
    if os.path.isdir(AVATAR_PATH):
        for entry in os.listdir(AVATAR_PATH):
            if entry.lower() == filename_lower:
                return os.path.join(AVATAR_PATH, entry)
    return os.path.join(AVATAR_PATH, filename)

def load_full_avatar(filename, size=(140, 140)):
    """
    Attempts to load avatar graphics from multiple path fallbacks,
    clips them into a perfectly round circle, and adds a sleek ring frame.
    """
    avatar_surf = pygame.Surface(size, pygame.SRCALPHA)
    raw_img = None

    possible_paths = [
        _find_avatar_path(filename)
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                raw_img = pygame.image.load(path)
                try:
                    if pygame.display.get_surface() is not None:
                        try:
                            raw_img = raw_img.convert_alpha()
                        except Exception:
                            raw_img = raw_img.convert()
                except Exception:
                    pass
                print(f"[SUCCESS] Loaded avatar from: {path}")
                break
            except Exception as e:
                print(f"[ERROR] Failed loading found file at {path}: {e}")

    if raw_img is None:
        print(f"[WARNING] Could not find '{filename}' in any expected directories. Using high-visibility fallback.")
        scaled_img = pygame.Surface(size, pygame.SRCALPHA)
        scaled_img.fill((45, 45, 55))
        pygame.draw.circle(scaled_img, (220, 60, 60) if "1" in filename else (60, 120, 220),
                           (size[0] // 2, size[1] // 2), size[0] // 3)
    else:
        scaled_img = pygame.transform.scale(raw_img, size)

    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (size[0] // 2, size[1] // 2), size[0] // 2)
    avatar_surf.blit(scaled_img, (0, 0))
    avatar_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.circle(avatar_surf, (220, 220, 230), (size[0] // 2, size[1] // 2), size[0] // 2, width=4)
    return avatar_surf

avatar_left = load_full_avatar("avatar.jfif", size=(140, 140))
avatar_right = load_full_avatar("avatar2.jfif", size=(140, 140))

def draw_ornate_button(surface, rect, label, mouse_pos, font=None):
    """Draw an ornate medieval-style button with decorative borders."""
    if font is None:
        font = FONT
    is_hovered = rect.collidepoint(mouse_pos)
    
    # Create button surface with alpha
    btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    # Base stone color - darker when not hovered, slightly lighter when hovered
    base_color = (45, 42, 38) if not is_hovered else (55, 50, 45)
    
    # Draw main button background
    pygame.draw.rect(btn_surf, (*base_color, 220), (0, 0, rect.width, rect.height), border_radius=16)
    
    # Draw ornate outer border (gold/brass effect)
    pygame.draw.rect(btn_surf, (184, 152, 75), (0, 0, rect.width, rect.height), width=4, border_radius=16)
    
    # Draw inner darker border for depth
    pygame.draw.rect(btn_surf, (100, 85, 50), (4, 4, rect.width - 8, rect.height - 8), width=2, border_radius=12)
    
    # Add decorative corner circles (ornate frame effect)
    corner_radius = 12
    corners = [
        (corner_radius, corner_radius),
        (rect.width - corner_radius, corner_radius),
        (corner_radius, rect.height - corner_radius),
        (rect.width - corner_radius, rect.height - corner_radius)
    ]
    for cx, cy in corners:
        pygame.draw.circle(btn_surf, (184, 152, 75), (cx, cy), 6)
        pygame.draw.circle(btn_surf, (100, 85, 50), (cx, cy), 3)
    
    # Draw subtle shadow/depth on bottom and right
    pygame.draw.line(btn_surf, (20, 18, 15), (0, rect.height - 1), (rect.width, rect.height - 1), width=2)
    pygame.draw.line(btn_surf, (20, 18, 15), (rect.width - 1, 0), (rect.width - 1, rect.height), width=2)
    
    # Draw highlight on top and left
    pygame.draw.line(btn_surf, (100, 90, 60), (0, 0), (rect.width, 0), width=1)
    pygame.draw.line(btn_surf, (100, 90, 60), (0, 0), (0, rect.height), width=1)
    
    surface.blit(btn_surf, (rect.x, rect.y))
    
    # Draw text in gold/brass color
    txt = font.render(label.upper(), True, (255, 223, 128))
    surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

def draw_main_menu(surface, buttons, lava_drops):
    from src.player import menu_background

    surface.blit(menu_background, (0, 0))

    title_path = os.path.join('assets', 'images', 'Game Title', 'Blade Clash Arena Game Title.png')
    if os.path.exists(title_path):
        try:
            title_image = pygame.image.load(title_path).convert_alpha()
            scaled_width = int(title_image.get_width() * 0.95)
            scaled_height = int(title_image.get_height() * 0.95)
            title_image = pygame.transform.smoothscale(title_image, (scaled_width, scaled_height))
            surface.blit(title_image, (WIDTH // 2 - scaled_width // 2, 24))
        except Exception:
            pass

    # Draw lava drops
    for drop in lava_drops:
        drop.draw(surface)

    mouse_pos = pygame.mouse.get_pos()
    for btn_rect, label in buttons:
        draw_ornate_button(surface, btn_rect, label, mouse_pos)


def draw_control_card(surface, rect, icon_surface, title, key_label, active=False):
    card_bg = (25, 28, 35)
    border_color = (0, 180, 255) if active else (70, 80, 95)
    fill_color = (40, 45, 55) if active else card_bg

    pygame.draw.rect(surface, fill_color, rect, border_radius=18)
    pygame.draw.rect(surface, border_color, rect, width=3, border_radius=18)

    icon_size = 72
    icon_pos = (rect.x + 20, rect.y + (rect.height - icon_size) // 2)
    icon = pygame.transform.smoothscale(icon_surface, (icon_size, icon_size))
    surface.blit(icon, icon_pos)

    title_surf = SMALL_FONT.render(title.upper(), True, (235, 235, 235))
    surface.blit(title_surf, (rect.x + 110, rect.y + 24))

    key_surf = FONT.render(key_label, True, (255, 220, 120))
    surface.blit(key_surf, (rect.x + 110, rect.y + rect.height - key_surf.get_height() - 20))

    label_surf = SMALL_FONT.render("PRESS KEY", True, (180, 180, 200))
    surface.blit(label_surf, (rect.x + 110, rect.y + rect.height - key_surf.get_height() - 42))


def draw_instruction_card(surface, rect, image_surface, title, key_label, extra_label=None):
    pygame.draw.rect(surface, (40, 40, 45), rect, border_radius=16)
    pygame.draw.rect(surface, (100, 110, 130), rect, width=2, border_radius=16)

    icon_size = min(120, rect.height - 24)
    icon_rect = pygame.Rect(rect.x + 16, rect.y + 16, icon_size, icon_size)
    icon = pygame.transform.smoothscale(image_surface, (icon_size, icon_size))
    surface.blit(icon, icon_rect.topleft)

    title_surf = FONT.render(title, True, (245, 245, 245))
    surface.blit(title_surf, (icon_rect.right + 16, rect.y + 22))

    key_surf = SMALL_FONT.render(key_label, True, (255, 215, 120))
    surface.blit(key_surf, (icon_rect.right + 16, rect.y + 22 + title_surf.get_height() + 8))

    if extra_label:
        extra_surf = SMALL_FONT.render(extra_label, True, (180, 180, 200))
        surface.blit(extra_surf, (icon_rect.right + 16, rect.y + rect.height - extra_surf.get_height() - 16))


def draw_ui_elements(surface):
    surface.blit(avatar_left, (35, 30))
    surface.blit(avatar_right, (WIDTH - 35 - 140, 30))

    small_radius = int(PAUSE_BUTTON_RADIUS * 0.75)
    circle_surface = pygame.Surface((small_radius * 2, small_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(circle_surface, (30, 30, 35, 178), (small_radius, small_radius), small_radius)
    surface.blit(circle_surface, (PAUSE_BUTTON_POS[0] - small_radius, PAUSE_BUTTON_POS[1] - small_radius))

    bar_width, bar_height = 8, 30
    pygame.draw.rect(surface, (255, 255, 255), (PAUSE_BUTTON_POS[0] - 12, PAUSE_BUTTON_POS[1] - bar_height // 2, bar_width, bar_height))
    pygame.draw.rect(surface, (255, 255, 255), (PAUSE_BUTTON_POS[0] + 4, PAUSE_BUTTON_POS[1] - bar_height // 2, bar_width, bar_height))


def draw_pause_menu(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    pygame.draw.rect(surface, (20, 20, 20), MENU_RECT, border_radius=15)
    pygame.draw.rect(surface, (60, 60, 60), MENU_RECT, width=3, border_radius=15)

    title = FONT.render("PAUSED", True, (255, 255, 255))
    surface.blit(title, (MENU_RECT.centerx - title.get_width() // 2, MENU_RECT.y + 25))

    options = ["RESUME MATCH", "OPTIONS", "QUIT TO MENU"]
    mouse_pos = pygame.mouse.get_pos()

    for i, opt in enumerate(options):
        opt_rect = pygame.Rect(MENU_RECT.x + 25, MENU_RECT.y + 90 + i * 65, MENU_RECT.width - 50, 45)
        
        # Draw ornate buttons for pause menu
        draw_ornate_button(surface, opt_rect, opt, mouse_pos, SMALL_FONT)

def draw_background_changer_menu(surface, local_index):
    from src.player import available_backgrounds

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    pygame.draw.rect(surface, (24, 24, 28), BG_MENU_RECT, border_radius=20)
    pygame.draw.rect(surface, (0, 180, 255), BG_MENU_RECT, width=4, border_radius=20)

    title = MENU_FONT.render("SELECT STAGE BACKGROUND", True, (255, 255, 255))
    surface.blit(title, (BG_MENU_RECT.centerx - title.get_width() // 2, BG_MENU_RECT.y + 40))

    if 0 <= local_index < len(available_backgrounds):
        file_name, original_surface = available_backgrounds[local_index]

        preview_rect = pygame.Rect(BG_MENU_RECT.centerx - BG_PREVIEW_SIZE[0] // 2, BG_MENU_RECT.y + 160, *BG_PREVIEW_SIZE)
        scaled_preview = pygame.transform.scale(original_surface, BG_PREVIEW_SIZE)

        surface.blit(scaled_preview, preview_rect.topleft)
        pygame.draw.rect(surface, (255, 255, 255), preview_rect, width=3)

        name_txt = FONT.render(file_name, True, (255, 255, 100))
        surface.blit(name_txt, (BG_MENU_RECT.centerx - name_txt.get_width() // 2, BG_MENU_RECT.y + 440))

        tracker_text = SMALL_FONT.render(f"Image {local_index + 1} of {len(available_backgrounds)}", True, (200, 200, 200))
        surface.blit(tracker_text, (BG_MENU_RECT.centerx - tracker_text.get_width() // 2, BG_MENU_RECT.y + 120))

        if local_index == current_bg_index:
            active_lbl = SMALL_FONT.render("[ ACTIVE BACKGROUND ]", True, (0, 255, 0))
            surface.blit(active_lbl, (BG_MENU_RECT.centerx - active_lbl.get_width() // 2, BG_MENU_RECT.y + 480))

    mouse_pos = pygame.mouse.get_pos()

    # Draw ornate buttons for background menu
    draw_ornate_button(surface, BG_SLIDE_LEFT_BTN, "<", mouse_pos, FONT)
    draw_ornate_button(surface, BG_SLIDE_RIGHT_BTN, ">", mouse_pos, FONT)
    draw_ornate_button(surface, BG_SELECT_BTN, "APPLY BACKGROUND", mouse_pos, FONT)
    draw_ornate_button(surface, BG_BACK_BTN, "SAVE & RETURN", mouse_pos, SMALL_FONT)

def draw_multiplayer_menu(surface, room_code, input_text, is_active, status_msg):
    pygame.draw.rect(surface, (24, 24, 28), MP_MENU_RECT, border_radius=16)
    pygame.draw.rect(surface, (100, 100, 110), MP_MENU_RECT, width=3, border_radius=16)

    title = MENU_FONT.render("MULTIPLAYER SETUP", True, (255, 255, 255))
    surface.blit(title, (MP_MENU_RECT.centerx - title.get_width() // 2, MP_MENU_RECT.y + 40))

    mouse = pygame.mouse.get_pos()

    # Draw ornate buttons for multiplayer menu
    draw_ornate_button(surface, MP_HOST_BTN, "HOST GAME ROOM", mouse, SMALL_FONT)

    # Input box styling - prevent text overflow
    bg_box = (40, 40, 45) if is_active else (25, 25, 28)
    border_c = (0, 180, 255) if is_active else (70, 70, 80)
    pygame.draw.rect(surface, bg_box, MP_INPUT_BOX, border_radius=8)
    pygame.draw.rect(surface, border_c, MP_INPUT_BOX, width=2, border_radius=8)

    # Display input text with clipping to prevent overflow
    display_text = input_text[:6] if input_text else "ENTER ROOM CODE"  # Limit to 6 digits
    txt_color = (255, 255, 255) if input_text else (120, 120, 130)
    txt_i = FONT.render(display_text, True, txt_color)
    
    # Clip the text to fit in the box
    max_text_width = MP_INPUT_BOX.width - 30
    if txt_i.get_width() > max_text_width:
        txt_i = pygame.transform.scale(txt_i, (max_text_width, txt_i.get_height()))
    
    surface.blit(txt_i, (MP_INPUT_BOX.x + 15, MP_INPUT_BOX.centery - txt_i.get_height() // 2))

    # Display room code (BOLD, GOLDEN, positioned above back button)
    if room_code:
        # Create a bold golden font for the room code
        code_font = pygame.font.SysFont("Arial", 32, bold=True)
        code_text = f"ROOM: {room_code}"
        code_surf = code_font.render(code_text, True, (255, 215, 0))  # Golden color
        
        # Position it exactly above the back button
        code_x = MP_MENU_RECT.centerx - code_surf.get_width() // 2
        code_y = MP_BACK_BTN.y - code_surf.get_height() - 25
        surface.blit(code_surf, (code_x, code_y))

    status_lbl = SMALL_FONT.render(f"STATUS: {status_msg}", True, (0, 255, 255))
    surface.blit(status_lbl, (MP_MENU_RECT.centerx - status_lbl.get_width() // 2, MP_MENU_RECT.y + 340))

    # Draw ornate buttons for join and back
    draw_ornate_button(surface, MP_JOIN_BTN, "JOIN ROOM MATCH", mouse, SMALL_FONT)
    draw_ornate_button(surface, MP_BACK_BTN, "BACK TO MENU", mouse, SMALL_FONT)

def draw_health_bars(surface, hp1, sh1, hp2, sh2, name1="Player 1", name2="Player 2", special1=0, special2=0, max_hp1=100, max_hp2=100, ready1=False, ready2=False):
    small_radius = int(PAUSE_BUTTON_RADIUS * 0.75)
    pause_center_x = PAUSE_BUTTON_POS[0]
    safety_gap = 20

    max_left_end = pause_center_x - small_radius - safety_gap
    max_right_start = pause_center_x + small_radius + safety_gap

    width_left = max_left_end - 190
    width_right = (WIDTH - 190) - max_right_start
    bar_w = min(width_left, width_right)

    p1_x = 190
    p2_x = WIDTH - 190 - bar_w

    hp_h = 38
    sh_h = 16
    special_h = 12
    border_thickness = 3

    font_names = pygame.font.SysFont('Arial', 20, bold=True)
    text_n1 = font_names.render(name1, True, (255, 255, 255))
    text_n2 = font_names.render(name2, True, (255, 255, 255))
    surface.blit(text_n1, (p1_x, 14))
    surface.blit(text_n2, (p2_x + bar_w - text_n2.get_width(), 14))

    pygame.draw.rect(surface, (80, 20, 20), (p1_x, 42, bar_w, hp_h))
    p1_hp_w = int((max(0, min(hp1, max_hp1)) / max_hp1) * bar_w)
    pygame.draw.rect(surface, (230, 35, 35), (p1_x, 42, p1_hp_w, hp_h))
    pygame.draw.rect(surface, (0, 0, 0), (p1_x, 42, bar_w, hp_h), width=border_thickness)

    pygame.draw.rect(surface, (15, 40, 80), (p1_x, 86, bar_w, sh_h))
    p1_sh_w = int((max(0, min(sh1, 100)) / 100) * bar_w)
    pygame.draw.rect(surface, (35, 115, 245), (p1_x, 86, p1_sh_w, sh_h))
    pygame.draw.rect(surface, (0, 0, 0), (p1_x, 86, bar_w, sh_h), width=border_thickness)

    pygame.draw.rect(surface, (25, 20, 0), (p1_x, 106, bar_w, special_h))
    p1_special_w = int((max(0, min(special1, 10)) / 10) * bar_w)
    pygame.draw.rect(surface, (245, 215, 50), (p1_x, 106, p1_special_w, special_h))
    pygame.draw.rect(surface, (0, 0, 0), (p1_x, 106, bar_w, special_h), width=border_thickness)
    if ready1:
        pulse_alpha = 150 + int(80 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 180)))
        glow_surface = pygame.Surface((p1_special_w, special_h), pygame.SRCALPHA)
        glow_surface.fill((255, 255, 200, pulse_alpha))
        surface.blit(glow_surface, (p1_x, 106))
        pygame.draw.rect(surface, (255, 240, 120), (p1_x + bar_w - 12, 106, 10, special_h), border_radius=4)

    pygame.draw.rect(surface, (80, 20, 20), (p2_x, 42, bar_w, hp_h))
    p2_hp_w = int((max(0, min(hp2, max_hp2)) / max_hp2) * bar_w)
    pygame.draw.rect(surface, (230, 35, 35), (p2_x + (bar_w - p2_hp_w), 42, p2_hp_w, hp_h))
    pygame.draw.rect(surface, (0, 0, 0), (p2_x, 42, bar_w, hp_h), width=border_thickness)

    pygame.draw.rect(surface, (15, 40, 80), (p2_x, 86, bar_w, sh_h))
    p2_sh_w = int((max(0, min(sh2, 100)) / 100) * bar_w)
    pygame.draw.rect(surface, (35, 115, 245), (p2_x + (bar_w - p2_sh_w), 86, p2_sh_w, sh_h))
    pygame.draw.rect(surface, (0, 0, 0), (p2_x, 86, bar_w, sh_h), width=border_thickness)

    pygame.draw.rect(surface, (25, 20, 0), (p2_x, 106, bar_w, special_h))
    p2_special_w = int((max(0, min(special2, 10)) / 10) * bar_w)
    pygame.draw.rect(surface, (245, 215, 50), (p2_x + (bar_w - p2_special_w), 106, p2_special_w, special_h))
    pygame.draw.rect(surface, (0, 0, 0), (p2_x, 106, bar_w, special_h), width=border_thickness)
    if ready2:
        pulse_alpha = 150 + int(80 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 180)))
        glow_surface = pygame.Surface((p2_special_w, special_h), pygame.SRCALPHA)
        glow_surface.fill((255, 255, 200, pulse_alpha))
        surface.blit(glow_surface, (p2_x + (bar_w - p2_special_w), 106))
        pygame.draw.rect(surface, (255, 240, 120), (p2_x + 2, 106, 10, special_h), border_radius=4)

def draw_fps_counter(surface, clock):
    fps_text = SMALL_FONT.render(f"FPS: {int(clock.get_fps())}", True, (0, 255, 0))
    surface.blit(fps_text, (20, HEIGHT - 40))

class UIManager:
    def __init__(self):
        # --- ADD THESE INSIDE UIManager.__init__ ---
        from src.config import MENU_MUSIC_PATH
        self.music_muted = False
        self.current_music_path = MENU_MUSIC_PATH
        self.show_gear_menu = False
        self.state = GameState.MAIN_MENU
        self.main_menu_buttons = self._build_main_menu_buttons()
        self.player1_name = "Player 1"
        self.player2_name = "Player 2"
        self.active_box = None

        self.fps_enabled = False
        self.game_voice_enabled = True
        self.music_enabled = True
        self.show_hitboxes = False
        self.screen_shake_enabled = True

        self.mp_role = None
        self.generated_code = ""
        self.inputted_code = ""
        self.active_mp_input = False
        self.status_msg = "Select HOST or enter a join code."
        self.selected_avatar_index = 0
        self.avatar_choices = [
            ("LEFT PLAYER", avatar_left),
            ("RIGHT PLAYER", avatar_right)
        ]

        self.background_index = current_bg_index
        
        # Single player mode variables
        self.single_player_mode = False
        self.current_round = 1
        self.bot = None
        self.active_saw_blade = None
        self.round_result_message = ""
        self.round_lost = False
        self.round_victory = False
        self.round_background_map = {1: 10, 2: 3, 3: 6, 4: 6}
        self.final_boss_round = 4
        
        # Initialize lava drops for menu animation
        self.lava_drops = []
        self.lava_drop_timer = 0
    
    
    def play_menu_music(self):
        """Loads and plays the active menu music loop if audio isn't muted."""
        if self.music_muted:
            return
            
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load(self.current_music_path)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(loops=-1)
            except pygame.error as e:
                print(f"Audio Error: {e}")

    def stop_music(self):
        """Stops the currently playing background music."""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    
    def _build_main_menu_buttons(self):
        labels = [
            "LOCAL MULTIPLAYER",
            "SINGLE PLAYER",
            "MULTIPLAYER (LAN)",
            "CHANGE BACKGROUND",
            "CHANGE AVATAR",
            "HOW TO PLAY",
            "EXIT GAME"
        ]
        small_w = int(BUTTON_WIDTH * 0.8)
        small_h = int(BUTTON_HEIGHT * 0.8)
        start_y = 300

        buttons = []
        for i, label in enumerate(labels):
            btn_x = WIDTH // 2 - small_w // 2
            btn_y = start_y + i * (small_h + BUTTON_PADDING)
            buttons.append((pygame.Rect(btn_x, btn_y, small_w, small_h), label))
        return buttons

    def handle_event(self, event, mouse_pos, player1, player2, net):
        if event.type == pygame.QUIT:
            return {"quit": True}
        
        # --- ADD TO GameState.MAIN_MENU EVENT ROUTER ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            from src.config import SPEAKER_BTN, GEAR_BTN, CHANGE_SOUND_BTN, MENU_MUSIC_PATH, MENU_MUSIC_PATH_2
            
            # 1. Speaker Mute/Unmute Toggle logic
            if SPEAKER_BTN.collidepoint(mouse_pos):
                self.music_muted = not self.music_muted
                if self.music_muted:
                    pygame.mixer.music.stop()
                else:
                    self.play_menu_music()
                return {"handled": True}
                
            # 2. Gear Menu Visibility Toggle logic
            elif GEAR_BTN.collidepoint(mouse_pos):
                self.show_gear_menu = not self.show_gear_menu
                return {"handled": True}
                
            # 3. Change Sound Option Selection (Dynamic 2-way toggle!)
            elif self.show_gear_menu and CHANGE_SOUND_BTN.collidepoint(mouse_pos):
                # Check what is currently playing and flip it to the other one
                if self.current_music_path == MENU_MUSIC_PATH:
                    self.current_music_path = MENU_MUSIC_PATH_2
                else:
                    self.current_music_path = MENU_MUSIC_PATH
                    
                # Stop the track and fire up the new one immediately
                pygame.mixer.music.stop()
                self.play_menu_music()
                self.show_gear_menu = False  # Close the popup menu automatically
                return {"handled": True}

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == GameState.MAIN_MENU:
                result = self._handle_main_menu_click(mouse_pos)
                if result:
                    return result
            elif self.state == GameState.HOW_TO_PLAY:
                # Clicking anywhere closes the How To Play overlay
                self.state = GameState.MAIN_MENU
            elif self.state == GameState.NAME_INPUT:
                self._handle_name_input_mouse(mouse_pos, player1, player2)
            elif self.state == GameState.SINGLE_PLAYER_NAME_INPUT:
                self._handle_single_player_name_input_mouse(mouse_pos, player1, player2)
            elif self.state == GameState.MULTIPLAYER_MENU:
                self._handle_multiplayer_menu_mouse(mouse_pos, player1, player2, net)
            elif self.state == GameState.BACKGROUND_MENU:
                self._handle_background_menu_mouse(mouse_pos)
            elif self.state == GameState.AVATAR_MENU:
                self._handle_avatar_menu_mouse(mouse_pos)
            elif self.state == GameState.PLAYING:
                self._handle_playing_mouse(mouse_pos)
            elif self.state == GameState.PAUSED:
                self._handle_paused_mouse(mouse_pos)
            elif self.state == GameState.OPTIONS:
                self._handle_options_mouse(mouse_pos)
            elif self.state == GameState.GAME_OVER:
                self.state = GameState.MAIN_MENU

        elif event.type == pygame.KEYDOWN:
            self._handle_keydown(event, player1, player2, net)

        return {}

    def _handle_main_menu_click(self, mouse_pos):
        for btn_rect, label in self.main_menu_buttons:
            if btn_rect.collidepoint(mouse_pos):
                if label == "LOCAL MULTIPLAYER":
                    self.player1_name = "Player 1"
                    self.player2_name = "Player 2"
                    self.active_box = None
                    self.mp_role = None
                    self.generated_code = ""
                    self.inputted_code = ""
                    self.active_mp_input = False
                    self.status_msg = "Enter names and start your local duel."
                    self.state = GameState.NAME_INPUT
                elif label == "SINGLE PLAYER":
                    self.player1_name = "Player"
                    self.active_box = 'sp_name'
                    self.single_player_mode = False
                    self.bot = None
                    self.current_round = 1
                    self.status_msg = "Enter your name for single player mode."
                    self.state = GameState.SINGLE_PLAYER_NAME_INPUT
                elif label == "MULTIPLAYER (LAN)":
                    self.mp_role = None
                    self.generated_code = ""
                    self.inputted_code = ""
                    self.active_mp_input = False
                    self.status_msg = "Select HOST to create a room or enter a join code."
                    self.state = GameState.MULTIPLAYER_MENU
                elif label == "CHANGE BACKGROUND":
                    self.status_msg = "Use the arrows to preview available stage backgrounds."
                    self.state = GameState.BACKGROUND_MENU
                elif label == "CHANGE AVATAR":
                    self.selected_avatar_index = 0
                    self.status_msg = "Choose your avatar. Active by default."
                    self.state = GameState.AVATAR_MENU
                elif label == "HOW TO PLAY":
                    self.state = GameState.HOW_TO_PLAY
                elif label == "EXIT GAME":
                    return {"quit": True}
                break
        return {}

    def _handle_name_input_mouse(self, mouse_pos, player1, player2):
        panel_w, panel_h = 400, 400
        panel_x = (WIDTH - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2
        p1_box = pygame.Rect(panel_x + 50, panel_y + 125, 300, 40)
        p2_box = pygame.Rect(panel_x + 50, panel_y + 215, 300, 40)
        continue_btn = pygame.Rect(panel_x + (panel_w - 240) // 2, panel_y + panel_h - 75, 240, 45)

        if p1_box.collidepoint(mouse_pos):
            self.active_box = 'p1'
            if self.player1_name == "Player 1":
                self.player1_name = ""
        elif p2_box.collidepoint(mouse_pos):
            self.active_box = 'p2'
            if self.player2_name == "Player 2":
                self.player2_name = ""
        elif continue_btn.collidepoint(mouse_pos):
            if self.player1_name.strip() == "":
                self.player1_name = "Player 1"
            if self.player2_name.strip() == "":
                self.player2_name = "Player 2"
            self._reset_match(player1, player2)
            self.state = GameState.PLAYING
        else:
            self.active_box = None

    def _handle_single_player_name_input_mouse(self, mouse_pos, player1, player2):
        panel_w, panel_h = 400, 320
        panel_x = (WIDTH - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2
        name_box = pygame.Rect(panel_x + 50, panel_y + 125, 300, 40)
        continue_btn = pygame.Rect(panel_x + (panel_w - 240) // 2, panel_y + panel_h - 75, 240, 45)

        if name_box.collidepoint(mouse_pos):
            self.active_box = 'sp_name'
            if self.player1_name == "Player":
                self.player1_name = ""
        elif continue_btn.collidepoint(mouse_pos):
            if self.player1_name.strip() == "":
                self.player1_name = "Player"
            self.player2_name = "BOT"
            self.single_player_mode = True
            self._start_single_player_match(player1, player2)
            self.state = GameState.PLAYING
        else:
            self.active_box = None

    def _handle_multiplayer_menu_mouse(self, mouse_pos, player1, player2, net):
        if MP_HOST_BTN.collidepoint(mouse_pos):
            self.mp_role = "HOST"
            self.generated_code = self._generate_room_code()
            if net.host_game(self.generated_code):
                self.status_msg = f"Hosting room {self.generated_code}. Waiting for client..."
            else:
                self.status_msg = "Failed to host. Check network."

        elif MP_INPUT_BOX.collidepoint(mouse_pos):
            self.active_mp_input = True
            self.mp_role = "CLIENT"
            self.player1_name = "Host (P1)"
            self.player2_name = "Client (P2)"
            self.status_msg = "Enter 6-digit code. Client on same WiFi."

        elif MP_JOIN_BTN.collidepoint(mouse_pos):
            if self.active_mp_input:
                self._attempt_join(player1, player2, net)
            else:
                self.status_msg = "Click input box first, then enter code."

        elif MP_BACK_BTN.collidepoint(mouse_pos):
            self.state = GameState.MAIN_MENU

    def _handle_background_menu_mouse(self, mouse_pos):
        if BG_SLIDE_LEFT_BTN.collidepoint(mouse_pos):
            self.background_index = max(0, self.background_index - 1)
            self.status_msg = "Preview updated."
        elif BG_SLIDE_RIGHT_BTN.collidepoint(mouse_pos):
            self.background_index = min(len(available_backgrounds) - 1, self.background_index + 1)
            self.status_msg = "Preview updated."
        elif BG_SELECT_BTN.collidepoint(mouse_pos):
            set_background(self.background_index)
            self.status_msg = "Background applied successfully."
        elif BG_BACK_BTN.collidepoint(mouse_pos):
            self.state = GameState.MAIN_MENU

    def _handle_avatar_menu_mouse(self, mouse_pos):
        avatar_count = len(self.avatar_choices)
        menu_x = BG_MENU_RECT.x + 40
        menu_y = BG_MENU_RECT.y + 120
        item_w = 260
        item_h = 280
        gap = 20

        for idx, (label, _) in enumerate(self.avatar_choices):
            item_x = menu_x + idx * (item_w + gap)
            item_rect = pygame.Rect(item_x, menu_y, item_w, item_h)
            if item_rect.collidepoint(mouse_pos):
                self.selected_avatar_index = idx
                self.status_msg = f"{label} selected."

        back_btn = pygame.Rect(BG_MENU_RECT.centerx - 100, BG_MENU_RECT.bottom - 90, 200, 50)
        if back_btn.collidepoint(mouse_pos):
            self.state = GameState.MAIN_MENU

    def _handle_playing_mouse(self, mouse_pos):
        distance = pygame.math.Vector2(mouse_pos).distance_to(PAUSE_BUTTON_POS)
        if distance <= PAUSE_BUTTON_RADIUS:
            self.state = GameState.PAUSED

    def _handle_paused_mouse(self, mouse_pos):
        resume_rect = pygame.Rect(MENU_RECT.x + 25, MENU_RECT.y + 90, MENU_RECT.width - 50, 45)
        options_rect = pygame.Rect(MENU_RECT.x + 25, MENU_RECT.y + 155, MENU_RECT.width - 50, 45)
        quit_rect = pygame.Rect(MENU_RECT.x + 25, MENU_RECT.y + 220, MENU_RECT.width - 50, 45)

        if resume_rect.collidepoint(mouse_pos):
            self.state = GameState.PLAYING
        elif options_rect.collidepoint(mouse_pos):
            self.state = GameState.OPTIONS
        elif quit_rect.collidepoint(mouse_pos):
            self.state = GameState.MAIN_MENU

    def _handle_options_mouse(self, mouse_pos):
        opt_w, opt_h = 700, 600
        opt_x = (WIDTH - opt_w) // 2
        opt_y = (HEIGHT - opt_h) // 2

        fps_check_rect = pygame.Rect(opt_x + 520, opt_y + 130, 30, 30)
        voice_check_rect = pygame.Rect(opt_x + 520, opt_y + 200, 30, 30)
        music_check_rect = pygame.Rect(opt_x + 520, opt_y + 270, 30, 30)
        hitbox_check_rect = pygame.Rect(opt_x + 520, opt_y + 340, 30, 30)
        shake_check_rect = pygame.Rect(opt_x + 520, opt_y + 410, 30, 30)
        opt_back_btn = pygame.Rect(opt_x + (opt_w - 220) // 2, opt_y + opt_h - 85, 220, 45)

        if fps_check_rect.collidepoint(mouse_pos):
            self.fps_enabled = not self.fps_enabled
        elif voice_check_rect.collidepoint(mouse_pos):
            self.game_voice_enabled = not self.game_voice_enabled
        elif music_check_rect.collidepoint(mouse_pos):
            self.music_enabled = not self.music_enabled
        elif hitbox_check_rect.collidepoint(mouse_pos):
            self.show_hitboxes = not self.show_hitboxes
        elif shake_check_rect.collidepoint(mouse_pos):
            self.screen_shake_enabled = not self.screen_shake_enabled
        elif opt_back_btn.collidepoint(mouse_pos):
            self.state = GameState.PAUSED

    def _handle_keydown(self, event, player1, player2, net):
        if self.state == GameState.ROUND_RESULT and event.key == pygame.K_SPACE:
            self._advance_round(player1)
            return
        if self.state == GameState.GAME_OVER and self.round_lost and event.key == pygame.K_SPACE:
            self._reset_to_menu(player1, player2)
            return

        if self.state == GameState.NAME_INPUT:
            if self.active_box == 'p1':
                if event.key == pygame.K_BACKSPACE:
                    self.player1_name = self.player1_name[:-1]
                elif event.key == pygame.K_RETURN:
                    self.active_box = 'p2'
                    if self.player2_name == "Player 2":
                        self.player2_name = ""
                else:
                    if len(self.player1_name) < 14 and event.unicode.isprintable():
                        self.player1_name += event.unicode

            elif self.active_box == 'p2':
                if event.key == pygame.K_BACKSPACE:
                    self.player2_name = self.player2_name[:-1]
                elif event.key == pygame.K_RETURN:
                    self.active_box = None
                else:
                    if len(self.player2_name) < 14 and event.unicode.isprintable():
                        self.player2_name += event.unicode

        elif self.state == GameState.SINGLE_PLAYER_NAME_INPUT:
            if self.active_box == 'sp_name':
                if event.key == pygame.K_BACKSPACE:
                    self.player1_name = self.player1_name[:-1]
                elif event.key == pygame.K_RETURN:
                    if self.player1_name.strip() == "":
                        self.player1_name = "Player"
                    self.player2_name = "BOT"
                    self.single_player_mode = True
                    self._start_single_player_match(player1, player2)
                    self.state = GameState.PLAYING
                else:
                    if len(self.player1_name) < 14 and event.unicode.isprintable():
                        self.player1_name += event.unicode

        elif self.state == GameState.MULTIPLAYER_MENU and self.active_mp_input:
            if event.key == pygame.K_BACKSPACE:
                self.inputted_code = self.inputted_code[:-1]
            elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                self._attempt_join(player1, player2, net)
            elif event.unicode.isdigit() and len(self.inputted_code) < 6:
                self.inputted_code += event.unicode

        if event.key == pygame.K_ESCAPE:
            if self.state == GameState.PLAYING:
                self.state = GameState.PAUSED
            elif self.state == GameState.PAUSED:
                self.state = GameState.PLAYING
            elif self.state == GameState.OPTIONS:
                self.state = GameState.PAUSED
            elif self.state in (GameState.MULTIPLAYER_MENU, GameState.HOW_TO_PLAY, GameState.AVATAR_MENU, GameState.SINGLE_PLAYER_NAME_INPUT):
                self.state = GameState.MAIN_MENU

        if self.state == GameState.GAME_OVER and event.key == pygame.K_SPACE and not self.round_lost:
            self.state = GameState.MAIN_MENU

    def _attempt_join(self, player1, player2, net):
        if len(self.inputted_code) != 6:
            self.status_msg = "Room code must be exactly 6 digits."
            return

        # For local LAN, use localhost. For remote, change to host IP
        host_ip = "127.0.0.1"  # Change this to the host's IP address for LAN play
        
        if net.join_game(self.inputted_code, host_ip=host_ip):
            self._reset_match(player1, player2)
            self.state = GameState.PLAYING
            self.status_msg = "Connected! Match starting..."
        else:
            self.status_msg = "Join failed. Wrong code or host not found."

    def _reset_match(self, player1, player2):
        player1.health = player1.max_health if hasattr(player1, "max_health") else 100
        player1.shield = 100
        player2.health = player2.max_health if hasattr(player2, "max_health") else 100
        player2.shield = 100
        player1.x, player1.y = 300, HEIGHT - 430
        player2.x, player2.y = WIDTH - 300, HEIGHT - 430
        player1.state, player2.state = "idle", "idle"
        
        # Reset new click-based attack/defend system states
        for player in [player1, player2]:
            player.is_attacking = False
            player.is_defending = False
            player.defend_locked = False
            player.attack_pressed = False
            player.defend_pressed = False
            player.attack_frame_timer = 0
            player.frame = 0

    def _restore_player_after_round(self, player1):
        player1.shield = 100
        player1.health = min(player1.max_health, player1.health + 20)

    def _set_round_background(self, round_num):
        if round_num in self.round_background_map:
            bg_index = self.round_background_map[round_num]
            if 0 <= bg_index < len(available_backgrounds):
                self.background_index = bg_index
                set_background(bg_index)

    def _prepare_next_round(self, player1):
        self._restore_player_after_round(player1)
        self._set_round_background(self.current_round)
        if self.current_round == 3:
            player1.attack_speed = max(0.22, player1.attack_speed - 0.08)
        else:
            player1.attack_speed = 0.3

        if self.bot is not None:
            self.bot.set_difficulty(self.current_round)
            if self.current_round == self.final_boss_round:
                self.bot.max_health = 300
                self.bot.health = 300
                self.bot.is_boss = True
                self.player2_name = "FINAL BOSS"
            else:
                self.player2_name = f"BOT - ROUND {self.current_round}"
        self._reset_match(player1, self.bot)

    def _start_single_player_match(self, player1, player2):
        self.current_round = max(1, min(self.current_round, self.final_boss_round))
        if self.current_round == self.final_boss_round:
            self.bot = Bot(WIDTH - 300, HEIGHT - 430, side="right", difficulty_round=self.final_boss_round)
            self.player2_name = "FINAL BOSS"
        else:
            self.bot = Bot(WIDTH - 300, HEIGHT - 430, side="right", difficulty_round=self.current_round)
            self.player2_name = f"BOT - ROUND {self.current_round}"

        self._set_round_background(self.current_round)
        if self.current_round == 3:
            player1.attack_speed = max(0.22, player1.attack_speed - 0.08)
        else:
            player1.attack_speed = 0.3

        self._reset_match(player1, self.bot)
        self.status_msg = f"Single player match started: Round {self.current_round}."

    def _generate_room_code(self):
        return f"{random.randint(100000, 999999)}"

    def update(self, player1, player2, net):
        if self.state == GameState.MULTIPLAYER_MENU and self.mp_role == "HOST" and net.connected:
            self.status_msg = "Client connected. Starting multiplayer match."
            self._reset_match(player1, player2)
            self.state = GameState.PLAYING

        if self.state == GameState.PLAYING and self.single_player_mode and self.bot is not None:
            if player1.health < 1 or self.bot.health < 1:
                self._stop_walk_audio(player1, self.bot)
                self.active_saw_blade = None
                if player1.health < 1:
                    self.round_lost = True
                    self.round_victory = False
                    self.round_result_message = "YOU LOSE"
                    self.status_msg = "Press SPACEBAR to go to Menu."
                    self.state = GameState.GAME_OVER
                else:
                    self.round_victory = True
                    self.round_lost = False
                    if self.current_round < 3:
                        self.round_result_message = f"{self.player1_name} wins Round {self.current_round}!"
                    elif self.current_round == 3:
                        self.round_result_message = f"{self.player1_name} wins Round 3! Final Boss incoming."
                    else:
                        self.round_result_message = f"{self.player1_name} defeats the Final Boss!"
                    self.state = GameState.ROUND_RESULT

        elif self.state == GameState.PLAYING and not self.single_player_mode and (player1.health < 1 or player2.health < 1):
            self.state = GameState.GAME_OVER

        if self.active_saw_blade:
            self.active_saw_blade.update()
            if not self.active_saw_blade.active:
                self.active_saw_blade = None

        if self.state == GameState.MAIN_MENU:
            self.play_menu_music()
            # ... draw main menu graphics ...
            
        elif self.state == GameState.PLAYING:
            self.stop_music()
            # ... draw gameplay ...    

    def render(self, surface, mouse_pos, player1, player2, clock):
        
        # Update and spawn lava drops for main menu
        if self.state == GameState.MAIN_MENU:
            self.lava_drop_timer += 1
            # Spawn new drops every 6 frames
            if self.lava_drop_timer > 6:
                spawn_x = random.randint(0, WIDTH)
                # Spawn from top of title area (y=24 to y=150)
                spawn_y = random.randint(24, 150)
                self.lava_drops.append(LavaDrop(spawn_x, spawn_y))
                self.lava_drop_timer = 0
            
            # Update existing drops and remove dead ones
            self.lava_drops = [drop for drop in self.lava_drops if drop.update()]
        
        # --- SCREEN ROUTER DRAWING SYSTEM ---
        if self.state == GameState.MAIN_MENU:
            draw_main_menu(surface, self.main_menu_buttons, self.lava_drops)
            
            # =================================================================
            # AUDIO ICON DRAWING (Now safely locked inside MAIN_MENU state!)
            # =================================================================
            import math
            from src.config import SPEAKER_BTN, GEAR_BTN, CHANGE_SOUND_BTN, SMALL_FONT
            
            GOLD = (212, 175, 55)
            DARK_GREY = (30, 30, 35)
            WHITE = (255, 255, 255)
            
            # 1. DRAW GEAR ICON DIRECTLY
            pygame.draw.rect(surface, DARK_GREY, GEAR_BTN, border_radius=8)
            pygame.draw.rect(surface, GOLD, GEAR_BTN, width=2, border_radius=8)
            g_cx, g_cy = GEAR_BTN.center
            for i in range(8):
                angle = i * (math.pi / 4)
                tx = g_cx + int(math.cos(angle) * 15)
                ty = g_cy + int(math.sin(angle) * 15)
                pygame.draw.circle(surface, GOLD, (tx, ty), 4)
            pygame.draw.circle(surface, GOLD, (g_cx, g_cy), 11)
            pygame.draw.circle(surface, DARK_GREY, (g_cx, g_cy), 5)
            
            # 2. DRAW SPEAKER ICON DIRECTLY
            pygame.draw.rect(surface, DARK_GREY, SPEAKER_BTN, border_radius=8)
            pygame.draw.rect(surface, GOLD, SPEAKER_BTN, width=2, border_radius=8)
            s_cx, s_cy = SPEAKER_BTN.center
            pygame.draw.rect(surface, GOLD, (s_cx - 14, s_cy - 7, 7, 14))
            pygame.draw.polygon(surface, GOLD, [(s_cx - 7, s_cy - 7), (s_cx + 2, s_cy - 14), (s_cx + 2, s_cy + 14), (s_cx - 7, s_cy + 7)])
            
            if not self.music_muted:
                pygame.draw.arc(surface, GOLD, (s_cx - 3, s_cy - 10, 14, 20), -math.pi/3, math.pi/3, 2)
                pygame.draw.arc(surface, GOLD, (s_cx + 3, s_cy - 15, 18, 30), -math.pi/3, math.pi/3, 2)
            else:
                pygame.draw.line(surface, GOLD, (s_cx + 7, s_cy - 6), (s_cx + 17, s_cy + 6), 2)
                pygame.draw.line(surface, GOLD, (s_cx + 17, s_cy - 6), (s_cx + 7, s_cy + 6), 2)
                
            # 3. DRAW DROPDOWN DIRECTLY
            if self.show_gear_menu:
                pygame.draw.rect(surface, DARK_GREY, CHANGE_SOUND_BTN, border_radius=6)
                pygame.draw.rect(surface, GOLD, CHANGE_SOUND_BTN, width=2, border_radius=6)
                pop_txt = SMALL_FONT.render("Change Sound", True, WHITE)
                surface.blit(pop_txt, (CHANGE_SOUND_BTN.centerx - pop_txt.get_width()//2, CHANGE_SOUND_BTN.centery - pop_txt.get_height()//2))    
            # =================================================================

        elif self.state == GameState.NAME_INPUT:
            self._draw_name_input(surface, mouse_pos)
        elif self.state == GameState.SINGLE_PLAYER_NAME_INPUT:
            self._draw_single_player_name_input(surface, mouse_pos)
        elif self.state == GameState.MULTIPLAYER_MENU:
            self._draw_multiplayer_menu(surface)
        elif self.state == GameState.BACKGROUND_MENU:
            self._draw_background_menu(surface)
        elif self.state == GameState.AVATAR_MENU:
            self._draw_avatar_menu(surface)
        elif self.state == GameState.HOW_TO_PLAY:
            self._draw_how_to_play(surface)
        elif self.state == GameState.ROUND_RESULT:
            self._draw_game_screen(surface, player1, player2)
            self._draw_round_result_overlay(surface)
        elif self.state == GameState.GAME_OVER and self.round_lost:
            self._draw_game_screen(surface, player1, player2)
            self._draw_round_result_overlay(surface)
        else:
            self._draw_game_screen(surface, player1, player2)

        # FPS overlay stays restricted exclusively to active playing states
        if self.state == GameState.PLAYING and self.fps_enabled:
            draw_fps_counter(surface, clock)

    def _draw_name_input(self, surface, mouse_pos):
        panel_w, panel_h = 400, 400
        panel_x = (WIDTH - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2

        surface.fill((20, 20, 25))
        pygame.draw.rect(surface, (40, 40, 45), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
        pygame.draw.rect(surface, (70, 70, 75), (panel_x, panel_y, panel_w, panel_h), width=2, border_radius=12)

        font_title = pygame.font.SysFont('Arial', 22, bold=True)
        font_lbl = pygame.font.SysFont('Arial', 14, bold=True)
        font_txt = pygame.font.SysFont('Arial', 16, bold=False)
        font_btn = pygame.font.SysFont('Arial', 18, bold=True)

        text_title = font_title.render("PLAYER SETUP", True, (255, 255, 255))
        surface.blit(text_title, text_title.get_rect(center=(panel_x + panel_w // 2, panel_y + 40)))

        text_lbl1 = font_lbl.render("PLAYER 1 NAME", True, (180, 180, 185))
        surface.blit(text_lbl1, (panel_x + 50, panel_y + 100))

        p1_box = pygame.Rect(panel_x + 50, panel_y + 125, 300, 40)
        b_color1 = (100, 160, 255) if self.active_box == 'p1' else (65, 65, 70)
        pygame.draw.rect(surface, (25, 25, 30), p1_box, border_radius=6)
        pygame.draw.rect(surface, b_color1, p1_box, width=2, border_radius=6)

        disp_str1 = self.player1_name if self.player1_name != "" or self.active_box == 'p1' else "Player 1"
        txt_surf1 = font_txt.render(disp_str1, True, (255, 255, 255) if self.player1_name != "" else (110, 110, 115))
        surface.blit(txt_surf1, (p1_box.x + 12, p1_box.y + 9))

        text_lbl2 = font_lbl.render("PLAYER 2 NAME", True, (180, 180, 185))
        surface.blit(text_lbl2, (panel_x + 50, panel_y + 190))

        p2_box = pygame.Rect(panel_x + 50, panel_y + 215, 300, 40)
        b_color2 = (100, 160, 255) if self.active_box == 'p2' else (65, 65, 70)
        pygame.draw.rect(surface, (25, 25, 30), p2_box, border_radius=6)
        pygame.draw.rect(surface, b_color2, p2_box, width=2, border_radius=6)

        disp_str2 = self.player2_name if self.player2_name != "" or self.active_box == 'p2' else "Player 2"
        txt_surf2 = font_txt.render(disp_str2, True, (255, 255, 255) if self.player2_name != "" else (110, 110, 115))
        surface.blit(txt_surf2, (p2_box.x + 12, p2_box.y + 9))

        continue_btn = pygame.Rect(panel_x + (panel_w - 240) // 2, panel_y + panel_h - 75, 240, 45)
        
        # Draw ornate continue button
        draw_ornate_button(surface, continue_btn, "CONTINUE", mouse_pos, font_btn)

    def _draw_single_player_name_input(self, surface, mouse_pos):
        panel_w, panel_h = 420, 300
        panel_x = (WIDTH - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2

        surface.fill((18, 18, 24))
        pygame.draw.rect(surface, (35, 35, 42), (panel_x, panel_y, panel_w, panel_h), border_radius=16)
        pygame.draw.rect(surface, (75, 110, 220), (panel_x, panel_y, panel_w, panel_h), width=3, border_radius=16)

        font_title = pygame.font.SysFont('Arial', 24, bold=True)
        font_lbl = pygame.font.SysFont('Arial', 14, bold=True)
        font_txt = pygame.font.SysFont('Arial', 18, bold=False)
        font_btn = pygame.font.SysFont('Arial', 18, bold=True)

        title_text = font_title.render("SINGLE PLAYER MODE", True, (255, 255, 255))
        surface.blit(title_text, (panel_x + panel_w // 2 - title_text.get_width() // 2, panel_y + 35))

        hint_text = font_lbl.render("ENTER YOUR NAME", True, (190, 190, 205))
        surface.blit(hint_text, (panel_x + 50, panel_y + 100))

        name_box = pygame.Rect(panel_x + 50, panel_y + 125, 320, 44)
        box_color = (100, 160, 255) if self.active_box == 'sp_name' else (70, 70, 80)
        pygame.draw.rect(surface, (25, 25, 30), name_box, border_radius=8)
        pygame.draw.rect(surface, box_color, name_box, width=2, border_radius=8)

        display_name = self.player1_name if self.player1_name != "" or self.active_box == 'sp_name' else "Player"
        name_surf = font_txt.render(display_name, True, (235, 235, 235) if self.player1_name != "" else (120, 120, 130))
        surface.blit(name_surf, (name_box.x + 14, name_box.y + 12))

        status_text = SMALL_FONT.render(self.status_msg, True, (200, 200, 210))
        surface.blit(status_text, (panel_x + 50, panel_y + 190))

        continue_btn = pygame.Rect(panel_x + (panel_w - 260) // 2, panel_y + panel_h - 75, 260, 48)
        draw_ornate_button(surface, continue_btn, "START DUEL", mouse_pos, font_btn)

    def _draw_multiplayer_menu(self, surface):
        surface.fill((15, 15, 18))
        draw_multiplayer_menu(surface, self.generated_code if self.mp_role == "HOST" else "", self.inputted_code, self.active_mp_input, self.status_msg)

    def _draw_background_menu(self, surface):
        surface.fill((10, 10, 15))
        draw_background_changer_menu(surface, self.background_index)

    def _draw_avatar_menu(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, (32, 32, 36), BG_MENU_RECT, border_radius=20)
        pygame.draw.rect(surface, (0, 180, 255), BG_MENU_RECT, width=4, border_radius=20)

        title = MENU_FONT.render("CHANGE PLAYER", True, (255, 255, 255))
        surface.blit(title, (BG_MENU_RECT.centerx - title.get_width() // 2, BG_MENU_RECT.y + 40))

        item_w = 260
        item_h = 280
        gap = 20
        start_x = BG_MENU_RECT.x + 40
        start_y = BG_MENU_RECT.y + 120

        for idx, (label, avatar_surf) in enumerate(self.avatar_choices):
            item_x = start_x + idx * (item_w + gap)
            item_rect = pygame.Rect(item_x, start_y, item_w, item_h)
            is_active = idx == self.selected_avatar_index

            pygame.draw.rect(surface, (40, 44, 51), item_rect, border_radius=18)
            pygame.draw.rect(surface, (0, 200, 145) if is_active else (80, 90, 110), item_rect, width=3, border_radius=18)

            icon = pygame.transform.smoothscale(avatar_surf, (item_w - 40, item_h - 120))
            surface.blit(icon, (item_rect.x + 20, item_rect.y + 20))

            label_surf = FONT.render(label, True, (235, 235, 235))
            surface.blit(label_surf, (item_rect.x + 20, item_rect.y + item_h - 84))

            status_surf = SMALL_FONT.render("ACTIVE" if is_active else "CLICK TO SELECT", True, (160, 220, 255) if is_active else (180, 180, 190))
            surface.blit(status_surf, (item_rect.x + 20, item_rect.y + item_h - 50))

        back_btn = pygame.Rect(BG_MENU_RECT.centerx - 100, BG_MENU_RECT.bottom - 90, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw ornate back button
        draw_ornate_button(surface, back_btn, "BACK TO MENU", mouse_pos, SMALL_FONT)
        
        instruction = SMALL_FONT.render("CLICK TO GO TO MENU OR PRESS ESC", True, (200, 200, 200))
        surface.blit(instruction, (BG_MENU_RECT.centerx - instruction.get_width() // 2, BG_MENU_RECT.bottom - 130))

    def _draw_game_screen(self, surface, player1, player2):
        from src.player import game_background

        surface.blit(game_background, (0, 0))
        player1.draw(surface, opponent_x=player2.x)
        player2.draw(surface, opponent_x=player1.x)
        if self.active_saw_blade is not None:
            self.active_saw_blade.draw(surface)
        draw_ui_elements(surface)
        max_hp2 = player2.max_health if hasattr(player2, "max_health") else 100
        draw_health_bars(
            surface,
            player1.health,
            player1.shield,
            player2.health,
            player2.shield,
            self.player1_name,
            self.player2_name,
            player1.special_meter,
            player2.special_meter,
            player1.max_health,
            max_hp2,
            player1.special_ready,
            player2.special_ready
        )

        if self.state == GameState.PAUSED:
            draw_pause_menu(surface)
        elif self.state == GameState.OPTIONS:
            self._draw_options_overlay(surface)
        elif self.state == GameState.GAME_OVER and not self.round_lost:
            self._draw_game_over(surface, player1, player2)

    def _draw_options_overlay(self, surface):
        opt_w, opt_h = 700, 600
        opt_x = (WIDTH - opt_w) // 2
        opt_y = (HEIGHT - opt_h) // 2

        opt_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        opt_mask.fill((15, 15, 20, 180))
        surface.blit(opt_mask, (0, 0))

        pygame.draw.rect(surface, (40, 40, 45), (opt_x, opt_y, opt_w, opt_h), border_radius=16)
        pygame.draw.rect(surface, (80, 80, 85), (opt_x, opt_y, opt_w, opt_h), width=2, border_radius=16)

        f_opt_title = pygame.font.SysFont('Arial', 32, bold=True)
        f_opt_text = pygame.font.SysFont('Arial', 20, bold=True)
        f_opt_btn = pygame.font.SysFont('Arial', 18, bold=True)

        t_opt_title = f_opt_title.render("GAME OPTIONS", True, (255, 255, 255))
        surface.blit(t_opt_title, t_opt_title.get_rect(center=(opt_x + opt_w // 2, opt_y + 50)))

        options_rows = [
            ("TURN ON FPS COUNTER", self.fps_enabled, pygame.Rect(opt_x + 520, opt_y + 130, 30, 30)),
            ("GAME VOICE SYNCHRONIZATION", self.game_voice_enabled, pygame.Rect(opt_x + 520, opt_y + 200, 30, 30)),
            ("AMBIENT MUSIC SOUND TRACKS", self.music_enabled, pygame.Rect(opt_x + 520, opt_y + 270, 30, 30)),
            ("RENDER HITBOXES RUNTIME MONITOR", self.show_hitboxes, pygame.Rect(opt_x + 520, opt_y + 340, 30, 30)),
            ("CAMERA ACTION SCREEN SHAKE", self.screen_shake_enabled, pygame.Rect(opt_x + 520, opt_y + 410, 30, 30))
        ]

        for label_str, state_val, check_box_rect in options_rows:
            lbl_surf = f_opt_text.render(label_str, True, (220, 220, 225))
            surface.blit(lbl_surf, (opt_x + 60, check_box_rect.y + 3))

            pygame.draw.rect(surface, (20, 20, 25), check_box_rect, border_radius=6)

            if state_val:
                pygame.draw.rect(surface, (40, 175, 95), (check_box_rect.x + 4, check_box_rect.y + 4, 22, 22), border_radius=4)
                pygame.draw.line(surface, (255, 255, 255), (check_box_rect.x + 9, check_box_rect.y + 15), (check_box_rect.x + 14, check_box_rect.y + 20), width=3)
                pygame.draw.line(surface, (255, 255, 255), (check_box_rect.x + 14, check_box_rect.y + 20), (check_box_rect.x + 22, check_box_rect.y + 9), width=3)
            else:
                pygame.draw.rect(surface, (90, 90, 95), check_box_rect, width=2, border_radius=6)

        opt_back_btn = pygame.Rect(opt_x + (opt_w - 220) // 2, opt_y + opt_h - 85, 220, 45)
        b_hover = opt_back_btn.collidepoint(pygame.mouse.get_pos())
        b_color = (60, 130, 240) if b_hover else (45, 105, 215)
        pygame.draw.rect(surface, b_color, opt_back_btn, border_radius=8)

        t_btn_back = f_opt_btn.render("SAVE & RETURN", True, (255, 255, 255))
        surface.blit(t_btn_back, t_btn_back.get_rect(center=opt_back_btn.center))

    def _draw_game_over(self, surface, player1, player2):
        font_title = pygame.font.SysFont('Arial', 72, bold=True)
        font_subtitle = pygame.font.SysFont('Arial', 38, bold=True)
        font_footer = pygame.font.SysFont('Arial', 20, bold=False)

        text_game_over = font_title.render("GAME OVER", True, (230, 35, 35))
        winner_text = f"{self.player1_name} Wins!" if player2.health < 1 else f"{self.player2_name} Wins!"
        text_winner = font_subtitle.render(winner_text, True, (255, 255, 255))
        text_continue = font_footer.render("Press SPACEBAR to return to Main Menu", True, (180, 180, 180))

        rect_game_over = text_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        rect_winner = text_winner.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25))
        rect_continue = text_continue.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 85))

        overlay_panel = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay_panel, (15, 15, 20, 200), (WIDTH // 2 - 300, HEIGHT // 2 - 120, 600, 240), border_radius=18)
        pygame.draw.rect(overlay_panel, (230, 35, 35), (WIDTH // 2 - 300, HEIGHT // 2 - 120, 600, 240), width=3, border_radius=18)

        surface.blit(overlay_panel, (0, 0))
        surface.blit(text_game_over, rect_game_over)
        surface.blit(text_winner, rect_winner)
        surface.blit(text_continue, rect_continue)

    def _draw_round_result_overlay(self, surface):
        font_title = pygame.font.SysFont('Arial', 64, bold=True)
        font_subtitle = pygame.font.SysFont('Arial', 28, bold=True)
        font_footer = pygame.font.SysFont('Arial', 20, bold=False)

        main_text = font_title.render(self.round_result_message, True, (255, 235, 100))
        if self.round_lost:
            subtitle = "Press SPACEBAR to go to Menu"
            subtitle_color = (255, 170, 170)
        elif self.current_round == self.final_boss_round and self.round_victory:
            subtitle = "Press SPACEBAR to return to Menu"
            subtitle_color = (200, 255, 180)
        else:
            subtitle = "Press SPACEBAR to continue to the next round"
            subtitle_color = (200, 255, 180)

        subtitle_text = font_subtitle.render(subtitle, True, subtitle_color)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        surface.blit(main_text, main_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
        surface.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))
        surface.blit(font_footer.render("Spacebar to continue", True, (220, 220, 220)), (WIDTH // 2 - 110, HEIGHT // 2 + 90))

    def _stop_walk_audio(self, player1, player2):
        for entity in (player1, player2):
            if getattr(entity, "walk_channel", None) is not None:
                try:
                    if entity.walk_channel.get_busy():
                        entity.walk_channel.stop()
                except Exception:
                    pass

    def _advance_round(self, player1):
        if self.current_round < 3:
            self.current_round += 1
            self.round_result_message = ""
            self.round_victory = False
            self._prepare_next_round(player1)
            self.state = GameState.PLAYING
        elif self.current_round == 3:
            self.current_round = self.final_boss_round
            self.round_result_message = ""
            self.round_victory = False
            self._start_single_player_match(player1, None)
            self.state = GameState.PLAYING
        else:
            self._reset_to_menu(player1, None)

    def _reset_to_menu(self, player1, player2):
        self.single_player_mode = False
        self.bot = None
        self.active_saw_blade = None
        self.current_round = 1
        self.round_result_message = ""
        self.round_lost = False
        self.round_victory = False
        self.state = GameState.MAIN_MENU
        self.status_msg = "Select HOST or enter a join code."
        if player1 is not None:
            player1.health = player1.max_health
            player1.shield = 100
            player1.attack_speed = 0.3
            player1.x, player1.y = 300, HEIGHT - 430
            player1.state = "idle"
        if player2 is not None:
            player2.health = player2.max_health if hasattr(player2, "max_health") else 100
            player2.shield = 100
            player2.x, player2.y = WIDTH - 300, HEIGHT - 430
            player2.state = "idle"

    def _draw_how_to_play(self, surface):
        # Full-screen scrollable instructional overlay
        try:
            from src.player import (
                left_walk_frames, left_attack_frames, left_defend_frames, left_jump_frames,
                right_walk_frames, right_attack_frames, right_defend_frames, right_jump_frames
            )
        except Exception:
            left_walk_frames = left_attack_frames = left_defend_frames = left_jump_frames = None
            right_walk_frames = right_attack_frames = right_defend_frames = right_jump_frames = None

        surface.fill((30, 30, 35))

        title = MENU_FONT.render("HOW TO PLAY — COMPLETE GUIDE", True, (245, 245, 245))
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        # ========== CONTROLS SECTION ==========
        subtitle = SMALL_FONT.render("BASIC CONTROLS", True, (255, 215, 0))
        surface.blit(subtitle, (50, 80))

        info_txt = SMALL_FONT.render("Left player: W A S D F R  |  Right player: ↑ ↓ ← → P O", True, (190, 190, 200))
        surface.blit(info_txt, (50, 115))

        card_w = 420
        card_h = 100
        gap = 8
        left_x = 50
        right_x = WIDTH - 50 - card_w
        top_y = 160

        left_actions = [
            ("W - JUMP", left_jump_frames[0] if left_jump_frames else None, "W"),
            ("S - DEFEND", left_defend_frames[0] if left_defend_frames else None, "S"),
            ("A - BACK WALK", left_walk_frames[0] if left_walk_frames else None, "A"),
            ("D - FORWARD WALK", left_walk_frames[-1] if left_walk_frames else None, "D"),
            ("F - ATTACK", left_attack_frames[3] if left_attack_frames and len(left_attack_frames) > 3 else (left_attack_frames[-1] if left_attack_frames else None), "F"),
        ]

        right_actions = [
            ("UP - JUMP", right_jump_frames[0] if right_jump_frames else None, "↑"),
            ("DOWN - DEFEND", right_defend_frames[0] if right_defend_frames else None, "↓"),
            ("LEFT - BACK WALK", right_walk_frames[0] if right_walk_frames else None, "←"),
            ("RIGHT - FORWARD WALK", right_walk_frames[-1] if right_walk_frames else None, "→"),
            ("P - ATTACK", right_attack_frames[3] if right_attack_frames and len(right_attack_frames) > 3 else (right_attack_frames[-1] if right_attack_frames else None), "P"),
        ]

        for idx, (text, frame_surf, key_text) in enumerate(left_actions):
            card_y = top_y + idx * (card_h + gap)
            rect = pygame.Rect(left_x, card_y, card_w, card_h)
            draw_instruction_card(surface, rect, frame_surf or pygame.Surface((1, 1), pygame.SRCALPHA), text, key_text)

        for idx, (text, frame_surf, key_text) in enumerate(right_actions):
            card_y = top_y + idx * (card_h + gap)
            rect = pygame.Rect(right_x, card_y, card_w, card_h)
            draw_instruction_card(surface, rect, frame_surf or pygame.Surface((1, 1), pygame.SRCALPHA), text, key_text)

        # ========== SPECIAL MOVE SECTION ==========
        special_y = top_y + len(left_actions) * (card_h + gap) + 30

        special_title = SMALL_FONT.render("SPECIAL MOVE - SAW BLADE", True, (255, 215, 0))
        surface.blit(special_title, (50, special_y))

        special_info = [
            "• Build Special Meter by landing attacks on opponent",
            "• When meter is full (golden bar shows 'READY'), press R (left) or O (right)",
            "• Unleash a spinning saw blade that damages the opponent",
            "• 5 second cooldown after use - plan your special moves wisely!"
        ]

        special_text_y = special_y + 35
        for line in special_info:
            line_surf = pygame.font.SysFont("Arial", 16, bold=False).render(line, True, (200, 200, 210))
            surface.blit(line_surf, (70, special_text_y))
            special_text_y += 28

        # ========== MULTIPLAYER (LAN) SECTION ==========
        mp_y = special_text_y + 30

        mp_title = SMALL_FONT.render("ONLINE MULTIPLAYER (LAN)", True, (255, 215, 0))
        surface.blit(mp_title, (50, mp_y))

        mp_steps = [
            "1. SELECT 'MULTIPLAYER (LAN)' FROM MAIN MENU",
            "2. HOST: Click 'HOST GAME ROOM' - you'll get a 6-digit code",
            "3. CLIENT: Click input box, enter the 6-digit code from host",
            "4. BOTH MUST BE ON THE SAME WiFi NETWORK",
            "5. After client joins, game starts - host is left player, client is right",
            "6. Note: For LAN on different machines, modify host IP in network settings"
        ]

        mp_text_y = mp_y + 35
        for step in mp_steps:
            step_surf = pygame.font.SysFont("Arial", 16, bold=False).render(step, True, (200, 200, 210))
            surface.blit(step_surf, (70, mp_text_y))
            mp_text_y += 26

        # ========== ATTACK & DEFEND MECHANICS ==========
        mechanics_y = mp_text_y + 30

        mech_title = SMALL_FONT.render("ATTACK & DEFEND MECHANICS", True, (255, 215, 0))
        surface.blit(mech_title, (50, mechanics_y))

        mech_info = [
            "ATTACK: Click F/P once and hold briefly - automatic swing takes ~0.3 seconds",
            "DEFEND: Click S/DOWN to toggle defend mode ON/OFF - stay locked in position",
            "SHIELD: Defend absorbs damage with a shield bar - use strategically",
            "⚠ IMPORTANT: Cannot attack or jump while already attacking. Plan ahead!"
        ]

        mech_text_y = mechanics_y + 35
        for info in mech_info:
            info_surf = pygame.font.SysFont("Arial", 16, bold=False).render(info, True, (200, 200, 210))
            surface.blit(info_surf, (70, mech_text_y))
            mech_text_y += 26

        footer = SMALL_FONT.render("CLICK TO GO TO MENU OR PRESS ESC", True, (200, 200, 200))
        surface.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 40))
