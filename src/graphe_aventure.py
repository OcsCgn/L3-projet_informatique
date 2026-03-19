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
import utils.settings as st
from core.graph import Graph
from entities.knight import Knight
from ui.hud import HUD
from core.node import Node
from core.edge import Edge
from ui.menu import Menu

class Game:
    """
    Orchestre la boucle principale Pygame, les états de jeu,
    les entrées utilisateur et le rendu.
    """

    STATE_PLAYING = "playing"
    STATE_WIN     = "win"
    STATE_LOSE    = "lose"
    STATE_MENU   = "menu"


    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((st.SCREEN_W, st.SCREEN_H))
        pygame.display.set_caption("⚔ Quête du Graphe — Chevalier & Ombre")
        self.clock = pygame.time.Clock()

        #Définission du menu
        self.menu = Menu(st.MENU_WIDTH,st.MENU_HEIGTH)
   
        # Polices
        self.font_title = pygame.font.SysFont(
            "bahnschrift,calibri,arial", 36, bold=True)
        self.font_small = pygame.font.SysFont(
            "segoeuisymbol,symbola,calibri,arial", 18)
        self.font_tiny  = pygame.font.SysFont(
            "segoeuisymbol,symbola,calibri,arial", 14)

        self._new_game()

    # ─── Nouvelle partie ────────────────────────
    def _new_game(self):
        n = random.randint(st.NUM_NODES_MIN, st.NUM_NODES_MAX)
        self.graph = Graph()
        self.graph.generate(n)

        # Choisit un départ et un objectif éloignés
        start_node = self.graph.nodes[0]
        goal_node  = max(
            (nd for nd in self.graph.nodes if nd is not start_node),
            key=lambda nd: math.hypot(nd.x - start_node.x,
                                      nd.y - start_node.y))
        start_node.visited = True

        self.knight = Knight(start_node, st.PLAYER_MAX_ENERGY)
        self.goal   = goal_node

        # Calcul du plus court chemin initial
        self._update_pathfinding()

        self.hud = HUD(self.font_small, self.font_tiny, self.font_title)
        self.hud.push_message(
            f"Quête : atteindre {self.goal.name} ! "
            f"(coût optimal : {self.optimal_cost})")

        self.state    = self.STATE_MENU
        self.moves    = 0
        self.hovered  = None   # nœud sous la souris
        self.dynamic_timer = st.DYNAMIC_INTERVAL

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

    # ─── Boucle principale ──────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(st.FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()

    # ─── Gestion des événements ─────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._new_game()
                    return
            if self.state == self.STATE_MENU:
                action = self.menu.handle_event(event)
                if action == "start":
                    self.state = self.STATE_PLAYING
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == self.STATE_PLAYING:
                    self._handle_click(event.pos)
                elif self.state in (self.STATE_WIN, self.STATE_LOSE):
                    self._new_game()

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
        if self.state == self.STATE_MENU:
            print("update menu")
            self.menu.update()
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


    # ─── Rendu ──────────────────────────────────
    def _render(self):
        self.screen.fill(st.C_BG)

        # ── Dessin des arêtes ──
        current_id = self.knight.current_node.id
        # Identifie les nœuds qui ne sont PAS sur le chemin optimal depuis actuel
        shadow_nodes: set = set()

        if self.state == self.STATE_MENU:
            self.menu.draw(self.screen)
            pygame.display.flip()
            return
        
        if (self.state == self.STATE_PLAYING and
                len(self.optimal_path) > 1):
            next_optimal = self.optimal_path[1]
            for nb, _ in self.graph.neighbors(self.knight.current_node):
                if nb is not next_optimal:
                    shadow_nodes.add(nb.id)

        for edge in self.graph.edges:
            on_optimal = id(edge) in self.optimal_edges
            # Détermine si l'arête mène vers une mauvaise direction
            # (depuis la position actuelle du joueur)
            leads_bad = False
            if not self.knight.moving:
                a_id, b_id = edge.node_a.id, edge.node_b.id
                if a_id == current_id and b_id in shadow_nodes:
                    leads_bad = True
                elif b_id == current_id and a_id in shadow_nodes:
                    leads_bad = True

            if on_optimal:
                edge.draw(self.screen, st.C_EDGE_BEST, 3,
                          self.font_tiny, alpha_overlay=False)
            elif leads_bad:
                edge.draw(self.screen, st.C_EDGE_SHADOW, 2,
                          self.font_tiny, alpha_overlay=True)
            else:
                edge.draw(self.screen, st.C_EDGE, 2, self.font_tiny)

        # ── Dessin des nœuds ──
        for node in self.graph.nodes:
            if node is self.knight.current_node:
                state = "player"
            elif node is self.goal:
                state = "goal"
            elif node is self.hovered:
                state = "hover"
            elif node.visited:
                state = "visited"
            else:
                state = "default"

            shadow = (node.id in shadow_nodes and
                      not self.knight.moving)
            node.draw(self.screen, state,
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
        overlay = pygame.Surface((st.SCREEN_W, st.SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        if self.state == self.STATE_WIN:
            color = st.C_GOLD
            line1 = "⚔ VICTOIRE ⚔"
            line2 = f"Arrivé à {self.goal.name} en {self.moves} mouvements"
        else:
            color = (220, 60, 60)
            line1 = "💀 DÉFAITE 💀"
            line2 = "L'énergie du chevalier est épuisée"

        t1 = self.font_title.render(line1, True, color)
        t2 = self.font_small.render(line2, True, st.C_TEXT)
        t3 = self.font_small.render("Clic ou R pour rejouer", True, (160, 160, 200))
        cx = st.SCREEN_W // 2
        cy = st.SCREEN_H // 2 - 40
        self.screen.blit(t1, t1.get_rect(center=(cx, cy)))
        self.screen.blit(t2, t2.get_rect(center=(cx, cy + 50)))
        self.screen.blit(t3, t3.get_rect(center=(cx, cy + 90)))


# ═════════════════════════════════════════════
#  POINT D'ENTRÉE
# ═════════════════════════════════════════════
if __name__ == "__main__":
    game = Game()
    game.run()


