import pygame 
import settings as st
from knight import Knight


class HUD:
    """
    Interface utilisateur : barre d'énergie, messages, légende.
    """

    def __init__(self, font_small, font_tiny, font_title):
        self.font_small = font_small
        self.font_tiny  = font_tiny
        self.font_title = font_title
        self.messages   = []   # liste de (texte, timer)
        self.MSG_DURATION = 4.0

    def push_message(self, text: str):
        self.messages.append([text, self.MSG_DURATION])

    def update(self, dt: float):
        self.messages = [[t, d - dt] for t, d in self.messages if d - dt > 0]

    def draw(self, surface: pygame.Surface, knight: Knight,
             goal_node, moves: int, dynamic_timer: float):
        """Dessine le HUD en bas de l'écran."""
        # Fond HUD
        pygame.draw.rect(surface, st.C_HUD_BG, st.HUD_AREA)
        pygame.draw.line(surface, st.C_EDGE, (0, st.HUD_AREA.top),
                         (st.SCREEN_W, st.HUD_AREA.top), 2)

        # Barre d'énergie
        bar_x, bar_y = 20, st.HUD_AREA.top + 18
        bar_w, bar_h = 260, 22
        ratio = max(0, knight.energy / knight.max_energy)
        fill_color = st.C_ENERGY_OK if ratio > 0.35 else st.C_ENERGY_LOW
        pygame.draw.rect(surface, (40, 40, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, fill_color,
                         (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
        pygame.draw.rect(surface, st.C_WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
        energy_txt = self.font_small.render(
            f"Énergie : {knight.energy} / {knight.max_energy}", True, st.C_TEXT)
        surface.blit(energy_txt, (bar_x + 4, bar_y + 2))

        # Position courante et objectif
        pos_txt = self.font_small.render(
            f"Lieu : {knight.current_node.name}   →   Objectif : {goal_node.name}",
            True,st.C_GOLD)
        surface.blit(pos_txt, (20, st.HUD_AREA.top + 52))

        # Compteur de mouvements
        move_txt = self.font_tiny.render(f"Déplacements : {moves}", True, st.C_TEXT)
        surface.blit(move_txt, (20, st.HUD_AREA.top + 78))

        # Légende
        leg_x = 300
        leg_y = st.HUD_AREA.top + 42
        legends = [
            (st.C_EDGE_BEST,   "Chemin optimal"),
            (st.C_NODE_GOAL,   "Objectif"),
            (st.C_NODE_PLAYER, "Vous"),
            (st.C_NODE_VISIT,  "Visité"),
        ]
        for i, (col, label) in enumerate(legends):
            lx = leg_x + i * 190
            pygame.draw.circle(surface, col, (lx, leg_y + 8), 8)
            lt = self.font_tiny.render(label, True, st.C_TEXT)
            surface.blit(lt, (lx + 14, leg_y))

        # Contrôles
        ctrl = self.font_tiny.render(
            "Clic sur un nœud adjacent pour se déplacer  |  R : Nouvelle partie",
            True, (120, 130, 160))
        surface.blit(ctrl, (300, st.HUD_AREA.top + 80))

        # Messages dynamiques (en haut à gauche)
        for i, (msg, timer) in enumerate(reversed(self.messages[-4:])):
            alpha = min(255, int(255 * timer))
            msg_surf = self.font_small.render(msg, True,
                                              (255, 255, 100, alpha))
            surface.blit(msg_surf, (20, 10 + i * 26))

