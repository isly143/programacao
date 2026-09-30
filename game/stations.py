"""
Purble Bakery - Conveyor Belt & Interactive Dispenser Stations
"""
import math
import pygame
from typing import List, Optional, Dict
from game.models import (
    Shape, Batter, Filling, Frosting, Topping, Cake, LevelConfig
)
from game.ui import Button, COLOR_ACCENT, COLOR_GOLD, COLOR_GREEN, COLOR_RED, COLOR_TEXT_DARK

class Station:
    def __init__(self, station_id: int, name: str, icon_symbol: str, 
                 center_x: int, top_y: int, width: int = 130, height: int = 240):
        self.station_id = station_id
        self.name = name
        self.icon_symbol = icon_symbol
        self.center_x = center_x
        self.top_y = top_y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(center_x - width // 2, top_y, width, height)
        self.buttons: List[Button] = []
        self.is_active = True
        self.dispensing_anim = 0.0 # timer for dispenser nozzle animation
        self.active_color = (200, 200, 200)

    def trigger_dispense(self, color=(255, 200, 100)):
        self.dispensing_anim = 0.35 # 350ms anim
        self.active_color = color

    def update(self, dt: float):
        if self.dispensing_anim > 0:
            self.dispensing_anim = max(0.0, self.dispensing_anim - dt)
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.check_hover(mouse_pos)

    def handle_event(self, event, audio=None) -> Optional[tuple]:
        """Returns (action_type, value) if a button was clicked."""
        if not self.is_active:
            return None
        for btn in self.buttons:
            if btn.handle_event(event, audio):
                return getattr(btn, 'action_payload', None)
        return None

    def draw_machine(self, surface: pygame.Surface, font_manager, is_selected: bool):
        rx, ry, rw, rh = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        
        # Machine Canopy / Upper housing
        housing_color = (235, 230, 240) if self.is_active else (210, 210, 215)
        border_color = (160, 150, 170) if not is_selected else (255, 120, 160)
        
        # Upper dispenser tank
        tank_rect = pygame.Rect(rx + 6, ry + 4, rw - 12, 60)
        pygame.draw.rect(surface, (220, 215, 230), tank_rect, border_radius=10)
        pygame.draw.rect(surface, border_color, tank_rect, width=3 if is_selected else 2, border_radius=10)
        
        # Station Title
        f_title = font_manager.get_font(13, bold=True)
        txt = f_title.render(self.name, True, (60, 50, 70) if self.is_active else (140, 140, 145))
        surface.blit(txt, (self.center_x - txt.get_width()//2, ry + 8))
        
        # Machine pipe / nozzle at bottom of tank
        pipe_w = 20
        pipe_h = 30
        pipe_rect = pygame.Rect(self.center_x - pipe_w//2, ry + 64, pipe_w, pipe_h)
        pygame.draw.rect(surface, (140, 145, 160), pipe_rect)
        pygame.draw.rect(surface, (100, 105, 120), pipe_rect, width=2)
        
        # Dispensing squirt effect if active
        if self.dispensing_anim > 0:
            drip_len = int(80 * (1.0 - (self.dispensing_anim / 0.35)))
            drip_rect = pygame.Rect(self.center_x - 6, pipe_rect.bottom, 12, drip_len)
            pygame.draw.rect(surface, self.active_color, drip_rect, border_radius=4)
            pygame.draw.circle(surface, self.active_color, (self.center_x, pipe_rect.bottom + drip_len), 8)

        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface, font_manager)

class ConveyorBelt:
    def __init__(self, rect: pygame.Rect, num_stations: int = 5):
        self.rect = pygame.Rect(rect)
        self.num_stations = num_stations
        self.current_station_idx = 0 # 0 to num_stations-1
        self.cake_x = 0.0 # interpolated X position
        self.target_x = 0.0
        self.station_x_coords = []
        self.roller_offset = 0.0
        self.is_moving = False
        
        # Initialize station positions
        station_spacing = self.rect.width / (num_stations + 1)
        for i in range(num_stations):
            x = self.rect.left + int((i + 1) * station_spacing)
            self.station_x_coords.append(x)
            
        self.cake_x = float(self.station_x_coords[0])
        self.target_x = self.cake_x
        
        # Delivery hatch at far right & trash at far left
        self.trash_x = self.rect.left + 40
        self.deliver_x = self.rect.right - 40

    def move_to_station(self, station_idx: int, audio=None):
        station_idx = max(0, min(self.num_stations - 1, station_idx))
        if station_idx != self.current_station_idx:
            self.current_station_idx = station_idx
            self.target_x = float(self.station_x_coords[station_idx])
            self.is_moving = True
            if audio:
                audio.play("conveyor")

    def move_next(self, audio=None):
        if self.current_station_idx < self.num_stations - 1:
            self.move_to_station(self.current_station_idx + 1, audio)

    def move_prev(self, audio=None):
        if self.current_station_idx > 0:
            self.move_to_station(self.current_station_idx - 1, audio)

    def update(self, dt: float):
        # Smooth interpolation to target X
        dx = self.target_x - self.cake_x
        if abs(dx) > 1.0:
            speed = 900.0 * dt
            step = math.copysign(min(abs(dx), speed), dx)
            self.cake_x += step
            self.roller_offset += step * 0.8
            self.is_moving = True
        else:
            self.cake_x = self.target_x
            self.is_moving = False

    def draw(self, surface: pygame.Surface):
        # Conveyor Belt Frame
        belt_top = self.rect.top
        belt_h = self.rect.height
        
        # Mechanical rails
        pygame.draw.rect(surface, (70, 75, 85), self.rect, border_radius=6)
        
        # Belt Track (Dark rubber belt)
        track_rect = pygame.Rect(self.rect.left + 8, belt_top + 10, self.rect.width - 16, 28)
        pygame.draw.rect(surface, (35, 38, 45), track_rect)
        
        # Animated Belt Rollers / Grooves
        spacing = 24
        start_x = track_rect.left + (self.roller_offset % spacing)
        x = start_x
        while x < track_rect.right:
            if x >= track_rect.left:
                pygame.draw.line(surface, (55, 60, 72), (x, track_rect.top), (x, track_rect.bottom), 2)
            x += spacing
            
        # Metal side rims & rivets
        pygame.draw.rect(surface, (130, 135, 150), (self.rect.left, belt_top, self.rect.width, 8), border_radius=4)
        pygame.draw.rect(surface, (90, 95, 110), (self.rect.left, track_rect.bottom, self.rect.width, 12))
        
        # Rivet dots along rail
        for rx in range(self.rect.left + 16, self.rect.right - 10, 45):
            pygame.draw.circle(surface, (180, 185, 200), (rx, belt_top + 4), 2)
            pygame.draw.circle(surface, (180, 185, 200), (rx, track_rect.bottom + 6), 2)

class StationManager:
    def __init__(self, conveyor: ConveyorBelt, config: LevelConfig):
        self.conveyor = conveyor
        self.config = config
        self.stations: List[Station] = []
        self._build_stations()

    def set_level_config(self, config: LevelConfig):
        self.config = config
        self._build_stations()

    def _build_stations(self):
        self.stations.clear()
        coords = self.conveyor.station_x_coords
        
        # Station 0: Formas (Pans)
        st0 = Station(0, "1. FORMAS", "", coords[0], 100, width=120, height=270)
        pan_shapes = [
            (Shape.SQUARE, "Quadrado", (200, 205, 215)),
            (Shape.CIRCLE, "Redondo", (200, 205, 215)),
            (Shape.HEART, "Coração", (255, 180, 195)),
            (Shape.STAR, "Estrela", (255, 235, 150)),
        ]
        btn_y = st0.top_y + 100
        for shape_id, label, col in pan_shapes:
            if shape_id in self.config.shapes:
                btn = Button(pygame.Rect(st0.center_x - 52, btn_y, 104, 30), text=label,
                             bg_color=col, font_size=12)
                btn.action_payload = ("pan", shape_id)
                st0.buttons.append(btn)
                btn_y += 36
        self.stations.append(st0)

        # Station 1: Massas (Batters)
        st1 = Station(1, "2. MASSAS", "", coords[1], 100, width=120, height=270)
        batter_types = [
            (Batter.VANILLA, "Baunilha", (250, 235, 175)),
            (Batter.CHOCOLATE, "Chocolate", (160, 105, 75)),
            (Batter.STRAWBERRY, "Morango", (255, 180, 195)),
        ]
        btn_y = st1.top_y + 100
        for bat_id, label, col in batter_types:
            if bat_id in self.config.batters:
                txt_col = (255, 255, 255) if bat_id == Batter.CHOCOLATE else COLOR_TEXT_DARK
                btn = Button(pygame.Rect(st1.center_x - 52, btn_y, 104, 30), text=label,
                             bg_color=col, text_color=txt_col, font_size=12)
                btn.action_payload = ("batter", bat_id)
                st1.buttons.append(btn)
                btn_y += 36
        self.stations.append(st1)

        # Station 2: Recheios (Fillings)
        st2 = Station(2, "3. RECHEIOS", "", coords[2], 100, width=120, height=270)
        st2.is_active = self.config.has_filling
        if self.config.has_filling:
            fill_types = [
                (Filling.VANILLA, "Baunilha", (255, 250, 210)),
                (Filling.CHOCOLATE, "Ganache", (125, 75, 50)),
                (Filling.STRAWBERRY, "Geleia", (245, 90, 120)),
            ]
            btn_y = st2.top_y + 100
            for fill_id, label, col in fill_types:
                if fill_id in self.config.fillings:
                    txt_col = (255, 255, 255) if fill_id in (Filling.CHOCOLATE, Filling.STRAWBERRY) else COLOR_TEXT_DARK
                    btn = Button(pygame.Rect(st2.center_x - 52, btn_y, 104, 30), text=label,
                                 bg_color=col, text_color=txt_col, font_size=12)
                    btn.action_payload = ("filling", fill_id)
                    st2.buttons.append(btn)
                    btn_y += 36
        self.stations.append(st2)

        # Station 3: Coberturas (Glazes / Frosting)
        st3 = Station(3, "4. COBERTURAS", "", coords[3], 100, width=120, height=270)
        frost_types = [
            (Frosting.WHITE, "Glacê Branco", (255, 255, 255)),
            (Frosting.CHOCOLATE, "Chocolate", (110, 60, 40)),
            (Frosting.PINK, "Rosa Morango", (255, 170, 200)),
        ]
        btn_y = st3.top_y + 100
        for frost_id, label, col in frost_types:
            if frost_id in self.config.frostings:
                txt_col = (255, 255, 255) if frost_id == Frosting.CHOCOLATE else COLOR_TEXT_DARK
                btn = Button(pygame.Rect(st3.center_x - 52, btn_y, 104, 30), text=label,
                             bg_color=col, text_color=txt_col, font_size=12)
                btn.action_payload = ("frosting", frost_id)
                st3.buttons.append(btn)
                btn_y += 36
        self.stations.append(st3)

        # Station 4: Confeitos (Toppings)
        st4 = Station(4, "5. CONFEITOS", "", coords[4], 100, width=120, height=270)
        top_types = [
            (Topping.CHERRY, "Cereja", (255, 230, 235)),
            (Topping.STRAWBERRY, "Morango", (255, 215, 220)),
            (Topping.STAR, "Estrela", (255, 245, 180)),
            (Topping.CANDLE, "Vela", (210, 240, 255)),
        ]
        btn_y = st4.top_y + 100
        for top_id, label, col in top_types:
            if top_id in self.config.toppings:
                btn = Button(pygame.Rect(st4.center_x - 52, btn_y, 104, 30), text=label,
                             bg_color=col, font_size=12)
                btn.action_payload = ("topping", top_id)
                st4.buttons.append(btn)
                btn_y += 36
        self.stations.append(st4)

    def update(self, dt: float):
        for st in self.stations:
            st.update(dt)

    def handle_event(self, event, audio=None) -> Optional[tuple]:
        for st in self.stations:
            res = st.handle_event(event, audio)
            if res:
                return (st.station_id, *res)
        return None

    def draw(self, surface: pygame.Surface, font_manager):
        selected_idx = self.conveyor.current_station_idx
        for st in self.stations:
            st.draw_machine(surface, font_manager, is_selected=(st.station_id == selected_idx))
