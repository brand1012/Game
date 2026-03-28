import pygame


WAREHOUSE_SHEET = "WarehouseV2.png"
FORKLIFT_RECT = pygame.Rect(384, 0, 110, 64)


def scaleToFit(surface, size):
    sourceWidth, sourceHeight = surface.get_size()
    if sourceWidth == 0 or sourceHeight == 0:
        return pygame.Surface(size, pygame.SRCALPHA)

    scale = min(size[0] / sourceWidth, size[1] / sourceHeight)
    scaledSize = (
        max(1, int(round(sourceWidth * scale))),
        max(1, int(round(sourceHeight * scale))),
    )
    scaled = pygame.transform.smoothscale(surface, scaledSize)

    canvas = pygame.Surface(size, pygame.SRCALPHA)
    drawX = (size[0] - scaledSize[0]) // 2
    drawY = (size[1] - scaledSize[1]) // 2
    canvas.blit(scaled, (drawX, drawY))
    return canvas


def loadForkliftSprite(spriteManager, size):
    forklift = spriteManager.getSprite(WAREHOUSE_SHEET, FORKLIFT_RECT).copy()
    return scaleToFit(forklift, size)
