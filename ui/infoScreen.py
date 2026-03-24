import systems.economy as economy


def drawInfoScreen(game, surface):
    surface.fill((40, 40, 60))

    title = game.infoFont.render("FACTORY INFO", True, (255, 255, 255))
    surface.blit(title, (120, 20))

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
        surface.blit(text, (50, 40 + index * 15))

    prompt = game.myFont.render("Press I to close", True, (200, 200, 200))
    surface.blit(prompt, (50, 200))
