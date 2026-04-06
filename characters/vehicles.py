from collections import deque
import math

import pygame

from characters.drawable import Drawable
from characters.props import Prop
from utils.vector import magnitude, normalize, pyVec, vec


def projectedHalfExtent(rect, axis):
    return ((abs(axis[0]) * rect.width) + (abs(axis[1]) * rect.height)) / 2.0


def isForwardImpact(targetRect, hazardRect, direction, crossRatio=0.35, forwardPadding=4.0):
    if targetRect is None or hazardRect is None or magnitude(direction) == 0:
        return False

    forward = normalize(direction)
    right = vec(-forward[1], forward[0])
    targetCenter = vec(*targetRect.center)
    hazardCenter = vec(*hazardRect.center)
    relative = targetCenter - hazardCenter

    forwardDistance = (relative[0] * forward[0]) + (relative[1] * forward[1])
    lateralDistance = abs((relative[0] * right[0]) + (relative[1] * right[1]))
    forwardReach = projectedHalfExtent(hazardRect, forward) + projectedHalfExtent(targetRect, forward)
    crossReach = (projectedHalfExtent(hazardRect, right) * crossRatio) + projectedHalfExtent(targetRect, right)
    gapToFront = forwardDistance - forwardReach

    return (
        forwardDistance > 0
        and gapToFront <= forwardPadding
        and lateralDistance <= max(8, crossReach)
    )


class LaneVehicle(Prop):
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
        collisionOffset=(0, 0),
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

    def stopAtSlot(self):
        self.updateRect()
        self.velocity = vec(0, 0)
        self.pauseTimer = self.pauseDuration
        self.hasStoppedAtSlot = True

    def finishWave(self):
        self.active = False
        self.hasExitedScreen = True
        self.velocity = vec(0, 0)

    def isMoving(self):
        return (
            self.active
            and self.startDelay <= 0
            and self.pauseTimer <= 0
            and magnitude(self.velocity) > 0
        )

    def isForwardImpact(self, targetRect):
        return isForwardImpact(targetRect, self.rect, self.velocity)

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
                self.stopAtSlot()
                return

        self.updateRect()

        if self.velocity[1] > 0 and self.position[1] > self.resetY[1]:
            self.finishWave()
        elif self.velocity[1] < 0 and self.position[1] < self.resetY[0]:
            self.finishWave()

    def draw(self, surface):
        if not self.active:
            return
        super().draw(surface)


class SemiTruckRig(object):
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
        hitchOffset=6.0,
    ):
        self.baseCabImage = cabImage
        self.baseTrailerImage = trailerImage
        self.cabSize = cabSize
        self.trailerSize = trailerSize
        self.pathPoints = [vec(*point) for point in pathPoints]
        self.dockPauseDuration = dockPauseDuration
        self.initialStartDelay = startDelay
        self.speed = speed
        self.trailerFollowDistance = trailerFollowDistance
        self.hitchOffset = hitchOffset
        self.pauseIndex = max(1, len(self.pathPoints) // 2)
        self.historySpacing = 4.0
        self.collisionInset = vec(18, 10)
        trailerWidth, trailerLength = self.trailerSize
        insetX, insetY = self.collisionInset
        self.collisionSize = (
            max(1, int(trailerWidth - insetX * 2)),
            max(1, int(trailerLength - insetY * 2)),
        )
        self.cabRect = pygame.Rect(0, 0, *self.cabSize)
        self.trailerRect = pygame.Rect(0, 0, *self.trailerSize)
        self.rect = pygame.Rect(0, 0, *self.collisionSize)
        self.restart()

    def restart(self):
        self.startDelay = self.initialStartDelay
        self.pauseTimer = 0.0
        self.finished = False
        self.active = True
        self.currentPointIndex = 0
        self.pauseConsumed = False
        self.currentCabCenter = self.pathPoints[0].copy()
        initialDirection = self.pathPoints[1] - self.pathPoints[0]
        if magnitude(initialDirection) == 0:
            initialDirection = vec(0, 1)
        else:
            initialDirection = normalize(initialDirection)
        self.cabDirection = initialDirection
        self.trailerDirection = initialDirection
        self.hitchHistory = deque()
        hitchDistanceFromCenter = max(0, (self.cabSize[1] / 2) - self.hitchOffset)
        initialHitch = self.currentCabCenter - self.cabDirection * hitchDistanceFromCenter
        for _ in range(160):
            self.hitchHistory.append(initialHitch.copy())
        self.trailerFrontPoint = initialHitch.copy()
        self.updateCollisionRect()

    def updateHitchHistory(self, hitchPoint):
        if not self.hitchHistory:
            self.hitchHistory.append(hitchPoint.copy())
            return

        lastPoint = self.hitchHistory[-1]
        delta = hitchPoint - lastPoint
        distance = magnitude(delta)
        if distance == 0:
            return

        direction = normalize(delta)
        while distance >= self.historySpacing:
            lastPoint = lastPoint + direction * self.historySpacing
            self.hitchHistory.append(lastPoint.copy())
            distance = magnitude(hitchPoint - lastPoint)

        self.hitchHistory.append(hitchPoint.copy())
        while len(self.hitchHistory) > 240:
            self.hitchHistory.popleft()

    def updateCollisionRect(self):
        cabAngle = math.degrees(math.atan2(-self.cabDirection[0], -self.cabDirection[1]))
        trailerAngle = math.degrees(math.atan2(-self.trailerDirection[0], -self.trailerDirection[1]))
        cabImage = pygame.transform.rotate(
            pygame.transform.smoothscale(self.baseCabImage, self.cabSize),
            cabAngle,
        )
        trailerImage = pygame.transform.rotate(
            pygame.transform.smoothscale(self.baseTrailerImage, self.trailerSize),
            trailerAngle,
        )
        cabRect = cabImage.get_rect(center=pyVec(self.currentCabCenter))
        trailerCenter = self.trailerFrontPoint - self.trailerDirection * (self.trailerSize[1] / 2)
        trailerRect = trailerImage.get_rect(center=pyVec(trailerCenter))
        self.cabRect = cabRect
        self.trailerRect = trailerRect
        self.rect = cabRect.union(trailerRect)

    def finishRoute(self):
        self.finished = True
        self.active = False
        self.updateCollisionRect()

    def isMoving(self):
        return (
            self.active
            and not self.finished
            and self.startDelay <= 0
            and self.pauseTimer <= 0
        )

    def isForwardImpact(self, targetRect):
        return isForwardImpact(targetRect, self.cabRect, self.cabDirection)

    def update(self, seconds):
        if not self.active:
            return

        if self.startDelay > 0:
            self.startDelay = max(0, self.startDelay - seconds)
            return

        if self.pauseTimer > 0:
            self.pauseTimer = max(0, self.pauseTimer - seconds)
            self.updateTrailer()
            return

        remainingDistance = self.speed * seconds
        while remainingDistance > 0 and not self.finished:
            if self.currentPointIndex >= len(self.pathPoints) - 1:
                self.finishRoute()
                return

            segmentEnd = self.pathPoints[self.currentPointIndex + 1]
            segmentVector = segmentEnd - self.currentCabCenter
            segmentLength = magnitude(segmentVector)

            if segmentLength == 0:
                self.currentPointIndex += 1
                continue

            direction = normalize(segmentVector)
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

        self.updateTrailer()

    def updateTrailer(self):
        hitchDistanceFromCenter = max(0, (self.cabSize[1] / 2) - self.hitchOffset)
        hitchPoint = self.currentCabCenter - self.cabDirection * hitchDistanceFromCenter
        self.updateHitchHistory(hitchPoint)

        if not self.hitchHistory:
            self.trailerFrontPoint = vec(0, 0)
            self.updateCollisionRect()
            return

        remaining = self.trailerFollowDistance
        points = list(self.hitchHistory)
        current = points[-1]
        trailerDirection = self.trailerDirection

        for index in range(len(points) - 2, -1, -1):
            previous = points[index]
            segment = current - previous
            segmentLength = magnitude(segment)
            if segmentLength == 0:
                current = previous
                continue
            if segmentLength >= remaining:
                trailerDirection = normalize(segment)
                self.trailerFrontPoint = current - trailerDirection * remaining
                self.trailerDirection = trailerDirection
                self.updateCollisionRect()
                return
            remaining -= segmentLength
            current = previous

        self.trailerFrontPoint = points[0].copy()
        if len(points) >= 2 and magnitude(points[1] - points[0]) != 0:
            self.trailerDirection = normalize(points[1] - points[0])
        self.updateCollisionRect()

    def draw(self, surface):
        if not self.active or self.startDelay > 0:
            return

        cabAngle = math.degrees(math.atan2(-self.cabDirection[0], -self.cabDirection[1]))
        trailerAngle = math.degrees(math.atan2(-self.trailerDirection[0], -self.trailerDirection[1]))
        cabImage = pygame.transform.rotate(
            pygame.transform.smoothscale(self.baseCabImage, self.cabSize),
            cabAngle,
        )
        trailerImage = pygame.transform.rotate(
            pygame.transform.smoothscale(self.baseTrailerImage, self.trailerSize),
            trailerAngle,
        )
        cabRect = cabImage.get_rect(center=pyVec(self.currentCabCenter))
        trailerCenter = self.trailerFrontPoint - self.trailerDirection * (self.trailerSize[1] / 2)
        trailerRect = trailerImage.get_rect(center=pyVec(trailerCenter))
        cabRect = cabRect.move(-int(Drawable.CAMERA_OFFSET[0]), -int(Drawable.CAMERA_OFFSET[1]))
        trailerRect = trailerRect.move(
            -int(Drawable.CAMERA_OFFSET[0]),
            -int(Drawable.CAMERA_OFFSET[1]),
        )

        surface.blit(cabImage, cabRect.topleft)
        surface.blit(trailerImage, trailerRect.topleft)
