"""
Purble Bakery - Game Data Models & Level Configurations
"""
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# Constants & Identifiers
class Shape:
    SQUARE = "square"
    CIRCLE = "circle"
    HEART = "heart"
    STAR = "star"
    
    LABELS = {
        SQUARE: "Quadrado",
        CIRCLE: "Redondo",
        HEART: "Coração",
        STAR: "Estrela"
    }

class Batter:
    VANILLA = "vanilla"
    CHOCOLATE = "chocolate"
    STRAWBERRY = "strawberry"
    
    LABELS = {
        VANILLA: "Baunilha",
        CHOCOLATE: "Chocolate",
        STRAWBERRY: "Morango"
    }
    
    COLORS = {
        VANILLA: (245, 222, 145),      # Golden sponge
        CHOCOLATE: (112, 66, 40),       # Rich chocolate brown
        STRAWBERRY: (245, 140, 160)     # Pink sponge
    }

class Filling:
    NONE = "none"
    VANILLA = "vanilla"
    CHOCOLATE = "chocolate"
    STRAWBERRY = "strawberry"
    
    LABELS = {
        NONE: "Nenhum",
        VANILLA: "Creme de Baunilha",
        CHOCOLATE: "Ganache de Chocolate",
        STRAWBERRY: "Geleia de Morango"
    }
    
    COLORS = {
        NONE: (0, 0, 0, 0),
        VANILLA: (255, 248, 200),
        CHOCOLATE: (75, 40, 25),
        STRAWBERRY: (220, 40, 70)
    }

class Frosting:
    NONE = "none"
    WHITE = "white"
    CHOCOLATE = "chocolate"
    PINK = "pink"
    
    LABELS = {
        NONE: "Sem Cobertura",
        WHITE: "Glacê de Baunilha",
        CHOCOLATE: "Chocolate Cremoso",
        PINK: "Cobertura de Morango"
    }
    
    COLORS = {
        NONE: (0, 0, 0, 0),
        WHITE: (252, 252, 250),
        CHOCOLATE: (95, 50, 30),
        PINK: (255, 150, 185)
    }

class Topping:
    NONE = "none"
    CHERRY = "cherry"
    STRAWBERRY = "strawberry"
    STAR = "star"
    CANDLE = "candle"
    
    LABELS = {
        NONE: "Sem Confeito",
        CHERRY: "Cereja com Folha",
        STRAWBERRY: "Morango Fresco",
        STAR: "Estrela de Açúcar",
        CANDLE: "Vela de Aniversário"
    }

@dataclass
class CakeLayer:
    shape: Optional[str] = None
    batter: Optional[str] = None
    filling: Optional[str] = None
    frosting: Optional[str] = None
    topping: Optional[str] = None
    
    def is_empty(self) -> bool:
        return self.shape is None and self.batter is None
        
    def clone(self) -> 'CakeLayer':
        return CakeLayer(
            shape=self.shape,
            batter=self.batter,
            filling=self.filling,
            frosting=self.frosting,
            topping=self.topping
        )

class Cake:
    def __init__(self):
        self.layers: List[CakeLayer] = []
        self.current_tier_idx = 0
        
    def is_empty(self) -> bool:
        return len(self.layers) == 0
        
    def clear(self):
        self.layers = []
        self.current_tier_idx = 0

    def apply_pan(self, shape: str):
        # If no layer exists, create tier 0
        if not self.layers:
            self.layers.append(CakeLayer(shape=shape))
            self.current_tier_idx = 0
        else:
            # If current layer has no batter yet, change its pan
            cur = self.layers[self.current_tier_idx]
            if cur.batter is None:
                cur.shape = shape
            else:
                # If layer is already baked, cannot change shape
                pass

    def apply_batter(self, flavor: str):
        if not self.layers:
            return False
        cur = self.layers[self.current_tier_idx]
        if cur.shape is not None and cur.batter is None:
            cur.batter = flavor
            return True
        return False

    def apply_filling(self, flavor: str):
        if not self.layers:
            return False
        cur = self.layers[self.current_tier_idx]
        if cur.batter is not None and cur.filling is None:
            cur.filling = flavor
            return True
        return False

    def apply_frosting(self, flavor: str):
        if not self.layers:
            return False
        cur = self.layers[self.current_tier_idx]
        if cur.batter is not None and cur.frosting is None:
            cur.frosting = flavor
            return True
        return False

    def apply_topping(self, item: str):
        if not self.layers:
            return False
        cur = self.layers[self.current_tier_idx]
        # Topping can be placed if cake has batter
        if cur.batter is not None and cur.topping is None:
            cur.topping = item
            return True
        return False

    def add_tier(self, max_allowed_tiers: int) -> bool:
        """Adds another layer/tier on top of the current one if current is baked."""
        if not self.layers:
            return False
        if len(self.layers) >= max_allowed_tiers:
            return False
        cur = self.layers[-1]
        if cur.batter is None:
            return False
            
        # Inherit shape from base or use same shape smaller
        new_layer = CakeLayer(shape=self.layers[0].shape)
        self.layers.append(new_layer)
        self.current_tier_idx = len(self.layers) - 1
        return True

    def clone(self) -> 'Cake':
        c = Cake()
        c.layers = [l.clone() for l in self.layers]
        c.current_tier_idx = self.current_tier_idx
        return c

@dataclass
class LevelConfig:
    level_num: int
    title: str
    subtitle: str
    target_cakes: int
    shapes: List[str]
    batters: List[str]
    has_filling: bool
    fillings: List[str]
    frostings: List[str]
    toppings: List[str]
    max_tiers: int = 1
    time_limit_sec: int = 60 # per cake (0 = infinite / relaxed)
    points_per_cake: int = 500

LEVELS = [
    LevelConfig(
        level_num=1,
        title="Fase 1: Aprendiz de Confeiteiro",
        subtitle="Monte bolos simples de 1 andar com forma, massa, cobertura e confeito.",
        target_cakes=3,
        shapes=[Shape.SQUARE, Shape.CIRCLE],
        batters=[Batter.VANILLA, Batter.CHOCOLATE],
        has_filling=False,
        fillings=[],
        frostings=[Frosting.WHITE, Frosting.CHOCOLATE],
        toppings=[Topping.CHERRY, Topping.STRAWBERRY],
        max_tiers=1,
        time_limit_sec=60,
        points_per_cake=300
    ),
    LevelConfig(
        level_num=2,
        title="Fase 2: Confeiteiro Júnior",
        subtitle="Agora com novas formas, massas e a deliciosa Estação de Recheios!",
        target_cakes=4,
        shapes=[Shape.SQUARE, Shape.CIRCLE, Shape.HEART],
        batters=[Batter.VANILLA, Batter.CHOCOLATE, Batter.STRAWBERRY],
        has_filling=True,
        fillings=[Filling.VANILLA, Filling.CHOCOLATE, Filling.STRAWBERRY],
        frostings=[Frosting.WHITE, Frosting.CHOCOLATE, Frosting.PINK],
        toppings=[Topping.CHERRY, Topping.STRAWBERRY, Topping.STAR],
        max_tiers=1,
        time_limit_sec=50,
        points_per_cake=500
    ),
    LevelConfig(
        level_num=3,
        title="Fase 3: Mestre Confeiteiro",
        subtitle="Desafio de 2 andares! Monte a base e adicione o segundo andar.",
        target_cakes=5,
        shapes=[Shape.SQUARE, Shape.CIRCLE, Shape.HEART, Shape.STAR],
        batters=[Batter.VANILLA, Batter.CHOCOLATE, Batter.STRAWBERRY],
        has_filling=True,
        fillings=[Filling.VANILLA, Filling.CHOCOLATE, Filling.STRAWBERRY],
        frostings=[Frosting.WHITE, Frosting.CHOCOLATE, Frosting.PINK],
        toppings=[Topping.CHERRY, Topping.STRAWBERRY, Topping.STAR, Topping.CANDLE],
        max_tiers=2,
        time_limit_sec=50,
        points_per_cake=800
    ),
    LevelConfig(
        level_num=4,
        title="Fase 4: Grande Chefe Purble",
        subtitle="O ápice da confeitaria! Bolos complexos de 2 e 3 andares contra o relógio!",
        target_cakes=6,
        shapes=[Shape.SQUARE, Shape.CIRCLE, Shape.HEART, Shape.STAR],
        batters=[Batter.VANILLA, Batter.CHOCOLATE, Batter.STRAWBERRY],
        has_filling=True,
        fillings=[Filling.VANILLA, Filling.CHOCOLATE, Filling.STRAWBERRY],
        frostings=[Frosting.WHITE, Frosting.CHOCOLATE, Frosting.PINK],
        toppings=[Topping.CHERRY, Topping.STRAWBERRY, Topping.STAR, Topping.CANDLE],
        max_tiers=3,
        time_limit_sec=40,
        points_per_cake=1200
    ),
]

def generate_order(config: LevelConfig) -> Cake:
    """Generates a random recipe conforming to the level rules."""
    cake = Cake()
    
    # Decide number of tiers for this order
    if config.max_tiers == 1:
        num_tiers = 1
    elif config.max_tiers == 2:
        num_tiers = 2 if random.random() > 0.3 else 1
    else: # max_tiers == 3
        r = random.random()
        num_tiers = 3 if r > 0.5 else (2 if r > 0.15 else 1)
        
    base_shape = random.choice(config.shapes)
    
    for tier in range(num_tiers):
        layer = CakeLayer(
            shape=base_shape,
            batter=random.choice(config.batters),
            filling=random.choice(config.fillings) if (config.has_filling and config.fillings) else None,
            frosting=random.choice(config.frostings),
            topping=random.choice(config.toppings) if (tier == num_tiers - 1) else None # top tier gets topping
        )
        cake.layers.append(layer)
        
    return cake

def compare_cakes(target: Cake, player: Cake) -> Tuple[bool, int, List[str]]:
    """
    Compares the player's cake with the target order.
    Returns:
        is_match: True if 100% identical.
        score: Points awarded.
        errors: List of specific error descriptions.
    """
    errors = []
    
    if len(player.layers) == 0:
        return False, 0, ["O prato está completamente vazio!"]
        
    if len(player.layers) != len(target.layers):
        if len(player.layers) < len(target.layers):
            errors.append(f"Faltaram andares! O pedido tem {len(target.layers)} andar(es), mas você fez {len(player.layers)}.")
        else:
            errors.append(f"Andares em excesso! O pedido tem {len(target.layers)} andar(es), você fez {len(player.layers)}.")

    total_checks = 0
    passed_checks = 0

    for i in range(max(len(target.layers), len(player.layers))):
        tier_label = f"Andar {i+1}"
        if i >= len(target.layers):
            errors.append(f"{tier_label}: Andar extra não solicitado.")
            continue
        if i >= len(player.layers):
            errors.append(f"{tier_label}: Faltou montar este andar.")
            continue
            
        t_layer = target.layers[i]
        p_layer = player.layers[i]
        
        # 1. Shape
        total_checks += 1
        if p_layer.shape != t_layer.shape:
            errors.append(f"{tier_label}: Forma incorreta ({Shape.LABELS.get(p_layer.shape, 'Nenhuma')} em vez de {Shape.LABELS.get(t_layer.shape)}).")
        else:
            passed_checks += 1
            
        # 2. Batter
        total_checks += 1
        if p_layer.batter != t_layer.batter:
            errors.append(f"{tier_label}: Massa incorreta ({Batter.LABELS.get(p_layer.batter, 'Nenhuma')} em vez de {Batter.LABELS.get(t_layer.batter)}).")
        else:
            passed_checks += 1
            
        # 3. Filling
        if t_layer.filling is not None:
            total_checks += 1
            if p_layer.filling != t_layer.filling:
                errors.append(f"{tier_label}: Recheio incorreto ({Filling.LABELS.get(p_layer.filling, 'Nenhum')} em vez de {Filling.LABELS.get(t_layer.filling)}).")
            else:
                passed_checks += 1
        elif p_layer.filling is not None:
            total_checks += 1
            errors.append(f"{tier_label}: Adicionou recheio quando não era pedido.")
            
        # 4. Frosting
        if t_layer.frosting is not None:
            total_checks += 1
            if p_layer.frosting != t_layer.frosting:
                errors.append(f"{tier_label}: Cobertura incorreta ({Frosting.LABELS.get(p_layer.frosting, 'Nenhuma')} em vez de {Frosting.LABELS.get(t_layer.frosting)}).")
            else:
                passed_checks += 1
                
        # 5. Topping
        if t_layer.topping is not None:
            total_checks += 1
            if p_layer.topping != t_layer.topping:
                errors.append(f"{tier_label}: Confeito incorreto ({Topping.LABELS.get(p_layer.topping, 'Nenhum')} em vez de {Topping.LABELS.get(t_layer.topping)}).")
            else:
                passed_checks += 1
        elif p_layer.topping is not None:
            total_checks += 1
            errors.append(f"{tier_label}: Confeito colocado sem ter sido pedido.")

    is_match = (len(errors) == 0)
    accuracy = (passed_checks / max(1, total_checks))
    score = int(1000 * accuracy) if not is_match else 1000
    
    return is_match, score, errors
