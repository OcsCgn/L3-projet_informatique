import pygame



# ─────────────────────────────────────────────
#  CONSTANTES GLOBALES
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1500, 700
FPS = 60
GRAPH_AREA = pygame.Rect(0, 0, SCREEN_W, SCREEN_H - 90)  # zone graphe
HUD_AREA   = pygame.Rect(0, SCREEN_H - 110, SCREEN_W, 110)

MARGIN = 40          # marge par rapport aux bords pour placer les nœuds
MIN_DIST = 110       # distance minimale entre deux nœuds
EDGE_EXTRA = 2       # arêtes supplémentaires ajoutées au MST pour créer des cycles
WEIGHT_MIN, WEIGHT_MAX = 5, 20   # coût des arêtes
KNIGHT_SPEED = 160   # pixels / seconde lors du déplacement
PLAYER_MAX_ENERGY = 200

#Menu settings
MENU_WIDTH = 1500
MENU_HEIGTH = 750
MENU_FONT_BIG = 70
MENU_FONT_MEDIUM = 45
MENU_FONT_SMALL = 30

DIFFICULTY_SETTINGS = {
    "facile": {
        "num_nodes": 20, 
        "difficulty_percent": 10, 
        "edge_dist": 400,
        "energy_margin": 1.8,
        "heal_percent": 0.25 
    },
    "moyen": {
        "num_nodes": 25, 
        "difficulty_percent": 10, # 35% de routes en plus
        "edge_dist": 350,
        "energy_margin": 1.3,
        "heal_percent": 0.15
    },
    "difficile": {
        "num_nodes": 37, 
        "difficulty_percent": 100, 
        "edge_dist": 280,
        "energy_margin": 1.05,
        "heal_percent": 0.05          
    }
}
HINTS_PAR_DIFFICULTE = {
    "facile":    2, # Je te conseille 3 pour facile, 1 c'est trop peu !
    "moyen":     1,
    "difficile": 1,
}


#Main states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_LOSE = "lose"
STATE_WIN = "win"


# Palette de couleurs
C_BG          = (15, 20, 40)       # fond nuit
C_EDGE        = (80, 90, 130)      # arête normale
C_EDGE_BEST   = (80, 220, 130)     # arête du meilleur chemin
C_EDGE_SHADOW = (10, 10, 20)       # arête "mauvaise voie"
C_NODE_DEF    = (50, 70, 180)      # nœud par défaut
C_NODE_HOVER  = (100, 140, 255)    # nœud survolé
C_NODE_PLAYER = (255, 220, 60)     # nœud actuel du joueur
C_NODE_GOAL   = (255, 80, 80)      # nœud objectif
C_NODE_VISIT  = (60, 180, 100)     # nœud déjà visité
C_SHADOW_OVL  = (0, 0, 0, 180)     # overlay sombre "mauvaise voie"
C_TEXT        = (220, 230, 255)
C_HUD_BG      = (10, 12, 28)
C_ENERGY_OK   = (60, 200, 100)
C_ENERGY_LOW  = (220, 80, 60)
C_WHITE       = (255, 255, 255)
C_GOLD        = (255, 200, 50)

# Noms de lieux (pool)
PLACE_NAMES = [
    "Aelindra", "Brumebois", "Castelmor", "Drakenfels", "Elfheim",
    "Frostpeak", "Grimhold", "Harvenfall", "Irongate", "Jadewood",
    "Keldorn", "Lunaris", "Mirefall", "Northpass", "Oldwatch",
    "Port-Sable", "Quartzhelm", "Rive-Argent", "Sombre-Val", "Tour-Cristal",
    "Uldar-Garde", "Val-Serein", "Wildrun", "Xylos", "Yew-Hollow",
    "Zénith", "Ambre-Lumière", "Bas-Fond", "Ciel-D'Orage", "Dague-Fidèle",
    "Épine-Verte", "Forge-Fer", "Grise-Mine", "Haute-Pierre", "Île-Perdue",
    "Jardin-Noble", "Khazad-Bourg", "Louve-Garde", "Mont-Vigile", "Nid-Du-Faucon"
]
# Émojis-texte pour les types de lieux (dessinés en formes géométriques)
NODE_TYPES = ["village", "castle", "forest", "ruin", "port"]
