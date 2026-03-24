import systems.economy as economy


def drawUpgradeScreen(game, surface):
    surface.fill((50, 50, 50))

    title = game.myFont.render("UPGRADE STATION", True, (255, 255, 255))
    surface.blit(title, (120, 20))

    upgrades = [
        ("+1 Extra Worker", economy.getWorkerCost(game)),
        ("+2 Van Capacity", economy.getCapacityCost(game)),
        ("+1 Extra Van", economy.getVanCost(game)),
    ]

    for index, (name, cost) in enumerate(upgrades):
        text = game.myFont.render(f"{index + 1}. {name} - ${cost}", True, (255, 255, 255))
        surface.blit(text, (50, 60 + index * 30))

    prompt = game.myFont.render("Press 1-3 to buy, backspace to exit", True, (200, 200, 200))
    surface.blit(prompt, (50, 160))
