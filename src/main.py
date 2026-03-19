import pygame
import time
from graph import Graph
from player import Player
from menu import Menu
from manager_score import load_scores, add_score

pygame.init()

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Carte du monde – Exploration")

clock = pygame.time.Clock()

font_big = pygame.font.SysFont(None, 70)
font_small = pygame.font.SysFont(None, 35)

# ======================
# VARIABLES
# ======================

game_state = "menu"

menu = Menu(WIDTH, HEIGHT)

restart_button = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 40, 240, 60)
quit_button = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 120, 240, 60)

start_time = None

# ======================
# CRÉATION DU JEU
# ======================

def create_game():
    graph = Graph()

    positions = {
        1:(100,300), 2:(220,200), 3:(350,250), 4:(480,200), 5:(620,250),
        6:(760,200), 7:(900,250), 8:(220,380), 9:(350,400), 10:(480,380),
        11:(620,420), 12:(760,380), 13:(900,420), 14:(480,520),
        15:(350,520), 16:(220,520), 17:(100,520), 18:(760,550),
        19:(620,560), 20:(900,580)
    }

    for cid, (x, y) in positions.items():
        graph.add_city(cid, x, y)

    edges = [
        (1,2,10),(2,3,10),(3,4,10),(4,5,15),
        (5,11,15),(11,19,15),(19,20,20),
        (3,9,10),(9,10,10),(10,11,10),
        (2,8,40),(4,10,40),(6,12,50),(7,13,50),
        (8,9,40),(12,13,50),(9,15,60),
        (10,14,60),(11,14,50),(15,16,70),
        (16,17,70),(12,18,80),(18,20,90)
    ]

    for a, b, cost in edges:
        graph.add_edge(a, b, cost)

    player = Player(start_city_id=1)
    player.place_on_city(graph.cities[1])
    graph.reveal_city_and_neighbors(1)

    return graph, player


graph = None
player = None
running = True

# ======================
# BOUCLE PRINCIPALE
# ======================

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ===== MENU =====
        if game_state == "menu":
            action = menu.handle_event(event)

            if action == "start":
                graph, player = create_game()
                start_time = time.time()
                game_state = "playing"

        # ===== JEU =====
        elif game_state == "playing":

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and player.state == "idle"
                and player.current_city != 20
            ):
                mx, my = pygame.mouse.get_pos()

                for neighbor_id, _ in graph.edges[player.current_city]:
                    city = graph.cities[neighbor_id]

                    if not city.visible:
                        continue

                    dx = mx - city.x
                    dy = my - city.y

                    if dx*dx + dy*dy <= city.radius**2:
                        cost = graph.get_cost(player.current_city, neighbor_id)

                        if player.can_move(cost):
                            player.consume_energy(cost)
                            player.start_moving(
                                graph.cities[player.current_city],
                                city
                            )

        # ===== FIN =====
        elif game_state in ["won", "lost"]:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if restart_button.collidepoint(event.pos):
                    graph, player = create_game()
                    start_time = time.time()
                    game_state = "playing"

                if quit_button.collidepoint(event.pos):
                    running = False

    # ======================
    # UPDATE
    # ======================

    if game_state == "menu":
        menu.update()

    elif game_state == "playing":
        player.update()

        if player.state == "idle":
            graph.reveal_city_and_neighbors(player.current_city)

        if player.energy == 0:
            game_state = "lost"

        if player.current_city == 20:
            elapsed_time = int(time.time() - start_time)

            add_score(
                menu.player_name,
                elapsed_time,
                menu.difficulty
            )

            menu.scores_data = load_scores()  # refresh leaderboard

            game_state = "won"

    # ======================
    # DRAW
    # ======================

    if game_state == "menu":
        menu.draw(screen)

    elif game_state == "playing":

        screen.fill((35, 35, 35))

        graph.draw(screen)
        player.draw(screen)
        player.draw_energy_bar(screen)

        name_text = font_small.render(menu.player_name, True, (255,255,255))
        screen.blit(name_text, (20, 20))

    elif game_state in ["won", "lost"]:

        screen.fill((35, 35, 35))

        graph.draw(screen)
        player.draw(screen)
        player.draw_energy_bar(screen)

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))

        message = "VICTOIRE !" if game_state == "won" else "VOUS AVEZ ÉCHOUÉ"
        color = (0,255,0) if game_state == "won" else (255,0,0)

        text = font_big.render(message, True, color)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 120))

        pygame.draw.rect(screen, (0,150,0), restart_button, border_radius=10)
        pygame.draw.rect(screen, (150,0,0), quit_button, border_radius=10)

        restart_text = font_small.render("RESTART", True, (255,255,255))
        quit_text = font_small.render("QUITTER", True, (255,255,255))

        screen.blit(restart_text,
            (restart_button.x + restart_button.width//2 - restart_text.get_width()//2,
             restart_button.y + 15)
        )

        screen.blit(quit_text,
            (quit_button.x + quit_button.width//2 - quit_text.get_width()//2,
             quit_button.y + 15)
        )

    pygame.display.flip()

pygame.quit()