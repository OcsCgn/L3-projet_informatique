import networkx as nx
import random
import matplotlib.pyplot as plt 

class MapGenerator:
    def __init__(self, largeur, hauteur, endurance_max):
        self.L = largeur
        self.H = hauteur
        self.endurance_max = endurance_max
        self.G = nx.Graph() # Création du graphe vide

    def generer_niveau(self, difficulte):
        # 1. On définit le nombre de villes selon la difficulté
        params = {
            "facile":  {"n": 10, "dist": 300},
            "moyen":   {"n": 15, "dist": 200},
            "difficile": {"n": 20, "dist": 150}
        }
        p = params[difficulte]

        # 2. On génère des positions aléatoires pour chaque ville
        for i in range(p["n"]):
            self.G.add_node(i, pos=(random.randint(50, self.L-50), 
                                    random.randint(50, self.H-50)))

        # 3. On crée les routes (arêtes) si les villes sont assez proches
        for i in self.G.nodes():
            for j in self.G.nodes():
                if i != j:
                    pos_i = self.G.nodes[i]['pos']
                    pos_j = self.G.nodes[j]['pos']
                    # Calcul de la distance euclidienne (le "poids")
                    dist = ((pos_i[0]-pos_j[0])**2 + (pos_i[1]-pos_j[1])**2)**0.5
                    
                    if dist < p["dist"]:
                        self.G.add_edge(i, j, weight=dist)

        # 4. LE TEST DE VALIDATION (Théorie des graphes)
        if not self.verifier_jouabilite():
            print("Map impossible, on recommence...")
            return self.generer_niveau(difficulte) # Récursion pour régénérer

    def verifier_jouabilite(self):
        try:
            # Dijkstra pour trouver la longueur du chemin le plus court entre ville 0 et la dernière
            longueur = nx.shortest_path_length(self.G, source=0, target=len(self.G.nodes)-1, weight='weight')
            return longueur <= self.endurance_max
        except nx.NetworkXNoPath:
            return False



# On initialise avec des valeurs cohérentes
largeur, hauteur = 800, 600
endurance = 1500
# Création de l'objet
ma_map = MapGenerator(largeur, hauteur, endurance)
ma_map.generer_niveau("difficile")

# Pour dessiner avec NetworkX et voir les positions réelles (x, y)
pos = nx.get_node_attributes(ma_map.G, 'pos')
nx.draw(ma_map.G, pos, with_labels=True, node_size=500, node_color='skyblue')

# Afficher la fenêtre de debug (ceci n'est pas Pygame, c'est pour ton test de ce soir)
plt.show()