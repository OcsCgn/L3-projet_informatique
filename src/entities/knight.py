import core.node as Node
import utils.settings as st
import core.edge as Edge
import pygame
import math 


class Knight:
    """
    Sprite du chevalier.
    Se déplace visuellement le long d'une arête entre deux nœuds.
    """

    SIZE = 20   # rayon du sprite

    def __init__(self, start_node: Node, max_energy: int):
        self.current_node = start_node
        self.px = float(start_node.x)   # position pixel actuelle
        self.py = float(start_node.y)
        self.energy = max_energy
        self.max_energy = max_energy
        self.moving = False
        self.target_node: st.Optional[Node] = None
        self.move_edge: st.Optional[Edge] = None
        self.move_progress = 0.0   # 0.0 → 1.0

    def move_to(self, target: Node, edge: Edge):
        """Lance un déplacement vers target via edge."""
        if self.moving:
            return
        self.target_node = target
        self.move_edge = edge
        self.move_progress = 0.0
        self.moving = True

    def update(self, dt: float) -> bool:
        """
        Met à jour la position du sprite.
        Retourne True quand l'arrivée est atteinte.
        """
        if not self.moving:
            return False

        dist = math.hypot(
            self.target_node.x - self.current_node.x,
            self.target_node.y - self.current_node.y)
        if dist < 1:
            self._arrive()
            return True

        speed_norm = st.KNIGHT_SPEED / dist
        self.move_progress += dt * speed_norm
        if self.move_progress >= 1.0:
            self._arrive()
            return True

        # Interpolation linéaire
        t = self.move_progress
        self.px = self.current_node.x + t * (self.target_node.x - self.current_node.x)
        self.py = self.current_node.y + t * (self.target_node.y - self.current_node.y)
        return False

    def _arrive(self):
        self.energy -= self.move_edge.weight
        self.current_node = self.target_node
        self.px = float(self.current_node.x)
        self.py = float(self.current_node.y)
        self.current_node.visited = True
        self.moving = False
        self.target_node = None
        self.move_edge = None
        self.move_progress = 0.0

    def draw(self, surface: pygame.Surface):
        """Dessine le chevalier (♞ stylisé)."""
        cx, cy = int(self.px), int(self.py)

        # Halo lumineux
        glow = pygame.Surface((self.SIZE * 4, self.SIZE * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 60, 60),
                           (self.SIZE * 2, self.SIZE * 2), self.SIZE * 2)
        surface.blit(glow, (cx - self.SIZE * 2, cy - self.SIZE * 2))

        # Corps du chevalier
        pygame.draw.circle(surface, (200, 160, 30), (cx, cy), self.SIZE)
        pygame.draw.circle(surface, st.C_WHITE, (cx, cy), self.SIZE, 2)

        # Symbole ♞
        font = pygame.font.SysFont("segoeuisymbol,symbola,unifont", 22)
        sym = font.render("♞", True, st.C_BG)
        surface.blit(sym, sym.get_rect(center=(cx, cy)))

