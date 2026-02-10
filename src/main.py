import pygame
from graph import Graph
from player import Player

pygame.init()

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Carte du monde – Exploration")

clock = pygame.time.Clock()

# =====================
# GRAPHE COMPLET (20 villes)
# =====================
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
    (1,2),(2,3),(3,4),(4,5),(5,6),(6,7),
    (2,8),(3,9),(4,10),(5,11),(6,12),(7,13),
    (8,9),(9,10),(10,11),(11,12),(12,13),
    (9,15),(10,14),(11,14),
    (15,16),(16,17),
    (11,19),(12,18),(19,20),(18,20)
]

for a, b in edges:
    graph.add_edge(a, b, 10)

# =====================
# JOUEUR
# =====================
player = Player(start_city_id=1)
player.place_on_city(graph.cities[1])
graph.reveal_city_and_neighbors(1)

# =====================
# BOUCLE PRINCIPALE
# =====================
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and player.state == "idle":
            mx, my = pygame.mouse.get_pos()

            for neighbor_id, _ in graph.edges[player.current_city]:
                city = graph.cities[neighbor_id]
                if not city.visible:
                    continue
                dx = mx - city.x
                dy = my - city.y
                if dx*dx + dy*dy <= city.radius**2:
                    player.start_moving(
                        graph.cities[player.current_city],
                        city
                    )

    player.update()

    if player.state == "idle":
        graph.reveal_city_and_neighbors(player.current_city)

    screen.fill((35, 35, 35))
    graph.draw(screen)
    player.draw(screen)
    pygame.display.flip()

pygame.quit()
