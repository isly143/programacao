"""
Purble Bakery - Vector Icons System
Draws crisp, resolution-independent vector icons without relying on font emoji tables.
"""
import math
import pygame
from typing import Tuple

def draw_heart(surface: pygame.Surface, cx: int, cy: int, size: int = 16, 
               color: Tuple[int, int, int] = (230, 40, 60), filled: bool = True):
    """Draws a cute crisp heart icon at (cx, cy)."""
    hw = size * 0.5
    hh = size * 0.5
    pts = []
    steps = 32
    for i in range(steps):
        t = (i / steps) * 2 * math.pi
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        px = cx + (x / 16.0) * hw
        py = cy + (y / 16.0) * hh
        pts.append((px, py))
    if filled:
        pygame.draw.polygon(surface, color, pts)
        # Add a subtle specular highlight
        hl_pts = pts[steps*3//8 : steps*5//8]
        if len(hl_pts) > 2:
            pygame.draw.lines(surface, (min(255, color[0]+60), min(255, color[1]+60), min(255, color[2]+60)), False, hl_pts, max(1, size//12))
    else:
        pygame.draw.polygon(surface, (160, 160, 165), pts, width=max(1, size//8))

def draw_star(surface: pygame.Surface, cx: int, cy: int, radius: int = 14, 
              color: Tuple[int, int, int] = (255, 215, 0), filled: bool = True):
    """Draws a clean 5-pointed star at (cx, cy)."""
    pts = []
    num_points = 5
    for i in range(num_points * 2):
        ang = i * (math.pi / num_points) - math.pi / 2
        r_scale = 1.0 if i % 2 == 0 else 0.45
        px = cx + (radius * r_scale) * math.cos(ang)
        py = cy + (radius * r_scale) * math.sin(ang)
        pts.append((px, py))
        
    if filled:
        # Star body
        pygame.draw.polygon(surface, color, pts)
        # Inner highlight
        inner_pts = [(p[0]*0.65 + cx*0.35, p[1]*0.65 + cy*0.35) for p in pts]
        pygame.draw.polygon(surface, (255, 245, 170), inner_pts)
        pygame.draw.polygon(surface, (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40)), pts, width=1)
    else:
        # Outline only (empty star)
        pygame.draw.polygon(surface, (170, 170, 180), pts, width=2)

def draw_speaker(surface: pygame.Surface, cx: int, cy: int, size: int = 20, 
                 muted: bool = False, color: Tuple[int, int, int] = (60, 60, 70)):
    """Draws an audio speaker icon with sound waves or mute cross."""
    hw = size // 2
    hh = size // 2
    
    # Speaker cone
    pts = [
        (cx - hw + 2, cy - hh//3),
        (cx - hw//3, cy - hh//3),
        (cx + 2, cy - hh + 2),
        (cx + 2, cy + hh - 2),
        (cx - hw//3, cy + hh//3),
        (cx - hw + 2, cy + hh//3)
    ]
    pygame.draw.polygon(surface, color, pts)
    
    if not muted:
        # Sound waves
        arc_box1 = (cx - 2, cy - hh//2, size//2, size)
        pygame.draw.arc(surface, color, arc_box1, -math.pi/3, math.pi/3, 2)
        arc_box2 = (cx + 3, cy - hh + 2, size//2 + 4, size * 4 // 3)
        pygame.draw.arc(surface, color, arc_box2, -math.pi/3, math.pi/3, 2)
    else:
        # Red Mute X
        rx = cx + 6
        pygame.draw.line(surface, (220, 40, 40), (rx - 4, cy - 5), (rx + 5, cy + 5), 2)
        pygame.draw.line(surface, (220, 40, 40), (rx - 4, cy + 5), (rx + 5, cy - 5), 2)

def draw_pause(surface: pygame.Surface, cx: int, cy: int, size: int = 18, 
               color: Tuple[int, int, int] = (60, 60, 70)):
    """Draws two vertical pause bars."""
    bar_w = max(3, size // 4)
    bar_h = size
    gap = max(3, size // 4)
    
    r1 = pygame.Rect(cx - gap - bar_w//2, cy - bar_h//2, bar_w, bar_h)
    r2 = pygame.Rect(cx + gap - bar_w//2, cy - bar_h//2, bar_w, bar_h)
    pygame.draw.rect(surface, color, r1, border_radius=2)
    pygame.draw.rect(surface, color, r2, border_radius=2)

def draw_trash(surface: pygame.Surface, cx: int, cy: int, size: int = 18, 
               color: Tuple[int, int, int] = (200, 40, 50)):
    """Draws a clean trash can icon."""
    tw = size * 3 // 4
    th = size
    
    # Can body
    body_pts = [
        (cx - tw//2 + 2, cy - th//4),
        (cx + tw//2 - 2, cy - th//4),
        (cx + tw//3, cy + th//2),
        (cx - tw//3, cy + th//2)
    ]
    pygame.draw.polygon(surface, color, body_pts)
    pygame.draw.polygon(surface, (max(0, color[0]-50), max(0, color[1]-50), max(0, color[2]-50)), body_pts, width=2)
    
    # Can lid & handle
    pygame.draw.line(surface, color, (cx - tw//2 - 2, cy - th//4), (cx + tw//2 + 2, cy - th//4), 3)
    pygame.draw.rect(surface, color, (cx - 4, cy - th//2, 8, 4), border_radius=1)

def draw_lock(surface: pygame.Surface, cx: int, cy: int, size: int = 16, 
              color: Tuple[int, int, int] = (100, 100, 110)):
    """Draws a padlock icon."""
    bw = size
    bh = int(size * 0.75)
    
    # Shackle (loop on top)
    shackle_rect = pygame.Rect(cx - bw//3, cy - bh//2 - 5, bw*2//3, 10)
    pygame.draw.arc(surface, color, shackle_rect, 0, math.pi, 2)
    
    # Body
    body_rect = pygame.Rect(cx - bw//2, cy - bh//4, bw, bh)
    pygame.draw.rect(surface, color, body_rect, border_radius=3)
    # Keyhole
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy + 2), 2)

def draw_flame(surface: pygame.Surface, cx: int, cy: int, size: int = 18):
    """Draws a flame icon for combo streaks."""
    # Outer orange flame
    pts_outer = [
        (cx, cy - size//2),
        (cx + size//3, cy - size//6),
        (cx + size//2, cy + size//4),
        (cx + size//4, cy + size//2),
        (cx - size//4, cy + size//2),
        (cx - size//2, cy + size//4),
        (cx - size//3, cy - size//6)
    ]
    pygame.draw.polygon(surface, (255, 120, 20), pts_outer)
    # Inner yellow core
    pts_inner = [(p[0]*0.55 + cx*0.45, p[1]*0.55 + (cy+2)*0.45) for p in pts_outer]
    pygame.draw.polygon(surface, (255, 230, 60), pts_inner)

def draw_trophy(surface: pygame.Surface, cx: int, cy: int, size: int = 24):
    """Draws a shiny gold trophy cup."""
    # Cup
    cup_rect = pygame.Rect(cx - size//3, cy - size//2, size*2//3, size//2)
    pygame.draw.rect(surface, (255, 200, 20), cup_rect, border_bottom_left_radius=size//3, border_bottom_right_radius=size//3)
    # Handles
    pygame.draw.arc(surface, (255, 200, 20), (cx - size//2 - 2, cy - size//2, size//3, size//3), math.pi/2, 3*math.pi/2, 2)
    pygame.draw.arc(surface, (255, 200, 20), (cx + size//3, cy - size//2, size//3, size//3), -math.pi/2, math.pi/2, 2)
    # Stem & Base
    pygame.draw.rect(surface, (210, 160, 10), (cx - 2, cy, 4, size//3))
    pygame.draw.rect(surface, (190, 140, 10), (cx - size//3, cy + size//3, size*2//3, 5), border_radius=2)

def draw_arrow(surface: pygame.Surface, cx: int, cy: int, size: int = 14, 
               direction: str = "right", color: Tuple[int, int, int] = (60, 60, 70)):
    """Draws a directional triangle arrow."""
    hw = size // 2
    hh = size // 2
    if direction == "right":
        pts = [(cx - hw, cy - hh), (cx + hw, cy), (cx - hw, cy + hh)]
    elif direction == "left":
        pts = [(cx + hw, cy - hh), (cx - hw, cy), (cx + hw, cy + hh)]
    elif direction == "up":
        pts = [(cx - hw, cy + hh), (cx, cy - hh), (cx + hw, cy + hh)]
    else: # down
        pts = [(cx - hw, cy - hh), (cx, cy + hh), (cx + hw, cy - hh)]
    pygame.draw.polygon(surface, color, pts)
