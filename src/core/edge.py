import pygame
import utils.settings as st
from core.node import Node
import math

class Edge:
    """Arête pondérée non orientée entre deux nœuds."""

    def __init__(self, node_a: Node, node_b: Node, weight: int):
        self.node_a = node_a
        self.node_b = node_b
        self.weight = weight

        self.edge_visited = []

    def other(self, node: Node) -> Node:
        """Retourne l'autre extrémité de l'arête."""
        return self.node_b if node is self.node_a else self.node_a

    def midpoint(self) -> tuple:
        mx = (self.node_a.x + self.node_b.x) // 2
        my = (self.node_a.y + self.node_b.y) // 2
        return (mx, my)

    def draw(self, surface: pygame.Surface, color: tuple, width: int,
             font_tiny: pygame.font.Font,
             shadow: bool = False, alpha_overlay: bool = False,player_node = None):
        """Dessine l'arête et affiche son poids."""
        a, b = self.node_a.pos, self.node_b.pos
        pygame.draw.line(surface, color, a, b, width)
        
        # Poids au milieu pour seulement le point de départ et les points visités
        if self.node_a is player_node or self.node_b is player_node or self.node_a.visited or self.node_b.visited:
            mid = self.midpoint()
            w_surf = font_tiny.render(str(self.weight), True, st.C_TEXT)
            bg_rect = w_surf.get_rect(center=mid).inflate(6, 2)
            pygame.draw.rect(surface, st.C_BG, bg_rect, border_radius=3)
            surface.blit(w_surf, w_surf.get_rect(center=mid))
