import pygame

from characters.drawable import Drawable
from characters.playerStates import IdleState
from utils.vector import pyVec, vec


class Player(Drawable):
    def __init__(self, position, spriteManager, bounds):
        self.frameWidth = 32
        self.frameHeight = 32
        self.directionColumns = {
            "down": 0,
            "right": 6,
            "up": 12,
            "left": 18,
        }
        self.bodySheet = spriteManager.getSprite(
            "Character Sprites/CharacterModel/Character Model.png"
        )
        self.suitSheet = spriteManager.getSprite("Character Sprites/Suit.png")
        self.shadow = spriteManager.getSprite("Character Sprites/CharacterModel/Shadow.png")

        self.animations = {
            "idle": self.buildDirectionalAnimations(
                row=0,
                outfitRow=3,
                frameIndices=[0],
            ),
            "walk": self.buildDirectionalAnimations(
                row=0,
                outfitRow=3,
                frameIndices=[0, 1, 2, 3, 4, 5],
            ),
        }

        self.stateName = "idle"
        self.frame = 0
        self.timer = 0
        self.framesPerSecond = 10
        self.facing = "down"

        self.image = self.animations["idle"][self.facing][0]
        super().__init__(position, self.image)

        self.velocity = vec(0, 0)
        self.bounds = bounds
        self.collisionOffset = vec(11, 27)
        self.collisionSize = (10, 4)
        self.rect = pygame.Rect(pyVec(position + self.collisionOffset), self.collisionSize)
        self.interactionOffset = vec(7, 8)
        self.interactionSize = (18, 24)
        self.interactionRect = pygame.Rect(
            pyVec(position + self.interactionOffset),
            self.interactionSize,
        )

        self.state = IdleState()
        self.state.enter(self)

    def setAnimation(self, name):
        if self.stateName != name:
            self.stateName = name
            self.frame = 0
            self.timer = 0
        self.image = self.getCurrentFrames()[0]

    def changeState(self, newState):
        self.state.exit(self)
        self.state = newState
        self.state.enter(self)

    def buildDirectionalAnimations(self, row, outfitRow, frameIndices):
        return {
            direction: [
                self.buildFrame(
                    row=row,
                    outfitRow=outfitRow,
                    frameIndex=startColumn + frameIndex,
                )
                for frameIndex in frameIndices
            ]
            for direction, startColumn in self.directionColumns.items()
        }

    def getCurrentFrames(self):
        return self.animations[self.stateName][self.facing]

    def buildFrame(self, row, outfitRow, frameIndex):
        surface = pygame.Surface((self.frameWidth, self.frameHeight), pygame.SRCALPHA)
        bodyRect = self.getFrameRect(row, frameIndex, self.bodySheet)
        outfitRect = self.getFrameRect(outfitRow, frameIndex, self.suitSheet)
        surface.blit(self.bodySheet, (0, 0), bodyRect)
        surface.blit(self.suitSheet, (0, 0), outfitRect)
        return surface

    def getFrameRect(self, row, frameIndex, sheet):
        columns = sheet.get_width() // self.frameWidth
        clampedIndex = max(0, min(frameIndex, columns - 1))
        return pygame.Rect(
            clampedIndex * self.frameWidth,
            row * self.frameHeight,
            self.frameWidth,
            self.frameHeight,
        )

    def updateRect(self):
        self.rect.topleft = pyVec(self.position + self.collisionOffset)
        self.interactionRect.topleft = pyVec(self.position + self.interactionOffset)

    def collisionDetection(self, dt, walls):
        self.position[0] += self.velocity[0] * dt
        self.updateRect()
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity[0] > 0:
                    self.rect.right = wall.rect.left
                elif self.velocity[0] < 0:
                    self.rect.left = wall.rect.right
                self.position[0] = self.rect.x - self.collisionOffset[0]

        self.position[1] += self.velocity[1] * dt
        self.updateRect()
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity[1] > 0:
                    self.rect.bottom = wall.rect.top
                elif self.velocity[1] < 0:
                    self.rect.top = wall.rect.bottom
                self.position[1] = self.rect.y - self.collisionOffset[1]

    def updateAnimation(self, dt):
        frames = self.getCurrentFrames()

        self.timer += dt
        if self.timer >= 1 / self.framesPerSecond:
            self.timer -= 1 / self.framesPerSecond
            self.frame = (self.frame + 1) % len(frames)

        self.image = frames[self.frame]

    def update(self, dt, walls=None):
        self.state.update(self, dt)

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
        self.updateAnimation(dt)

    def draw(self, surface):
        screenPos = self.position - Drawable.CAMERA_OFFSET
        surface.blit(self.shadow, pyVec(screenPos))
        surface.blit(self.image, pyVec(screenPos))
