import pygame
import utils.settings as st
from node import Node
import math

class Edge:
    """Arête pondérée non orientée entre deux nœuds."""

    def __init__(self, node_a: Node, node_b: Node, weight: int):
        self.node_a = node_a
        self.node_b = node_b
        self.weight = weight

    def other(self, node: Node) -> Node:
        """Retourne l'autre extrémité de l'arête."""
        return self.node_b if node is self.node_a else self.node_a

    def midpoint(self) -> tuple:
        mx = (self.node_a.x + self.node_b.x) // 2
        my = (self.node_a.y + self.node_b.y) // 2
        return (mx, my)

    def draw(self, surface: pygame.Surface, color: tuple, width: int,
             font_tiny: pygame.font.Font,
             shadow: bool = False, alpha_overlay: bool = False):
        """Dessine l'arête et affiche son poids."""
        a, b = self.node_a.pos, self.node_b.pos
        pygame.draw.line(surface, color, a, b, width)

        # Poids au milieu
        mid = self.midpoint()
        w_surf = font_tiny.render(str(self.weight), True, st.C_TEXT)
        bg_rect = w_surf.get_rect(center=mid).inflate(6, 2)
        pygame.draw.rect(surface, st.C_BG, bg_rect, border_radius=3)
        surface.blit(w_surf, w_surf.get_rect(center=mid))

        # Voile sombre sur l'arête (mauvaise voie)
        if alpha_overlay:
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            if length < 1:
                return
            overlay = pygame.Surface((int(length) + 4, 14), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            angle = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            rotated = pygame.transform.rotate(overlay, -angle)
            cx = (a[0] + b[0]) // 2
            cy = (a[1] + b[1]) // 2
            surface.blit(rotated, rotated.get_rect(center=(cx, cy)))
