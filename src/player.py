import pygame
import math

class Player:
    def __init__(self, start_city_id):
        self.current_city = start_city_id
        self.target_city = None
        self.state = "idle"
        self.speed = 2

        self.image = pygame.image.load("assets/knight.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()

        self.pos_x = 0
        self.pos_y = 0

    def place_on_city(self, city):
        self.pos_x = city.x
        self.pos_y = city.y
        self.rect.center = (city.x, city.y)

    def start_moving(self, from_city, to_city):
        self.state = "moving"
        self.target_city = to_city

        dx = to_city.x - from_city.x
        dy = to_city.y - from_city.y
        dist = math.hypot(dx, dy)

        self.dir_x = dx / dist
        self.dir_y = dy / dist

    def update(self):
        if self.state == "moving":
            self.pos_x += self.dir_x * self.speed
            self.pos_y += self.dir_y * self.speed
            self.rect.center = (self.pos_x, self.pos_y)

            if math.hypot(
                self.target_city.x - self.pos_x,
                self.target_city.y - self.pos_y
            ) < self.speed:
                self.place_on_city(self.target_city)
                self.current_city = self.target_city.id
                self.state = "idle"

    def draw(self, screen):
        screen.blit(self.image, self.rect)
