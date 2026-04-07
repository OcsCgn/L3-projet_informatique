import pygame 
import utils.settings as st

class Node:
    """Représente un nœud (lieu) du graphe."""

    RADIUS = 22

    def __init__(self, node_id: int, x: int, y: int, name: str, node_type: str):
        self.id = node_id
        self.x = x
        self.y = y
        self.name = name
        self.node_type = node_type
        self.visited = False
        self.healed = False 

    @property
    def pos(self) -> tuple:
        return (self.x, self.y)

    def draw(self, surface: pygame.Surface, state: str,
             font_small: pygame.font.Font, font_tiny: pygame.font.Font,
             shadow: bool = False):
        """
        Dessine le nœud avec son icône et son nom.
        state : 'default' | 'hover' | 'player' | 'goal' | 'visited'
        """
        color = {
            "default": st.C_NODE_DEF,
            "hover":   st.C_NODE_HOVER,
            "player":  st.C_NODE_PLAYER,
            "goal":    st.C_NODE_GOAL,
            "visited": st.C_NODE_VISIT,
        }.get(state, st.C_NODE_DEF)

        # Cercle principal
        pygame.draw.circle(surface, color, self.pos, self.RADIUS)
        pygame.draw.circle(surface, st.C_WHITE, self.pos, self.RADIUS, 2)

        if self.node_type == "village" and not self.healed:
            pygame.draw.circle(surface, st.C_ENERGY_OK, self.pos, self.RADIUS + 4, 3)

        # Icône selon le type
        icon = {"village": "⌂", "castle": "♜", "forest": "♣",
                "ruin": "☩", "port": "⚓"}.get(self.node_type, "●")
        icon_surf = font_small.render(icon, True, st.C_BG)
        icon_rect = icon_surf.get_rect(center=self.pos)
        surface.blit(icon_surf, icon_rect)

        # Nom sous le nœud
        name_surf = font_tiny.render(self.name, True, st.C_TEXT)
        name_rect = name_surf.get_rect(
            midtop=(self.x, self.y + self.RADIUS + 4))
        surface.blit(name_surf, name_rect)

