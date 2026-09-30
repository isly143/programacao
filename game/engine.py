"""
Purble Bakery - Main Game Engine, States, Screens & Logic
"""
import os
import sys
import json
import time
import math
import pygame
from typing import Optional, Dict

from game.models import (
    Shape, Batter, Filling, Frosting, Topping, Cake, LevelConfig, LEVELS,
    generate_order, compare_cakes
)
from game.audio import AudioManager
from game.cake_renderer import CakeRenderer
from game.stations import ConveyorBelt, StationManager
import game.icons as icons
from game.ui import (
    Button, ParticleManager, FontManager, OrderTV,
    COLOR_BG_DARK, COLOR_PANEL, COLOR_PANEL_BORDER, COLOR_ACCENT,
    COLOR_ACCENT_HOVER, COLOR_GOLD, COLOR_GREEN, COLOR_RED, COLOR_BLUE,
    COLOR_TEXT_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED
)

# Game States
STATE_MENU = "menu"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_TUTORIAL = "tutorial"
STATE_VICTORY = "victory"
STATE_GAME_OVER = "game_over"

SAVE_FILE = "F:/isly/save_data.json"

class GameEngine:
    def __init__(self, screen_width: int = 1024, screen_height: int = 640):
        self.width = screen_width
        self.height = screen_height
        
        # Pygame Setup
        pygame.init()
        pygame.display.set_caption("Purble Bakery - Edição Comfy Cakes (Windows 7 Style)")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # Subsystems
        self.audio = AudioManager()
        self.cake_renderer = CakeRenderer()
        self.particle_mgr = ParticleManager()
        self.font_mgr = FontManager()
        
        # Conveyor & Stations
        self.conveyor_rect = pygame.Rect(260, 420, 740, 50)
        self.conveyor = ConveyorBelt(self.conveyor_rect, num_stations=5)
        self.station_mgr = StationManager(self.conveyor, LEVELS[0])
        
        # Order Monitor
        self.order_tv = OrderTV(pygame.Rect(20, 75, 220, 240))
        
        # Save Data (high scores & unlocked levels)
        self.save_data = self._load_save_data()
        
        # Current Game State
        self.state = STATE_MENU
        self.current_level_idx = 0
        self.current_config: LevelConfig = LEVELS[0]
        
        # In-Game Variables
        self.current_order: Optional[Cake] = None
        self.player_cake = Cake()
        self.cakes_completed = 0
        self.score = 0
        self.streak = 0
        self.lives = 3
        self.order_time_left = 60.0
        self.total_order_time = 60.0
        self.last_feedback = ""
        self.feedback_timer = 0.0
        self.feedback_is_error = False
        
        # Delivery & Trash Animation
        self.delivery_anim = 0.0 # slides off right
        self.trash_anim = 0.0 # drops into trash chute
        self.temp_anim_cake: Optional[Cake] = None
        
        # UI Buttons
        self._init_ui_buttons()
        
        # Start BGM
        self.audio.start_bgm()

    def _load_save_data(self) -> dict:
        default_data = {
            "unlocked_level": 1,
            "high_scores": {"1": 0, "2": 0, "3": 0, "4": 0},
            "stars": {"1": 0, "2": 0, "3": 0, "4": 0}
        }
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return default_data

    def _save_save_data(self):
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.save_data, f, indent=2)
        except Exception as e:
            print("Failed to save progress:", e)

    def _init_ui_buttons(self):
        # 1. Menu Buttons
        btn_cx = self.width // 2
        self.btn_menu_play = Button(pygame.Rect(btn_cx - 120, 280, 240, 48), "JOGAR", bg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=(255, 255, 255), font_size=22)
        self.btn_menu_levels = Button(pygame.Rect(btn_cx - 120, 340, 240, 44), "SELECIONAR FASE", bg_color=(240, 240, 250), font_size=18)
        self.btn_menu_tutorial = Button(pygame.Rect(btn_cx - 120, 396, 240, 44), "COMO JOGAR", bg_color=(240, 240, 250), font_size=18)
        self.btn_menu_quit = Button(pygame.Rect(btn_cx - 120, 452, 240, 44), "SAIR DO JOGO", bg_color=(240, 240, 250), font_size=18)
        
        # 2. Gameplay Controls (Bottom bar)
        self.btn_prev_station = Button(pygame.Rect(260, 575, 110, 40), "VOLTAR", icon="arrow_left", bg_color=(220, 225, 235), font_size=13)
        self.btn_next_station = Button(pygame.Rect(380, 575, 110, 40), "AVANÇAR", icon="arrow_right", bg_color=(220, 225, 235), font_size=13)
        self.btn_add_tier = Button(pygame.Rect(500, 575, 130, 40), "+ NOVO ANDAR", bg_color=(255, 230, 160), hover_color=(255, 245, 180), font_size=14)
        self.btn_trash = Button(pygame.Rect(640, 575, 120, 40), "DESCARTAR", icon="trash", bg_color=(255, 200, 200), hover_color=(255, 220, 220), font_size=13)
        self.btn_deliver = Button(pygame.Rect(770, 570, 230, 50), "ENTREGAR BOLO", icon="deliver_star", bg_color=COLOR_GREEN, hover_color=(60, 225, 130), text_color=(255, 255, 255), font_size=16)
        
        # Top HUD Controls
        self.btn_hud_pause = Button(pygame.Rect(self.width - 50, 10, 40, 40), "", icon="pause", bg_color=(255, 255, 255))
        self.btn_hud_sound = Button(pygame.Rect(self.width - 100, 10, 40, 40), "", icon="sound", bg_color=(255, 255, 255))
        
        # Pause Screen Buttons
        self.btn_pause_resume = Button(pygame.Rect(btn_cx - 100, 260, 200, 45), "CONTINUAR", bg_color=COLOR_GREEN, text_color=(255, 255, 255), font_size=18)
        self.btn_pause_restart = Button(pygame.Rect(btn_cx - 100, 320, 200, 45), "REINICIAR FASE", bg_color=(240, 240, 250), font_size=16)
        self.btn_pause_menu = Button(pygame.Rect(btn_cx - 100, 380, 200, 45), "MENU PRINCIPAL", bg_color=(240, 240, 250), font_size=16)
        
        # Tutorial Close Button
        self.btn_tutorial_back = Button(pygame.Rect(btn_cx - 100, 560, 200, 45), "ENTENDI! VOLTAR", bg_color=COLOR_ACCENT, text_color=(255, 255, 255), font_size=16)
        
        # Victory / Game Over Buttons
        self.btn_modal_next = Button(pygame.Rect(btn_cx - 110, 420, 220, 45), "PRÓXIMA FASE", icon="arrow_right", bg_color=COLOR_GREEN, text_color=(255, 255, 255), font_size=18)
        self.btn_modal_retry = Button(pygame.Rect(btn_cx - 110, 475, 220, 40), "TENTAR NOVAMENTE", bg_color=(240, 240, 250), font_size=16)
        self.btn_modal_menu = Button(pygame.Rect(btn_cx - 110, 525, 220, 40), "MENU PRINCIPAL", bg_color=(240, 240, 250), font_size=16)

    def start_level(self, level_index: int):
        self.current_level_idx = max(0, min(len(LEVELS) - 1, level_index))
        self.current_config = LEVELS[self.current_level_idx]
        self.station_mgr.set_level_config(self.current_config)
        
        self.cakes_completed = 0
        self.score = 0
        self.streak = 0
        self.lives = 3
        self.last_feedback = ""
        self.feedback_timer = 0.0
        
        self.player_cake = Cake()
        self.conveyor.move_to_station(0)
        self._spawn_next_order()
        self.state = STATE_PLAYING

    def _spawn_next_order(self):
        self.current_order = generate_order(self.current_config)
        self.total_order_time = float(self.current_config.time_limit_sec)
        self.order_time_left = self.total_order_time

    def run(self):
        while self.is_running:
            dt = self.clock.tick(60) / 1000.0 # Delta time in seconds
            dt = min(dt, 0.1) # clamp against huge lag spikes
            
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                    elif self.state in (STATE_LEVEL_SELECT, STATE_TUTORIAL):
                        self.state = STATE_MENU

            # Handle State-Specific Events
            if self.state == STATE_MENU:
                if self.btn_menu_play.handle_event(event, self.audio):
                    self.start_level(self.save_data.get("unlocked_level", 1) - 1)
                elif self.btn_menu_levels.handle_event(event, self.audio):
                    self.state = STATE_LEVEL_SELECT
                elif self.btn_menu_tutorial.handle_event(event, self.audio):
                    self.state = STATE_TUTORIAL
                elif self.btn_menu_quit.handle_event(event, self.audio):
                    self.is_running = False

            elif self.state == STATE_LEVEL_SELECT:
                # Handled in custom click detection
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self._handle_level_select_click(event.pos)

            elif self.state == STATE_PLAYING:
                self._handle_gameplay_events(event)

            elif self.state == STATE_PAUSED:
                if self.btn_pause_resume.handle_event(event, self.audio):
                    self.state = STATE_PLAYING
                elif self.btn_pause_restart.handle_event(event, self.audio):
                    self.start_level(self.current_level_idx)
                elif self.btn_pause_menu.handle_event(event, self.audio):
                    self.state = STATE_MENU

            elif self.state == STATE_TUTORIAL:
                if self.btn_tutorial_back.handle_event(event, self.audio):
                    self.state = STATE_MENU

            elif self.state in (STATE_VICTORY, STATE_GAME_OVER):
                if self.state == STATE_VICTORY and self.btn_modal_next.handle_event(event, self.audio):
                    if self.current_level_idx < len(LEVELS) - 1:
                        self.start_level(self.current_level_idx + 1)
                    else:
                        self.state = STATE_MENU
                elif self.btn_modal_retry.handle_event(event, self.audio):
                    self.start_level(self.current_level_idx)
                elif self.btn_modal_menu.handle_event(event, self.audio):
                    self.state = STATE_MENU

    def _handle_gameplay_events(self, event):
        # HUD buttons
        if self.btn_hud_pause.handle_event(event, self.audio):
            self.state = STATE_PAUSED
            return
        if self.btn_hud_sound.handle_event(event, self.audio):
            muted = self.audio.toggle_mute()
            self.btn_hud_sound.icon_state = muted
            return
            
        # Conveyor Buttons
        if self.btn_prev_station.handle_event(event, self.audio):
            self.conveyor.move_prev(self.audio)
            return
        if self.btn_next_station.handle_event(event, self.audio):
            self.conveyor.move_next(self.audio)
            return
        if self.btn_add_tier.handle_event(event, self.audio):
            self._action_add_tier()
            return
        if self.btn_trash.handle_event(event, self.audio):
            self._action_trash_cake()
            return
        if self.btn_deliver.handle_event(event, self.audio):
            self._action_deliver_cake()
            return

        # Station actions
        station_action = self.station_mgr.handle_event(event, self.audio)
        if station_action:
            station_id, action_type, val = station_action
            self._apply_station_action(station_id, action_type, val)

    def _apply_station_action(self, station_id: int, action_type: str, val: str):
        # Move conveyor automatically to that station!
        self.conveyor.move_to_station(station_id, self.audio)
        st = self.station_mgr.stations[station_id]
        
        if action_type == "pan":
            self.player_cake.apply_pan(val)
            st.trigger_dispense((190, 195, 205))
            self.audio.play("dispense_pan")
            self.particle_mgr.spawn_confetti(self.conveyor.station_x_coords[0], 430, count=10)
            
        elif action_type == "batter":
            if self.player_cake.apply_batter(val):
                color = Batter.COLORS.get(val, (240, 220, 140))
                st.trigger_dispense(color)
                self.audio.play("dispense_batter")
                self.particle_mgr.spawn_confetti(self.conveyor.station_x_coords[1], 430, count=15)
            else:
                self._show_feedback("Coloque a forma primeiro!", is_error=True)
                
        elif action_type == "filling":
            if self.player_cake.apply_filling(val):
                color = Filling.COLORS.get(val, (255, 255, 255))
                st.trigger_dispense(color)
                self.audio.play("dispense_filling")
                self.particle_mgr.spawn_confetti(self.conveyor.station_x_coords[2], 430, count=15)
            else:
                self._show_feedback("Asse a massa antes do recheio!", is_error=True)
                
        elif action_type == "frosting":
            if self.player_cake.apply_frosting(val):
                color = Frosting.COLORS.get(val, (255, 255, 255))
                st.trigger_dispense(color)
                self.audio.play("dispense_frosting")
                self.particle_mgr.spawn_confetti(self.conveyor.station_x_coords[3], 430, count=15)
            else:
                self._show_feedback("Coloque a massa primeiro!", is_error=True)
                
        elif action_type == "topping":
            if self.player_cake.apply_topping(val):
                st.trigger_dispense((255, 80, 100))
                self.audio.play("dispense_topping")
                self.particle_mgr.spawn_confetti(self.conveyor.station_x_coords[4], 400, count=18)
            else:
                self._show_feedback("Coloque a massa antes do confeito!", is_error=True)

    def _action_add_tier(self):
        if self.current_config.max_tiers <= 1:
            self._show_feedback("Esta fase permite apenas 1 andar.", is_error=True)
            return
        if self.player_cake.add_tier(self.current_config.max_tiers):
            self.audio.play("dispense_pan")
            tier_num = len(self.player_cake.layers)
            self._show_feedback(f"Andar {tier_num} adicionado! Agora escolha a massa.", is_error=False)
            self.particle_mgr.add_floating_text(f"Andar {tier_num}!", int(self.conveyor.cake_x), 350, COLOR_GOLD, 26)
        else:
            self._show_feedback("Termine o andar atual antes de empilhar!", is_error=True)

    def _action_trash_cake(self):
        if self.player_cake.is_empty():
            self._show_feedback("O prato já está vazio.", is_error=False)
            return
        self.audio.play("trash")
        self.player_cake.clear()
        self.conveyor.move_to_station(0)
        self._show_feedback("Bolo descartado. Novo prato pronto!", is_error=False)
        self.particle_mgr.add_floating_text("Descartado!", int(self.conveyor.cake_x), 400, COLOR_RED, 22)

    def _action_deliver_cake(self):
        if self.player_cake.is_empty():
            self._show_feedback("Você precisa montar um bolo antes de entregar!", is_error=True)
            return

        is_match, score_awarded, errors = compare_cakes(self.current_order, self.player_cake)
        
        if is_match:
            # Correct Cake!
            self.audio.play("correct")
            self.streak += 1
            streak_bonus = (self.streak - 1) * 150
            speed_bonus = int((self.order_time_left / self.total_order_time) * 300)
            total_earned = self.current_config.points_per_cake + streak_bonus + speed_bonus
            self.score += total_earned
            self.cakes_completed += 1
            
            txt = f"+{total_earned} PTS!"
            if self.streak > 1:
                txt += f" (Combo x{self.streak})"
            self.particle_mgr.add_floating_text(txt, int(self.conveyor.cake_x), 320, COLOR_GREEN, 28)
            self.particle_mgr.spawn_confetti(int(self.conveyor.cake_x), 380, count=60)
            self._show_feedback("BOLO PERFEITO! O cliente adorou!", is_error=False)
            
            # Check Level Complete
            if self.cakes_completed >= self.current_config.target_cakes:
                self._trigger_level_victory()
                return
            else:
                self.player_cake.clear()
                self.conveyor.move_to_station(0)
                self._spawn_next_order()
                
        else:
            # Wrong Cake!
            self.audio.play("wrong")
            self.streak = 0
            self.lives -= 1
            err_msg = errors[0] if errors else "O bolo não condiz com o pedido!"
            self._show_feedback(f"Erro: {err_msg}", is_error=True)
            self.particle_mgr.add_floating_text("ERRADO!", int(self.conveyor.cake_x), 340, COLOR_RED, 26)
            
            if self.lives <= 0:
                self._trigger_game_over()
            else:
                self.player_cake.clear()
                self.conveyor.move_to_station(0)

    def _trigger_level_victory(self):
        self.audio.play("level_win")
        self.state = STATE_VICTORY
        self.particle_mgr.spawn_confetti(self.width // 2, 200, count=120)
        
        # Update high score and unlocked level
        lvl_key = str(self.current_level_idx + 1)
        cur_high = self.save_data["high_scores"].get(lvl_key, 0)
        if self.score > cur_high:
            self.save_data["high_scores"][lvl_key] = self.score
            
        # Compute stars (1 to 3)
        stars = 3 if self.lives == 3 else (2 if self.lives == 2 else 1)
        self.save_data["stars"][lvl_key] = max(self.save_data["stars"].get(lvl_key, 0), stars)
        
        # Unlock next level
        if self.current_level_idx + 2 > self.save_data.get("unlocked_level", 1):
            self.save_data["unlocked_level"] = min(len(LEVELS), self.current_level_idx + 2)
            
        self._save_save_data()

    def _trigger_game_over(self):
        self.state = STATE_GAME_OVER

    def _show_feedback(self, text: str, is_error: bool = False):
        self.last_feedback = text
        self.feedback_timer = 3.0
        self.feedback_is_error = is_error

    def _update(self, dt: float):
        self.cake_renderer.update_animations(dt)
        self.particle_mgr.update(dt)
        
        if self.feedback_timer > 0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)

        # Update hover for UI buttons
        mouse_pos = pygame.mouse.get_pos()
        for btn in [self.btn_menu_play, self.btn_menu_levels, self.btn_menu_tutorial, self.btn_menu_quit,
                    self.btn_prev_station, self.btn_next_station, self.btn_add_tier, self.btn_trash, self.btn_deliver,
                    self.btn_hud_pause, self.btn_hud_sound, self.btn_pause_resume, self.btn_pause_restart,
                    self.btn_pause_menu, self.btn_tutorial_back, self.btn_modal_next, self.btn_modal_retry,
                    self.btn_modal_menu]:
            btn.check_hover(mouse_pos)

        if self.state == STATE_PLAYING:
            self.conveyor.update(dt)
            self.station_mgr.update(dt)
            
            # Update Add Tier button visibility/enabled state
            self.btn_add_tier.visible = (self.current_config.max_tiers > 1)
            
            # Timer countdown
            if self.total_order_time > 0:
                self.order_time_left -= dt
                if self.order_time_left <= 0:
                    # Time out on this cake!
                    self.audio.play("wrong")
                    self.lives -= 1
                    self.streak = 0
                    self._show_feedback("Tempo esgotado! O cliente foi embora chateado.", is_error=True)
                    self.particle_mgr.add_floating_text("TEMPO ESGOTADO!", 130, 200, COLOR_RED, 22)
                    if self.lives <= 0:
                        self._trigger_game_over()
                    else:
                        self.player_cake.clear()
                        self.conveyor.move_to_station(0)
                        self._spawn_next_order()

    def _draw(self):
        # Draw background kitchen
        self._draw_bakery_background()

        if self.state == STATE_MENU:
            self._draw_menu_screen()
        elif self.state == STATE_LEVEL_SELECT:
            self._draw_level_select_screen()
        elif self.state == STATE_TUTORIAL:
            self._draw_tutorial_screen()
        elif self.state in (STATE_PLAYING, STATE_PAUSED, STATE_VICTORY, STATE_GAME_OVER):
            self._draw_gameplay_screen()
            if self.state == STATE_PAUSED:
                self._draw_pause_overlay()
            elif self.state == STATE_VICTORY:
                self._draw_victory_modal()
            elif self.state == STATE_GAME_OVER:
                self._draw_game_over_modal()

        # Draw floating particles on top of everything
        self.particle_mgr.draw(self.screen, self.font_mgr)

    def _draw_bakery_background(self):
        # Pastel bakery wallpaper (stripes)
        self.screen.fill((250, 240, 235))
        for x in range(0, self.width, 40):
            pygame.draw.rect(self.screen, (243, 230, 225), (x, 0, 20, self.height))
            
        # Kitchen counter floor tiles at bottom
        counter_top = 400
        pygame.draw.rect(self.screen, (215, 205, 195), (0, counter_top, self.width, self.height - counter_top))
        # Checkered floor tiles
        tile_size = 30
        for tx in range(0, self.width, tile_size):
            for ty in range(counter_top, self.height, tile_size):
                if ((tx // tile_size) + (ty // tile_size)) % 2 == 0:
                    pygame.draw.rect(self.screen, (205, 195, 185), (tx, ty, tile_size, tile_size))
        pygame.draw.line(self.screen, (160, 150, 140), (0, counter_top), (self.width, counter_top), 3)

    def _draw_menu_screen(self):
        cx = self.width // 2
        
        # Logo Card
        logo_rect = pygame.Rect(cx - 280, 50, 560, 190)
        pygame.draw.rect(self.screen, COLOR_PANEL, logo_rect, border_radius=20)
        pygame.draw.rect(self.screen, COLOR_ACCENT, logo_rect, width=4, border_radius=20)
        
        # Title Text
        f_main = self.font_mgr.get_font(42, bold=True)
        txt_main = f_main.render("PURBLE BAKERY", True, (230, 60, 110))
        self.screen.blit(txt_main, (cx - txt_main.get_width()//2, 70))
        
        f_sub = self.font_mgr.get_font(20, bold=True)
        txt_sub = f_sub.render("Fábrica de Bolos - Clássico Comfy Cakes", True, (90, 70, 85))
        self.screen.blit(txt_sub, (cx - txt_sub.get_width()//2, 130))
        
        f_info = self.font_mgr.get_font(15)
        txt_info = f_info.render("Reviva a magia dos bolos do Purble Place em 4 fases deliciosas!", True, COLOR_TEXT_MUTED)
        self.screen.blit(txt_info, (cx - txt_info.get_width()//2, 175))

        # Menu Buttons
        self.btn_menu_play.draw(self.screen, self.font_mgr)
        self.btn_menu_levels.draw(self.screen, self.font_mgr)
        self.btn_menu_tutorial.draw(self.screen, self.font_mgr)
        self.btn_menu_quit.draw(self.screen, self.font_mgr)
        
        # Version footer
        f_foot = self.font_mgr.get_font(13)
        txt_foot = f_foot.render("Projeto Python - F:\\isly | 4 Fases com Dificuldade Progressiva", True, (150, 140, 145))
        self.screen.blit(txt_foot, (cx - txt_foot.get_width()//2, self.height - 30))

    def _draw_level_select_screen(self):
        cx = self.width // 2
        
        # Header
        f_title = self.font_mgr.get_font(32, bold=True)
        txt = f_title.render("SELECIONE A FASE", True, (70, 50, 65))
        self.screen.blit(txt, (cx - txt.get_width()//2, 35))
        
        # 4 Level Cards
        unlocked = self.save_data.get("unlocked_level", 1)
        card_w, card_h = 220, 360
        start_x = 45
        spacing = 240
        
        for i, lvl in enumerate(LEVELS):
            x = start_x + i * spacing
            y = 110
            card_rect = pygame.Rect(x, y, card_w, card_h)
            is_unlocked = (i + 1) <= unlocked
            
            # Card Background
            bg_col = (255, 255, 255) if is_unlocked else (225, 225, 230)
            pygame.draw.rect(self.screen, bg_col, card_rect, border_radius=16)
            border_col = COLOR_ACCENT if is_unlocked else (180, 180, 185)
            pygame.draw.rect(self.screen, border_col, card_rect, width=3, border_radius=16)
            
            # Level Number Badge
            badge_rect = pygame.Rect(x + 20, y + 15, card_w - 40, 36)
            badge_col = COLOR_ACCENT if is_unlocked else (160, 160, 165)
            pygame.draw.rect(self.screen, badge_col, badge_rect, border_radius=8)
            f_num = self.font_mgr.get_font(16, bold=True)
            txt_num = f_num.render(f"FASE {lvl.level_num}", True, (255, 255, 255))
            self.screen.blit(txt_num, (badge_rect.centerx - txt_num.get_width()//2, badge_rect.centery - txt_num.get_height()//2))
            
            # Level Title
            f_ltitle = self.font_mgr.get_font(15, bold=True)
            short_title = lvl.title.split(": ")[-1]
            txt_lt = f_ltitle.render(short_title, True, COLOR_TEXT_DARK if is_unlocked else COLOR_TEXT_MUTED)
            self.screen.blit(txt_lt, (x + card_w//2 - txt_lt.get_width()//2, y + 65))
            
            # Subtitle / Description
            f_sub = self.font_mgr.get_font(12)
            # Word wrap subtitle
            words = lvl.subtitle.split(" ")
            line1 = " ".join(words[:len(words)//2])
            line2 = " ".join(words[len(words)//2:])
            txt_s1 = f_sub.render(line1, True, COLOR_TEXT_MUTED)
            txt_s2 = f_sub.render(line2, True, COLOR_TEXT_MUTED)
            self.screen.blit(txt_s1, (x + card_w//2 - txt_s1.get_width()//2, y + 100))
            self.screen.blit(txt_s2, (x + card_w//2 - txt_s2.get_width()//2, y + 120))
            
            # Features icons / bullets
            f_feat = self.font_mgr.get_font(12, bold=True)
            tier_txt = f"> Andares: ate {lvl.max_tiers}"
            fill_txt = "> Recheio: " + ("Sim" if lvl.has_filling else "Nao")
            cakes_txt = f"> Meta: {lvl.target_cakes} bolos"
            time_txt = f"> Tempo: {lvl.time_limit_sec}s/bolo"
            
            self.screen.blit(f_feat.render(tier_txt, True, (80, 80, 90)), (x + 20, y + 160))
            self.screen.blit(f_feat.render(fill_txt, True, (80, 80, 90)), (x + 20, y + 185))
            self.screen.blit(f_feat.render(cakes_txt, True, (80, 80, 90)), (x + 20, y + 210))
            self.screen.blit(f_feat.render(time_txt, True, (80, 80, 90)), (x + 20, y + 235))
            
            # Stars & High Score
            lvl_key = str(lvl.level_num)
            stars_count = self.save_data["stars"].get(lvl_key, 0)
            star_start_x = x + card_w//2 - 32
            for s_idx in range(3):
                is_filled = (s_idx < stars_count) if is_unlocked else False
                icons.draw_star(self.screen, star_start_x + s_idx * 32, y + 275, radius=12, color=COLOR_GOLD if is_unlocked else (170, 170, 175), filled=is_filled)
            
            # Play / Locked Button
            btn_play_rect = pygame.Rect(x + 20, y + 305, card_w - 40, 38)
            if is_unlocked:
                pygame.draw.rect(self.screen, COLOR_GREEN, btn_play_rect, border_radius=8)
                f_p = self.font_mgr.get_font(15, bold=True)
                txt_p = f_p.render("JOGAR FASE", True, (255, 255, 255))
                self.screen.blit(txt_p, (btn_play_rect.centerx - txt_p.get_width()//2, btn_play_rect.centery - txt_p.get_height()//2))
            else:
                pygame.draw.rect(self.screen, (190, 190, 195), btn_play_rect, border_radius=8)
                icons.draw_lock(self.screen, btn_play_rect.centerx - 48, btn_play_rect.centery, size=14, color=(100, 100, 105))
                f_p = self.font_mgr.get_font(14, bold=True)
                txt_p = f_p.render("BLOQUEADO", True, (100, 100, 105))
                self.screen.blit(txt_p, (btn_play_rect.centerx - 30, btn_play_rect.centery - txt_p.get_height()//2))

        # Back Button at Bottom
        f_b = self.font_mgr.get_font(16, bold=True)
        txt_b = f_b.render("Pressione ESC para voltar ao Menu", True, COLOR_TEXT_MUTED)
        self.screen.blit(txt_b, (cx - txt_b.get_width()//2, self.height - 40))

    def _handle_level_select_click(self, mouse_pos):
        unlocked = self.save_data.get("unlocked_level", 1)
        card_w, card_h = 220, 360
        start_x = 45
        spacing = 240
        for i, lvl in enumerate(LEVELS):
            x = start_x + i * spacing
            y = 110
            btn_play_rect = pygame.Rect(x + 20, y + 305, card_w - 40, 38)
            if btn_play_rect.collidepoint(mouse_pos) and (i + 1) <= unlocked:
                self.audio.play("click")
                self.start_level(i)
                return

    def _draw_tutorial_screen(self):
        cx = self.width // 2
        
        panel_rect = pygame.Rect(cx - 380, 40, 760, 500)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect, border_radius=16)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, panel_rect, width=3, border_radius=16)
        
        f_title = self.font_mgr.get_font(26, bold=True)
        t_surf = f_title.render("COMO JOGAR - MANUAL DO CONFEITEIRO", True, (70, 50, 65))
        self.screen.blit(t_surf, (cx - t_surf.get_width()//2, 60))
        
        steps = [
            ("1. Olhe a TV de Pedidos:", "No canto esquerdo, o cliente mostra a foto do bolo que ele deseja com tempo limite."),
            ("2. Estação 1 - Formas:", "Escolha a forma correta (Quadrado, Redondo, Coração ou Estrela)."),
            ("3. Estação 2 - Massas:", "Derrame a massa do sabor pedido (Baunilha, Chocolate ou Morango)."),
            ("4. Estação 3 - Recheios:", "Adicione o recheio delicioso (Creme de Baunilha, Ganache ou Geleia)."),
            ("5. Estação 4 - Coberturas:", "Passe a cobertura por cima do bolo (Glacê Branco, Chocolate ou Rosa)."),
            ("6. Estação 5 - Confeitos:", "Finalize com o confeito pedido (Cereja, Morango, Estrela ou Vela)."),
            ("7. Bolos de 2 ou 3 Andares:", "Nas Fases 3 e 4, use o botão '+ NOVO ANDAR' para empilhar camadas!"),
            ("8. Entregar / Descartar:", "Clique em 'ENTREGAR BOLO' para pontuar, ou 'DESCARTAR' se errar algo."),
        ]
        
        f_s_title = self.font_mgr.get_font(15, bold=True)
        f_s_desc = self.font_mgr.get_font(13)
        
        sy = 110
        for st_title, st_desc in steps:
            t1 = f_s_title.render(st_title, True, COLOR_ACCENT)
            t2 = f_s_desc.render(st_desc, True, COLOR_TEXT_DARK)
            self.screen.blit(t1, (panel_rect.left + 30, sy))
            self.screen.blit(t2, (panel_rect.left + 230, sy))
            sy += 48
            
        self.btn_tutorial_back.draw(self.screen, self.font_mgr)

    def _draw_gameplay_screen(self):
        # 1. Top HUD Bar
        hud_rect = pygame.Rect(0, 0, self.width, 60)
        pygame.draw.rect(self.screen, (255, 255, 255), hud_rect)
        pygame.draw.line(self.screen, (220, 215, 225), (0, 60), (self.width, 60), 2)
        
        # Level Title
        f_lvl = self.font_mgr.get_font(18, bold=True)
        txt_lvl = f_lvl.render(self.current_config.title, True, (80, 50, 75))
        self.screen.blit(txt_lvl, (20, 18))
        
        # Score
        f_sc = self.font_mgr.get_font(18, bold=True)
        txt_sc = f_sc.render(f"PONTOS: {self.score}", True, (50, 60, 80))
        self.screen.blit(txt_sc, (380, 18))
        
        # Streak / Combo
        if self.streak > 1:
            icons.draw_flame(self.screen, 545, 30, size=18)
            f_st = self.font_mgr.get_font(15, bold=True)
            txt_st = f_st.render(f"COMBO x{self.streak}", True, (230, 90, 40))
            self.screen.blit(txt_st, (560, 20))
            
        # Lives (Vector Hearts)
        f_lv = self.font_mgr.get_font(16, bold=True)
        txt_lv = f_lv.render("Vidas:", True, (80, 70, 80))
        self.screen.blit(txt_lv, (700, 20))
        
        heart_start_x = 760
        for i in range(3):
            icons.draw_heart(self.screen, heart_start_x + i * 24, 30, size=18, 
                             color=COLOR_RED, filled=(i < self.lives))
        
        # HUD Buttons (Sound & Pause)
        self.btn_hud_sound.draw(self.screen, self.font_mgr)
        self.btn_hud_pause.draw(self.screen, self.font_mgr)

        # 2. Order TV Monitor (Top-Left)
        time_ratio = (self.order_time_left / max(1.0, self.total_order_time))
        self.order_tv.draw(self.screen, self.current_order, time_ratio, 
                           self.cake_renderer, self.font_mgr, 
                           self.cakes_completed, self.current_config.target_cakes)

        # 3. Dispenser Stations (Top-Right)
        self.station_mgr.draw(self.screen, self.font_mgr)

        # 4. Conveyor Belt
        self.conveyor.draw(self.screen)

        # 5. Render Active Cake on Conveyor Belt
        cake_draw_x = int(self.conveyor.cake_x)
        cake_draw_y = self.conveyor_rect.top + 28
        
        if not self.player_cake.is_empty():
            self.cake_renderer.draw_cake(self.screen, self.player_cake, cake_draw_x, cake_draw_y, scale=0.92)
        else:
            # Draw empty silver plate
            pygame.draw.ellipse(self.screen, (160, 165, 175), (cake_draw_x - 90, cake_draw_y - 25, 180, 45))
            pygame.draw.ellipse(self.screen, (220, 225, 235), (cake_draw_x - 85, cake_draw_y - 28, 170, 40))
            f_pl = self.font_mgr.get_font(12, bold=True)
            txt_pl = f_pl.render("Prato Vazio", True, (140, 145, 155))
            self.screen.blit(txt_pl, (cake_draw_x - txt_pl.get_width()//2, cake_draw_y - 15))

        # 6. Bottom Controls Bar
        pygame.draw.rect(self.screen, (245, 240, 248), (0, 560, self.width, 80))
        pygame.draw.line(self.screen, (215, 205, 220), (0, 560), (self.width, 560), 2)
        
        self.btn_prev_station.draw(self.screen, self.font_mgr)
        self.btn_next_station.draw(self.screen, self.font_mgr)
        if self.current_config.max_tiers > 1:
            self.btn_add_tier.draw(self.screen, self.font_mgr)
        self.btn_trash.draw(self.screen, self.font_mgr)
        self.btn_deliver.draw(self.screen, self.font_mgr)

        # 7. Feedback Notification Banner
        if self.feedback_timer > 0 and self.last_feedback:
            banner_col = (255, 230, 235) if self.feedback_is_error else (230, 255, 235)
            border_col = COLOR_RED if self.feedback_is_error else COLOR_GREEN
            text_col   = (180, 30, 30) if self.feedback_is_error else (20, 120, 40)
            
            f_fb = self.font_mgr.get_font(14, bold=True)
            txt_fb = f_fb.render(self.last_feedback, True, text_col)
            
            fb_rect = pygame.Rect(self.width//2 - txt_fb.get_width()//2 - 20, 335, txt_fb.get_width() + 40, 32)
            pygame.draw.rect(self.screen, banner_col, fb_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_col, fb_rect, width=2, border_radius=8)
            self.screen.blit(txt_fb, (fb_rect.centerx - txt_fb.get_width()//2, fb_rect.centery - txt_fb.get_height()//2))

    def _draw_pause_overlay(self):
        # Dark translucent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        cx = self.width // 2
        modal_rect = pygame.Rect(cx - 160, 180, 320, 280)
        pygame.draw.rect(self.screen, COLOR_PANEL, modal_rect, border_radius=16)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, modal_rect, width=3, border_radius=16)
        
        f_p = self.font_mgr.get_font(28, bold=True)
        txt_p = f_p.render("JOGO PAUSADO", True, (70, 50, 65))
        self.screen.blit(txt_p, (cx - txt_p.get_width()//2, 205))
        
        self.btn_pause_resume.draw(self.screen, self.font_mgr)
        self.btn_pause_restart.draw(self.screen, self.font_mgr)
        self.btn_pause_menu.draw(self.screen, self.font_mgr)

    def _draw_victory_modal(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        
        cx = self.width // 2
        modal_rect = pygame.Rect(cx - 200, 100, 400, 480)
        pygame.draw.rect(self.screen, COLOR_PANEL, modal_rect, border_radius=20)
        pygame.draw.rect(self.screen, COLOR_GOLD, modal_rect, width=4, border_radius=20)
        
        f_v = self.font_mgr.get_font(30, bold=True)
        txt_v = f_v.render("FASE CONCLUÍDA!", True, (230, 60, 110))
        self.screen.blit(txt_v, (cx - txt_v.get_width()//2, 130))
        
        # Star Rating (Vector Stars)
        stars = 3 if self.lives == 3 else (2 if self.lives == 2 else 1)
        v_star_start_x = cx - 44
        for s_idx in range(3):
            is_filled = (s_idx < stars)
            icons.draw_star(self.screen, v_star_start_x + s_idx * 44, 195, radius=18, color=COLOR_GOLD, filled=is_filled)
        
        # Score Breakdown
        f_sc = self.font_mgr.get_font(20, bold=True)
        txt_sc = f_sc.render(f"Pontuação Final: {self.score}", True, (50, 60, 80))
        self.screen.blit(txt_sc, (cx - txt_sc.get_width()//2, 245))
        
        f_meta = self.font_mgr.get_font(15)
        txt_meta = f_meta.render(f"Bolos Entregues: {self.cakes_completed} / {self.current_config.target_cakes}", True, COLOR_TEXT_MUTED)
        self.screen.blit(txt_meta, (cx - txt_meta.get_width()//2, 285))
        
        # Next / Menu Buttons
        if self.current_level_idx < len(LEVELS) - 1:
            self.btn_modal_next.draw(self.screen, self.font_mgr)
        else:
            icons.draw_trophy(self.screen, cx - 180, 430, size=24)
            icons.draw_trophy(self.screen, cx + 180, 430, size=24)
            f_all = self.font_mgr.get_font(16, bold=True)
            txt_all = f_all.render("Parabéns! Você zerou todas as fases!", True, COLOR_GREEN)
            self.screen.blit(txt_all, (cx - txt_all.get_width()//2, 420))
            
        self.btn_modal_retry.draw(self.screen, self.font_mgr)
        self.btn_modal_menu.draw(self.screen, self.font_mgr)

    def _draw_game_over_modal(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        
        cx = self.width // 2
        modal_rect = pygame.Rect(cx - 180, 140, 360, 420)
        pygame.draw.rect(self.screen, COLOR_PANEL, modal_rect, border_radius=20)
        pygame.draw.rect(self.screen, COLOR_RED, modal_rect, width=4, border_radius=20)
        
        f_go = self.font_mgr.get_font(30, bold=True)
        txt_go = f_go.render("FIM DE JOGO!", True, COLOR_RED)
        self.screen.blit(txt_go, (cx - txt_go.get_width()//2, 170))
        
        f_sub = self.font_mgr.get_font(16)
        txt_sub = f_sub.render("Você cometeu muitos erros nesta fase.", True, COLOR_TEXT_DARK)
        self.screen.blit(txt_sub, (cx - txt_sub.get_width()//2, 225))
        
        f_sc = self.font_mgr.get_font(18, bold=True)
        txt_sc = f_sc.render(f"Pontos Feitos: {self.score}", True, (80, 80, 90))
        self.screen.blit(txt_sc, (cx - txt_sc.get_width()//2, 270))
        
        self.btn_modal_retry.rect.centerx = cx
        self.btn_modal_retry.rect.top = 340
        self.btn_modal_retry.draw(self.screen, self.font_mgr)
        
        self.btn_modal_menu.rect.centerx = cx
        self.btn_modal_menu.rect.top = 395
        self.btn_modal_menu.draw(self.screen, self.font_mgr)
