import pygame
import random
import math

class Map:
    def __init__(self, difficulte):
        self.sommets = {}  # {id: (x, y)}
        self.aretes = []   # [(id1, id2), ...]
        self.difficulte = difficulte
        self.generer_map()

    def generer_map(self):
        # Paramètres selon la difficulté
        if self.difficulte == "facile":
            nb_sommets = 6
            densite = 0.5 # Plus de routes
        elif self.difficulte == "moyen":
            nb_sommets = 12
            densite = 0.3
        else: # difficile
            nb_sommets = 20
            densite = 0.15 # Très peu de routes, plus d'impasses

        # 1. Créer les sommets à des positions aléatoires
        for i in range(nb_sommets):
            x = random.randint(50, 750)
            y = random.randint(50, 550)
            self.sommets[i] = (x, y)

        # 2. Créer les arêtes (on relie les points)
        # Pour être sûr que le jeu est jouable, on peut relier chaque point au suivant
        for i in range(nb_sommets - 1):
            self.aretes.append((i, i + 1))
        
        # 3. Ajouter du chaos selon la densité (routes bonus ou raccourcis)
        for i in self.sommets:
            for j in self.sommets:
                if i != j and (i, j) not in self.aretes and (j, i) not in self.aretes:
                    if random.random() < densite:
                        self.aretes.append((i, j))

    def dessiner(self, screen):
        # Dessiner les routes (arêtes)
        for start_id, end_id in self.aretes:
            pygame.draw.line(screen, (200, 200, 200), self.sommets[start_id], self.sommets[end_id], 2)
        
        # Dessiner les sommets
        for id, pos in self.sommets.items():
            couleur = (255, 0, 0) if id == 0 else (0, 255, 0) # Départ rouge, autres vert
            if id == len(self.sommets) - 1: couleur = (0, 0, 255) # Arrivée bleue
            pygame.draw.circle(screen, couleur, pos, 10)


map  = Map('facile')