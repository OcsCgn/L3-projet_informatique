from os import name
import pygame
from setting import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, name, energie, life, invetory):
        super().__init__(group)
        self.name = name 
        self.energie = energie
        self.life = life
        self.invetory = invetory
        self.score = 0



        #Définition de l'image du joueur
        

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['tool use'].active:
            #direction	
            if keys[pygame.K_LEFT] or keys[pygame.K_q]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            else :
                self.direction.x = 0
                
            if keys[pygame.K_UP] or keys[pygame.K_z]:
                self.direction.y = -1	
                self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'	
            else:
                self.direction.y = 0
