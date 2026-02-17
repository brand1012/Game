import pygame
import sys
from gameEngine import gameEngine

def main():

    game = gameEngine()
    RUNNING = True

    while RUNNING:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                RUNNING = False
            else:
                game.handleEvent(event)

        game.gameClock.tick(60)
        seconds = game.gameClock.get_time() / 1000
        game.update(seconds)
        game.draw(game.drawSurface)

    pygame.quit()

if __name__ == "__main__":
    main()