"""
Purble Bakery - UI Components, Particle Effects, Order Display & Modals
"""
import math
import random
import pygame
from typing import List, Tuple, Optional, Callable
from game.models import Cake, Shape, Batter, Filling, Frosting, Topping, LevelConfig
import game.icons as icons

# Color Palette
COLOR_BG_DARK = (45, 30, 40)
COLOR_PANEL = (255, 245, 235)
COLOR_PANEL_BORDER = (210, 180, 160)
COLOR_ACCENT = (255, 105, 140) # Pastel Magenta/Pink
COLOR_ACCENT_HOVER = (255, 140, 170)
COLOR_GOLD = (255, 215, 0)
COLOR_TEXT_DARK = (50, 40, 45)
COLOR_TEXT_LIGHT = (255, 255, 255)
COLOR_TEXT_MUTED = (120, 110, 115)
COLOR_GREEN = (46, 204, 113)
COLOR_RED = (231, 76, 60)
COLOR_BLUE = (52, 152, 219)

class Button:
    def __init__(self, rect: pygame.Rect, text: str = "", icon: Optional[str] = None, 
                 icon_state: bool = False,
                 bg_color=(240, 240, 245), hover_color=(255, 255, 255), 
                 text_color=COLOR_TEXT_DARK, border_color=(190, 190, 200),
                 border_radius=8, font_size=18, tooltip=""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.icon = icon
        self.icon_state = icon_state # e.g. muted for sound
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.font_size = font_size
        self.tooltip = tooltip
        
        self.is_hovered = False
        self.is_pressed = False
        self.enabled = True
        self.visible = True
        self.scale_anim = 1.0

    def check_hover(self, mouse_pos) -> bool:
        if not self.enabled or not self.visible:
            self.is_hovered = False
            return False
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def handle_event(self, event, audio=None) -> bool:
        if not self.enabled or not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if audio:
                    audio.play("click")
                return True
            self.is_pressed = False
        return False

    def draw(self, surface: pygame.Surface, font_manager):
        if not self.visible:
            return
            
        color = self.hover_color if self.is_hovered and self.enabled else self.bg_color
        if not self.enabled:
            color = (200, 200, 205)
            
        # Draw shadow
        shadow_rect = self.rect.move(0, 3 if not self.is_pressed else 1)
        pygame.draw.rect(surface, (0, 0, 0, 35), shadow_rect, border_radius=self.border_radius)
        
        # Draw button body
        draw_rect = self.rect.move(0, 2 if self.is_pressed else 0)
        pygame.draw.rect(surface, color, draw_rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.border_color, draw_rect, width=2, border_radius=self.border_radius)
        
        # Draw Vector Icon if present
        cx, cy = draw_rect.centerx, draw_rect.centery
        t_col = self.text_color if self.enabled else (140, 140, 145)
        
        if self.icon == "pause":
            icons.draw_pause(surface, cx, cy, size=16, color=t_col)
        elif self.icon == "sound":
            icons.draw_speaker(surface, cx, cy, size=18, muted=self.icon_state, color=t_col)
        elif self.icon == "trash":
            icons.draw_trash(surface, draw_rect.left + 22, cy, size=16, color=COLOR_RED)
            # Text next to trash icon
            f = font_manager.get_font(self.font_size, bold=True)
            txt_surf = f.render(self.text, True, t_col)
            surface.blit(txt_surf, (draw_rect.left + 38, cy - txt_surf.get_height()//2))
        elif self.icon == "deliver_star":
            # Star icon on left and right of deliver text
            f = font_manager.get_font(self.font_size, bold=True)
            txt_surf = f.render(self.text, True, t_col)
            surface.blit(txt_surf, (cx - txt_surf.get_width()//2, cy - txt_surf.get_height()//2))
            icons.draw_star(surface, cx - txt_surf.get_width()//2 - 16, cy, radius=8, color=COLOR_GOLD)
            icons.draw_star(surface, cx + txt_surf.get_width()//2 + 16, cy, radius=8, color=COLOR_GOLD)
        elif self.icon == "arrow_left":
            icons.draw_arrow(surface, draw_rect.left + 16, cy, size=12, direction="left", color=t_col)
            f = font_manager.get_font(self.font_size, bold=True)
            txt_surf = f.render(self.text, True, t_col)
            surface.blit(txt_surf, (draw_rect.left + 28, cy - txt_surf.get_height()//2))
        elif self.icon == "arrow_right":
            f = font_manager.get_font(self.font_size, bold=True)
            txt_surf = f.render(self.text, True, t_col)
            surface.blit(txt_surf, (draw_rect.left + 16, cy - txt_surf.get_height()//2))
            icons.draw_arrow(surface, draw_rect.right - 18, cy, size=12, direction="right", color=t_col)
        elif self.icon == "lock":
            icons.draw_lock(surface, cx - 45, cy, size=14, color=(120, 120, 125))
            f = font_manager.get_font(self.font_size, bold=True)
            txt_surf = f.render(self.text, True, (120, 120, 125))
            surface.blit(txt_surf, (cx - 30, cy - txt_surf.get_height()//2))
        else:
            # Standard Text button
            if self.text:
                f = font_manager.get_font(self.font_size, bold=True)
                txt_surf = f.render(self.text, True, t_col)
                txt_rect = txt_surf.get_rect(center=draw_rect.center)
                surface.blit(txt_surf, txt_rect)

class FloatingText:
    def __init__(self, text: str, x: int, y: int, color=(255, 255, 255), size=24, lifetime=1.2):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.elapsed = 0.0
        
    def update(self, dt: float) -> bool:
        self.elapsed += dt
        self.y -= dt * 35.0 # Float upward
        return self.elapsed < self.lifetime

    def draw(self, surface: pygame.Surface, font_manager):
        alpha = max(0, int(255 * (1.0 - (self.elapsed / self.lifetime))))
        f = font_manager.get_font(self.size, bold=True)
        txt = f.render(self.text, True, self.color)
        txt.set_alpha(alpha)
        # Shadow
        sh = f.render(self.text, True, (0, 0, 0))
        sh.set_alpha(int(alpha * 0.5))
        surface.blit(sh, (self.x - txt.get_width()//2 + 2, self.y - txt.get_height()//2 + 2))
        surface.blit(txt, (self.x - txt.get_width()//2, self.y - txt.get_height()//2))

class Particle:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(80, 320)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(60, 150)
        self.gravity = 400.0
        self.size = random.uniform(4, 9)
        self.rotation = random.uniform(0, 360)
        self.v_rot = random.uniform(-180, 180)
        self.lifetime = random.uniform(1.0, 2.2)
        self.elapsed = 0.0

    def update(self, dt: float) -> bool:
        self.elapsed += dt
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.v_rot * dt
        return self.elapsed < self.lifetime

    def draw(self, surface: pygame.Surface):
        alpha = max(0, int(255 * (1.0 - (self.elapsed / self.lifetime))))
        s = pygame.Surface((int(self.size * 2), int(self.size)), pygame.SRCALPHA)
        col = (*self.color, alpha)
        pygame.draw.rect(s, col, (0, 0, int(self.size * 2), int(self.size)), border_radius=2)
        rot_s = pygame.transform.rotate(s, self.rotation)
        surface.blit(rot_s, (self.x - rot_s.get_width()//2, self.y - rot_s.get_height()//2))

class ParticleManager:
    def __init__(self):
        self.particles: List[Particle] = []
        self.floating_texts: List[FloatingText] = []

    def spawn_confetti(self, x: int, y: int, count: int = 40):
        colors = [
            (255, 80, 120), (80, 200, 255), (255, 220, 60), 
            (100, 240, 130), (200, 100, 255), (255, 160, 60)
        ]
        for _ in range(count):
            self.particles.append(Particle(x, y, random.choice(colors)))

    def add_floating_text(self, text: str, x: int, y: int, color=(255, 255, 255), size=24):
        self.floating_texts.append(FloatingText(text, x, y, color, size))

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]

    def draw(self, surface: pygame.Surface, font_manager):
        for p in self.particles:
            p.draw(surface)
        for ft in self.floating_texts:
            ft.draw(surface, font_manager)

class FontManager:
    def __init__(self):
        self.fonts = {}
        
    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in self.fonts:
            try:
                font_name = pygame.font.match_font('segoeui') or pygame.font.match_font('arial')
                if font_name:
                    self.fonts[key] = pygame.font.Font(font_name, size)
                    if bold:
                        self.fonts[key].set_bold(True)
                else:
                    self.fonts[key] = pygame.font.SysFont('Arial', size, bold=bold)
            except Exception:
                self.fonts[key] = pygame.font.SysFont(None, size, bold=bold)
        return self.fonts[key]

class OrderTV:
    """
    Retro Purble Place style order monitor with preview of requested cake,
    recipe checklist, and time progress bar.
    """
    def __init__(self, rect: pygame.Rect):
        self.rect = pygame.Rect(rect)
        
    def draw(self, surface: pygame.Surface, target_cake: Cake, time_ratio: float, 
             cake_renderer, font_manager, cakes_done: int, total_cakes: int):
        # TV Monitor Outer Frame
        pygame.draw.rect(surface, (139, 90, 43), self.rect, border_radius=16) # Wood frame
        pygame.draw.rect(surface, (90, 55, 25), self.rect, width=4, border_radius=16)
        
        # TV Antenna on top
        ax, ay = self.rect.centerx, self.rect.top
        pygame.draw.line(surface, (180, 180, 190), (ax, ay), (ax - 25, ay - 18), 3)
        pygame.draw.line(surface, (180, 180, 190), (ax, ay), (ax + 25, ay - 18), 3)
        pygame.draw.circle(surface, (220, 50, 50), (ax - 25, ay - 18), 5)
        pygame.draw.circle(surface, (220, 50, 50), (ax + 25, ay - 18), 5)
        
        # Screen Bezel & Screen
        screen_rect = self.rect.inflate(-18, -18)
        pygame.draw.rect(surface, (40, 35, 45), screen_rect, border_radius=10)
        
        inner_screen = screen_rect.inflate(-8, -8)
        pygame.draw.rect(surface, (230, 240, 250), inner_screen, border_radius=8)
        
        # Header: Order title
        f_title = font_manager.get_font(16, bold=True)
        t_surf = f_title.render("PEDIDO DO CLIENTE", True, (60, 70, 90))
        surface.blit(t_surf, (inner_screen.centerx - t_surf.get_width()//2, inner_screen.top + 6))
        
        # Counter badge (e.g. "Bolo 2 de 4")
        f_badge = font_manager.get_font(13, bold=True)
        b_surf = f_badge.render(f"Bolo: {cakes_done + 1}/{total_cakes}", True, (255, 255, 255))
        badge_rect = b_surf.get_rect(center=(inner_screen.centerx, inner_screen.top + 28))
        pygame.draw.rect(surface, COLOR_ACCENT, badge_rect.inflate(14, 4), border_radius=10)
        surface.blit(b_surf, badge_rect)
        
        # Render Target Cake in Center of TV screen
        if target_cake:
            preview_y = inner_screen.bottom - 48
            cake_renderer.draw_cake(surface, target_cake, inner_screen.centerx, preview_y, scale=0.55, is_preview=True)
            
        # Draw Timer Bar at bottom of screen
        time_bar_rect = pygame.Rect(inner_screen.left + 10, inner_screen.bottom - 16, inner_screen.width - 20, 10)
        pygame.draw.rect(surface, (200, 205, 215), time_bar_rect, border_radius=5)
        
        if time_ratio > 0.5:
            bar_col = COLOR_GREEN
        elif time_ratio > 0.25:
            bar_col = COLOR_GOLD
        else:
            bar_col = COLOR_RED
            
        fill_w = int(time_bar_rect.width * max(0.0, min(1.0, time_ratio)))
        if fill_w > 0:
            fill_rect = pygame.Rect(time_bar_rect.left, time_bar_rect.top, fill_w, time_bar_rect.height)
            pygame.draw.rect(surface, bar_col, fill_rect, border_radius=5)
        pygame.draw.rect(surface, (140, 145, 155), time_bar_rect, width=1, border_radius=5)
