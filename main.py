from setting import *
import pygame,sys
from src import map 
class Game : 
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SECREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title = pygame.display.set_caption("Adventure Game")
        self.map = map.Map('facile')


    def run(self): 
        while True :
            for event in pygame.event.get() : 
                if event.type == pygame.QUIT : 
                    pygame.quit() 
                    sys.exit()
                
            dt = self.clock.tick(60) / 1000 
            self.map.dessiner(self.screen)
            
            
            pygame.display.update()


if __name__ == '__main__' :
    game = Game()
    game.run()
                

