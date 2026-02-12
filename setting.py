from pygame.math import Vector2

SECREEN_WIDTH = 960
SCREEN_HEIGHT = 580
TILE_SIZE = 64


OVERLAY_POSITIONS = {
    'map' :(SECREEN_WIDTH-280,SCREEN_HEIGHT-700)
}

PLAYER_TOOL_OFFSET = {
    'left': Vector2(-10, 10), 
    'right': Vector2(10, 10),
    'up': Vector2(0, -10), 
    'down': Vector2(0, 10) 
}

