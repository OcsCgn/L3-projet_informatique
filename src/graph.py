import pygame
from city import City

class Graph:
    def __init__(self):
        self.cities = {}
        self.edges = {}

    def add_city(self, city_id, x, y):
        self.cities[city_id] = City(city_id, x, y)
        self.edges[city_id] = []

    def add_edge(self, a, b, cost):
        self.edges[a].append((b, cost))
        self.edges[b].append((a, cost))

    def reveal_city_and_neighbors(self, city_id):
        self.cities[city_id].visible = True
        for neighbor_id, _ in self.edges[city_id]:
            self.cities[neighbor_id].visible = True

    def draw(self, screen):
        # routes
        for a, neighbors in self.edges.items():
            if not self.cities[a].visible:
                continue
            for b, _ in neighbors:
                if self.cities[b].visible:
                    pygame.draw.line(
                        screen, (120, 120, 120),
                        (self.cities[a].x, self.cities[a].y),
                        (self.cities[b].x, self.cities[b].y), 2
                    )

        # villes
        for city in self.cities.values():
            city.draw(screen)
