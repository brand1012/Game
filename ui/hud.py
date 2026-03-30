import pygame


def drawUI(game, surface):
    statsPanelRect = pygame.Rect(5, 5, 122, 34)
    controlsPanelRect = pygame.Rect(133, 5, 74, 26)
    controlFont = pygame.font.SysFont("Arial", 9, bold=True)

    pygame.draw.rect(surface, (236, 236, 236), statsPanelRect)
    pygame.draw.rect(surface, (0, 0, 0), statsPanelRect, 2)
    pygame.draw.rect(surface, (236, 236, 236), controlsPanelRect)
    pygame.draw.rect(surface, (0, 0, 0), controlsPanelRect, 2)

    moneyText = game.uiFont.render(f"Money: ${int(game.money)}", True, (0, 0, 0))
    surface.blit(moneyText, (10, 8))

    packageText = game.uiFont.render(
        f"Packages: {int(game.packagesShipped)}",
        True,
        (0, 0, 0),
    )
    surface.blit(packageText, (10, 21))

    infoHint = controlFont.render("I Info", True, (0, 0, 0))
    stockHint = controlFont.render("S Stock", True, (0, 0, 0))
    surface.blit(infoHint, (138, 8))
    surface.blit(stockHint, (138, 17))

    if game.showInteractPrompt:
        prompt = game.uiFont.render("Press E to interact", True, (0, 0, 0))
        x = (game.RESOLUTION[0] - prompt.get_width()) // 2
        y = game.RESOLUTION[1] - 30
        surface.blit(prompt, (x, y))
