import pygame 
import utils.settings as st
from entities.knight import Knight


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

        #bouton restart
        self.restart_button = pygame.Rect(0, 0, 110, 30)

        self.menu_btn = pygame.Rect(0, 0, 150, 30)

    def push_message(self, text: str):
        self.messages.append([text, self.MSG_DURATION])

    def update(self, dt: float):
        self.messages = [[t, d - dt] for t, d in self.messages if d - dt > 0]

    def draw(self, surface: pygame.Surface, knight: Knight,
             goal_node, moves: int):
        """Dessine le HUD en bas de l'écran."""

        # ======================
        # fond hud
        # ======================
        pygame.draw.rect(surface, st.C_HUD_BG, st.HUD_AREA)
        pygame.draw.line(surface, st.C_EDGE, (0, st.HUD_AREA.top),
                         (st.SCREEN_W, st.HUD_AREA.top), 2)

        # ======================
        # energie (gauche)
        # ======================
        bar_x, bar_y = 20, st.HUD_AREA.top + 15
        bar_w, bar_h = 260, 27

        ratio = max(0, knight.energy / knight.max_energy)
        fill_color = st.C_ENERGY_OK if ratio > 0.35 else st.C_ENERGY_LOW

        pygame.draw.rect(surface, (40, 40, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, fill_color,
                         (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
        pygame.draw.rect(surface, st.C_WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

        energy_txt = self.font_small.render(
            f"Énergie : {knight.energy} / {knight.max_energy}", True, st.C_TEXT)
        surface.blit(energy_txt, (bar_x + 6, bar_y + 2))

        # ======================
        # infos (gauche bas)
        # ======================
        pos_txt = self.font_small.render(
            f"Lieu : {knight.current_node.name}   →   Objectif : {goal_node.name}",
            True, st.C_GOLD)
        surface.blit(pos_txt, (20, st.HUD_AREA.top + 48))

        move_txt = self.font_tiny.render(f"Déplacements : {moves}", True, st.C_TEXT)
        surface.blit(move_txt, (20, st.HUD_AREA.top + 74))

        # ======================
        # légende (CENTRÉE PROPRE)
        # ======================
        center_x = st.SCREEN_W // 2
        y = st.HUD_AREA.top + 48

        spacing = 160

        elements = [
            (st.C_NODE_GOAL, "Objectif"),
            (st.C_NODE_PLAYER, "Vous"),
            (st.C_NODE_VISIT, "Visité"),
        ]

        total_width = spacing * (len(elements) - 1)
        start_x = center_x - total_width // 2

        for i, (color, label) in enumerate(elements):
            x = start_x + i * spacing

            pygame.draw.circle(surface, color, (x, y + 6), 8)

            txt = self.font_tiny.render(label, True, st.C_TEXT)
            surface.blit(txt, (x + 14, y))

        # ======================
        # bouton restart (droite)
        # ======================

        restart_x = st.SCREEN_W - 150
        restart_y = y - 20

        self.restart_button.topleft = (restart_x, restart_y)

        mouse_pos = pygame.mouse.get_pos()

        if self.restart_button.collidepoint(mouse_pos):
            btn_color = (220, 60, 60)
        else:
            btn_color = (180, 40, 40)

        pygame.draw.rect(surface, btn_color, self.restart_button, border_radius=6)

        txt = self.font_tiny.render("Restart", True, st.C_WHITE)
        surface.blit(txt,
            (self.restart_button.x + self.restart_button.width//2 - txt.get_width()//2,
             self.restart_button.y + 6)
        )


        #Bouton pour retourner au menu

        menu_x = st.SCREEN_W - 310
        menu_y = y - 20

        self.menu_btn.topleft = (menu_x, menu_y)

        mouse_pos = pygame.mouse.get_pos()

        if self.menu_btn.collidepoint(mouse_pos):
            btn_color = (220, 60, 60)
        else:
            btn_color = (180, 40, 40)

        pygame.draw.rect(surface, btn_color, self.menu_btn, border_radius=6)

        txt = self.font_tiny.render("Retour au menu", True, st.C_WHITE)
        surface.blit(txt,
            (self.menu_btn.x + self.menu_btn.width//2 - txt.get_width()//2,
             self.menu_btn.y + 6)
        )

        # ======================
        # controles
        # ======================
        ctrl = self.font_tiny.render(
            "Clic sur un nœud adjacent pour se déplacer  |  R : Nouvelle partie",
            True, (120, 130, 160))
        surface.blit(ctrl, (center_x - ctrl.get_width()//2, st.HUD_AREA.top + 80))

        # ======================
        # messages
        # ======================
        for i, (msg, timer) in enumerate(reversed(self.messages[-4:])):
            alpha = min(255, int(255 * timer))
            msg_surf = self.font_small.render(msg, True,
                                              (255, 255, 100, alpha))
            surface.blit(msg_surf, (20, 10 + i * 26))