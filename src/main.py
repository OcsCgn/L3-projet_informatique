import pygame
from graph import Graph
from player import Player

pygame.init()

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Carte du monde – Exploration")

clock = pygame.time.Clock()

font_big = pygame.font.SysFont(None, 70)
font_medium = pygame.font.SysFont(None, 50)
font_small = pygame.font.SysFont(None, 35)

# ======================
# VARIABLES
# ======================

game_state = "menu"  # menu / playing / won / lost
player_name = ""
input_active = True

input_box = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 40, 300, 50)
start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50)

restart_button = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 40, 240, 60)
quit_button = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 120, 240, 60)


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

        # ======================
        # MENU
        # ======================
        if game_state == "menu":

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    if player_name.strip() != "":
                        graph, player = create_game()
                        game_state = "playing"
                else:
                    if len(player_name) < 15:
                        player_name += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    if player_name.strip() != "":
                        graph, player = create_game()
                        game_state = "playing"

        # ======================
        # JEU NORMAL
        # ======================
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

        # ======================
        # ÉCRAN FINAL
        # ======================
        elif game_state in ["won", "lost"]:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if restart_button.collidepoint(event.pos):
                    # On garde le nom et on relance directement
                    graph, player = create_game()
                    game_state = "playing"

                if quit_button.collidepoint(event.pos):
                    running = False

    # ======================
    # UPDATE
    # ======================

    if game_state == "playing":
        player.update()

        if player.state == "idle":
            graph.reveal_city_and_neighbors(player.current_city)

        if player.energy == 0:
            game_state = "lost"

        if player.current_city == 20:
            game_state = "won"

    # ======================
    # AFFICHAGE
    # ======================

    screen.fill((35, 35, 35))

    if game_state == "menu":

        title = font_big.render("ENTREZ VOTRE NOM", True, (255,255,255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))

        pygame.draw.rect(screen, (255,255,255), input_box, 2)

        name_surface = font_medium.render(player_name, True, (255,255,255))
        screen.blit(name_surface, (input_box.x + 10, input_box.y + 10))

        pygame.draw.rect(screen, (0,150,0), start_button)
        start_text = font_small.render("START", True, (255,255,255))
        screen.blit(start_text,
            (start_button.x + start_button.width//2 - start_text.get_width()//2,
             start_button.y + 10)
        )

    elif game_state == "playing":

        graph.draw(screen)
        player.draw(screen)
        player.draw_energy_bar(screen)

        # Nom au-dessus de la barre avec espace propre
        name_text = font_small.render(player_name, True, (255,255,255))
        screen.blit(name_text, (20, 20))

    elif game_state in ["won", "lost"]:

        graph.draw(screen)
        player.draw(screen)
        player.draw_energy_bar(screen)

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))

        if game_state == "won":
            message = "VICTOIRE !"
            color = (0,255,0)
        else:
            message = "VOUS AVEZ ÉCHOUÉ"
            color = (255,0,0)

        text = font_big.render(message, True, color)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 120))

        pygame.draw.rect(screen, (0,150,0), restart_button)
        pygame.draw.rect(screen, (150,0,0), quit_button)

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