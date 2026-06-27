import pygame
import os
import random
from src.config import (
    WIDTH, HEIGHT, PAUSE_BUTTON_POS, PAUSE_BUTTON_RADIUS,
    MENU_RECT, MP_MENU_RECT, MP_HOST_BTN, MP_INPUT_BOX, MP_JOIN_BTN,
    MP_BACK_BTN, BG_MENU_RECT, BG_PREVIEW_SIZE, BG_SLIDE_LEFT_BTN,
    BG_SLIDE_RIGHT_BTN, BG_SELECT_BTN, BG_BACK_BTN, FONT, SMALL_FONT,
    MENU_FONT, AVATAR_PATH, BUTTON_WIDTH, BUTTON_HEIGHT,
    BUTTON_PADDING, BUTTON_BORDER_RADIUS,
)
from src.states import GameState
from src.player import set_background, available_backgrounds, current_bg_index

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

def draw_main_menu(surface, buttons):
    from src.player import menu_background

    surface.blit(menu_background, (0, 0))

    for btn_rect, label in buttons:
        mouse_pos = pygame.mouse.get_pos()
        bg_color = (40, 40, 55) if btn_rect.collidepoint(mouse_pos) else (15, 15, 22)

        btn_surf = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (*bg_color, 178), (0, 0, btn_rect.width, btn_rect.height), border_radius=BUTTON_BORDER_RADIUS)
        surface.blit(btn_surf, (btn_rect.x, btn_rect.y))

        txt = FONT.render(label, True, (255, 255, 255))
        surface.blit(txt, (btn_rect.centerx - txt.get_width() // 2, btn_rect.centery - txt.get_height() // 2))


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
        bg_color = (50, 50, 70) if opt_rect.collidepoint(mouse_pos) else (30, 30, 30)

        pygame.draw.rect(surface, bg_color, opt_rect, border_radius=8)
        txt = SMALL_FONT.render(opt, True, (255, 255, 255))
        surface.blit(txt, (opt_rect.centerx - txt.get_width() // 2, opt_rect.centery - txt.get_height() // 2))

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

    left_color = (80, 80, 100) if BG_SLIDE_LEFT_BTN.collidepoint(mouse_pos) else (30, 30, 35)
    right_color = (80, 80, 100) if BG_SLIDE_RIGHT_BTN.collidepoint(mouse_pos) else (30, 30, 35)
    select_color = (0, 150, 200) if BG_SELECT_BTN.collidepoint(mouse_pos) else (0, 100, 150)
    back_color = (150, 40, 40) if BG_BACK_BTN.collidepoint(mouse_pos) else (100, 20, 20)

    pygame.draw.rect(surface, left_color, BG_SLIDE_LEFT_BTN, border_radius=8)
    pygame.draw.rect(surface, right_color, BG_SLIDE_RIGHT_BTN, border_radius=8)
    pygame.draw.rect(surface, select_color, BG_SELECT_BTN, border_radius=10)
    pygame.draw.rect(surface, back_color, BG_BACK_BTN, border_radius=10)

    lbl_l = FONT.render("<", True, (255, 255, 255))
    lbl_r = FONT.render(">", True, (255, 255, 255))
    lbl_s = FONT.render("APPLY BACKGROUND", True, (255, 255, 255))
    lbl_b = SMALL_FONT.render("SAVE & RETURN", True, (255, 255, 255))

    surface.blit(lbl_l, (BG_SLIDE_LEFT_BTN.centerx - lbl_l.get_width() // 2, BG_SLIDE_LEFT_BTN.centery - lbl_l.get_height() // 2))
    surface.blit(lbl_r, (BG_SLIDE_RIGHT_BTN.centerx - lbl_r.get_width() // 2, BG_SLIDE_RIGHT_BTN.centery - lbl_r.get_height() // 2))
    surface.blit(lbl_s, (BG_SELECT_BTN.centerx - lbl_s.get_width() // 2, BG_SELECT_BTN.centery - lbl_s.get_height() // 2))
    surface.blit(lbl_b, (BG_BACK_BTN.centerx - lbl_b.get_width() // 2, BG_BACK_BTN.centery - lbl_b.get_height() // 2))

def draw_multiplayer_menu(surface, room_code, input_text, is_active, status_msg):
    pygame.draw.rect(surface, (24, 24, 28), MP_MENU_RECT, border_radius=16)
    pygame.draw.rect(surface, (100, 100, 110), MP_MENU_RECT, width=3, border_radius=16)

    title = MENU_FONT.render("MULTIPLAYER SETUP", True, (255, 255, 255))
    surface.blit(title, (MP_MENU_RECT.centerx - title.get_width() // 2, MP_MENU_RECT.y + 40))

    mouse = pygame.mouse.get_pos()

    bg_h = (40, 80, 40) if MP_HOST_BTN.collidepoint(mouse) else (20, 50, 20)
    pygame.draw.rect(surface, bg_h, MP_HOST_BTN, border_radius=8)
    lbl_h = SMALL_FONT.render("HOST GAME ROOM", True, (255, 255, 255))
    surface.blit(lbl_h, (MP_HOST_BTN.centerx - lbl_h.get_width() // 2, MP_HOST_BTN.centery - lbl_h.get_height() // 2))

    bg_box = (40, 40, 45) if is_active else (25, 25, 28)
    border_c = (0, 180, 255) if is_active else (70, 70, 80)
    pygame.draw.rect(surface, bg_box, MP_INPUT_BOX, border_radius=8)
    pygame.draw.rect(surface, border_c, MP_INPUT_BOX, width=2, border_radius=8)

    txt_i = FONT.render(input_text if input_text else "ENTER ROOM CODE", True, (255, 255, 255) if input_text else (120, 120, 130))
    surface.blit(txt_i, (MP_INPUT_BOX.x + 15, MP_INPUT_BOX.centery - txt_i.get_height() // 2))

    if room_code:
        code_lbl = FONT.render(f"YOUR ROOM CODE: {room_code}", True, (255, 255, 100))
        surface.blit(code_lbl, (MP_MENU_RECT.centerx - code_lbl.get_width() // 2, MP_MENU_RECT.y + 260))

    status_lbl = SMALL_FONT.render(f"STATUS: {status_msg}", True, (0, 255, 255))
    surface.blit(status_lbl, (MP_MENU_RECT.centerx - status_lbl.get_width() // 2, MP_MENU_RECT.y + 340))

    bg_j = (40, 40, 80) if MP_JOIN_BTN.collidepoint(mouse) else (25, 25, 50)
    pygame.draw.rect(surface, bg_j, MP_JOIN_BTN, border_radius=8)
    lbl_j = SMALL_FONT.render("JOIN ROOM MATCH", True, (255, 255, 255))
    surface.blit(lbl_j, (MP_JOIN_BTN.centerx - lbl_j.get_width() // 2, MP_JOIN_BTN.centery - lbl_j.get_height() // 2))

    bg_b = (100, 30, 30) if MP_BACK_BTN.collidepoint(mouse) else (60, 20, 20)
    pygame.draw.rect(surface, bg_b, MP_BACK_BTN, border_radius=8)
    lbl_b = SMALL_FONT.render("BACK TO MENU", True, (255, 255, 255))
    surface.blit(lbl_b, (MP_BACK_BTN.centerx - lbl_b.get_width() // 2, MP_BACK_BTN.centery - lbl_b.get_height() // 2))

def draw_health_bars(surface, hp1, sh1, hp2, sh2, name1="Player 1", name2="Player 2"):
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
    border_thickness = 3

    font_names = pygame.font.SysFont('Arial', 20, bold=True)
    text_n1 = font_names.render(name1, True, (255, 255, 255))
    text_n2 = font_names.render(name2, True, (255, 255, 255))
    surface.blit(text_n1, (p1_x, 14))
    surface.blit(text_n2, (p2_x + bar_w - text_n2.get_width(), 14))

    pygame.draw.rect(surface, (80, 20, 20), (p1_x, 42, bar_w, hp_h))
    p1_hp_w = int((max(0, min(hp1, 100)) / 100) * bar_w)
    pygame.draw.rect(surface, (230, 35, 35), (p1_x, 42, p1_hp_w, hp_h))
    pygame.draw.rect(surface, (0, 0, 0), (p1_x, 42, bar_w, hp_h), width=border_thickness)

    pygame.draw.rect(surface, (15, 40, 80), (p1_x, 86, bar_w, sh_h))
    p1_sh_w = int((max(0, min(sh1, 100)) / 100) * bar_w)
    pygame.draw.rect(surface, (35, 115, 245), (p1_x, 86, p1_sh_w, sh_h))
    pygame.draw.rect(surface, (0, 0, 0), (p1_x, 86, bar_w, sh_h), width=border_thickness)

    pygame.draw.rect(surface, (80, 20, 20), (p2_x, 42, bar_w, hp_h))
    p2_hp_w = int((max(0, min(hp2, 100)) / 100) * bar_w)
    pygame.draw.rect(surface, (230, 35, 35), (p2_x + (bar_w - p2_hp_w), 42, p2_hp_w, hp_h))
    pygame.draw.rect(surface, (0, 0, 0), (p2_x, 42, bar_w, hp_h), width=border_thickness)

    pygame.draw.rect(surface, (15, 40, 80), (p2_x, 86, bar_w, sh_h))
    p2_sh_w = int((max(0, min(sh2, 100)) / 100) * bar_w)
    pygame.draw.rect(surface, (35, 115, 245), (p2_x + (bar_w - p2_sh_w), 86, p2_sh_w, sh_h))
    pygame.draw.rect(surface, (0, 0, 0), (p2_x, 86, bar_w, sh_h), width=border_thickness)

def draw_fps_counter(surface, clock):
    fps_text = SMALL_FONT.render(f"FPS: {int(clock.get_fps())}", True, (0, 255, 0))
    surface.blit(fps_text, (20, HEIGHT - 40))

class UIManager:
    def __init__(self):
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

        self.background_index = current_bg_index

    def _build_main_menu_buttons(self):
        labels = [
            "LOCAL MATCH",
            "MULTIPLAYER (LAN)",
            "CHANGE BACKGROUND",
            "GAME OPTIONS",
            "EXIT GAME"
        ]
        small_w = int(BUTTON_WIDTH * 0.8)
        small_h = int(BUTTON_HEIGHT * 0.8)
        start_y = 350

        buttons = []
        for i, label in enumerate(labels):
            btn_x = WIDTH // 2 - small_w // 2
            btn_y = start_y + i * (small_h + BUTTON_PADDING)
            buttons.append((pygame.Rect(btn_x, btn_y, small_w, small_h), label))
        return buttons

    def handle_event(self, event, mouse_pos, player1, player2, net):
        if event.type == pygame.QUIT:
            return {"quit": True}

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == GameState.MAIN_MENU:
                result = self._handle_main_menu_click(mouse_pos)
                if result:
                    return result
            elif self.state == GameState.NAME_INPUT:
                self._handle_name_input_mouse(mouse_pos, player1, player2)
            elif self.state == GameState.MULTIPLAYER_MENU:
                self._handle_multiplayer_menu_mouse(mouse_pos, player1, player2, net)
            elif self.state == GameState.BACKGROUND_MENU:
                self._handle_background_menu_mouse(mouse_pos)
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
                if label == "LOCAL MATCH":
                    self.player1_name = "Player 1"
                    self.player2_name = "Player 2"
                    self.active_box = None
                    self.mp_role = None
                    self.generated_code = ""
                    self.inputted_code = ""
                    self.active_mp_input = False
                    self.status_msg = "Enter names and start your local duel."
                    self.state = GameState.NAME_INPUT
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
                elif label == "GAME OPTIONS":
                    self.state = GameState.OPTIONS
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

    def _handle_multiplayer_menu_mouse(self, mouse_pos, player1, player2, net):
        if MP_HOST_BTN.collidepoint(mouse_pos):
            self.mp_role = "HOST"
            self.generated_code = self._generate_room_code()
            if net.host_game(self.generated_code):
                self.status_msg = f"Hosting room {self.generated_code}. Waiting for client to connect."
            else:
                self.status_msg = "Unable to host room. Check the network broker."

        elif MP_INPUT_BOX.collidepoint(mouse_pos):
            self.active_mp_input = True
            self.mp_role = "CLIENT"
            self.player1_name = "Host (P1)"
            self.player2_name = "Client (P2)"
            self.status_msg = "Enter the 6-digit room code and press ENTER."

        elif MP_JOIN_BTN.collidepoint(mouse_pos):
            if self.active_mp_input:
                self._attempt_join(player1, player2, net)
            else:
                self.status_msg = "Select the code input field first."

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
            elif self.state == GameState.MULTIPLAYER_MENU:
                self.state = GameState.MAIN_MENU

        if self.state == GameState.GAME_OVER and event.key != pygame.K_ESCAPE:
            self.state = GameState.MAIN_MENU

    def _attempt_join(self, player1, player2, net):
        if len(self.inputted_code) != 6:
            self.status_msg = "Room code must be exactly 6 digits."
            return

        if net.join_game(self.inputted_code):
            self._reset_match(player1, player2)
            self.state = GameState.PLAYING
            self.status_msg = "Successfully joined. Starting match."
        else:
            self.status_msg = "Unable to join room. Check the code or broker."

    def _reset_match(self, player1, player2):
        player1.health, player1.shield = 100, 100
        player2.health, player2.shield = 100, 100
        player1.x, player1.y = 300, HEIGHT - 450
        player2.x, player2.y = WIDTH - 300, HEIGHT - 450
        player1.state, player2.state = "idle", "idle"

    def _generate_room_code(self):
        return f"{random.randint(100000, 999999)}"

    def update(self, player1, player2, net):
        if self.state == GameState.MULTIPLAYER_MENU and self.mp_role == "HOST" and net.connected:
            self.status_msg = "Client connected. Starting multiplayer match."
            self._reset_match(player1, player2)
            self.state = GameState.PLAYING

        if self.state == GameState.PLAYING and (player1.health < 1 or player2.health < 1):
            self.state = GameState.GAME_OVER

    def render(self, surface, mouse_pos, player1, player2, clock):
        if self.state == GameState.MAIN_MENU:
            draw_main_menu(surface, self.main_menu_buttons)
        elif self.state == GameState.NAME_INPUT:
            self._draw_name_input(surface, mouse_pos)
        elif self.state == GameState.MULTIPLAYER_MENU:
            self._draw_multiplayer_menu(surface)
        elif self.state == GameState.BACKGROUND_MENU:
            self._draw_background_menu(surface)
        else:
            self._draw_game_screen(surface, player1, player2)

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
        btn_hover = continue_btn.collidepoint(mouse_pos)
        btn_color = (40, 175, 95) if btn_hover else (30, 145, 75)
        pygame.draw.rect(surface, btn_color, continue_btn, border_radius=8)

        text_btn = font_btn.render("CONTINUE", True, (255, 255, 255))
        surface.blit(text_btn, text_btn.get_rect(center=continue_btn.center))

    def _draw_multiplayer_menu(self, surface):
        surface.fill((15, 15, 18))
        draw_multiplayer_menu(surface, self.generated_code if self.mp_role == "HOST" else "", self.inputted_code, self.active_mp_input, self.status_msg)

    def _draw_background_menu(self, surface):
        surface.fill((10, 10, 15))
        draw_background_changer_menu(surface, self.background_index)

    def _draw_game_screen(self, surface, player1, player2):
        from src.player import game_background

        surface.blit(game_background, (0, 0))
        player1.draw(surface, opponent_x=player2.x)
        player2.draw(surface, opponent_x=player1.x)
        draw_ui_elements(surface)
        draw_health_bars(surface, player1.health, player1.shield, player2.health, player2.shield, self.player1_name, self.player2_name)

        if self.state == GameState.PAUSED:
            draw_pause_menu(surface)
        elif self.state == GameState.OPTIONS:
            self._draw_options_overlay(surface)
        elif self.state == GameState.GAME_OVER:
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
        text_continue = font_footer.render("Press any key or click to return to Main Menu", True, (180, 180, 180))

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