from characters.vehicles import SemiTruckRig
from systems.traffic import SemiTruckWave


def buildLoadingDock(game, zone):
    spriteSheet = "2D_TOPDOWN_PIXELART_CARS.png"
    cabRect = (129, 0, 40, 96)
    trailerRect = (172, 0, 36, 96)
    cabImage = game.spriteManager.getSprite(spriteSheet, cabRect)
    trailerImage = game.spriteManager.getSprite(spriteSheet, trailerRect)

    pathPoints = [
        (525, -132),
        (525, 16),
        (525, 60),
        (500, 62),
        (470, 63),
        (430, 63),
        (330, 63),
        (275, 58),
        (255, 36),
        (255, -162),
    ]

    semiRig = SemiTruckRig(
        cabImage=cabImage,
        trailerImage=trailerImage,
        cabSize=(64, 115),
        trailerSize=(54, 240),
        pathPoints=pathPoints,
        dockPauseDuration=10.0,
        startDelay=0.0,
        speed=88.0,
        trailerFollowDistance=-28.0,
        hitchOffset=40.0,
    )
    game.semiTruckRigs.append(semiRig)
    game.semiTruckWaves.append(SemiTruckWave([semiRig], restartDelay=5.0))
