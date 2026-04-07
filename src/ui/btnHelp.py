import pygame
import utils.settings as st

class Button:
    COLOR_ACTIVE   = (255, 180,  0)
    COLOR_HOVER    = (255, 210, 60)
    COLOR_DISABLED = ( 80,  80, 80)
    COLOR_TEXT_ON  = (  0,   0,  0)
    COLOR_TEXT_OFF = (180, 180, 180)
    COLOR_BORDER   = (200, 140,  0)

    def __init__(self, x, y, width, height, label, difficulte="facile", font=None):
        self.rect       = pygame.Rect(x, y, width, height)
        self.label      = label
        self.max_hints  = st.HINTS_PAR_DIFFICULTE.get(difficulte, 1)
        self.hints_left = self.max_hints
        self._hovered   = False
        self.font       = font or pygame.font.SysFont("arial", 14, bold=True)

    @property
    def used(self):
        return self.hints_left <= 0

    def handle_event(self, event):
        """Retourne True si le bouton est cliqué validement."""
        if self.used:
            return False
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.hints_left -= 1
                self._hovered = False
                return True
        return False

    def draw(self, surface):
        if self.used:
            bg         = self.COLOR_DISABLED
            text_color = self.COLOR_TEXT_OFF
            label      = "Indice épuisé"
        elif self._hovered:
            bg         = self.COLOR_HOVER
            text_color = self.COLOR_TEXT_ON
            label      = f"❔ Indice ({self.hints_left} restant{'s' if self.hints_left > 1 else ''})"
        else:
            bg         = self.COLOR_ACTIVE
            text_color = self.COLOR_TEXT_ON
            label      = f"❔ Indice ({self.hints_left})"

        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        if not self.used:
            pygame.draw.rect(surface, self.COLOR_BORDER, self.rect, 2, border_radius=8)
        
        text = self.font.render(label, True, text_color)
        surface.blit(text, text.get_rect(center=self.rect.center))