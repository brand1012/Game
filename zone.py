import pygame
from vector import vec, pyVec
from drawable import drawable

class Zone:
    '''
    This is just to set up the general layout, may not be used in final
    '''

    def __init__(self, position, size, name, color=(200,200,200), showLabel=True):
        self.position = vec(*position)
        self.size = size
        self.name = name
        self.color = color
        self.showLabel = showLabel

        self.rect = pygame.Rect(pyVec(position), size)

    def draw(self, surface):
        screenPos = self.position - drawable.CAMERA_OFFSET

        rect = pygame.Rect(tuple(int(x) for x in screenPos.ravel()), self.size)
        
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (0,0,0), rect, 3)

        if self.showLabel:
            font = pygame.font.SysFont("Arial", 20, bold=True)
            label = font.render(self.name, True, (0,0,0))
            surface.blit(label, (rect.x + 10, rect.y + 10))
