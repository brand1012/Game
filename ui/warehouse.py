import pygame

from characters.drawable import Drawable
from ui.hud import drawUI


def drawVehicleLaneDetails(game, surface):
    stripeColor = (245, 229, 110)
    phase = None

    for lane in [game.getZone("Vehicle Lane", 0), game.getZone("Vehicle Lane", 1)]:
        laneScreenX = int(lane.position[0] - Drawable.CAMERA_OFFSET[0])
        laneScreenY = int(lane.position[1] - Drawable.CAMERA_OFFSET[1])
        stripeX = laneScreenX + (lane.size[0] // 2) - 3

        for yOffset in range(10, lane.size[1] - 10, 55):
            stripeRect = pygame.Rect(stripeX, laneScreenY + yOffset, 6, 28)
            pygame.draw.rect(surface, stripeColor, stripeRect)

def drawWarehouse(game, surface):
    surface.fill((230, 230, 230))
    surface.blit(game.floor, -Drawable.CAMERA_OFFSET)

    for zone in game.zones:
        zone.draw(surface)

    drawVehicleLaneDetails(game, surface)

    for worldProp in game.worldProps:
        worldProp.draw(surface)

    for movingVehicle in game.laneVehicles:
        movingVehicle.draw(surface)

    for semiTruckRigObject in game.semiTruckRigs:
        semiTruckRigObject.draw(surface)

    game.player.draw(surface)

    drawUI(game, surface)
