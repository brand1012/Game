import pygame

from characters.drawable import Drawable
from utils.vector import pyVec, vec

class Zone:
    def __init__(self, position, size, name, color=(200, 200, 200), showLabel=True):
        self.position = vec(*position)
        self.size = size
        self.name = name
        self.color = color
        self.showLabel = showLabel

        self.rect = pygame.Rect(pyVec(position), size)

    def draw(self, surface):
        screenPos = self.position - Drawable.CAMERA_OFFSET
        rect = pygame.Rect(tuple(int(x) for x in screenPos.ravel()), self.size)

        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 3)

        if self.showLabel:
            font = pygame.font.SysFont("Arial", 20, bold=True)
            label = font.render(self.name, True, (0, 0, 0))
            surface.blit(label, (rect.x + 10, rect.y + 10))
