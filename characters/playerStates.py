import pygame

from utils.vector import vec


class State:
    def enter(self, player):
        pass

    def exit(self, player):
        pass

    def update(self, player, dt):
        pass


class IdleState(State):
    def enter(self, player):
        player.setAnimation("idle")
        player.velocity = vec(0, 0)

    def update(self, player, dt):
        keys = pygame.key.get_pressed()
        if (
            keys[pygame.K_LEFT]
            or keys[pygame.K_RIGHT]
            or keys[pygame.K_UP]
            or keys[pygame.K_DOWN]
        ):
            player.changeState(WalkState())


class WalkState(State):
    SPEED = 126

    def enter(self, player):
        player.setAnimation("walk")

    def update(self, player, dt):
        keys = pygame.key.get_pressed()

        xVelo = 0
        yVelo = 0

        if keys[pygame.K_LEFT]:
            xVelo = -self.SPEED
            player.facing = "left"
        elif keys[pygame.K_RIGHT]:
            xVelo = self.SPEED
            player.facing = "right"

        if keys[pygame.K_UP]:
            yVelo = -self.SPEED
            player.facing = "up"
        elif keys[pygame.K_DOWN]:
            yVelo = self.SPEED
            player.facing = "down"

        player.velocity = vec(xVelo, yVelo)

        if xVelo == 0 and yVelo == 0:
            player.changeState(IdleState())
