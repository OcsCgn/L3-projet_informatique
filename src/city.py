import pygame

class City:
    def __init__(self, city_id, x, y):
        self.id = city_id
        self.x = x
        self.y = y
        self.radius = 16
        self.visible = False

    def draw(self, screen):
        if not self.visible:
            return

        pygame.draw.circle(screen, (220, 220, 220), (self.x, self.y), self.radius)
        font = pygame.font.SysFont(None, 18)
        text = font.render(str(self.id), True, (0, 0, 0))
        screen.blit(text, (self.x - 6, self.y - 9))
