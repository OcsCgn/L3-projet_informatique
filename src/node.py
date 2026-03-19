import pygame 
import settings as st

class Node:
    """Représente un nœud (lieu) du graphe."""

    RADIUS = 22

    def __init__(self, node_id: int, x: int, y: int, name: str, node_type: str):
        self.id = node_id
        self.x = x
        self.y = y
        self.name = name
        self.node_type = node_type
        self.visited = False        # le chevalier y est déjà passé

    @property
    def pos(self) -> tuple:
        return (self.x, self.y)

    def draw(self, surface: pygame.Surface, state: str,
             font_small: pygame.font.Font, font_tiny: pygame.font.Font,
             shadow: bool = False):
        """
        Dessine le nœud avec son icône et son nom.
        state : 'default' | 'hover' | 'player' | 'goal' | 'visited'
        shadow : superpose un voile sombre "mauvaise voie"
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

        # Overlay sombre si mauvaise voie
        if shadow:
            shadow_surf = pygame.Surface(
                (self.RADIUS * 2 + 4, self.RADIUS * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surf, (0, 0, 0, 190),
                               (self.RADIUS + 2, self.RADIUS + 2),
                               self.RADIUS + 2)
            surface.blit(shadow_surf,
                         (self.x - self.RADIUS - 2, self.y - self.RADIUS - 2))

