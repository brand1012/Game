import pygame
from vector import vec

class State:
    def enter(self, kirby):
        pass

    def exit(self, kirby):
        pass

    def handleEvent(self, kirby, event):
        pass

    def update(self, kirby, dt):
        pass

class IdleState(State):
    def enter(self, kirby):
        kirby.setAnimation("idle")
        kirby.velocity = vec(0, 0)

    def update(self, kirby, dt):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or
            keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            kirby.changeState(WalkState())

class WalkState(State):
    SPEED = 60

    def enter(self, kirby):
        kirby.setAnimation("walk")

    def update(self, kirby, dt):
        keys = pygame.key.get_pressed()

        xVelo = 0
        yVelo = 0

        if keys[pygame.K_LEFT]:
            xVelo = -self.SPEED
            kirby.facing = "left"
        elif keys[pygame.K_RIGHT]:
            xVelo = self.SPEED
            kirby.facing = "right"

        if keys[pygame.K_UP]:
            yVelo = -self.SPEED
        elif keys[pygame.K_DOWN]:
            yVelo = self.SPEED

        kirby.velocity = vec(xVelo, yVelo)

        # change to idle if not moving
        if xVelo == 0 and yVelo == 0:
            kirby.changeState(IdleState())

