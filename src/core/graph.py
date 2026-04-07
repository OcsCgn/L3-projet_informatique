from core.node import Node
from core.edge import Edge

import random
import utils.settings as st
import math
import heapq


class Graph:
    """
    Graphe du monde de jeu.
    Gère : génération aléatoire, Dijkstra, A*,
           mutations dynamiques (ajout/suppression d'arête).
    """

    def __init__(self,difficulty):
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []
        self._adj: dict[int, list[Edge]] = {}   # liste d'adjacence id → [Edge]

        self.difficulty = difficulty
        

    # ─── Génération ─────────────────────────────
    def generate(self, n_nodes: int):
        """
        Génère un graphe connexe intelligent :
        - Poids logiques (distance + terrain).
        - Arbre couvrant pour la connexité.
        - Ajout de routes limitées par la distance pour éviter les croisements visuels.
        """
        self.nodes.clear()
        self.edges.clear()
        self._adj.clear()

        # --- 1. PLACEMENT DES NŒUDS ---
        names = random.sample(st.PLACE_NAMES, min(n_nodes, len(st.PLACE_NAMES)))
        nb_villages = random.randint(1, 2) 
        types = ["village"] * nb_villages
        
        autres_types = [t for t in st.NODE_TYPES if t != "village"]
        for _ in range(n_nodes - nb_villages):
            types.append(random.choice(autres_types))
        random.shuffle(types)

        positions = []
        attempts = 0
        while len(positions) < n_nodes and attempts < 10000:
            attempts += 1
            x = random.randint(st.MARGIN, st.GRAPH_AREA.width - st.MARGIN)
            y = random.randint(st.MARGIN, st.GRAPH_AREA.height - st.MARGIN)
            if all(math.hypot(x - px, y - py) >= st.MIN_DIST for px, py in positions):
                positions.append((x, y))

        positions.sort(key=lambda p: p[0], reverse=True)
        
        for i, (x, y) in enumerate(positions):
            node = Node(i, x, y, names[i], types[i])
            self.nodes.append(node)
            self._adj[i] = []
        n_nodes = len(self.nodes)
        # --- 2. FONCTION DE COÛT LOGIQUE ---
        def calculer_poids(n1: Node, n2: Node) -> int:
            """Calcule un coût d'énergie basé sur la distance et le terrain."""
            dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
            multiplicateur = 1.0
            

            punition_terrain = {
                "facile": 1.2,    # Coûte un peu plus cher
                "moyen": 1.5,     # Coûte 50% plus cher
                "difficile": 2.5  # Coûte extrêmement cher !
            }[self.difficulty]


            # Modificateurs de terrain (les ruines et forêts fatiguent plus)
            terrains_difficiles = ["ruin", "forest", "castle"]
            if n1.node_type in terrains_difficiles or n2.node_type in terrains_difficiles:
                multiplicateur = punition_terrain  
            if n1.node_type == "village" and n2.node_type == "village":
                multiplicateur = 0.8  
                
            return max(1, int((dist / 10) * multiplicateur))

        # --- 3. SQUELETTE DE CONNEXITÉ (Arbre de Prim) ---
        in_tree = {0}
        while len(in_tree) < n_nodes:
            candidates = []
            for u in in_tree:
                for v in range(n_nodes):
                    if v not in in_tree:
                        d = math.hypot(
                            self.nodes[u].x - self.nodes[v].x,
                            self.nodes[u].y - self.nodes[v].y)
                        candidates.append((d, u, v))
            
            # On trie par distance pour éviter les traits absurdes qui traversent l'écran
            candidates.sort(key=lambda x: x[0])
            
            top_k = min(10, len(candidates)) 
            _, u, v = random.choice(candidates[:top_k])
            
            w = calculer_poids(self.nodes[u], self.nodes[v])
            self._add_edge(u, v, w)
            in_tree.add(v)

        # --- 4. AJOUT DES ROUTES SECONDAIRES (Gérées par la difficulté) ---
        MAX_EDGE_LENGTH = st.DIFFICULTY_SETTINGS[self.difficulty]["edge_dist"]
        potential_edges = []
        
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if not self._connected(i, j):
                    n1, n2 = self.nodes[i], self.nodes[j]
                    dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                    
                    if dist <= MAX_EDGE_LENGTH:
                        w = calculer_poids(n1, n2)
                        potential_edges.append((w, n1, n2))

        # On calcule le nombre de routes à ajouter
        pourcentage = st.DIFFICULTY_SETTINGS[self.difficulty]["difficulty_percent"]
        nb_to_add = int(len(potential_edges) * pourcentage)
        
        # LE CHANGEMENT EST ICI : On mélange TOUTES les routes possibles au lieu de trier.
        # Ça va créer de vrais cycles et des raccourcis inattendus.
        random.shuffle(potential_edges)
        
        # On ajoute les routes
        for k in range(min(nb_to_add, len(potential_edges))):
            w, n1, n2 = potential_edges[k]
            self._add_edge(n1.id, n2.id, w)

    def _add_edge(self, i: int, j: int, w: int):
        edge = Edge(self.nodes[i], self.nodes[j], w)
        self.edges.append(edge)
        self._adj[i].append(edge)
        self._adj[j].append(edge)

    def _connected(self, i: int, j: int) -> bool:
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


    '''def short_hint():
        path = shortest_path()'''
    # ─── Mutation dynamique ──────────────────────
    '''def mutate(self) -> str:
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
                w = random.randint(st.WEIGHT_MIN, st.WEIGHT_MAX)
                self._add_edge(i, j, w)
                return (f"Nouvelle route {self.nodes[i].name}↔"
                        f"{self.nodes[j].name} ouverte !")
            return "Aucune nouvelle route possible."
    '''
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
