import os
import math
import pygame


class Player:
    def __init__(self, start_city_id):
        self.current_city = start_city_id
        self.target_city = None
        self.state = "idle"
        self.speed = 2

        self.max_energy = 100
        self.energy = 100

        # Pour affichage perte/gain
        self.energy_message = ""
        self.energy_message_timer = 0

        base_path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_path, "assets", "knight.png")

        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.dir_x = 0.0
        self.dir_y = 0.0

    def place_on_city(self, city):
        self.pos_x = float(city.x)
        self.pos_y = float(city.y)
        self.rect.center = (city.x, city.y)

    def can_move(self, cost):
        return cost is not None and self.energy >= cost

    def consume_energy(self, cost):
        self.energy -= cost
        if self.energy < 0:
            self.energy = 0

        # Message perte énergie
        self.energy_message = f"-{cost} énergie"
        self.energy_message_timer = 60  # durée affichage (frames)

    def start_moving(self, from_city, to_city):
        dx = to_city.x - from_city.x
        dy = to_city.y - from_city.y
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        self.dir_x = dx / dist
        self.dir_y = dy / dist
        self.target_city = to_city
        self.state = "moving"

    def update(self):
        if self.state == "moving" and self.target_city is not None:
            self.pos_x += self.dir_x * self.speed
            self.pos_y += self.dir_y * self.speed
            self.rect.center = (int(self.pos_x), int(self.pos_y))

            remaining = math.hypot(
                self.target_city.x - self.pos_x,
                self.target_city.y - self.pos_y
            )

            if remaining < self.speed:
                self.place_on_city(self.target_city)
                self.current_city = self.target_city.id
                self.target_city = None
                self.state = "idle"

        # Timer message énergie
        if self.energy_message_timer > 0:
            self.energy_message_timer -= 1

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def draw_energy_bar(self, screen):
        bar_width = 250
        bar_height = 25
        x = 20
        y = 60  # ESPACE SOUS LE NOM

        ratio = self.energy / self.max_energy
        fill_width = int(bar_width * ratio)

        # Fond
        pygame.draw.rect(screen, (60, 60, 60), (x, y, bar_width, bar_height), border_radius=8)

        # Dégradé simple
        if ratio > 0.5:
            color = (0, 200, 0)
        elif ratio > 0.25:
            color = (255, 165, 0)
        else:
            color = (200, 0, 0)

        pygame.draw.rect(screen, color, (x, y, fill_width, bar_height), border_radius=8)

        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2, border_radius=8)

        # Texte énergie centré
        font = pygame.font.SysFont(None, 22)
        text = font.render(f"{self.energy} / {self.max_energy}", True, (255,255,255))
        screen.blit(text, (x + bar_width//2 - text.get_width()//2, y + 3))

        # Message perte énergie
        if self.energy_message_timer > 0:
            msg_font = pygame.font.SysFont(None, 28)
            msg = msg_font.render(self.energy_message, True, (255, 0, 0))
            screen.blit(msg, (x + bar_width + 20, y))