import pygame

from assets.warehouseSprites import loadForkliftSprite
from characters.props import Prop
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
        dockPauseDuration=15.0,
        startDelay=0.0,
        speed=88.0,
        trailerFollowDistance=-28.0,
        hitchOffset=40.0,
    )
    game.semiTruckRigs.append(semiRig)
    game.semiTruckWaves.append(SemiTruckWave([semiRig], restartDelay=5.0))

    forkliftImage = loadForkliftSprite(game.spriteManager, (48, 42))
    forkliftProp = Prop(
        (zone.position[0] + zone.size[0] - 172, zone.position[1] + 61),
        forkliftImage,
        collisionSize=(32, 21),
        collisionOffset=(6, 14),
    )
    forkliftProp.interactionRect = pygame.Rect(
        int(forkliftProp.position[0]) - 8,
        int(forkliftProp.position[1]) - 6,
        64,
        56,
    )
    game.worldProps.append(forkliftProp)
    game.walls.append(forkliftProp)
    game.loadingDockForklifts.append(forkliftProp)

    coneImage = pygame.transform.smoothscale(
        game.spriteManager.getSprite("kenney_car-kit_3.0/Previews/cone.png"),
        (16, 20),
    )
    for coneX in [zone.position[0] + zone.size[0] - 112, zone.position[0] + zone.size[0] - 72, zone.position[0] + zone.size[0] - 32]:
        game.worldProps.append(
            Prop(
                (coneX, zone.position[1] + 68),
                coneImage.copy(),
            )
        )
