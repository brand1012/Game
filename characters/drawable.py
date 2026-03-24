import pygame

from utils.vector import pyVec, vec


class Drawable(object):

    CAMERA_OFFSET = vec(0, 0)

    def __init__(self, position, image):
        self.position = position
        self.image = image

    def draw(self, surface):
        screenPos = self.position - Drawable.CAMERA_OFFSET
        surface.blit(self.image, pyVec(screenPos))

    def update(self, seconds):
        pass

class Mobile(Drawable):
    def __init__(self, position, image, bounds):
        super().__init__(position, image)
        self.velocity = vec(0, 0)
        self.bounds = bounds
        self.rect = pygame.Rect(pyVec(position), image.get_size())

    def updateRect(self):
        self.rect.topleft = pyVec(self.position)

    def collisionDetection(self, dt, walls):
        self.position[0] += self.velocity[0] * dt
        self.updateRect()
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity[0] > 0:
                    self.rect.right = wall.rect.left
                elif self.velocity[0] < 0:
                    self.rect.left = wall.rect.right
                self.position[0] = self.rect.x

        self.position[1] += self.velocity[1] * dt
        self.updateRect()
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity[1] > 0:
                    self.rect.bottom = wall.rect.top
                elif self.velocity[1] < 0:
                    self.rect.top = wall.rect.bottom
                self.position[1] = self.rect.y

    def update(self, dt, walls=None):
        if walls:
            self.collisionDetection(dt, walls)
        else:
            self.position += self.velocity * dt
            self.updateRect()

        w, h = self.bounds
        spriteWidth, spriteHeight = self.image.get_size()

        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] = 0
        elif self.position[0] > w - spriteWidth:
            self.position[0] = w - spriteWidth
            self.velocity[0] = 0

        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity[1] = 0
        elif self.position[1] > h - spriteHeight:
            self.position[1] = h - spriteHeight
            self.velocity[1] = 0

        self.updateRect()
