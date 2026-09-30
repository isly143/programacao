"""
Purble Bakery - High Fidelity Cake & Particle Renderer
Renders 2.5D cakes with realistic depth, dripping glaze, creamy fillings, and toppings.
"""
import math
import pygame
from game.models import Shape, Batter, Filling, Frosting, Topping, Cake, CakeLayer

class CakeRenderer:
    def __init__(self):
        # Cache surfaces for performance
        self.flame_frame = 0
        
    def update_animations(self, dt: float):
        self.flame_frame += dt * 8.0

    def draw_cake(self, surface: pygame.Surface, cake: Cake, center_x: int, bottom_y: int, scale: float = 1.0, is_preview: bool = False):
        """
        Draws the complete tiered cake onto the target surface.
        """
        if cake is None or len(cake.layers) == 0:
            return

        # Draw tiers from bottom (0) to top (len-1)
        num_tiers = len(cake.layers)
        tier_scales = [1.0, 0.72, 0.52] if num_tiers > 1 else [1.0]
        
        # Calculate Y offsets for stacking
        current_y = bottom_y
        
        for i, layer in enumerate(cake.layers):
            tier_scale = scale * tier_scales[min(i, len(tier_scales)-1)]
            layer_height = int(50 * tier_scale)
            
            self._draw_single_tier(
                surface=surface,
                layer=layer,
                center_x=center_x,
                tier_y=current_y,
                scale=tier_scale,
                tier_index=i,
                is_top_tier=(i == num_tiers - 1),
                is_preview=is_preview
            )
            
            # Move Y up for next tier (stacking)
            # Only move up if this tier has batter
            if layer.batter is not None:
                current_y -= int(42 * tier_scale)
            else:
                current_y -= int(18 * tier_scale)

    def _draw_single_tier(self, surface: pygame.Surface, layer: CakeLayer, 
                           center_x: int, tier_y: int, scale: float, 
                           tier_index: int, is_top_tier: bool, is_preview: bool):
        shape = layer.shape or Shape.CIRCLE
        base_w = int(210 * scale)
        base_h = int(90 * scale)
        depth = int(45 * scale)
        
        # 1. Draw Pan (if present and tier 0 or if pan is active)
        if tier_index == 0 or layer.shape is not None:
            self._draw_pan(surface, shape, center_x, tier_y, base_w, base_h, depth)
            
        # 2. Draw Batter (Baked Sponge)
        if layer.batter is not None:
            self._draw_sponge(surface, shape, layer.batter, center_x, tier_y - int(8 * scale), base_w - int(12 * scale), base_h - int(6 * scale), depth)
            
            # 3. Draw Filling (if added)
            if layer.filling and layer.filling != Filling.NONE:
                self._draw_filling(surface, shape, layer.filling, center_x, tier_y - int(8 * scale), base_w - int(12 * scale), base_h - int(6 * scale), depth)
                
            # 4. Draw Frosting / Glaze (if added)
            if layer.frosting and layer.frosting != Frosting.NONE:
                self._draw_frosting(surface, shape, layer.frosting, center_x, tier_y - int(8 * scale), base_w - int(12 * scale), base_h - int(6 * scale), depth)
                
            # 5. Draw Toppings (if added)
            if layer.topping and layer.topping != Topping.NONE:
                self._draw_topping(surface, shape, layer.topping, center_x, tier_y - depth - int(12 * scale), scale)

    def _draw_pan(self, surface: pygame.Surface, shape: str, cx: int, cy: int, w: int, h: int, depth: int):
        """Draws metallic baking pan with rim and sheen."""
        pan_edge_col = (110, 115, 125)
        pan_body_col = (165, 172, 185)
        pan_hl_col   = (215, 222, 235)
        pan_inner_col= (135, 142, 155)
        
        if shape == Shape.CIRCLE:
            # 3D Cylinder for Pan
            # Outer lower rim shadow
            pygame.draw.ellipse(surface, (80, 85, 95), (cx - w//2 - 2, cy - depth//2 + 2, w + 4, h))
            # Pan sides (body)
            points = [
                (cx - w//2, cy),
                (cx + w//2, cy),
                (cx + w//2, cy - depth),
                (cx - w//2, cy - depth)
            ]
            pygame.draw.polygon(surface, pan_body_col, points)
            # Front curved side shading
            pygame.draw.ellipse(surface, pan_body_col, (cx - w//2, cy - h//2, w, h))
            # Side highlights
            pygame.draw.line(surface, pan_hl_col, (cx - w//4, cy - depth + 2), (cx - w//4, cy - 2), 3)
            # Inner pan top oval
            pygame.draw.ellipse(surface, pan_inner_col, (cx - w//2, cy - depth - h//2, w, h))
            pygame.draw.ellipse(surface, pan_edge_col, (cx - w//2, cy - depth - h//2, w, h), 3)
            
        elif shape == Shape.SQUARE:
            # Rounded rectangular baking pan
            rw, rh = w, int(h * 0.85)
            rect_top = pygame.Rect(cx - rw//2, cy - depth - rh//2, rw, rh)
            rect_bot = pygame.Rect(cx - rw//2, cy - rh//2, rw, rh)
            
            # Bottom & Sides
            pygame.draw.rect(surface, pan_edge_col, rect_bot.inflate(4, 4), border_radius=12)
            # Side polygon
            side_pts = [
                (rect_top.left, rect_top.centery),
                (rect_top.right, rect_top.centery),
                (rect_bot.right, rect_bot.centery),
                (rect_bot.left, rect_bot.centery)
            ]
            pygame.draw.polygon(surface, pan_body_col, side_pts)
            pygame.draw.rect(surface, pan_body_col, rect_bot, border_radius=12)
            pygame.draw.line(surface, pan_hl_col, (rect_top.left + 15, rect_top.centery), (rect_bot.left + 15, rect_bot.centery), 3)
            # Top inside
            pygame.draw.rect(surface, pan_inner_col, rect_top, border_radius=12)
            pygame.draw.rect(surface, pan_edge_col, rect_top, width=3, border_radius=12)

        elif shape == Shape.HEART:
            # Cute Heart Pan
            self._draw_heart_pan(surface, cx, cy, w, h, depth, pan_body_col, pan_inner_col, pan_edge_col)

        elif shape == Shape.STAR:
            # Star Pan
            self._draw_star_pan(surface, cx, cy, w, h, depth, pan_body_col, pan_inner_col, pan_edge_col)

    def _draw_sponge(self, surface: pygame.Surface, shape: str, batter: str, cx: int, cy: int, w: int, h: int, depth: int):
        """Draws the baked sponge cake tier."""
        base_color = Batter.COLORS.get(batter, (240, 210, 140))
        # Darker shading for side
        side_color = (
            max(0, int(base_color[0] * 0.75)),
            max(0, int(base_color[1] * 0.75)),
            max(0, int(base_color[2] * 0.75))
        )
        top_color = base_color
        
        if shape == Shape.CIRCLE:
            # Sides
            points = [
                (cx - w//2, cy),
                (cx + w//2, cy),
                (cx + w//2, cy - depth),
                (cx - w//2, cy - depth)
            ]
            pygame.draw.polygon(surface, side_color, points)
            pygame.draw.ellipse(surface, side_color, (cx - w//2, cy - h//2, w, h))
            # Top
            pygame.draw.ellipse(surface, top_color, (cx - w//2, cy - depth - h//2, w, h))
            pygame.draw.ellipse(surface, (max(0, top_color[0]-30), max(0, top_color[1]-30), max(0, top_color[2]-30)), 
                                (cx - w//2, cy - depth - h//2, w, h), 2)
                                
        elif shape == Shape.SQUARE:
            rw, rh = w, int(h * 0.85)
            rect_top = pygame.Rect(cx - rw//2, cy - depth - rh//2, rw, rh)
            rect_bot = pygame.Rect(cx - rw//2, cy - rh//2, rw, rh)
            
            side_pts = [
                (rect_top.left, rect_top.centery),
                (rect_top.right, rect_top.centery),
                (rect_bot.right, rect_bot.centery),
                (rect_bot.left, rect_bot.centery)
            ]
            pygame.draw.polygon(surface, side_color, side_pts)
            pygame.draw.rect(surface, side_color, rect_bot, border_radius=10)
            pygame.draw.rect(surface, top_color, rect_top, border_radius=10)
            pygame.draw.rect(surface, (max(0, top_color[0]-30), max(0, top_color[1]-30), max(0, top_color[2]-30)), rect_top, width=2, border_radius=10)

        elif shape == Shape.HEART:
            self._draw_heart_3d(surface, cx, cy, w, h, depth, side_color, top_color)
            
        elif shape == Shape.STAR:
            self._draw_star_3d(surface, cx, cy, w, h, depth, side_color, top_color)

    def _draw_filling(self, surface: pygame.Surface, shape: str, filling: str, cx: int, cy: int, w: int, h: int, depth: int):
        """Draws creamy delicious filling stripe in the middle of the cake layer."""
        f_color = Filling.COLORS.get(filling, (255, 255, 255))
        if f_color[0] == 0 and f_color[1] == 0:
            return
            
        mid_y = cy - depth // 2
        fill_h = max(6, depth // 4)
        
        # Draw filling belt across the front
        fill_rect = pygame.Rect(cx - w//2 + 4, mid_y - fill_h//2, w - 8, fill_h)
        pygame.draw.rect(surface, f_color, fill_rect, border_radius=fill_h//2)
        # Cute drip dots
        for drip_x in [cx - w//3, cx, cx + w//3]:
            pygame.draw.circle(surface, f_color, (drip_x, mid_y + fill_h//2 + 2), 3)

    def _draw_frosting(self, surface: pygame.Surface, shape: str, frosting: str, cx: int, cy: int, w: int, h: int, depth: int):
        """Draws lush glossy icing covering top and dripping down."""
        frost_color = Frosting.COLORS.get(frosting, (255, 255, 255))
        if frost_color[0] == 0 and frost_color[1] == 0:
            return
            
        highlight = (
            min(255, frost_color[0] + 45),
            min(255, frost_color[1] + 45),
            min(255, frost_color[2] + 45)
        )
        shadow = (
            max(0, frost_color[0] - 35),
            max(0, frost_color[1] - 35),
            max(0, frost_color[2] - 35)
        )
        
        top_y = cy - depth
        
        if shape == Shape.CIRCLE:
            # Drips on the sides
            drip_h = int(depth * 0.45)
            # Side drip band
            pygame.draw.ellipse(surface, shadow, (cx - w//2 + 1, top_y - h//2 + 2, w - 2, h + drip_h))
            # Smooth top glaze
            pygame.draw.ellipse(surface, frost_color, (cx - w//2 + 2, top_y - h//2 + 1, w - 4, h - 2))
            # Gloss shine arc
            shiny_rect = (cx - w//3, top_y - h//3, int(w * 0.4), int(h * 0.35))
            pygame.draw.arc(surface, highlight, shiny_rect, 0.5, 2.5, 4)
            
        elif shape == Shape.SQUARE:
            rw, rh = w - 6, int(h * 0.85) - 4
            rect_frost = pygame.Rect(cx - rw//2, top_y - rh//2, rw, rh)
            # Drip skirt
            skirt = pygame.Rect(cx - rw//2, top_y, rw, int(depth * 0.4))
            pygame.draw.rect(surface, shadow, skirt, border_radius=6)
            pygame.draw.rect(surface, frost_color, rect_frost, border_radius=8)
            # Shiny gloss line
            pygame.draw.line(surface, highlight, (rect_frost.left + 10, rect_frost.top + 8), (rect_frost.right - 20, rect_frost.top + 8), 3)

        elif shape == Shape.HEART:
            self._draw_heart_frosting(surface, cx, top_y, w, h, depth, frost_color, highlight)
            
        elif shape == Shape.STAR:
            self._draw_star_frosting(surface, cx, top_y, w, h, depth, frost_color, highlight)

    def _draw_topping(self, surface: pygame.Surface, shape: str, topping: str, cx: int, top_y: int, scale: float):
        """Draws detailed toppings on top of the cake."""
        if topping == Topping.CHERRY:
            # Glossy Red Cherry with Stem and Leaf
            r = int(14 * scale)
            cy = top_y + int(4 * scale)
            # Leaf
            leaf_pts = [(cx + 2, cy - r - 8), (cx + 12, cy - r - 14), (cx + 16, cy - r - 4)]
            pygame.draw.polygon(surface, (60, 160, 60), leaf_pts)
            # Curved Stem
            pygame.draw.arc(surface, (90, 50, 30), (cx - 2, cy - r - 16, 16, 20), 0.5, 2.2, max(2, int(2 * scale)))
            # Shadow
            pygame.draw.circle(surface, (140, 0, 15), (cx, cy), r)
            # Cherry Body
            pygame.draw.circle(surface, (215, 15, 35), (cx - 1, cy - 1), r - 1)
            # Specular shine
            pygame.draw.circle(surface, (255, 200, 210), (cx - r//3, cy - r//3), max(2, r//4))
            
        elif topping == Topping.STRAWBERRY:
            # Juicy Strawberry with green crown
            sw = int(16 * scale)
            sh = int(22 * scale)
            cy = top_y + int(6 * scale)
            pts = [
                (cx, cy + sh//2),
                (cx - sw, cy - sh//3),
                (cx, cy - sh//2),
                (cx + sw, cy - sh//3)
            ]
            pygame.draw.polygon(surface, (225, 25, 45), pts)
            # Green cap
            for angle in [-0.5, 0, 0.5]:
                leaf_x = cx + int(math.sin(angle) * 12 * scale)
                leaf_y = cy - sh//2 + int(math.cos(angle) * 4)
                pygame.draw.circle(surface, (50, 180, 50), (leaf_x, leaf_y), max(2, int(4 * scale)))
            # Seeds
            for sx, sy in [(cx - 4, cy), (cx + 4, cy), (cx, cy + 6), (cx, cy - 4)]:
                pygame.draw.circle(surface, (255, 230, 100), (sx, sy), 1)

        elif topping == Topping.STAR:
            # Golden sugar star
            sr = int(18 * scale)
            cy = top_y + int(4 * scale)
            star_pts = []
            for i in range(10):
                ang = i * (math.pi / 5) - math.pi / 2
                rad = sr if i % 2 == 0 else sr * 0.45
                star_pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
            pygame.draw.polygon(surface, (255, 205, 30), star_pts)
            pygame.draw.polygon(surface, (255, 245, 150), [(p[0]*0.7 + cx*0.3, p[1]*0.7 + cy*0.3) for p in star_pts])
            # Sparkle
            pygame.draw.circle(surface, (255, 255, 255), (cx - 3, cy - 3), 2)

        elif topping == Topping.CANDLE:
            # Birthday Candle with flickering flame!
            cw = max(4, int(7 * scale))
            ch = int(26 * scale)
            cy = top_y - ch//2
            
            # Candle Body
            candle_rect = pygame.Rect(cx - cw//2, top_y - ch, cw, ch)
            pygame.draw.rect(surface, (100, 200, 255), candle_rect, border_radius=2)
            # Stripes
            for sy in range(candle_rect.top + 4, candle_rect.bottom - 4, 7):
                pygame.draw.line(surface, (255, 255, 255), (candle_rect.left, sy), (candle_rect.right, sy + 3), 2)
            # Wick
            pygame.draw.line(surface, (40, 40, 40), (cx, candle_rect.top), (cx, candle_rect.top - 4), 2)
            
            # Flickering Flame
            flicker = math.sin(self.flame_frame) * 2.0
            flame_pts = [
                (cx, candle_rect.top - 16 + flicker),
                (cx - 5, candle_rect.top - 8),
                (cx, candle_rect.top - 4),
                (cx + 5, candle_rect.top - 8)
            ]
            # Outer glow
            pygame.draw.circle(surface, (255, 180, 50), (cx, int(candle_rect.top - 8)), int(8 * scale))
            # Inner flame
            pygame.draw.polygon(surface, (255, 240, 100), flame_pts)
            pygame.draw.circle(surface, (255, 255, 255), (cx, int(candle_rect.top - 7)), 2)

    # Helper Geometry for Heart & Star Shapes
    def _draw_heart_pan(self, surface, cx, cy, w, h, depth, body_col, inner_col, edge_col):
        # 3D Heart extrusion
        self._draw_heart_shape(surface, cx, cy, w, h, body_col)
        self._draw_heart_shape(surface, cx, cy - depth, w, h, inner_col)
        self._draw_heart_shape(surface, cx, cy - depth, w, h, edge_col, width=3)

    def _draw_heart_3d(self, surface, cx, cy, w, h, depth, side_col, top_col):
        # Side extrusion
        for d in range(0, depth, 3):
            self._draw_heart_shape(surface, cx, cy - d, w, h, side_col)
        self._draw_heart_shape(surface, cx, cy - depth, w, h, top_col)

    def _draw_heart_frosting(self, surface, cx, top_y, w, h, depth, frost_col, highlight):
        self._draw_heart_shape(surface, cx, top_y + 2, w, h, frost_col)
        self._draw_heart_shape(surface, cx, top_y, w - 4, h - 4, highlight, width=2)

    def _draw_heart_shape(self, surface, cx, cy, w, h, color, width=0):
        # Generate heart polygon points
        pts = []
        steps = 36
        hw = w * 0.48
        hh = h * 0.52
        for i in range(steps):
            t = (i / steps) * 2 * math.pi
            # Parametric heart equation
            x = 16 * (math.sin(t) ** 3)
            y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            px = cx + (x / 16.0) * hw
            py = cy + (y / 16.0) * hh
            pts.append((px, py))
        if width == 0:
            pygame.draw.polygon(surface, color, pts)
        else:
            pygame.draw.lines(surface, color, True, pts, width)

    def _draw_star_pan(self, surface, cx, cy, w, h, depth, body_col, inner_col, edge_col):
        self._draw_star_shape(surface, cx, cy, w, h, body_col)
        self._draw_star_shape(surface, cx, cy - depth, w, h, inner_col)
        self._draw_star_shape(surface, cx, cy - depth, w, h, edge_col, width=3)

    def _draw_star_3d(self, surface, cx, cy, w, h, depth, side_col, top_col):
        for d in range(0, depth, 3):
            self._draw_star_shape(surface, cx, cy - d, w, h, side_col)
        self._draw_star_shape(surface, cx, cy - depth, w, h, top_col)

    def _draw_star_frosting(self, surface, cx, top_y, w, h, depth, frost_col, highlight):
        self._draw_star_shape(surface, cx, top_y + 2, w, h, frost_col)
        self._draw_star_shape(surface, cx, top_y, w - 6, h - 6, highlight, width=2)

    def _draw_star_shape(self, surface, cx, cy, w, h, color, width=0):
        pts = []
        num_points = 5
        rx = w * 0.5
        ry = h * 0.5
        for i in range(num_points * 2):
            ang = i * (math.pi / num_points) - math.pi / 2
            r_scale = 1.0 if i % 2 == 0 else 0.5
            px = cx + (rx * r_scale) * math.cos(ang)
            py = cy + (ry * r_scale) * math.sin(ang)
            pts.append((px, py))
        if width == 0:
            pygame.draw.polygon(surface, color, pts)
        else:
            pygame.draw.lines(surface, color, True, pts, width)
