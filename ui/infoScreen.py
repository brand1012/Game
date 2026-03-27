import pygame

import systems.economy as economy


def drawInfoScreen(game, surface):
    surface.fill((37, 44, 61))

    title = game.myFont.render("WAREHOUSE INFO", True, (255, 255, 255))
    surface.blit(title, (112, 12))

    stats = [
        f"Workers: {game.workers}",
        f"Vans: {game.vans}",
        f"Van capacity: {game.vanCapacity} packages",
        f"Money: ${int(game.money)}",
        f"Packages shipped: {int(game.packagesShipped)}",
        f"Income per second: ${economy.getIncomePerSecond(game)}/sec",
        f"Contract multiplier: x{game.contractMultiplier}",
    ]

    for index, stat in enumerate(stats):
        text = game.infoFont.render(stat, True, (255, 255, 255))
        surface.blit(text, (44, 42 + index * 16))

    pygame.draw.line(surface, (88, 101, 126), (16, 170), (384, 170), 1)
    prompt = game.infoFont.render("Press I to close", True, (220, 220, 220))
    surface.blit(prompt, (surface.get_width() - prompt.get_width() - 14, 178))
