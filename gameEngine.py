import pygame

import assets.spriteManager as spriteManager
import minigames.semiUnloading as semiUnloading
import minigames.sorting as sorting
import systems.economy as economy
import systems.highScores as highScores
import ui.infoScreen as infoScreen
import ui.resultsScreen as resultsScreen
import ui.stockScreen as stockScreen
import ui.upgradeScreen as upgradeScreen
import ui.warehouse as warehouse
import world.floor as floor
import world.layout as layout
import world.zoneBuilders.loadingDock as loadingDock
import world.zoneBuilders.offices as offices
import world.zoneBuilders.sortingArea as sortingArea
import world.zoneBuilders.storage as storage
import world.zoneBuilders.vanPrep as vanPrep
import world.zoneBuilders.vehicleLanes as vehicleLanes

from characters.drawable import Drawable
from characters.player import Player
from characters.props import AnimatedProp, LoopingProp, Prop
from characters.vehicles import LaneVehicle
from utils.vector import vec


class GameEngine(object):
    def __init__(self):
        pygame.init()

        self.RESOLUTION = (400, 200)
        self.WORLD_SIZE = (1000, 700)
        self.SCALE = 3
        self.UPSCALED = [int(x * self.SCALE) for x in self.RESOLUTION]

        self.screen = pygame.display.set_mode(list(self.UPSCALED))
        self.drawSurface = pygame.Surface(list(self.RESOLUTION))

        self.myFont = pygame.font.SysFont("Arial", 16)
        self.infoFont = pygame.font.SysFont("Arial", 12)
        self.uiFont = pygame.font.SysFont("Arial", 10, bold=True)

        self.spriteManager = spriteManager.SpriteManager()
        self.player = Player(vec(500, 600), self.spriteManager, self.WORLD_SIZE)
        self.floor = floor.buildFloor(self)

        self.baseWorkerCost = 10
        self.baseCapacityCost = 50
        self.baseVanCost = 200
        self.costGrowth = 1.5

        self.state = "warehouse"
        self.currentMinigame = None
        self.currentMinigameType = None
        self.resultsData = None
        self.highScores = highScores.loadHighScores("highscores.json")

        self.workers = 1
        self.vans = 1
        self.vanCapacity = 1
        self.contractMultiplier = 1

        self.stockValue = 100
        self.stockHistory = [self.stockValue]
        self.stockTimer = 0
        self.trafficWaveVehicleCount = 4

        self.zones = layout.createZones()

        self.worldProps = []
        self.laneVehicles = []
        self.vehicleWaves = []
        self.semiTruckRigs = []
        self.semiTruckWaves = []
        self.walls = []
        self.sortingPallets = []
        self.loadingDockForklifts = []
        self.upgradeDesks = []
        self.buildWorldProps()

        self.money = 0
        self.packagesShipped = 0
        self.showInteractPrompt = False
        self.currentInteraction = None

        self.gameClock = pygame.time.Clock()

    def draw(self, surface):
        if self.state == "warehouse":
            warehouse.drawWarehouse(self, surface)
        elif self.state == "minigame":
            self.currentMinigame.draw(surface)
        elif self.state == "results":
            resultsScreen.drawResults(self, surface)
        elif self.state == "upgrade":
            upgradeScreen.drawUpgradeScreen(self, surface)
        elif self.state == "info":
            infoScreen.drawInfoScreen(self, surface)
        elif self.state == "stock":
            stockScreen.drawStockGraph(self, surface)

        pygame.transform.scale(surface, self.UPSCALED, self.screen)
        pygame.display.flip()

    def updateWarehouse(self, seconds):
        self.money += economy.getIncomePerSecond(self) * seconds
        self.packagesShipped += economy.getPackagesDeliveredPerSecond(self) * seconds
        economy.updateStockHistory(self, seconds)

        activeVehicleWalls = [vehicle for vehicle in self.laneVehicles if vehicle.active and vehicle.rect]
        activeSemiWalls = [
            rig for rig in self.semiTruckRigs
            if rig.active and getattr(rig, "rect", None)
        ]
        collisionWalls = self.walls + activeVehicleWalls + activeSemiWalls

        self.player.update(seconds, collisionWalls)
        for worldProp in self.worldProps:
            worldProp.update(seconds)
        for vehicleWave in self.vehicleWaves:
            vehicleWave.update(seconds)
        for semiTruckWave in self.semiTruckWaves:
            semiTruckWave.update(seconds)

        self.updateInteractionPrompt()
        self.centerCameraOnPlayer()
        self.clampCamera()

    def update(self, seconds):
        if self.state == "warehouse":
            self.updateWarehouse(seconds)
        elif self.state == "minigame":
            self.currentMinigame.update(seconds)

    def clampCamera(self):
        maxX = self.WORLD_SIZE[0] - self.RESOLUTION[0]
        maxY = self.WORLD_SIZE[1] - self.RESOLUTION[1]

        Drawable.CAMERA_OFFSET[0] = max(0, min(Drawable.CAMERA_OFFSET[0], maxX))
        Drawable.CAMERA_OFFSET[1] = max(0, min(Drawable.CAMERA_OFFSET[1], maxY))

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "warehouse" and event.key == pygame.K_e and self.currentInteraction:
                if self.currentInteraction == "sorting":
                    self.startMinigame("sorting")
                elif self.currentInteraction == "semiUnloading":
                    self.startMinigame("semiUnloading")
                elif self.currentInteraction == "upgrade":
                    self.state = "upgrade"

            if self.state == "results" and event.key == pygame.K_SPACE:
                self.state = "warehouse"
                self.currentMinigame = None
                self.resultsData = None

            if self.state == "upgrade":
                if event.key == pygame.K_BACKSPACE:
                    self.state = "warehouse"
                elif event.key == pygame.K_1:
                    self.purchaseUpgrade("+1 Extra Worker")
                elif event.key == pygame.K_2:
                    self.purchaseUpgrade("+2 Van Capacity")
                elif event.key == pygame.K_3:
                    self.purchaseUpgrade("+1 Extra Van")

            if event.key == pygame.K_i:
                if self.state == "info":
                    self.state = "warehouse"
                elif self.state == "warehouse":
                    self.state = "info"

            if event.key == pygame.K_s:
                if self.state == "stock":
                    self.state = "warehouse"
                elif self.state == "warehouse":
                    self.state = "stock"

        if self.state == "warehouse" and event.type == pygame.KEYUP:
            if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                self.player.velocity[0] = 0
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                self.player.velocity[1] = 0

        if event.type == pygame.MOUSEBUTTONUP:
            self.player.velocity[0] = 0
            self.player.velocity[1] = 0

        if self.state == "minigame":
            self.currentMinigame.handleEvent(event)
            return

        self.centerCameraOnPlayer()

    def centerCameraOnPlayer(self):
        Drawable.CAMERA_OFFSET = (
            self.player.position +
            vec(*self.player.image.get_size()) / 2 -
            vec(*self.RESOLUTION) / 2
        )

    def getZone(self, name, index=0):
        matches = [zone for zone in self.zones if zone.name == name]
        return matches[index]

    def addWorldProp(self, position, fileName, size, collisionSize=None, collisionOffset=(0, 0)):
        image = pygame.transform.smoothscale(self.spriteManager.getSprite(fileName), size)
        worldProp = Prop(position, image, collisionSize, collisionOffset)
        self.worldProps.append(worldProp)

        if worldProp.rect:
            self.walls.append(worldProp)

        return worldProp

    def addAnimatedWorldPropRects(
        self,
        position,
        fileName,
        rects,
        size,
        framesPerSecond=6,
        collisionSize=None,
        collisionOffset=(0, 0)
    ):
        frames = [
            pygame.transform.smoothscale(self.spriteManager.getSprite(fileName, rect), size)
            for rect in rects
        ]
        worldProp = AnimatedProp(
            position,
            frames,
            framesPerSecond=framesPerSecond,
            collisionSize=collisionSize,
            collisionOffset=collisionOffset
        )
        self.worldProps.append(worldProp)

        if worldProp.rect:
            self.walls.append(worldProp)

        return worldProp

    def addLoopingWorldProp(self, position, fileName, size, speed, loopStartX, loopEndX):
        image = pygame.transform.smoothscale(self.spriteManager.getSprite(fileName), size)
        worldProp = LoopingProp(position, image, speed, loopStartX, loopEndX)
        self.worldProps.append(worldProp)

        return worldProp

    def addLaneVehicle(
        self,
        position,
        fileName,
        size,
        velocity,
        resetY,
        stopY=None,
        pauseDuration=0,
        startDelay=0,
        collisionSize=None,
        collisionOffset=(0, 0)
    ):
        image = pygame.transform.smoothscale(self.spriteManager.getSprite(fileName), size)
        vehicle = LaneVehicle(
            position,
            image,
            velocity,
            resetY,
            stopY=stopY,
            pauseDuration=pauseDuration,
            startDelay=startDelay,
            collisionSize=collisionSize,
            collisionOffset=collisionOffset
        )
        self.laneVehicles.append(vehicle)
        return vehicle

    def buildWorldProps(self):
        self.worldProps = []
        self.laneVehicles = []
        self.vehicleWaves = []
        self.semiTruckRigs = []
        self.semiTruckWaves = []
        self.walls = []
        self.sortingPallets = []
        self.loadingDockForklifts = []
        self.upgradeDesks = []

        loadingDock.buildLoadingDock(self, self.getZone("Semi Unloading Dock"))
        sortingArea.buildSortingZone(self, self.getZone("Sorting Area"))
        storage.buildStorageZone(self, self.getZone("Storage"))
        vanPrep.buildVanPrep(self, self.getZone("Van Prep", 0), self.getZone("Van Prep", 1))
        offices.buildOfficeZone(self, self.getZone("Offices"))
        vehicleLanes.buildVehicleTraffic(self, self.getZone("Vehicle Lane", 0), self.getZone("Vehicle Lane", 1))

    def updateInteractionPrompt(self):
        self.showInteractPrompt = False
        self.currentInteraction = None
        interactionRect = self.player.interactionRect

        if self.isSemiReadyForUnload():
            for forklift in self.loadingDockForklifts:
                targetRect = getattr(forklift, "interactionRect", forklift.rect)
                if targetRect and interactionRect.colliderect(targetRect):
                    self.showInteractPrompt = True
                    self.currentInteraction = "semiUnloading"
                    return

        sortingZone = self.getZone("Sorting Area")
        if sortingZone.rect.colliderect(interactionRect):
            for pallet in self.sortingPallets:
                if pallet.rect and interactionRect.colliderect(pallet.rect):
                    self.showInteractPrompt = True
                    self.currentInteraction = "sorting"
                    return

        for desk in self.upgradeDesks:
            if desk.rect and interactionRect.colliderect(desk.rect):
                self.showInteractPrompt = True
                self.currentInteraction = "upgrade"
                return

    def startMinigame(self, gameType):
        self.currentMinigameType = gameType

        if gameType == "sorting":
            self.currentMinigame = sorting.SortingMinigame(self)
            self.state = "minigame"
        elif gameType == "semiUnloading":
            self.currentMinigame = semiUnloading.SemiUnloadingMinigame(self)
            self.state = "minigame"

    def purchaseUpgrade(self, name):
        economy.purchaseUpgrade(self, name)

    def isSemiReadyForUnload(self):
        for rig in self.semiTruckRigs:
            if rig.active and rig.startDelay <= 0 and getattr(rig, "pauseTimer", 0) > 0:
                return True
        return False


gameEngine = GameEngine
