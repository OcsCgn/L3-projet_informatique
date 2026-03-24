import pygame
from utils.manager_score import load_scores, add_score
import utils.settings as st
from tkinter import messagebox
import tkinter as tk

class Menu:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        self.root = tk.Tk()

        self.left_width = int(width * 0.6)
        self.right_width = width - self.left_width

        # Fonts
        self.font_big = pygame.font.SysFont(None, st.MENU_FONT_BIG)
        self.font_medium = pygame.font.SysFont(None, st.MENU_FONT_MEDIUM)
        self.font_small = pygame.font.SysFont(None, st.MENU_FONT_SMALL)

        # INPUT
        self.player_name = ""
        self.input_active = True

        self.input_box = pygame.Rect(
            self.left_width//2 - 150,
            230,
            300,
            50
        )

        # START BUTTON
        self.start_button = pygame.Rect(
            self.left_width//2 - 100,
            420,
            200,
            50
        )

        # DIFFICULTÉ
        self.difficulty = "facile"
        self.diff_buttons = {
            "facile": pygame.Rect(0, 0, 100, 40),
            "moyen": pygame.Rect(0, 0, 100, 40),
            "difficile": pygame.Rect(0, 0, 120, 40),
        }

        # CURSOR
        self.cursor_visible = True
        self.cursor_timer = 0

        # SCORES (JSON)


    # ======================
    # EVENTS
    # ======================

    def handle_event(self, event):

        self.scores_data = load_scores()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_RETURN:
                if self.player_name.strip():
                    return "start"
            else:
                if len(self.player_name) < 15:
                    self.player_name += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:

            # Sélection difficulté
            for diff, rect in self.diff_buttons.items():
                if rect.collidepoint(event.pos):
                    self.difficulty = diff
                    

            # Bouton START
            if self.start_button.collidepoint(event.pos):
                if self.player_name.strip():
                    return "start"
                else : 
                    self.root.withdraw()  # Cacher la fenêtre principale Tkinter
                    messagebox.showerror("Erreur", "Veuillez entrer un nom de joueur valide !")
        return None
    # 
    # ======================
    # UPDATE
    # ======================

    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    # ======================
    # DRAW
    # ======================

    def draw(self, screen):
        screen.fill((20, 20, 25))
        mouse_pos = pygame.mouse.get_pos()

        # ===== LEFT PANEL =====
        pygame.draw.rect(screen, (30, 30, 35), (0, 0, self.left_width, self.HEIGHT))
        center_x = self.left_width // 2

        # TITLE
        title = self.font_big.render("ENTREZ VOTRE NOM", True, (240,240,240))
        screen.blit(title, (center_x - title.get_width()//2, 100))

        # INPUT
        pygame.draw.rect(screen, (60,60,70), self.input_box, border_radius=10)
        pygame.draw.rect(screen, (0,180,255), self.input_box, 2, border_radius=10)

        display_text = self.player_name + ("|" if self.cursor_visible else "")
        name_surface = self.font_medium.render(display_text, True, (255,255,255))
        screen.blit(name_surface, (self.input_box.x + 10, self.input_box.y + 10))

        # ===== DIFFICULTÉ =====
        diff_y = self.input_box.y + 90

        buttons = list(self.diff_buttons.items())
        total_width = sum(rect.width for _, rect in buttons) + 20 * (len(buttons) - 1)
        start_x = center_x - total_width // 2

        current_x = start_x

        colors = {
            "facile": (0, 200, 100),      # vert
            "moyen": (255, 140, 0),      # orange
            "difficile": (220, 50, 50)   # rouge
        }

        for diff, rect in buttons:
            rect.x = current_x
            rect.y = diff_y
            current_x += rect.width + 20

            selected = self.difficulty == diff
            hover = rect.collidepoint(mouse_pos)

            base_color = colors[diff]

            if selected:
                color = base_color
            else:
                color = (60, 60, 70)

            if hover:
                if selected:
                    color = tuple(min(c + 40, 255) for c in base_color)
                else:
                    color = (100, 100, 120)

            # Glow
            if selected:
                glow = rect.inflate(10, 10)
                pygame.draw.rect(screen, base_color, glow, border_radius=15)

            pygame.draw.rect(screen, color, rect, border_radius=12)

            text = self.font_small.render(diff.upper(), True, (255,255,255))
            screen.blit(text,
                (rect.x + rect.width//2 - text.get_width()//2,
                 rect.y + 8)
            )

        # ===== START BUTTON =====
        self.start_button.y = diff_y + 90

        hover = self.start_button.collidepoint(mouse_pos)
        btn_color = (0, 220, 120) if hover else (0, 180, 100)

        glow = self.start_button.inflate(10, 10)
        pygame.draw.rect(screen, (0,200,120), glow, border_radius=15)
        pygame.draw.rect(screen, btn_color, self.start_button, border_radius=15)

        start_text = self.font_small.render("START", True, (255,255,255))
        screen.blit(start_text,
            (self.start_button.x + self.start_button.width//2 - start_text.get_width()//2,
             self.start_button.y + 12)
        )

        # ===== RIGHT PANEL =====
        pygame.draw.rect(screen, (15, 15, 20),
                         (self.left_width, 0, self.right_width, self.HEIGHT))

        lb_title = self.font_medium.render("LEADERBOARD", True, (255,255,255))
        screen.blit(lb_title,
            (self.left_width + self.right_width//2 - lb_title.get_width()//2, 80)
        )

        scores = self.scores_data[self.difficulty]

        y_offset = 150

        if not scores:
            txt = self.font_small.render("Aucun score", True, (120,120,120))
            screen.blit(txt,
                (self.left_width + self.right_width//2 - txt.get_width()//2, y_offset)
            )
        else:
            for i, entry in enumerate(scores):
                text = f"{i+1}. {entry['name']} - {entry['time']}s"
                surf = self.font_small.render(text, True, (200,200,200))
                screen.blit(surf, (self.left_width + 40, y_offset))
                y_offset += 50

                
    def getDifficulty(self):
        return self.difficulty
    
    def getPlayerName(self):
        return self.player_name