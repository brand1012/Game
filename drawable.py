from vector import pyVec, vec, normalize, magnitude
import pygame
import math
from collections import deque
from kirbystates import IdleState, WalkState

class drawable(object):

    CAMERA_OFFSET = vec(0,0)

    def __init__(self, position, image):
        self.position = position
        self.image = image

    def draw(self, surface):
        screenPos = self.position - drawable.CAMERA_OFFSET
        surface.blit(self.image, pyVec(screenPos))

    def setPosition(self, newPosition):
        self.position = newPosition

    def update(self, seconds):
        pass

    def handleEvent(self, event):
        pass


class mobile(drawable):
    def __init__(self, position, image, bounds):
        super().__init__(position, image)
        self.velocity = vec(0,0)
        self.bounds = bounds # (width, height)
        self.rect = pygame.Rect(pyVec(position), image.get_size())

    def updateRect(self):
        self.rect.topleft = pyVec(self.position)

    def collisionDetection(self, dt, walls):
        # X axis
        self.position[0] += self.velocity[0] * dt
        self.updateRect()
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity[0] > 0:
                    self.rect.right = wall.rect.left
                elif self.velocity[0] < 0:
                    self.rect.left = wall.rect.right
                self.position[0] = self.rect.x

        # Y axis
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

        # Clamp X
        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] = 0
        elif self.position[0] > w - spriteWidth:
            self.position[0] = w - spriteWidth
            self.velocity[0] = 0

        # Clamp Y
        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity[1] = 0
        elif self.position[1] > h - spriteHeight:
            self.position[1] = h - spriteHeight
            self.velocity[1] = 0

        self.updateRect()


class wall(drawable):
    def __init__(self, position, image):
        super().__init__(position, image)
        self.rect = pygame.Rect(pyVec(position), image.get_size())

    def updateRect(self):
        self.rect.topleft = pyVec(self.position)


class prop(drawable):
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


class animatedProp(prop):
    def __init__(
        self,
        position,
        frames,
        framesPerSecond=6,
        collisionSize=None,
        collisionOffset=(0, 0)
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


class loopingProp(prop):
    def __init__(self, position, image, speed, loopStartX, loopEndX, collisionSize=None, collisionOffset=(0, 0)):
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


class laneVehicle(prop):
    def __init__(
        self,
        position,
        image,
        velocity,
        resetY,
        stopY=None,
        pauseDuration=0,
        startDelay=0,
        collisionSize=None,
        collisionOffset=(0, 0)
    ):
        super().__init__(position, image, collisionSize, collisionOffset)
        self.spawnPosition = vec(*position)
        self.baseVelocity = vec(*velocity)
        self.velocity = vec(*velocity)
        self.resetY = resetY
        self.stopY = stopY
        self.pauseDuration = pauseDuration
        self.pauseTimer = 0
        self.startDelay = startDelay
        self.initialStartDelay = startDelay
        self.hasStoppedAtSlot = False
        self.active = True
        self.hasExitedScreen = False

    def restartWave(self):
        self.position = self.spawnPosition.copy()
        self.velocity = self.baseVelocity.copy()
        self.pauseTimer = 0
        self.startDelay = self.initialStartDelay
        self.hasStoppedAtSlot = False
        self.active = True
        self.hasExitedScreen = False
        self.updateRect()

    def update(self, seconds):
        if not self.active:
            return

        if self.startDelay > 0:
            self.startDelay = max(0, self.startDelay - seconds)
            return

        if self.pauseTimer > 0:
            self.pauseTimer = max(0, self.pauseTimer - seconds)
            if self.pauseTimer == 0:
                self.velocity = self.baseVelocity.copy()
            return

        previousY = self.position[1]
        self.position += self.velocity * seconds

        if self.stopY is not None and self.velocity[1] != 0 and not self.hasStoppedAtSlot:
            movingDownIntoStop = self.velocity[1] > 0 and previousY < self.stopY <= self.position[1]
            movingUpIntoStop = self.velocity[1] < 0 and previousY > self.stopY >= self.position[1]
            if movingDownIntoStop or movingUpIntoStop:
                self.position[1] = self.stopY
                self.updateRect()
                self.velocity = vec(0, 0)
                self.pauseTimer = self.pauseDuration
                self.hasStoppedAtSlot = True
                return

        self.updateRect()

        if self.velocity[1] > 0 and self.position[1] > self.resetY[1]:
            self.active = False
            self.hasExitedScreen = True
            self.velocity = vec(0, 0)
        elif self.velocity[1] < 0 and self.position[1] < self.resetY[0]:
            self.active = False
            self.hasExitedScreen = True
            self.velocity = vec(0, 0)

    def draw(self, surface):
        if not self.active:
            return
        super().draw(surface)


class semiTruckRig(object):
    def __init__(
        self,
        cabImage,
        trailerImage,
        cabSize,
        trailerSize,
        pathPoints,
        dockPauseDuration=10.0,
        startDelay=0.0,
        speed=90.0,
        trailerFollowDistance=70.0,
        hitchOffset=6.0
    ):
        self.baseCabImage = cabImage
        self.baseTrailerImage = trailerImage
        self.cabSize = cabSize
        self.trailerSize = trailerSize
        self.cabWidth = self.cabSize[0]
        self.cabLength = self.cabSize[1]
        self.trailerWidth = self.trailerSize[0]
        self.trailerLength = self.trailerSize[1]
        self.pathPoints = [vec(*point) for point in pathPoints]
        self.dockPauseDuration = dockPauseDuration
        self.initialStartDelay = startDelay
        self.speed = speed
        self.trailerFollowDistance = trailerFollowDistance
        self.hitchOffset = hitchOffset
        self.pauseIndex = max(1, len(self.pathPoints) // 2)
        self.historySpacing = 4.0
        self.collisionInset = vec(18, 10)
        self.collisionSize = (
            max(1, int(self.trailerWidth - self.collisionInset[0] * 2)),
            max(1, int(self.trailerLength - self.collisionInset[1] * 2))
        )
        self.rect = pygame.Rect(0, 0, *self.collisionSize)
        self.restart()

    def normalizeDirection(self, direction, fallback=None):
        if magnitude(direction) == 0:
            if fallback is not None:
                return fallback.copy()
            return vec(0, 1)
        return normalize(direction)

    def restart(self):
        self.startDelay = self.initialStartDelay
        self.pauseTimer = 0.0
        self.finished = False
        self.active = True
        self.currentPointIndex = 0
        self.pauseConsumed = False
        self.currentCabCenter = self.pathPoints[0].copy()
        initialDirection = self.normalizeDirection(self.pathPoints[1] - self.pathPoints[0])
        self.cabDirection = initialDirection
        self.trailerDirection = initialDirection
        self.hitchHistory = deque()
        initialHitch = self.getCabHitchPoint()
        for _ in range(160):
            self.hitchHistory.append(initialHitch.copy())
        self.trailerFrontPoint = initialHitch.copy()
        self.updateCollisionRect()

    def getAngleFromDirection(self, direction):
        return math.degrees(math.atan2(-direction[0], -direction[1]))

    def getCabHitchPoint(self):
        hitchDistanceFromCenter = max(0, (self.cabLength / 2) - self.hitchOffset)
        return self.currentCabCenter - self.cabDirection * hitchDistanceFromCenter

    def addHitchHistoryPoint(self, point):
        if not self.hitchHistory:
            self.hitchHistory.append(point.copy())
            return

        lastPoint = self.hitchHistory[-1]
        delta = point - lastPoint
        distance = magnitude(delta)
        if distance == 0:
            return

        direction = self.normalizeDirection(delta, self.cabDirection)
        while distance >= self.historySpacing:
            lastPoint = lastPoint + direction * self.historySpacing
            self.hitchHistory.append(lastPoint.copy())
            distance = magnitude(point - lastPoint)

        self.hitchHistory.append(point.copy())
        while len(self.hitchHistory) > 240:
            self.hitchHistory.popleft()

    def getPointAlongHistory(self, followDistance):
        if not self.hitchHistory:
            return vec(0, 0), self.trailerDirection

        remaining = followDistance
        points = list(self.hitchHistory)
        current = points[-1]
        for index in range(len(points) - 2, -1, -1):
            previous = points[index]
            segment = current - previous
            segmentLength = magnitude(segment)
            if segmentLength == 0:
                current = previous
                continue
            if segmentLength >= remaining:
                direction = self.normalizeDirection(segment, self.trailerDirection)
                point = current - direction * remaining
                return point, direction
            remaining -= segmentLength
            current = previous

        if len(points) >= 2:
            fallbackDirection = self.normalizeDirection(points[1] - points[0], self.trailerDirection)
        else:
            fallbackDirection = self.trailerDirection
        return points[0].copy(), fallbackDirection

    def updateCollisionRect(self):
        cabRect, trailerRect = self.getWorldRects()
        self.rect = cabRect.union(trailerRect)

    def getRotatedImages(self):
        cabAngle = self.getAngleFromDirection(self.cabDirection)
        trailerAngle = self.getAngleFromDirection(self.trailerDirection)

        cabImage = pygame.transform.rotate(
            pygame.transform.smoothscale(self.baseCabImage, self.cabSize),
            cabAngle
        )
        trailerImage = pygame.transform.rotate(
            pygame.transform.smoothscale(self.baseTrailerImage, self.trailerSize),
            trailerAngle
        )
        return cabImage, trailerImage

    def getWorldRects(self):
        cabImage, trailerImage = self.getRotatedImages()
        cabRect = cabImage.get_rect(center=pyVec(self.currentCabCenter))
        trailerRect = trailerImage.get_rect(center=pyVec(self.getTrailerCenter()))
        return cabRect, trailerRect

    def getCabTopLeft(self):
        return self.currentCabCenter - vec(self.cabWidth, self.cabLength) / 2

    def getTrailerCenter(self):
        return self.trailerFrontPoint - self.trailerDirection * (self.trailerLength / 2)

    def getTrailerTopLeft(self):
        return self.getTrailerCenter() - vec(self.trailerWidth, self.trailerLength) / 2

    def update(self, seconds):
        if not self.active:
            return

        if self.startDelay > 0:
            self.startDelay = max(0, self.startDelay - seconds)
            return

        if self.pauseTimer > 0:
            self.pauseTimer = max(0, self.pauseTimer - seconds)
            hitchPoint = self.getCabHitchPoint()
            self.addHitchHistoryPoint(hitchPoint)
            self.trailerFrontPoint, trailerDirection = self.getPointAlongHistory(self.trailerFollowDistance)
            self.trailerDirection = trailerDirection
            self.updateCollisionRect()
            return

        remainingDistance = self.speed * seconds
        while remainingDistance > 0 and not self.finished:
            if self.currentPointIndex >= len(self.pathPoints) - 1:
                self.finished = True
                self.active = False
                self.updateCollisionRect()
                return

            segmentStart = self.pathPoints[self.currentPointIndex]
            segmentEnd = self.pathPoints[self.currentPointIndex + 1]
            segmentVector = segmentEnd - self.currentCabCenter
            segmentLength = magnitude(segmentVector)

            if segmentLength == 0:
                self.currentPointIndex += 1
                continue

            direction = self.normalizeDirection(segmentVector, self.cabDirection)
            travel = min(remainingDistance, segmentLength)
            self.currentCabCenter += direction * travel
            self.cabDirection = direction
            remainingDistance -= travel

            if magnitude(segmentEnd - self.currentCabCenter) <= 0.01:
                self.currentCabCenter = segmentEnd.copy()
                self.currentPointIndex += 1
                if self.currentPointIndex == self.pauseIndex and not self.pauseConsumed:
                    self.pauseTimer = self.dockPauseDuration
                    self.pauseConsumed = True
                    break

        hitchPoint = self.getCabHitchPoint()
        self.addHitchHistoryPoint(hitchPoint)
        self.trailerFrontPoint, trailerDirection = self.getPointAlongHistory(self.trailerFollowDistance)
        self.trailerDirection = trailerDirection
        self.updateCollisionRect()

    def draw(self, surface):
        if not self.active or self.startDelay > 0:
            return

        cabImage, trailerImage = self.getRotatedImages()
        cabRect, trailerRect = self.getWorldRects()
        cabRect = cabRect.move(-int(drawable.CAMERA_OFFSET[0]), -int(drawable.CAMERA_OFFSET[1]))
        trailerRect = trailerRect.move(-int(drawable.CAMERA_OFFSET[0]), -int(drawable.CAMERA_OFFSET[1]))

        surface.blit(cabImage, cabRect.topleft)
        surface.blit(trailerImage, trailerRect.topleft)

class kirby(drawable):
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
        self.shadow = spriteManager.getSprite(
            "Character Sprites/CharacterModel/Shadow.png"
        )

        self.animations = {
            "idle": self.buildDirectionalAnimations(
                row=0,
                outfitRow=3,
                frameIndices=[0]
            ),
            "walk": self.buildDirectionalAnimations(
                row=0,
                outfitRow=3,
                frameIndices=[0, 1, 2, 3, 4, 5]
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
        self.rect = pygame.Rect(
            pyVec(position + self.collisionOffset),
            self.collisionSize
        )
        self.interactionOffset = vec(7, 8)
        self.interactionSize = (18, 24)
        self.interactionRect = pygame.Rect(
            pyVec(position + self.interactionOffset),
            self.interactionSize
        )

        # --- Finite State Machine ---
        self.state = IdleState()
        self.state.enter(self)

    def getPosition(self):
        return self.position
    
    def getSize(self):
        return vec(*self.image.get_size())
    
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
                    frameIndex=startColumn + frameIndex
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
        # X axis
        self.position[0] += self.velocity[0] * dt
        self.updateRect()
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity[0] > 0:
                    self.rect.right = wall.rect.left
                elif self.velocity[0] < 0:
                    self.rect.left = wall.rect.right
                self.position[0] = self.rect.x - self.collisionOffset[0]

        # Y axis
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
        screenPos = self.position - drawable.CAMERA_OFFSET
        surface.blit(self.shadow, pyVec(screenPos))
        surface.blit(self.image, pyVec(screenPos))
