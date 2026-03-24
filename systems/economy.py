def getIncomePerSecond(game):
    baseWorkerIncome = game.workers * 0.5
    vanIncome = game.vans * game.vanCapacity * 0.5
    return (baseWorkerIncome + vanIncome) * game.contractMultiplier


def getPackagesDeliveredPerSecond(game):
    baseWorker = game.workers * 1
    van = game.vans * game.vanCapacity * 1
    return (baseWorker + van) * game.contractMultiplier


def updateStockHistory(game, seconds):
    game.stockTimer += seconds

    if game.stockTimer >= 2:
        game.stockTimer = 0
        growth = getIncomePerSecond(game) * 0.01
        game.stockValue += growth
        game.stockHistory.append(game.stockValue)

        if len(game.stockHistory) > 200:
            game.stockHistory.pop(0)


def getWorkerCost(game):
    return int(game.baseWorkerCost * (game.costGrowth ** game.workers))


def getVanCost(game):
    return int(game.baseVanCost * (game.costGrowth ** game.vans))


def getCapacityCost(game):
    upgradesOwned = game.vanCapacity // 2
    return int(game.baseCapacityCost * (game.costGrowth ** upgradesOwned))


def purchaseUpgrade(game, name):
    if name == "+1 Extra Worker":
        cost = getWorkerCost(game)
        if game.money >= cost:
            game.money -= cost
            game.workers += 1

    elif name == "+2 Van Capacity":
        cost = getCapacityCost(game)
        if game.money >= cost:
            game.money -= cost
            game.vanCapacity += 2

    elif name == "+1 Extra Van":
        cost = getVanCost(game)
        if game.money >= cost:
            game.money -= cost
            game.vans += 1
