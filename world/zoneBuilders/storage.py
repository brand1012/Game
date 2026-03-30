import pygame


class InteractionZone(object):
    def __init__(self, interactionRect):
        self.interactionRect = interactionRect
        self.rect = None


def buildStorageZone(game, zone):
    conveyorFrameRects = [(0, 0, 49, 15), (49, 0, 49, 15), (98, 0, 49, 15)]
    conveyorSize = (120, 30)
    boxSize = (22, 22)
    boxTravelSpeed = 26
    beltsPerPair = 2
    beltGap = -8
    pairWidth = beltsPerPair * conveyorSize[0] + (beltsPerPair - 1) * beltGap
    startX = zone.position[0] + (zone.size[0] - pairWidth) / 2
    pairYPositions = [zone.position[1] + 36, zone.position[1] + 132]

    for pairY in pairYPositions:
        for beltIndex in range(beltsPerPair):
            beltX = startX + beltIndex * (conveyorSize[0] + beltGap)
            game.addAnimatedWorldPropRects(
                position=(beltX, pairY),
                fileName="Conveyor Belts sprite sheet.png",
                rects=conveyorFrameRects,
                size=conveyorSize,
                collisionSize=conveyorSize,
            )

        boxY = pairY - 1
        loopStartX = startX - boxSize[0]
        loopEndX = startX + pairWidth
        for boxOffset in [20, 120]:
            game.addLoopingWorldProp(
                position=(startX + boxOffset, boxY),
                fileName="kenney_car-kit_3.0/Previews/box.png",
                size=boxSize,
                speed=boxTravelSpeed,
                loopStartX=loopStartX,
                loopEndX=loopEndX,
            )

    controlRect = pygame.Rect(
        int(startX) - 10,
        int(pairYPositions[0]) - 10,
        int(pairWidth) + 20,
        int(pairYPositions[-1] - pairYPositions[0] + conveyorSize[1]) + 20,
    )
    game.storageControls.append(InteractionZone(controlRect))
