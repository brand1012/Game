import pygame

from characters.drawable import Drawable
from utils.vector import pyVec, vec


class Wall(Drawable):
    def __init__(self, position, image):
        super().__init__(position, image)
        self.rect = pygame.Rect(pyVec(position), image.get_size())

    def updateRect(self):
        self.rect.topleft = pyVec(self.position)


class Prop(Drawable):
    def __init__(self, position, image, collisionSize=None, collisionOffset=(0, 0)):
        position = vec(*position)
        super().__init__(position, image)

        self.rect = None
        self.collisionOffset = vec(*collisionOffset)
        if collisionSize:
            collisionPosition = position + self.collisionOffset
            self.rect = pygame.Rect(pyVec(collisionPosition), collisionSize)

    def updateRect(self):
        if self.rect:
            self.rect.topleft = pyVec(self.position + self.collisionOffset)


class AnimatedProp(Prop):
    def __init__(
        self,
        position,
        frames,
        framesPerSecond=6,
        collisionSize=None,
        collisionOffset=(0, 0),
    ):
        super().__init__(position, frames[0], collisionSize, collisionOffset)
        self.frames = frames
        self.framesPerSecond = framesPerSecond
        self.frameIndex = 0
        self.timer = 0

    def update(self, seconds):
        if len(self.frames) <= 1 or self.framesPerSecond <= 0:
            return

        self.timer += seconds
        frameDuration = 1 / self.framesPerSecond
        while self.timer >= frameDuration:
            self.timer -= frameDuration
            self.frameIndex = (self.frameIndex + 1) % len(self.frames)
            self.image = self.frames[self.frameIndex]


class LoopingProp(Prop):
    def __init__(
        self,
        position,
        image,
        speed,
        loopStartX,
        loopEndX,
        collisionSize=None,
        collisionOffset=(0, 0),
    ):
        super().__init__(position, image, collisionSize, collisionOffset)
        self.speed = speed
        self.loopStartX = loopStartX
        self.loopEndX = loopEndX

    def update(self, seconds):
        self.position[0] += self.speed * seconds

        if self.speed > 0 and self.position[0] > self.loopEndX:
            self.position[0] = self.loopStartX
        elif self.speed < 0 and self.position[0] + self.image.get_width() < self.loopStartX:
            self.position[0] = self.loopEndX

        self.updateRect()
