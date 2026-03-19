import pygame



# ─────────────────────────────────────────────
#  CONSTANTES GLOBALES
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1500, 750
FPS = 60
GRAPH_AREA = pygame.Rect(0, 0, SCREEN_W, SCREEN_H - 110)  # zone graphe
HUD_AREA   = pygame.Rect(0, SCREEN_H - 110, SCREEN_W, 110)

NUM_NODES_MIN, NUM_NODES_MAX = 10, 15
MARGIN = 90          # marge par rapport aux bords pour placer les nœuds
MIN_DIST = 130       # distance minimale entre deux nœuds
EDGE_EXTRA = 2       # arêtes supplémentaires ajoutées au MST pour créer des cycles
WEIGHT_MIN, WEIGHT_MAX = 5, 20   # coût des arêtes
KNIGHT_SPEED = 160   # pixels / seconde lors du déplacement
PLAYER_MAX_ENERGY = 120
DYNAMIC_INTERVAL = 8  # secondes entre chaque mutation du graphe

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
]

# Émojis-texte pour les types de lieux (dessinés en formes géométriques)
NODE_TYPES = ["village", "castle", "forest", "ruin", "port"]
