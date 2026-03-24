import pygame


def drawUI(game, surface):
    panelRect = pygame.Rect(5, 5, 90, 30)
    pygame.draw.rect(surface, (220, 220, 220), panelRect)
    pygame.draw.rect(surface, (0, 0, 0), panelRect, 2)

    moneyText = game.uiFont.render(f"Money: ${int(game.money)}", True, (0, 0, 0))
    surface.blit(moneyText, (10, 8))

    packageText = game.uiFont.render(f"Packages: {int(game.packagesShipped)}", True, (0, 0, 0))
    surface.blit(packageText, (10, 20))

    if game.showInteractPrompt:
        prompt = game.uiFont.render("Press E to interact", True, (0, 0, 0))
        x = (game.RESOLUTION[0] - prompt.get_width()) // 2
        y = game.RESOLUTION[1] - 30
        surface.blit(prompt, (x, y))
