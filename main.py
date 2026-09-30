"""
Purble Bakery - Comfy Cakes Edition
Jogo inspirado no clássico Purble Place do Windows 7.
"""
import os
import sys

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from game.engine import GameEngine

def main():
    try:
        engine = GameEngine(screen_width=1024, screen_height=640)
        engine.run()
    except KeyboardInterrupt:
        print("Jogo finalizado pelo usuário.")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
