"""
=============================================================
 JEU D'AVENTURE - THÉORIE DES GRAPHES
 Prototype Pygame — Chevalier & Quête du Plus Court Chemin
=============================================================
 Structure :
   - Node       : un nœud du graphe (lieu)
   - Edge       : une arête pondérée entre deux nœuds
   - Graph      : le graphe du monde (génération, Dijkstra, A*, dynamisme)
   - Knight     : le sprite joueur (déplacement animé sur les arêtes)
   - HUD        : interface utilisateur (barre d'énergie, messages)
   - Game       : boucle principale, événements, rendu

 Dépendances : Python 3.8+, pygame 2.x
 Installation : pip install pygame
 Lancement    : python graphe_aventure.py
=============================================================
"""

import pygame
import random
import math
import heapq
import sys
from typing import Optional

# ─────────────────────────────────────────────
#  CONSTANTES GLOBALES
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 750
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

# ─── Paramètres par difficulté ────────────────
# (énergie max, intervalle mutation, nb checkpoints)
DIFFICULTY_SETTINGS = {
    "easy":   {"energy": 150, "mutation": 12, "checkpoints": 0, "label": "Facile",   "color": (60, 200, 100)},
    "medium": {"energy": 120, "mutation": 8,  "checkpoints": 1, "label": "Moyen",    "color": (220, 180, 50)},
    "hard":   {"energy": 80,  "mutation": 5,  "checkpoints": 1, "label": "Difficile", "color": (220, 70, 60)},
}

# Couleurs supplémentaires
C_CHECKPOINT = (100, 200, 255)   # nœud checkpoint
C_MENU_BG    = (8, 12, 30)       # fond du menu difficulté

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


# ═════════════════════════════════════════════
#  CLASSE NODE
# ═════════════════════════════════════════════
class Node:
    """Représente un nœud (lieu) du graphe."""

    RADIUS = 22

    def __init__(self, node_id: int, x: int, y: int, name: str, node_type: str):
        self.id = node_id
        self.x = x
        self.y = y
        self.name = name
        self.node_type = node_type
        self.visited = False        # le chevalier y est déjà passé

    @property
    def pos(self) -> tuple:
        return (self.x, self.y)

    def draw(self, surface: pygame.Surface, state: str,
             font_small: pygame.font.Font, font_tiny: pygame.font.Font,
             shadow: bool = False):
        """
        Dessine le nœud avec son icône et son nom.
        state : 'default' | 'hover' | 'player' | 'goal' | 'visited'
        shadow : superpose un voile sombre "mauvaise voie"
        """
        color = {
            "default": C_NODE_DEF,
            "hover":   C_NODE_HOVER,
            "player":  C_NODE_PLAYER,
            "goal":    C_NODE_GOAL,
            "visited": C_NODE_VISIT,
        }.get(state, C_NODE_DEF)

        # Cercle principal
        pygame.draw.circle(surface, color, self.pos, self.RADIUS)
        pygame.draw.circle(surface, C_WHITE, self.pos, self.RADIUS, 2)

        # Icône selon le type
        icon = {"village": "⌂", "castle": "♜", "forest": "♣",
                "ruin": "☩", "port": "⚓"}.get(self.node_type, "●")
        icon_surf = font_small.render(icon, True, C_BG)
        icon_rect = icon_surf.get_rect(center=self.pos)
        surface.blit(icon_surf, icon_rect)

        # Nom sous le nœud
        name_surf = font_tiny.render(self.name, True, C_TEXT)
        name_rect = name_surf.get_rect(
            midtop=(self.x, self.y + self.RADIUS + 4))
        surface.blit(name_surf, name_rect)

        # Overlay sombre si mauvaise voie
        if shadow:
            shadow_surf = pygame.Surface(
                (self.RADIUS * 2 + 4, self.RADIUS * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surf, (0, 0, 0, 190),
                               (self.RADIUS + 2, self.RADIUS + 2),
                               self.RADIUS + 2)
            surface.blit(shadow_surf,
                         (self.x - self.RADIUS - 2, self.y - self.RADIUS - 2))


# ═════════════════════════════════════════════
#  CLASSE EDGE
# ═════════════════════════════════════════════
class Edge:
    """Arête pondérée non orientée entre deux nœuds."""

    def __init__(self, node_a: Node, node_b: Node, weight: int):
        self.node_a = node_a
        self.node_b = node_b
        self.weight = weight

    def other(self, node: Node) -> Node:
        """Retourne l'autre extrémité de l'arête."""
        return self.node_b if node is self.node_a else self.node_a

    def midpoint(self) -> tuple:
        mx = (self.node_a.x + self.node_b.x) // 2
        my = (self.node_a.y + self.node_b.y) // 2
        return (mx, my)

    def draw(self, surface: pygame.Surface, color: tuple, width: int,
             font_tiny: pygame.font.Font,
             shadow: bool = False, alpha_overlay: bool = False):
        """Dessine l'arête et affiche son poids."""
        a, b = self.node_a.pos, self.node_b.pos
        pygame.draw.line(surface, color, a, b, width)

        # Poids au milieu
        mid = self.midpoint()
        w_surf = font_tiny.render(str(self.weight), True, C_TEXT)
        bg_rect = w_surf.get_rect(center=mid).inflate(6, 2)
        pygame.draw.rect(surface, C_BG, bg_rect, border_radius=3)
        surface.blit(w_surf, w_surf.get_rect(center=mid))

        # Voile sombre sur l'arête (mauvaise voie)
        if alpha_overlay:
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            if length < 1:
                return
            overlay = pygame.Surface((int(length) + 4, 14), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            angle = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            rotated = pygame.transform.rotate(overlay, -angle)
            cx = (a[0] + b[0]) // 2
            cy = (a[1] + b[1]) // 2
            surface.blit(rotated, rotated.get_rect(center=(cx, cy)))


# ═════════════════════════════════════════════
#  CLASSE GRAPH
# ═════════════════════════════════════════════
class Graph:
    """
    Graphe du monde de jeu.
    Gère : génération aléatoire, Dijkstra, A*,
           mutations dynamiques (ajout/suppression d'arête).
    """

    def __init__(self):
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []
        self._adj: dict[int, list[Edge]] = {}   # liste d'adjacence id → [Edge]

    # ─── Génération ─────────────────────────────
    def generate(self, n_nodes: int):
        """Génère un graphe connexe aléatoire avec n_nodes nœuds."""
        self.nodes.clear()
        self.edges.clear()
        self._adj.clear()

        names = random.sample(PLACE_NAMES, n_nodes)
        types = [random.choice(NODE_TYPES) for _ in range(n_nodes)]

        # Placement aléatoire avec distance minimale
        positions = []
        attempts = 0
        while len(positions) < n_nodes and attempts < 10000:
            attempts += 1
            x = random.randint(MARGIN, GRAPH_AREA.width - MARGIN)
            y = random.randint(MARGIN, GRAPH_AREA.height - MARGIN)
            if all(math.hypot(x - px, y - py) >= MIN_DIST
                   for px, py in positions):
                positions.append((x, y))

        for i, (x, y) in enumerate(positions):
            node = Node(i, x, y, names[i], types[i])
            self.nodes.append(node)
            self._adj[i] = []

        # Arbre couvrant minimal (Prim simplifié) pour garantir la connexité
        in_tree = {0}
        while len(in_tree) < n_nodes:
            best = None
            for u in in_tree:
                for v in range(n_nodes):
                    if v not in in_tree:
                        d = math.hypot(
                            self.nodes[u].x - self.nodes[v].x,
                            self.nodes[u].y - self.nodes[v].y)
                        if best is None or d < best[0]:
                            best = (d, u, v)
            if best:
                _, u, v = best
                w = random.randint(WEIGHT_MIN, WEIGHT_MAX)
                self._add_edge(u, v, w)
                in_tree.add(v)

        # Arêtes supplémentaires pour créer des cycles
        all_pairs = [(i, j) for i in range(n_nodes)
                     for j in range(i + 1, n_nodes)
                     if not self._connected(i, j)]
        random.shuffle(all_pairs)
        added = 0
        for i, j in all_pairs:
            if added >= EDGE_EXTRA + random.randint(0, 3):
                break
            w = random.randint(WEIGHT_MIN, WEIGHT_MAX)
            self._add_edge(i, j, w)
            added += 1

    def _add_edge(self, i: int, j: int, w: int):
        edge = Edge(self.nodes[i], self.nodes[j], w)
        self.edges.append(edge)
        self._adj[i].append(edge)
        self._adj[j].append(edge)

    def _connected(self, i: int, j: int) -> bool:
        """Vérifie si une arête directe existe déjà entre i et j."""
        return any(
            (e.node_a.id == i and e.node_b.id == j) or
            (e.node_a.id == j and e.node_b.id == i)
            for e in self.edges
        )

    def neighbors(self, node: Node) -> list[tuple]:
        """Retourne [(voisin, edge), ...] pour un nœud donné."""
        result = []
        for edge in self._adj[node.id]:
            result.append((edge.other(node), edge))
        return result

    # ─── Dijkstra ───────────────────────────────
    def dijkstra(self, start: Node, goal: Node) -> tuple:
        """
        Algorithme de Dijkstra.
        Retourne (dist, previous) :
          dist     : dict id → coût minimal depuis start
          previous : dict id → id du prédécesseur sur le chemin optimal
        """
        dist = {n.id: float('inf') for n in self.nodes}
        prev = {n.id: None for n in self.nodes}
        dist[start.id] = 0
        heap = [(0, start.id)]

        while heap:
            cost, uid = heapq.heappop(heap)
            if cost > dist[uid]:
                continue
            u = self.nodes[uid]
            for v, edge in self.neighbors(u):
                new_cost = dist[uid] + edge.weight
                if new_cost < dist[v.id]:
                    dist[v.id] = new_cost
                    prev[v.id] = uid
                    heapq.heappush(heap, (new_cost, v.id))

        return dist, prev

    def shortest_path(self, start: Node, goal: Node) -> list[Node]:
        """Retourne la liste ordonnée des nœuds du plus court chemin."""
        _, prev = self.dijkstra(start, goal)
        path = []
        cur = goal.id
        while cur is not None:
            path.append(self.nodes[cur])
            cur = prev[cur]
        path.reverse()
        if path and path[0] is start:
            return path
        return []

    def shortest_path_cost(self, start: Node, goal: Node) -> int:
        """Coût total du plus court chemin."""
        dist, _ = self.dijkstra(start, goal)
        return dist[goal.id]

    # ─── Mutation dynamique ──────────────────────
    def mutate(self) -> str:
        """
        Modifie aléatoirement le graphe :
          - supprime une arête non essentielle  OU
          - ajoute une nouvelle arête
        Retourne un message descriptif.
        """
        action = random.choice(["add", "remove"])

        if action == "remove" and len(self.edges) > len(self.nodes) - 1:
            # Choisit une arête à supprimer en vérifiant que le graphe reste connexe
            random.shuffle(self.edges)
            for edge in self.edges:
                self.edges.remove(edge)
                self._adj[edge.node_a.id].remove(edge)
                self._adj[edge.node_b.id].remove(edge)
                if self._is_connected():
                    return (f"Route {edge.node_a.name}↔{edge.node_b.name} "
                            f"effondrée !")
                # Annule si le graphe devient non connexe
                self.edges.append(edge)
                self._adj[edge.node_a.id].append(edge)
                self._adj[edge.node_b.id].append(edge)
            return "Aucune route supprimée (graphe resterait déconnecté)."

        else:  # add
            n = len(self.nodes)
            candidates = [(i, j) for i in range(n)
                          for j in range(i + 1, n)
                          if not self._connected(i, j)]
            if candidates:
                i, j = random.choice(candidates)
                w = random.randint(WEIGHT_MIN, WEIGHT_MAX)
                self._add_edge(i, j, w)
                return (f"Nouvelle route {self.nodes[i].name}↔"
                        f"{self.nodes[j].name} ouverte !")
            return "Aucune nouvelle route possible."

    def _is_connected(self) -> bool:
        """BFS pour vérifier que le graphe est connexe."""
        if not self.nodes:
            return True
        visited = set()
        queue = [self.nodes[0]]
        while queue:
            cur = queue.pop()
            if cur.id in visited:
                continue
            visited.add(cur.id)
            for nb, _ in self.neighbors(cur):
                if nb.id not in visited:
                    queue.append(nb)
        return len(visited) == len(self.nodes)


# ═════════════════════════════════════════════
#  CLASSE KNIGHT (Sprite joueur)
# ═════════════════════════════════════════════
class Knight:
    """
    Sprite du chevalier.
    Se déplace visuellement le long d'une arête entre deux nœuds.
    """

    SIZE = 20   # rayon du sprite

    def __init__(self, start_node: Node, max_energy: int):
        self.current_node = start_node
        self.px = float(start_node.x)   # position pixel actuelle
        self.py = float(start_node.y)
        self.energy = max_energy
        self.max_energy = max_energy
        self.moving = False
        self.target_node: Optional[Node] = None
        self.move_edge: Optional[Edge] = None
        self.move_progress = 0.0   # 0.0 → 1.0

    def move_to(self, target: Node, edge: Edge):
        """Lance un déplacement vers target via edge."""
        if self.moving:
            return
        self.target_node = target
        self.move_edge = edge
        self.move_progress = 0.0
        self.moving = True

    def update(self, dt: float) -> bool:
        """
        Met à jour la position du sprite.
        Retourne True quand l'arrivée est atteinte.
        """
        if not self.moving:
            return False

        dist = math.hypot(
            self.target_node.x - self.current_node.x,
            self.target_node.y - self.current_node.y)
        if dist < 1:
            self._arrive()
            return True

        speed_norm = KNIGHT_SPEED / dist
        self.move_progress += dt * speed_norm
        if self.move_progress >= 1.0:
            self._arrive()
            return True

        # Interpolation linéaire
        t = self.move_progress
        self.px = self.current_node.x + t * (self.target_node.x - self.current_node.x)
        self.py = self.current_node.y + t * (self.target_node.y - self.current_node.y)
        return False

    def _arrive(self):
        self.energy -= self.move_edge.weight
        self.current_node = self.target_node
        self.px = float(self.current_node.x)
        self.py = float(self.current_node.y)
        self.current_node.visited = True
        self.moving = False
        self.target_node = None
        self.move_edge = None
        self.move_progress = 0.0

    def draw(self, surface: pygame.Surface):
        """Dessine le chevalier (♞ stylisé)."""
        cx, cy = int(self.px), int(self.py)

        # Halo lumineux
        glow = pygame.Surface((self.SIZE * 4, self.SIZE * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 60, 60),
                           (self.SIZE * 2, self.SIZE * 2), self.SIZE * 2)
        surface.blit(glow, (cx - self.SIZE * 2, cy - self.SIZE * 2))

        # Corps du chevalier
        pygame.draw.circle(surface, (200, 160, 30), (cx, cy), self.SIZE)
        pygame.draw.circle(surface, C_WHITE, (cx, cy), self.SIZE, 2)

        # Symbole ♞
        font = pygame.font.SysFont("segoeuisymbol,symbola,unifont", 22)
        sym = font.render("♞", True, C_BG)
        surface.blit(sym, sym.get_rect(center=(cx, cy)))


# ═════════════════════════════════════════════
#  CLASSE HUD
# ═════════════════════════════════════════════
class HUD:
    """
    Interface utilisateur : barre d'énergie, messages, légende.
    """

    def __init__(self, font_small, font_tiny, font_title):
        self.font_small = font_small
        self.font_tiny  = font_tiny
        self.font_title = font_title
        self.messages   = []   # liste de (texte, timer)
        self.MSG_DURATION = 4.0

    def push_message(self, text: str):
        self.messages.append([text, self.MSG_DURATION])

    def update(self, dt: float):
        self.messages = [[t, d - dt] for t, d in self.messages if d - dt > 0]

    def draw(self, surface: pygame.Surface, knight: Knight,
             goal_node, moves: int, dynamic_timer: float):
        """Dessine le HUD en bas de l'écran."""
        # Fond HUD
        pygame.draw.rect(surface, C_HUD_BG, HUD_AREA)
        pygame.draw.line(surface, C_EDGE, (0, HUD_AREA.top),
                         (SCREEN_W, HUD_AREA.top), 2)

        # Barre d'énergie
        bar_x, bar_y = 20, HUD_AREA.top + 18
        bar_w, bar_h = 260, 22
        ratio = max(0, knight.energy / knight.max_energy)
        fill_color = C_ENERGY_OK if ratio > 0.35 else C_ENERGY_LOW
        pygame.draw.rect(surface, (40, 40, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, fill_color,
                         (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
        pygame.draw.rect(surface, C_WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
        energy_txt = self.font_small.render(
            f"Énergie : {knight.energy} / {knight.max_energy}", True, C_TEXT)
        surface.blit(energy_txt, (bar_x + 4, bar_y + 2))

        # Position courante et objectif
        pos_txt = self.font_small.render(
            f"Lieu : {knight.current_node.name}   →   Objectif : {goal_node.name}",
            True, C_GOLD)
        surface.blit(pos_txt, (20, HUD_AREA.top + 52))

        # Compteur de mouvements
        move_txt = self.font_tiny.render(f"Déplacements : {moves}", True, C_TEXT)
        surface.blit(move_txt, (20, HUD_AREA.top + 78))

        # Timer mutation
        dyn_txt = self.font_tiny.render(
            f"Prochaine mutation dans : {dynamic_timer:.1f}s", True, (150, 150, 200))
        surface.blit(dyn_txt, (300, HUD_AREA.top + 18))

        # Légende
        leg_x = 300
        leg_y = HUD_AREA.top + 42
        legends = [
            (C_EDGE_BEST,   "Chemin optimal"),
            (C_NODE_GOAL,   "Objectif"),
            (C_NODE_PLAYER, "Vous"),
            (C_NODE_VISIT,  "Visité"),
        ]
        for i, (col, label) in enumerate(legends):
            lx = leg_x + i * 190
            pygame.draw.circle(surface, col, (lx, leg_y + 8), 8)
            lt = self.font_tiny.render(label, True, C_TEXT)
            surface.blit(lt, (lx + 14, leg_y))

        # Contrôles
        ctrl = self.font_tiny.render(
            "Clic sur un nœud adjacent pour se déplacer  |  R : Nouvelle partie",
            True, (120, 130, 160))
        surface.blit(ctrl, (300, HUD_AREA.top + 80))

        # Messages dynamiques (en haut à gauche)
        for i, (msg, timer) in enumerate(reversed(self.messages[-4:])):
            alpha = min(255, int(255 * timer))
            msg_surf = self.font_small.render(msg, True,
                                              (255, 255, 100, alpha))
            surface.blit(msg_surf, (20, 10 + i * 26))


# ═════════════════════════════════════════════
#  CLASSE GAME (Boucle principale)
# ═════════════════════════════════════════════
class Game:
    """
    Orchestre la boucle principale Pygame, les états de jeu,
    les entrées utilisateur et le rendu.
    """

    STATE_PLAYING = "playing"
    STATE_WIN     = "win"
    STATE_LOSE    = "lose"
    STATE_MENU    = "menu"      # écran de sélection de difficulté

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("⚔ Quête du Graphe — Chevalier & Ombre")
        self.clock = pygame.time.Clock()

        # Polices
        self.font_title = pygame.font.SysFont(
            "bahnschrift,calibri,arial", 36, bold=True)
        self.font_small = pygame.font.SysFont(
            "segoeuisymbol,symbola,calibri,arial", 18)
        self.font_tiny  = pygame.font.SysFont(
            "segoeuisymbol,symbola,calibri,arial", 14)
        self.font_big   = pygame.font.SysFont(
            "bahnschrift,calibri,arial", 54, bold=True)

        # ── Image de fond (chargée une seule fois) ──────
        import os
        _bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "background.png")
        try:
            _bg_raw = pygame.image.load(_bg_path).convert()
            self.bg_image = pygame.transform.scale(_bg_raw, (SCREEN_W, SCREEN_H))
            # Voile sombre pour garder les nœuds lisibles
            _overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            _overlay.set_alpha(110)
            _overlay.fill((5, 8, 20))
            self.bg_image.blit(_overlay, (0, 0))
        except Exception:
            self.bg_image = None  # fallback : fond uni si l'image est absente

        # Difficulté par défaut
        self.difficulty = "easy"

        # État menu
        self.state = self.STATE_MENU
        self._menu_buttons = []   # liste de (Rect, key_difficulté)
        self._build_menu_buttons()

        # Attributs de jeu initialisés à None (seront remplis par _new_game)
        self.graph = None
        self.knight = None
        self.goal = None
        self.hud = None
        self.optimal_path = []
        self.optimal_cost = 0
        self.optimal_edges = set()
        self.state = self.STATE_MENU
        self.moves = 0
        self.hovered = None
        self.dynamic_timer = 8
        self.checkpoint_available = False
        self.checkpoint_used = False
        self.checkpoint_data = None

    # ─── Menu difficulté ────────────────────────
    def _build_menu_buttons(self):
        """Construit les rectangles des boutons de sélection de difficulté."""
        self._menu_buttons = []
        btn_w, btn_h = 240, 70
        spacing = 30
        total_w = len(DIFFICULTY_SETTINGS) * btn_w + (len(DIFFICULTY_SETTINGS) - 1) * spacing
        start_x = (SCREEN_W - total_w) // 2
        btn_y   = SCREEN_H // 2 + 30
        for i, key in enumerate(DIFFICULTY_SETTINGS):
            rx = start_x + i * (btn_w + spacing)
            rect = pygame.Rect(rx, btn_y, btn_w, btn_h)
            self._menu_buttons.append((rect, key))

    def _render_menu(self):
        """Affiche l'écran de sélection de difficulté."""
        self.screen.fill(C_MENU_BG)

        # Titre
        t = self.font_big.render("⚔ Quête du Graphe", True, C_GOLD)
        self.screen.blit(t, t.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 180)))

        sub = self.font_small.render(
            "Choisissez votre niveau de difficulté", True, C_TEXT)
        self.screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 120)))

        # Informations par difficulté
        descs = {
            "easy":   ["Chemin optimal visible",  "Mutations lentes",       "Énergie abondante",   "Pas de checkpoint"],
            "medium": ["Chemin optimal visible",  "Mutations normales",     "Énergie standard",    "1 checkpoint disponible (C/L)"],
            "hard":   ["Chemin optimal visible",  "Mutations rapides",      "Énergie limitée",     "1 checkpoint disponible (C/L)"],
        }

        mx, my = pygame.mouse.get_pos()
        for rect, key in self._menu_buttons:
            cfg = DIFFICULTY_SETTINGS[key]
            hovered = rect.collidepoint(mx, my)

            # Fond bouton
            base_color = cfg["color"]
            btn_color  = tuple(min(255, int(c * 1.3)) for c in base_color) if hovered else base_color
            pygame.draw.rect(self.screen, btn_color, rect, border_radius=12)
            pygame.draw.rect(self.screen, C_WHITE, rect, 2, border_radius=12)

            # Étiquette
            lbl = self.font_title.render(cfg["label"], True, C_BG)
            self.screen.blit(lbl, lbl.get_rect(center=(rect.centerx, rect.centery)))

            # Description
            for j, line in enumerate(descs[key]):
                dl = self.font_tiny.render(line, True, C_TEXT)
                self.screen.blit(dl, dl.get_rect(
                    center=(rect.centerx, rect.bottom + 22 + j * 18)))

        pygame.display.flip()

    # ─── Nouvelle partie ────────────────────────
    def _new_game(self, difficulty: str = None):
        if difficulty:
            self.difficulty = difficulty
        cfg = DIFFICULTY_SETTINGS[self.difficulty]

        n = random.randint(NUM_NODES_MIN, NUM_NODES_MAX)
        self.graph = Graph()
        self.graph.generate(n)

        # Choisit un départ et un objectif éloignés
        start_node = self.graph.nodes[0]
        goal_node  = max(
            (nd for nd in self.graph.nodes if nd is not start_node),
            key=lambda nd: math.hypot(nd.x - start_node.x,
                                      nd.y - start_node.y))
        start_node.visited = True

        max_energy = cfg["energy"]
        self.knight = Knight(start_node, max_energy)
        self.goal   = goal_node

        # Calcul du plus court chemin initial
        self._update_pathfinding()

        self.hud = HUD(self.font_small, self.font_tiny, self.font_title)
        self.hud.push_message(
            f"Quête : atteindre {self.goal.name} ! "
            f"(coût optimal : {self.optimal_cost})")
        if cfg["checkpoints"] > 0:
            self.hud.push_message("💾 Appuie sur C pour créer un checkpoint, L pour le charger")

        self.state    = self.STATE_PLAYING
        self.moves    = 0
        self.hovered  = None
        self.dynamic_timer = float(cfg["mutation"])

        # ── Système de checkpoint ──
        self.checkpoint_available = cfg["checkpoints"] > 0
        self.checkpoint_used      = False
        self.checkpoint_data      = None

    def _update_pathfinding(self):
        """Recalcule le chemin optimal depuis la position actuelle."""
        self.optimal_path = self.graph.shortest_path(
            self.knight.current_node, self.goal)
        dist, _ = self.graph.dijkstra(self.knight.current_node, self.goal)
        self.optimal_cost = dist.get(self.goal.id, float('inf'))
        # Ensemble des arêtes du chemin optimal (pour coloration)
        self.optimal_edges: set = set()
        for i in range(len(self.optimal_path) - 1):
            a = self.optimal_path[i]
            b = self.optimal_path[i + 1]
            for edge in self.graph.edges:
                if ({edge.node_a.id, edge.node_b.id} == {a.id, b.id}):
                    self.optimal_edges.add(id(edge))

    # ─── Checkpoint : sauvegarder ───────────────
    def _save_checkpoint(self):
        """Enregistre l'état actuel (position + énergie + graphe)."""
        if not self.checkpoint_available:
            self.hud.push_message("⚠ Aucun checkpoint disponible !")
            return
        if self.knight.moving:
            self.hud.push_message("⚠ Impossible : le chevalier est en mouvement !")
            return

        # Sauvegarde : ID du nœud courant, énergie, mouvements, état des arêtes
        self.checkpoint_data = {
            "node_id":   self.knight.current_node.id,
            "energy":    self.knight.energy,
            "moves":     self.moves,
            "visited":   {n.id: n.visited for n in self.graph.nodes},
            "edges":     [(e.node_a.id, e.node_b.id, e.weight) for e in self.graph.edges],
        }
        self.hud.push_message(
            f"💾 Checkpoint sauvegardé à {self.knight.current_node.name} !")

    # ─── Checkpoint : charger ───────────────────
    def _load_checkpoint(self):
        """Restaure l'état sauvegardé."""
        if self.checkpoint_data is None:
            self.hud.push_message("⚠ Aucun checkpoint sauvegardé ! Appuie d'abord sur C.")
            return

        data = self.checkpoint_data

        # Restaure le graphe (arêtes)
        self.graph.edges.clear()
        for nid in self.graph._adj:
            self.graph._adj[nid].clear()
        for (a_id, b_id, w) in data["edges"]:
            self.graph._add_edge(a_id, b_id, w)

        # Restaure les visites
        for node in self.graph.nodes:
            node.visited = data["visited"].get(node.id, False)

        # Restaure le chevalier
        restore_node = self.graph.nodes[data["node_id"]]
        self.knight.current_node = restore_node
        self.knight.px = float(restore_node.x)
        self.knight.py = float(restore_node.y)
        self.knight.energy = data["energy"]
        self.knight.moving = False
        self.knight.target_node = None
        self.knight.move_edge = None
        self.knight.move_progress = 0.0

        self.moves = data["moves"]
        self._update_pathfinding()

        # Après chargement, on consomme le checkpoint (une seule utilisation)
        self.checkpoint_available = False
        self.hud.push_message(
            f"⏪ Checkpoint rechargé à {restore_node.name} ! (Plus de checkpoint disponible)")

    # ─── Boucle principale ──────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()

            if self.state == self.STATE_MENU:
                self._render_menu()
            else:
                self._update(dt)
                self._render()

    # ─── Gestion des événements ─────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Menu de difficulté ──
            if self.state == self.STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for rect, key in self._menu_buttons:
                        if rect.collidepoint(mx, my):
                            self._new_game(difficulty=key)
                            return
                continue   # ignore les autres events pendant le menu

            # ── En jeu ──
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.state = self.STATE_MENU
                    self._build_menu_buttons()
                    return

                # Checkpoint : sauvegarder (touche C)
                if event.key == pygame.K_c:
                    if self.state == self.STATE_PLAYING:
                        self._save_checkpoint()

                # Checkpoint : charger (touche L)
                if event.key == pygame.K_l:
                    if self.state == self.STATE_PLAYING:
                        self._load_checkpoint()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == self.STATE_PLAYING:
                    self._handle_click(event.pos)
                elif self.state in (self.STATE_WIN, self.STATE_LOSE):
                    self.state = self.STATE_MENU
                    self._build_menu_buttons()

    def _handle_click(self, pos):
        """Déplace le chevalier vers le nœud cliqué (s'il est adjacent)."""
        if self.knight.moving:
            return

        clicked = self._node_at(pos)
        if clicked is None:
            return

        # Vérifie que le nœud est adjacent au nœud actuel
        for neighbor, edge in self.graph.neighbors(self.knight.current_node):
            if neighbor is clicked:
                self.knight.move_to(clicked, edge)
                self.moves += 1

                # Feedback ombre si le mouvement n'est pas sur le chemin optimal
                if (len(self.optimal_path) > 1 and
                        clicked is not self.optimal_path[1]):
                    self.hud.push_message(
                        f"⚠ Mauvaise piste ! Ombre sur {clicked.name}…")
                else:
                    self.hud.push_message(
                        f"✓ Bonne direction vers {clicked.name} !")
                return

    def _node_at(self, pos) -> Optional[Node]:
        """Retourne le nœud sous le curseur, ou None."""
        for node in self.graph.nodes:
            if math.hypot(pos[0] - node.x, pos[1] - node.y) <= Node.RADIUS + 6:
                return node
        return None

    # ─── Mise à jour ────────────────────────────
    def _update(self, dt: float):
        if self.state != self.STATE_PLAYING:
            return

        arrived = self.knight.update(dt)
        if arrived:
            self._update_pathfinding()
            # Victoire ?
            if self.knight.current_node is self.goal:
                self.state = self.STATE_WIN
                self.hud.push_message(
                    f"🏆 VICTOIRE ! Arrivé à {self.goal.name} "
                    f"en {self.moves} mouvements !")
            # Défaite (énergie épuisée) ?
            elif self.knight.energy <= 0:
                self.state = self.STATE_LOSE
                self.hud.push_message("💀 Énergie épuisée… Défaite !")

        self.hud.update(dt)

        # Nœud survolé
        mx, my = pygame.mouse.get_pos()
        self.hovered = self._node_at((mx, my))

        # Mutation dynamique
        if self.state == self.STATE_PLAYING:
            self.dynamic_timer -= dt
            if self.dynamic_timer <= 0:
                msg = self.graph.mutate()
                self._update_pathfinding()
                self.hud.push_message(f"🌍 {msg}")
                self.dynamic_timer = float(DIFFICULTY_SETTINGS[self.difficulty]["mutation"])

    # ─── Rendu ──────────────────────────────────
    def _render(self):
        # Fond : image fantasy ou couleur unie en fallback
        if self.bg_image is not None:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(C_BG)

        # ── Dessin des arêtes ──
        current_id = self.knight.current_node.id
        shadow_nodes: set = set()
        if (self.state == self.STATE_PLAYING and
                len(self.optimal_path) > 1):
            next_optimal = self.optimal_path[1]
            for nb, _ in self.graph.neighbors(self.knight.current_node):
                if nb is not next_optimal:
                    shadow_nodes.add(nb.id)

        for edge in self.graph.edges:
            on_optimal = id(edge) in self.optimal_edges
            leads_bad = False
            if not self.knight.moving:
                a_id, b_id = edge.node_a.id, edge.node_b.id
                if a_id == current_id and b_id in shadow_nodes:
                    leads_bad = True
                elif b_id == current_id and a_id in shadow_nodes:
                    leads_bad = True

            if on_optimal:
                edge.draw(self.screen, C_EDGE_BEST, 3,
                          self.font_tiny, alpha_overlay=False)
            elif leads_bad:
                edge.draw(self.screen, C_EDGE_SHADOW, 2,
                          self.font_tiny, alpha_overlay=True)
            else:
                edge.draw(self.screen, C_EDGE, 2, self.font_tiny)

        # ── Dessin des nœuds ──
        checkpoint_node_id = (
            self.checkpoint_data["node_id"]
            if self.checkpoint_data is not None else None
        )
        for node in self.graph.nodes:
            if node is self.knight.current_node:
                node_state = "player"
            elif node is self.goal:
                node_state = "goal"
            elif node is self.hovered:
                node_state = "hover"
            elif node.visited:
                node_state = "visited"
            else:
                node_state = "default"

            shadow = (node.id in shadow_nodes and
                      not self.knight.moving)
            node.draw(self.screen, node_state,
                      self.font_small, self.font_tiny, shadow=shadow)

        # ── Chevalier ──
        self.knight.draw(self.screen)

        # ── HUD ──
        self.hud.draw(self.screen, self.knight, self.goal,
                      self.moves, self.dynamic_timer)

        # ── Écran de fin ──
        if self.state in (self.STATE_WIN, self.STATE_LOSE):
            self._render_endscreen()

        pygame.display.flip()

    def _render_endscreen(self):
        """Overlay de fin de partie."""
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        if self.state == self.STATE_WIN:
            color = C_GOLD
            line1 = "⚔ VICTOIRE ⚔"
            line2 = f"Arrivé à {self.goal.name} en {self.moves} mouvements"
        else:
            color = (220, 60, 60)
            line1 = "💀 DÉFAITE 💀"
            line2 = "L'énergie du chevalier est épuisée"

        t1 = self.font_title.render(line1, True, color)
        t2 = self.font_small.render(line2, True, C_TEXT)
        t3 = self.font_small.render("Clic ou R pour rejouer", True, (160, 160, 200))
        cx = SCREEN_W // 2
        cy = SCREEN_H // 2 - 40
        self.screen.blit(t1, t1.get_rect(center=(cx, cy)))
        self.screen.blit(t2, t2.get_rect(center=(cx, cy + 50)))
        self.screen.blit(t3, t3.get_rect(center=(cx, cy + 90)))


# ═════════════════════════════════════════════
#  POINT D'ENTRÉE
# ═════════════════════════════════════════════
if __name__ == "__main__":
    game = Game()
    game.run()
