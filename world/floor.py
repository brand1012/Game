import pygame

def buildFloor(game):
    floor = pygame.Surface(game.WORLD_SIZE)
    floor.fill((225, 225, 225))

    pygame.draw.rect(floor, (196, 196, 196), pygame.Rect(25, 25, 950, 625))
    pygame.draw.rect(floor, (80, 80, 80), pygame.Rect(25, 25, 950, 625), 8)

    pygame.draw.rect(floor, (168, 182, 196), pygame.Rect(200, 25, 600, 100))
    for x in range(220, 780, 80):
        pygame.draw.line(floor, (230, 230, 235), (x, 25), (x, 125), 4)

    pygame.draw.rect(floor, (191, 214, 191), pygame.Rect(200, 150, 600, 150))
    pygame.draw.rect(floor, (214, 189, 161), pygame.Rect(350, 325, 300, 200))
    pygame.draw.rect(floor, (206, 188, 223), pygame.Rect(200, 325, 125, 200))
    pygame.draw.rect(floor, (206, 188, 223), pygame.Rect(675, 325, 125, 200))
    pygame.draw.rect(floor, (205, 205, 205), pygame.Rect(200, 550, 600, 100))

    laneColor = (20, 20, 24)
    pygame.draw.rect(floor, laneColor, pygame.Rect(50, 25, 100, 625))
    pygame.draw.rect(floor, laneColor, pygame.Rect(850, 25, 100, 625))
    for y in range(35, 625, 55):
        pygame.draw.rect(floor, (245, 229, 110), pygame.Rect(97, y, 6, 28))
        pygame.draw.rect(floor, (245, 229, 110), pygame.Rect(897, y, 6, 28))

    pygame.draw.line(floor, (120, 120, 120), (325, 325), (325, 525), 4)
    pygame.draw.line(floor, (120, 120, 120), (675, 325), (675, 525), 4)

    return floor
