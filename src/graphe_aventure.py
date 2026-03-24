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
import sys
from typing import Optional
import utils.settings as st
from core.graph import Graph
from entities.knight import Knight
from ui.hud import HUD
from core.node import Node
from core.edge import Edge
from ui.menu import Menu
from utils.timer import Timer
from utils.manager_score import add_score

class Game:

    #Constant d'état du jeu
    STATE_PLAYING = "playing"
    STATE_WIN     = "win"
    STATE_LOSE    = "lose"
    STATE_MENU   = "menu"


    #Variable 
    player_name = ""
    timer = Timer()
    time_used = 0

    def __init__(self):
        pygame.init()

        self.menu = Menu(st.MENU_WIDTH,st.MENU_HEIGTH)

        self.screen = pygame.display.set_mode((st.SCREEN_W, st.SCREEN_H))
        pygame.display.set_caption("⚔ Quête du Graphe — Chevalier & Ombre")
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont(
            "bahnschrift,calibri,arial", 36, bold=True)
        self.font_small = pygame.font.SysFont(
            "segoeuisymbol,symbola,calibri,arial", 18)
        self.font_tiny  = pygame.font.SysFont(
            "segoeuisymbol,symbola,calibri,arial", 14)
        
        self.init_game()

    def init_game(self):
        self.state    = self.STATE_MENU
        self.moves    = 0



    def _new_game(self):
        self.graph = Graph(self.menu.getDifficulty())
        self.graph.generate(st.DIFFICULTY_SETTINGS[self.menu.getDifficulty()]["num_nodes"])

        start_node = self.graph.nodes[0]
        goal_node  = max(
            (nd for nd in self.graph.nodes if nd is not start_node),
            key=lambda nd: math.hypot(nd.x - start_node.x,
                                      nd.y - start_node.y))
        start_node.visited = True

        self.knight = Knight(start_node, st.PLAYER_MAX_ENERGY)
        self.goal   = goal_node

        self._update_pathfinding()
        self.hud = HUD(self.font_small, self.font_tiny, self.font_title)
        self.hud.push_message(
            f"Quête : atteindre {self.goal.name} ! "
            f"(coût optimal : {self.optimal_cost})")

       

    def _update_pathfinding(self):
        self.optimal_path = self.graph.shortest_path(
            self.knight.current_node, self.goal)
        dist, _ = self.graph.dijkstra(self.knight.current_node, self.goal)
        self.optimal_cost = dist.get(self.goal.id, float('inf'))

        self.optimal_edges: set = set()
        for i in range(len(self.optimal_path) - 1):
            a = self.optimal_path[i]
            b = self.optimal_path[i + 1]
            for edge in self.graph.edges:
                if ({edge.node_a.id, edge.node_b.id} == {a.id, b.id}):
                    self.optimal_edges.add(id(edge))

    def run(self):
        while True:
            dt = self.clock.tick(st.FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()

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
                    self.player_name = self.menu.getPlayerName()
                    self._new_game()
                    self.timer.start()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == self.STATE_PLAYING:

                    # 🔴 restart bouton hud (reset sans changer la map)
                    if self.hud.restart_button.collidepoint(event.pos):

                        start_node = self.graph.nodes[0]

                        self.knight = Knight(start_node, st.PLAYER_MAX_ENERGY)
                        start_node.visited = True

                        self.moves = 0
                        self.dynamic_timer = st.DYNAMIC_INTERVAL

                        self._update_pathfinding()

                        self.hud.push_message("↺ Partie réinitialisée")

                        return

                    self._handle_click(event.pos)
                    
                elif self.state in (self.STATE_WIN, self.STATE_LOSE):
                    self._new_game()

    def _handle_click(self, pos):
        if self.knight.moving:
            return

        clicked = self._node_at(pos)
        if clicked is None:
            return

        for neighbor, edge in self.graph.neighbors(self.knight.current_node):
            if neighbor is clicked:
                self.knight.move_to(clicked, edge)
                self.moves += 1

                if (len(self.optimal_path) > 1 and
                        clicked is not self.optimal_path[1]):
                    self.hud.push_message(
                        f"⚠ Mauvaise piste ! Ombre sur {clicked.name}…")
                else:
                    self.hud.push_message(
                        f"✓ Bonne direction vers {clicked.name} !")
                return

    def _node_at(self, pos) -> Optional[Node]:
        for node in self.graph.nodes:
            if math.hypot(pos[0] - node.x, pos[1] - node.y) <= Node.RADIUS + 6:
                return node
        return None

    def _update(self, dt: float):
        if self.state != self.STATE_PLAYING:
            return
        if self.state == self.STATE_MENU:
            self.menu.update()
            return
        
        arrived = self.knight.update(dt)
        if arrived:
            self._update_pathfinding()

            if self.knight.current_node is self.goal:
                self.state = self.STATE_WIN
                self.hud.push_message(
                    f"🏆 VICTOIRE ! Arrivé à {self.goal.name} "
                    f"en {self.moves} mouvements !")
                self.timer.stop()
                self.time_used = round(self.timer.get_elapsed(), 2)
                add_score(self.player_name, self.time_used, self.menu.getDifficulty())

            elif self.knight.energy <= 0:
                self.state = self.STATE_LOSE
                self.hud.push_message("💀 Énergie épuisée… Défaite !")

        self.hud.update(dt)

        mx, my = pygame.mouse.get_pos()
        self.hovered = self._node_at((mx, my))

    def _render(self):
        self.screen.fill(st.C_BG)

        if self.state == self.STATE_MENU:
            self.menu.draw(self.screen)
            pygame.display.flip()
            return

        for edge in self.graph.edges:
            edge.draw(self.screen, st.C_EDGE, 2, self.font_tiny,self.knight.current_node)

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

            node.draw(self.screen, state,
                      self.font_small, self.font_tiny, shadow=None)

        self.knight.draw(self.screen)

        self.hud.draw(self.screen, self.knight, self.goal,
                      self.moves)

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
            line1 = "⚔ VICTOIRE en " + str(self.time_used) + "s ! ⚔"
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

if __name__ == "__main__":
    game = Game()
    game.run()