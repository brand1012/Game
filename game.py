import pygame
from gameEngine import GameEngine

def main():
    game = GameEngine()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            else:
                game.handleEvent(event)

        game.gameClock.tick(60)
        seconds = game.gameClock.get_time() / 1000
        game.update(seconds)
        game.draw(game.drawSurface)

    pygame.quit()

if __name__ == "__main__":
    main()