import systems.economy as economy


def drawUpgradeScreen(game, surface):
    surface.fill((50, 50, 50))

    title = game.myFont.render("UPGRADE STATION", True, (255, 255, 255))
    surface.blit(title, (114, 18))

    moneyLabel = "Business cash" if game.mode == "story" and game.campaign else "Money"
    moneyText = game.infoFont.render("{0}: ${1}".format(moneyLabel, int(game.money)), True, (228, 228, 228))
    surface.blit(moneyText, (28, 44))

    statsText = game.infoFont.render(
        "Workers {0}   Vans {1}   Capacity {2}".format(game.workers, game.vans, game.vanCapacity),
        True,
        (214, 214, 214),
    )
    surface.blit(statsText, (28, 58))

    surface.blit(game.infoFont.render("Current stats and next purchase costs", True, (194, 194, 194)), (28, 72))

    upgrades = [
        ("+1 Extra Worker", economy.getWorkerCost(game)),
        ("+2 Van Capacity", economy.getCapacityCost(game)),
        ("+1 Extra Van", economy.getVanCost(game)),
    ]

    for index, (name, cost) in enumerate(upgrades):
        text = game.myFont.render(f"{index + 1}. {name} - ${cost}", True, (255, 255, 255))
        surface.blit(text, (34, 98 + index * 22))

    prompt = game.myFont.render("Press 1-3 to buy, backspace to exit", True, (200, 200, 200))
    surface.blit(prompt, (32, 170))
