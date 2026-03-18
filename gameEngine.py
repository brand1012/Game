import pygame
from vector import vec, pyVec
from drawable import drawable, mobile, wall, kirby, prop, laneVehicle, animatedProp, loopingProp, semiTruckRig
from spriteManager import SpriteManager
from zone import Zone
from sortingMinigame import SortingMinigame
import json


class VehicleWave:
    def __init__(self, vehicles, restartDelay=5.0):
        self.vehicles = vehicles
        self.restartDelay = restartDelay
        self.cooldownTimer = restartDelay
        self.waitingForRestart = False

    def update(self, seconds):
        anyActive = False
        allExited = True

        for vehicle in self.vehicles:
            vehicle.update(seconds)
            if vehicle.active:
                anyActive = True
            if not vehicle.hasExitedScreen:
                allExited = False

        if anyActive or not allExited:
            self.waitingForRestart = False
            self.cooldownTimer = self.restartDelay
            return

        if not self.waitingForRestart:
            self.waitingForRestart = True
            self.cooldownTimer = self.restartDelay

        self.cooldownTimer = max(0, self.cooldownTimer - seconds)
        if self.cooldownTimer == 0:
            for vehicle in self.vehicles:
                vehicle.restartWave()
            self.waitingForRestart = False
            self.cooldownTimer = self.restartDelay


class SemiTruckWave:
    def __init__(self, rigs, restartDelay=5.0):
        self.rigs = rigs
        self.restartDelay = restartDelay
        self.cooldownTimer = restartDelay
        self.waitingForRestart = False

    def update(self, seconds):
        anyActive = False
        allFinished = True

        for rig in self.rigs:
            rig.update(seconds)
            if rig.active:
                anyActive = True
            if not rig.finished:
                allFinished = False

        if anyActive or not allFinished:
            self.waitingForRestart = False
            self.cooldownTimer = self.restartDelay
            return

        if not self.waitingForRestart:
            self.waitingForRestart = True
            self.cooldownTimer = self.restartDelay

        self.cooldownTimer = max(0, self.cooldownTimer - seconds)
        if self.cooldownTimer == 0:
            for rig in self.rigs:
                rig.restart()
            self.waitingForRestart = False
            self.cooldownTimer = self.restartDelay

class gameEngine(object):
    def __init__(self):
        pygame.init()
        
        self.RESOLUTION = (400, 200)
        self.WORLD_SIZE = (1000, 700)
        self.SCALE = 3
        self.UPSCALED = [int(x * self.SCALE) for x in self.RESOLUTION]

        self.screen = pygame.display.set_mode(list(self.UPSCALED))
        self.drawSurface = pygame.Surface(list(self.RESOLUTION))

        self.myFont = pygame.font.SysFont("Arial", 16)
        self.infoFont = pygame.font.SysFont("Arial", 12)  # smaller font for info screen

        self.spriteManager = SpriteManager()

        self.kirby = kirby(vec(500, 600), self.spriteManager, self.WORLD_SIZE)
        self.floor = self.buildFloor()

        self.dragging = False
        self.dragOffset = vec(0, 0)

        brick = self.spriteManager.getSprite("brick.png")

        self.baseWorkerCost = 10
        self.baseCapacityCost = 50
        self.baseVanCost = 200
        self.costGrowth = 1.5

        self.state = "warehouse"
        self.currentMinigame = None
        self.highScores = self.loadHighScores()

        self.workers = 1
        self.vans = 1
        self.vanCapacity = 1
        self.contractMultiplier = 1

        self.stockValue = 100
        self.stockHistory = [self.stockValue]
        self.stockTimer = 0
        self.trafficWaveVehicleCount = 4

        self.zones = [

            # Semi unloading dock (top)
            Zone(
                position=(200, 25),
                size=(600, 100),
                name="Semi Unloading Dock",
                color=(180, 220, 255)
            ),

            # Sorting area (almost top)
            Zone(
                position=(200, 150),
                size=(600, 150),
                name="Sorting Area",
                color=(180, 255, 180)
            ),

            # Storage (center)
            Zone(
                position=(350, 325),
                size=(300, 200),
                name="Storage",
                color=(255, 220, 180)
            ),

            # Van prep (left)
            Zone(
                position=(200, 325),
                size=(125, 200),
                name="Van Prep",
                color=(255, 180, 255)
            ),

            # Van prep (right)
            Zone(
                position=(675, 325),
                size=(125, 200),
                name="Van Prep",
                color=(255, 180, 255)
            ),

            # Offices (bottom)
            Zone(
                position=(200, 550),
                size=(600, 100),
                name="Offices",
                color=(220, 220, 220)
            ),

            # Vehicle lane (left)
            Zone(
                position=(50, 25),
                size=(100, 625),
                name="Vehicle Lane",
                color=(32, 32, 36),
                showLabel=False
            ),

            # Vehicle lane (right)
            Zone(
                position=(850, 25),
                size=(100, 625),
                name="Vehicle Lane",
                color=(32, 32, 36),
                showLabel=False
            )

        ]

        self.worldProps = []
        self.laneVehicles = []
        self.vehicleWaves = []
        self.semiTruckRigs = []
        self.semiTruckWaves = []
        self.walls = []
        self.buildWorldProps()

        # ----- UI / Tycoon Stats -----
        self.money = 0
        self.packagesShipped = 0
        self.showInteractPrompt = False
        self.currentInteraction = None

        self.uiFont = pygame.font.SysFont("Arial", 10, bold=True)

        self.gameClock = pygame.time.Clock()
    
    def getIncomePerSecond(self):
        baseWorkerIncome = self.workers * 0.5
        vanIncome = self.vans * self.vanCapacity * 0.5
        return (baseWorkerIncome + vanIncome) * self.contractMultiplier
    
    def getPackagesDeliveredPerSecond(self):
        baseWorker = self.workers * 1
        van = self.vans * self.vanCapacity * 1
        return (baseWorker + van) * self.contractMultiplier

    def drawWarehouse(self, surface):
        surface.fill((230,230,230))
        surface.blit(self.floor, -drawable.CAMERA_OFFSET)

        for zone in self.zones:
            zone.draw(surface)

        self.drawVehicleLaneDetails(surface)
        
        for worldProp in self.worldProps:
            worldProp.draw(surface)

        for movingVehicle in self.laneVehicles:
            movingVehicle.draw(surface)

        for semiTruckRigObject in self.semiTruckRigs:
            semiTruckRigObject.draw(surface)

        self.kirby.draw(surface)

        self.drawUI(surface)

    def drawVehicleLaneDetails(self, surface):
        stripeColor = (245, 229, 110)

        for lane in [self.getZone("Vehicle Lane", 0), self.getZone("Vehicle Lane", 1)]:
            laneScreenX = int(lane.position[0] - drawable.CAMERA_OFFSET[0])
            laneScreenY = int(lane.position[1] - drawable.CAMERA_OFFSET[1])
            stripeX = laneScreenX + (lane.size[0] // 2) - 3

            for yOffset in range(10, lane.size[1] - 10, 55):
                stripeRect = pygame.Rect(stripeX, laneScreenY + yOffset, 6, 28)
                pygame.draw.rect(surface, stripeColor, stripeRect)
    
    def drawResults(self, surface):
        surface.fill((30,30,30))

        title = self.myFont.render("SHIFT COMPLETE", True, (255,255,255))
        surface.blit(title, (140, 30))

        scoreText = self.myFont.render(
            f"Score: {self.resultsData['score']}", True, (255,255,255))
        surface.blit(scoreText, (140, 70))

        moneyText = self.myFont.render(
            f"Money earned: ${self.resultsData['money']}", True, (255,255,255))
        surface.blit(moneyText, (140, 100))

        highText = self.myFont.render(
            f"High Score: {self.resultsData['highScore']}",
            True,
            (255,255,255)
        )
        surface.blit(highText, (140, 130))


        continueText = self.myFont.render(
            "Press SPACE to continue", True, (200,200,200))
        surface.blit(continueText, (120, 170))

    def drawInfoScreen(self, surface):
        surface.fill((40, 40, 60))

        title = self.infoFont.render("FACTORY INFO", True, (255, 255, 255))
        surface.blit(title, (120, 20))

        stats = [
            f"Workers: {self.workers}",
            f"Vans: {self.vans}",
            f"Van capacity: {self.vanCapacity} packages",
            f"Money: ${int(self.money)}",
            f"Packages shipped: {int(self.packagesShipped)}",
            f"Income per second: ${self.getIncomePerSecond()}/sec",
            f"Contract multiplier: x{self.contractMultiplier}"
        ]

        for i, stat in enumerate(stats):
            text = self.infoFont.render(stat, True, (255, 255, 255))
            surface.blit(text, (50, 40 + i*15))

        prompt = self.myFont.render("Press I to close", True, (200, 200, 200))
        surface.blit(prompt, (50, 200))


    def draw(self, surface):

        if self.state == "warehouse":
            self.drawWarehouse(surface)

        elif self.state == "minigame":
            self.currentMinigame.draw(surface)

        elif self.state == "results":
            self.drawResults(surface)

        elif self.state == "upgrade":
            self.drawUpgradeScreen(surface)

        elif self.state == "info":
            self.drawInfoScreen(surface)

        elif self.state == "stock":
            self.drawStockGraph(surface)

        pygame.transform.scale(surface, self.UPSCALED, self.screen)
        pygame.display.flip()

    def updateWarehouse(self, seconds):
        income = self.getIncomePerSecond() * seconds
        self.money += income

        packages = self.getPackagesDeliveredPerSecond() * seconds
        self.packagesShipped += packages

        self.stockTimer += seconds

        if self.stockTimer >= 2: # update every 2 seconds
            self.stockTimer = 0
            
            growth = self.getIncomePerSecond() * 0.01
            
            self.stockValue += growth
            
            self.stockHistory.append(self.stockValue)
            
            if len(self.stockHistory) > 200:
                self.stockHistory.pop(0)


        activeVehicleWalls = [vehicle for vehicle in self.laneVehicles if vehicle.active and vehicle.rect]
        activeSemiWalls = [
            rig for rig in self.semiTruckRigs
            if rig.active and getattr(rig, "rect", None)
        ]
        collisionWalls = self.walls + activeVehicleWalls + activeSemiWalls

        self.kirby.update(seconds, collisionWalls)
        for worldProp in self.worldProps:
            worldProp.update(seconds)
        for vehicleWave in self.vehicleWaves:
            vehicleWave.update(seconds)
        for semiTruckWave in self.semiTruckWaves:
            semiTruckWave.update(seconds)

        self.updateInteractionPrompt()

        drawable.CAMERA_OFFSET = (
            self.kirby.position +
            vec(*self.kirby.image.get_size()) / 2 -
            vec(*self.RESOLUTION) / 2
        )

        self.clampCamera()

    def update(self, seconds):

        if self.state == "warehouse":
            self.updateWarehouse(seconds)

        elif self.state == "minigame":
            self.currentMinigame.update(seconds)


    def clampCamera(self):
        maxX = self.WORLD_SIZE[0] - self.RESOLUTION[0]
        maxY = self.WORLD_SIZE[1] - self.RESOLUTION[1]

        drawable.CAMERA_OFFSET[0] = max(0, min(drawable.CAMERA_OFFSET[0], maxX))
        drawable.CAMERA_OFFSET[1] = max(0, min(drawable.CAMERA_OFFSET[1], maxY))

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "warehouse" and event.key == pygame.K_e and self.currentInteraction:
                if self.currentInteraction == "sorting":
                    self.startMinigame("sorting")
                elif self.currentInteraction == "upgrade":
                    self.state = "upgrade"
            
            # exit results screen
            if self.state == "results" and event.key == pygame.K_SPACE:
                self.state = "warehouse"
                self.currentMinigame = None
                self.resultsData = None

            # upgrade screen input
            if self.state == "upgrade":
                if event.key == pygame.K_BACKSPACE:
                    self.state = "warehouse"
                elif event.key == pygame.K_1:
                    self.purchaseUpgrade("+1 Extra Worker")
                elif event.key == pygame.K_2:
                    self.purchaseUpgrade("+2 Van Capacity")
                elif event.key == pygame.K_3:
                    self.purchaseUpgrade("+1 Extra Van")

            #toggle info screen
            if event.key == pygame.K_i:
                if self.state == "info":
                    self.state = "warehouse"
                elif self.state == "warehouse":
                    self.state = "info"

            #toggle stock screen
            if event.key == pygame.K_s:
                if self.state == "stock":
                    self.state = "warehouse"
                elif self.state == "warehouse":
                    self.state = "stock"

        # release keys
        if self.state == "warehouse" and event.type == pygame.KEYUP:
            if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                self.kirby.velocity[0] = 0
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                self.kirby.velocity[1] = 0
        
        # mouse handling
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = vec(*event.pos) / self.SCALE
            kirbyRect = self.kirby.image.get_rect(topleft=self.kirby.position)

            if kirbyRect.collidepoint(mouse):
                self.dragging = True
                self.dragOffset = mouse - self.kirby.position
        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            self.kirby.velocity[0] = 0
            self.kirby.velocity[1] = 0
        if self.state == "minigame":
            self.currentMinigame.handleEvent(event)
            return

        drawable.CAMERA_OFFSET = self.kirby.position + vec(*self.kirby.image.get_size()) / 2 - vec(*self.RESOLUTION) / 2

    def drawUI(self, surface):

        # Background panel
        panelRect = pygame.Rect(5, 5, 90, 30)
        pygame.draw.rect(surface, (220,220,220), panelRect)
        pygame.draw.rect(surface, (0,0,0), panelRect, 2)

        # Money
        moneyText = self.uiFont.render(f"Money: ${int(self.money)}", True, (0,0,0))
        surface.blit(moneyText, (10, 8))

        # Packages shipped
        packageText = self.uiFont.render(f"Packages: {int(self.packagesShipped)}", True, (0,0,0))
        surface.blit(packageText, (10, 20))

        # Interaction prompt
        if self.showInteractPrompt:
            prompt = self.uiFont.render("Press E to interact", True, (0,0,0))

            x = (self.RESOLUTION[0] - prompt.get_width()) // 2
            y = self.RESOLUTION[1] - 30

            surface.blit(prompt, (x, y))

    def drawUpgradeScreen(self, surface):
        surface.fill((50, 50, 50))
        
        title = self.myFont.render("UPGRADE STATION", True, (255,255,255))
        surface.blit(title, (120, 20))
        
        upgrades = [
            ("+1 Extra Worker", self.getWorkerCost()),
            ("+2 Van Capacity", self.getCapacityCost()),
            ("+1 Extra Van", self.getVanCost())
        ]
        
        for i, (name, cost) in enumerate(upgrades):
            text = self.myFont.render(f"{i+1}. {name} - ${cost}", True, (255,255,255))
            surface.blit(text, (50, 60 + i*30))
        
        prompt = self.myFont.render("Press 1-3 to buy, backspace to exit", True, (200,200,200))
        surface.blit(prompt, (50, 160))

    
    def createPlaceholder(self, size, color):

        surf = pygame.Surface(size)
        surf.fill(color)

        pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)

        return surf
    
    def buildFloor(self):
        floor = pygame.Surface(self.WORLD_SIZE)
        floor.fill((225, 225, 225))

        # Warehouse shell
        pygame.draw.rect(floor, (196, 196, 196), pygame.Rect(25, 25, 950, 625))
        pygame.draw.rect(floor, (80, 80, 80), pygame.Rect(25, 25, 950, 625), 8)

        # Loading dock strip
        pygame.draw.rect(floor, (168, 182, 196), pygame.Rect(200, 25, 600, 100))
        for x in range(220, 780, 80):
            pygame.draw.line(floor, (230, 230, 235), (x, 25), (x, 125), 4)

        # Central work zones
        pygame.draw.rect(floor, (191, 214, 191), pygame.Rect(200, 150, 600, 150))
        pygame.draw.rect(floor, (214, 189, 161), pygame.Rect(350, 325, 300, 200))
        pygame.draw.rect(floor, (206, 188, 223), pygame.Rect(200, 325, 125, 200))
        pygame.draw.rect(floor, (206, 188, 223), pygame.Rect(675, 325, 125, 200))
        pygame.draw.rect(floor, (205, 205, 205), pygame.Rect(200, 550, 600, 100))

        # Vehicle lanes and parking markings
        laneColor = (20, 20, 24)
        pygame.draw.rect(floor, laneColor, pygame.Rect(50, 25, 100, 625))
        pygame.draw.rect(floor, laneColor, pygame.Rect(850, 25, 100, 625))
        for y in range(35, 625, 55):
            pygame.draw.rect(floor, (245, 229, 110), pygame.Rect(97, y, 6, 28))
            pygame.draw.rect(floor, (245, 229, 110), pygame.Rect(897, y, 6, 28))

        # Interior lane dividers
        pygame.draw.line(floor, (120, 120, 120), (325, 325), (325, 525), 4)
        pygame.draw.line(floor, (120, 120, 120), (675, 325), (675, 525), 4)

        return floor

    def getScaledSprite(self, fileName, size):
        sprite = self.spriteManager.getSprite(fileName)
        return pygame.transform.smoothscale(sprite, size)

    def getScaledSpriteRect(self, fileName, rect, size):
        sprite = self.spriteManager.getSprite(fileName, rect)
        return pygame.transform.smoothscale(sprite, size)

    def getScaledRotatedSpriteRect(self, fileName, rect, size, angle):
        sprite = self.spriteManager.getSprite(fileName, rect)
        rotatedSprite = pygame.transform.rotate(sprite, angle)
        return pygame.transform.smoothscale(rotatedSprite, size)

    def getScaledStackedSpriteRects(self, fileName, rects, size):
        sourceWidth = rects[0][2]
        sourceHeight = sum(rect[3] for rect in rects)
        stackedSprite = pygame.Surface((sourceWidth, sourceHeight), pygame.SRCALPHA)
        sourceSheet = self.spriteManager.getSprite(fileName)

        destY = 0
        for rect in rects:
            stackedSprite.blit(sourceSheet, (0, destY), rect)
            destY += rect[3]

        return pygame.transform.smoothscale(stackedSprite, size)
    
    def getZone(self, name, index=0):
        matches = [zone for zone in self.zones if zone.name == name]
        return matches[index]

    def addWorldProp(self, position, fileName, size, collisionSize=None, collisionOffset=(0, 0)):
        image = self.getScaledSprite(fileName, size)
        worldProp = prop(position, image, collisionSize, collisionOffset)
        self.worldProps.append(worldProp)

        if worldProp.rect:
            self.walls.append(worldProp)

        return worldProp

    def addWorldPropRect(self, position, fileName, rect, size, collisionSize=None, collisionOffset=(0, 0)):
        image = self.getScaledSpriteRect(fileName, rect, size)
        worldProp = prop(position, image, collisionSize, collisionOffset)
        self.worldProps.append(worldProp)

        if worldProp.rect:
            self.walls.append(worldProp)

        return worldProp

    def addWorldPropRotatedRect(self, position, fileName, rect, size, angle, collisionSize=None, collisionOffset=(0, 0)):
        image = self.getScaledRotatedSpriteRect(fileName, rect, size, angle)
        worldProp = prop(position, image, collisionSize, collisionOffset)
        self.worldProps.append(worldProp)

        if worldProp.rect:
            self.walls.append(worldProp)

        return worldProp

    def addWorldPropStackedRects(self, position, fileName, rects, size, collisionSize=None, collisionOffset=(0, 0)):
        image = self.getScaledStackedSpriteRects(fileName, rects, size)
        worldProp = prop(position, image, collisionSize, collisionOffset)
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
        frames = [self.getScaledSpriteRect(fileName, rect, size) for rect in rects]
        worldProp = animatedProp(
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
        image = self.getScaledSprite(fileName, size)
        worldProp = loopingProp(position, image, speed, loopStartX, loopEndX)
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
        image = self.getScaledSprite(fileName, size)
        vehicle = laneVehicle(
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
    
    def addPalletStack(self, palletPosition, palletSize, boxOffsets):
        self.addWorldProp(
            position=palletPosition,
            fileName="freight/Freight-1.png",
            size=palletSize,
            collisionSize=palletSize
        )
        for boxOffset, boxSize in boxOffsets:
            boxPosition = (palletPosition[0] + boxOffset[0], palletPosition[1] + boxOffset[1])
            self.addWorldProp(position=boxPosition, fileName="kenney_car-kit_3.0/Previews/box.png", size=boxSize)

    def buildLoadingDock(self, zone):
        spriteSheet = "2D_TOPDOWN_PIXELART_CARS.png"
        cabRect = (129, 0, 40, 96)
        trailerRect = (172, 0, 36, 96)
        cabImage = self.spriteManager.getSprite(spriteSheet, cabRect)
        trailerImage = self.spriteManager.getSprite(spriteSheet, trailerRect)

        dockCenterY = zone.position[1] + zone.size[1] / 2 + 1
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

        semiRig = semiTruckRig(
            cabImage=cabImage,
            trailerImage=trailerImage,
            cabSize=(64, 115),
            trailerSize=(54, 240),
            pathPoints=pathPoints,
            dockPauseDuration=10.0,
            startDelay=0.0,
            speed=88.0,
            trailerFollowDistance=-28.0,
            hitchOffset=40.0
        )
        self.semiTruckRigs.append(semiRig)
        self.semiTruckWaves.append(SemiTruckWave([semiRig], restartDelay=5.0))

    def buildSortingZone(self, zone):
        palletSize = (22, 26)
        files = [
            "freight/Freight-5.png",
            "freight/Freight-6.png",
            "freight/Freight-7.png",
            "freight/Freight-8.png",
            "freight/Freight-9.png",
            "freight/Freight-10.png",
        ]

        sidePadding = 8
        columnGap = 0
        rowGap = 0
        topMargin = 8
        bottomMargin = 8
        middleWalkwayHeight = 32
        columns = max(1, int((zone.size[0] - sidePadding * 2 + columnGap) / (palletSize[0] + columnGap)))
        totalWidth = columns * palletSize[0] + (columns - 1) * columnGap
        startX = zone.position[0] + (zone.size[0] - totalWidth) / 2
        walkwayColumns = 2
        aisleStart = max(1, (columns // 2) - (walkwayColumns // 2))
        aisleColumns = set(range(aisleStart, aisleStart + walkwayColumns))

        topPairStart = zone.position[1] + topMargin
        bottomPairStart = (
            zone.position[1] + zone.size[1] - bottomMargin - (palletSize[1] * 2) - rowGap
        )

        yPositions = [
            topPairStart,
            topPairStart + palletSize[1] + rowGap,
            bottomPairStart,
            bottomPairStart + palletSize[1] + rowGap,
        ]

        fileIndex = 0
        for y in yPositions:
            for col in range(columns):
                if col in aisleColumns:
                    continue
                x = startX + col * (palletSize[0] + columnGap)
                fileName = files[fileIndex % len(files)]
                fileIndex += 1
                self.addWorldProp(
                    position=(x, y),
                    fileName=fileName,
                    size=palletSize,
                    collisionSize=palletSize
                )
                self.sortingPallets.append(self.worldProps[-1])

    def buildStorageZone(self, zone):
        conveyorFrameRects = [
            (0, 0, 49, 15),
            (49, 0, 49, 15),
            (98, 0, 49, 15),
        ]
        conveyorSize = (120, 30)
        boxSize = (22, 22)
        boxTravelSpeed = 26
        beltsPerPair = 2
        beltGap = -8
        pairWidth = beltsPerPair * conveyorSize[0] + (beltsPerPair - 1) * beltGap
        startX = zone.position[0] + (zone.size[0] - pairWidth) / 2
        pairYPositions = [
            zone.position[1] + 36,
            zone.position[1] + 132,
        ]

        for pairY in pairYPositions:
            for beltIndex in range(beltsPerPair):
                beltX = startX + beltIndex * (conveyorSize[0] + beltGap)
                self.addAnimatedWorldPropRects(
                    position=(beltX, pairY),
                    fileName="Conveyor Belts sprite sheet.png",
                    rects=conveyorFrameRects,
                    size=conveyorSize,
                    collisionSize=conveyorSize
                )

            boxY = pairY - 1
            loopStartX = startX - boxSize[0]
            loopEndX = startX + pairWidth
            boxOffsets = [20, 120]
            for boxOffset in boxOffsets:
                self.addLoopingWorldProp(
                    position=(startX + boxOffset, boxY),
                    fileName="kenney_car-kit_3.0/Previews/box.png",
                    size=boxSize,
                    speed=boxTravelSpeed,
                    loopStartX=loopStartX,
                    loopEndX=loopEndX
                )
    
    def buildVanPrep(self, leftZone, rightZone):
        return

    def buildOfficeZone(self, officeZone):
        officeX, officeY = officeZone.position
        brickTileSize = 20
        wallHeight = 40

        for x in range(0, officeZone.size[0], brickTileSize):
            for y in range(0, wallHeight, brickTileSize):
                self.addWorldProp(
                    position=(officeX + x, officeY + y),
                    fileName="brick.png",
                    size=(brickTileSize, brickTileSize),
                    collisionSize=(brickTileSize, brickTileSize)
                )

        def addOfficeProp(position, fileName, size, collisionSize=None, collisionOffset=(0, 0)):
            return self.addWorldProp(
                position=(officeX + position[0], officeY + position[1]),
                fileName=f"Office-Furniture-Pixel-Art/{fileName}",
                size=size,
                collisionSize=collisionSize,
                collisionOffset=collisionOffset
            )

        # A few wall details help the office read as a room without cluttering the floor.
        addOfficeProp((60, 8), "Wall-Clock.png", (18, 18))
        addOfficeProp((196, 8), "Wall-Note.png", (18, 18))
        addOfficeProp((336, 8), "Wall-Graph.png", (18, 18))
        addOfficeProp((496, 8), "Wall-Shelf.png", (18, 18))

        # Keep the office clean and readable with a single back wall row of fixtures.
        rowBottom = 54
        addOfficeProp((18, rowBottom - 42), "Wide-Filing-Cabinet.png", (42, 42), collisionSize=(34, 14), collisionOffset=(4, 26))
        self.upgradeDesks.append(addOfficeProp((88, rowBottom - 40), "Desk.png", (40, 40), collisionSize=(34, 14), collisionOffset=(3, 25)))
        self.upgradeDesks.append(addOfficeProp((208, rowBottom - 40), "Desk.png", (40, 40), collisionSize=(34, 14), collisionOffset=(3, 25)))
        self.upgradeDesks.append(addOfficeProp((328, rowBottom - 40), "Desk.png", (40, 40), collisionSize=(34, 14), collisionOffset=(3, 25)))
        addOfficeProp((392, rowBottom - 40), "Printer-Furniture.png", (40, 40), collisionSize=(34, 14), collisionOffset=(3, 25))
        addOfficeProp((468, rowBottom - 42), "Vending-Machine.png", (42, 42), collisionSize=(24, 16), collisionOffset=(9, 24))
        addOfficeProp((474, rowBottom - 24), "Water-Dispenser.png", (24, 24), collisionSize=(14, 10), collisionOffset=(5, 14))
        addOfficeProp((516, rowBottom - 42), "Wide-Filing-Cabinet.png", (42, 42), collisionSize=(34, 14), collisionOffset=(4, 26))
        self.upgradeDesks.append(addOfficeProp((560, rowBottom - 40), "Desk.png", (40, 40), collisionSize=(34, 14), collisionOffset=(3, 25)))
    
    def buildVehicleTraffic(self, leftLane, rightLane):
        def addLaneColumnTraffic(lane, specs):
            laneVehicles = []
            laneXOffset = -3 if lane.position[0] > self.WORLD_SIZE[0] / 2 else 0
            leftColumnX = lane.position[0] - 10 + laneXOffset
            rightColumnX = lane.position[0] + 46 + laneXOffset

            for spec in specs:
                columnX = leftColumnX if spec["column"] == "left" else rightColumnX
                vehicleX = columnX + spec.get("xOffset", 0)
                laneVehicles.append(self.addLaneVehicle(
                    position=(vehicleX, lane.position[1] + spec["spawnY"]),
                    fileName=spec["fileName"],
                    size=spec["size"],
                    velocity=(0, spec["speed"]),
                    resetY=(lane.position[1] + spec["spawnY"], lane.position[1] + lane.size[1] + 48),
                    stopY=lane.position[1] + spec["stopY"],
                    pauseDuration=spec["pauseDuration"],
                    startDelay=spec["startDelay"],
                    collisionSize=spec["collisionSize"],
                    collisionOffset=spec["collisionOffset"]
                ))

            self.vehicleWaves.append(VehicleWave(laneVehicles, restartDelay=5.0))

        trafficSpecTemplates = [
            {
                "column": "left",
                "fileName": "BOX TRUCK TOPDOWN/Blue/MOVE/SOUTH/SEPARATED/Blue_BOXTRUCK_CLEAN_SOUTH_000.png",
                "size": (80, 80),
                "xOffset": -6,
                "speed": 34,
                "spawnY": -90,
                "stopY": 438,
                "pauseDuration": 10.0,
                "startDelay": 0.0,
                "collisionSize": (34, 64),
                "collisionOffset": (23, 10)
            },
            {
                "column": "right",
                "fileName": "VAN TOP DOWN/Yellow/MOVE/SOUTH/SEPARATED/Yellow_VAN_CLEAN_SOUTH_000.png",
                "size": (68, 68),
                "speed": 32,
                "spawnY": -150,
                "stopY": 368,
                "pauseDuration": 10.0,
                "startDelay": 0.55,
                "collisionSize": (34, 52),
                "collisionOffset": (17, 10)
            },
            {
                "column": "left",
                "fileName": "VAN TOP DOWN/White/MOVE/SOUTH/SEPARATED/White_VAN_CLEAN_SOUTH_000.png",
                "size": (68, 68),
                "speed": 31,
                "spawnY": -220,
                "stopY": 298,
                "pauseDuration": 10.0,
                "startDelay": 1.15,
                "collisionSize": (34, 52),
                "collisionOffset": (17, 10)
            },
            {
                "column": "right",
                "fileName": "BOX TRUCK TOPDOWN/Red/MOVE/SOUTH/SEPARATED/Red_BOXTRUCK_CLEAN_SOUTH_000.png",
                "size": (80, 80),
                "xOffset": -6,
                "speed": 33,
                "spawnY": -300,
                "stopY": 228,
                "pauseDuration": 10.0,
                "startDelay": 1.8,
                "collisionSize": (34, 64),
                "collisionOffset": (23, 10)
            }
        ]

        trafficSpecs = trafficSpecTemplates[:max(1, min(self.trafficWaveVehicleCount, len(trafficSpecTemplates)))]

        addLaneColumnTraffic(leftLane, trafficSpecs)
        addLaneColumnTraffic(rightLane, trafficSpecs)

    def buildWorldProps(self):
        self.worldProps = []
        self.laneVehicles = []
        self.vehicleWaves = []
        self.semiTruckRigs = []
        self.semiTruckWaves = []
        self.walls = []
        self.sortingPallets = []
        self.upgradeDesks = []

        self.buildLoadingDock(self.getZone("Semi Unloading Dock"))
        self.buildSortingZone(self.getZone("Sorting Area"))
        self.buildStorageZone(self.getZone("Storage"))
        self.buildVanPrep(self.getZone("Van Prep", 0), self.getZone("Van Prep", 1))
        self.buildOfficeZone(self.getZone("Offices"))
        self.buildVehicleTraffic(self.getZone("Vehicle Lane", 0), self.getZone("Vehicle Lane", 1))

    def updateInteractionPrompt(self):
        self.showInteractPrompt = False
        self.currentInteraction = None
        interactionRect = self.kirby.interactionRect

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

    def startMinigame(self, type):

        self.currentMinigameType = type

        if type == "sorting":
            self.currentMinigame = SortingMinigame(self)
            self.state = "minigame"
        pass

    def loadHighScores(self):
        try:
            with open("highscores.json", "r") as f:
                return json.load(f)
        except:
            return {}
    
    def saveHighScores(self):

        with open("highscores.json", "w") as f:
            json.dump(self.highScores, f)

    def getWorkerCost(self):
        return int(self.baseWorkerCost * (self.costGrowth ** self.workers))

    def getVanCost(self):
        return int(self.baseVanCost * (self.costGrowth ** self.vans))

    def getCapacityCost(self):
        upgradesOwned = self.vanCapacity // 2
        return int(self.baseCapacityCost * (self.costGrowth ** upgradesOwned))

    def purchaseUpgrade(self, name):
        if name == "+1 Extra Worker":
            cost = self.getWorkerCost()
            if self.money >= cost:
                self.money -= cost
                self.workers += 1

        elif name == "+2 Van Capacity":
            cost = self.getCapacityCost()
            if self.money >= cost:
                self.money -= cost
                self.vanCapacity += 2

        elif name == "+1 Extra Van":
            cost = self.getVanCost()
            if self.money >= cost:
                self.money -= cost
                self.vans += 1

    def drawStockGraph(self, surface):

        rect = pygame.Rect(50, 50, 300, 120)

        # Colors
        bg = (25, 25, 25)
        border = (200, 200, 200)
        grid = (60, 60, 60)
        lineColor = (0, 220, 120)
        textColor = (0, 0, 0)

        font = pygame.font.SysFont(None, 16)

        # Background
        pygame.draw.rect(surface, bg, rect)
        pygame.draw.rect(surface, border, rect, 2)

        if len(self.stockHistory) < 2:
            return

        # Padding in the graph
        pad = 10
        graphRect = rect.inflate(-pad*2, -pad*2)

        minVal = min(self.stockHistory)
        maxVal = max(self.stockHistory)

        # Add vertical margin so line doesn't touch borders
        margin = (maxVal - minVal) * 0.1
        if margin == 0:
            margin = 1

        minVal -= margin
        maxVal += margin

        rangeVal = maxVal - minVal

        # Draw horizontal gridlines + labels
        gridLines = 4
        for i in range(gridLines + 1):

            t = i / gridLines
            y = graphRect.bottom - t * graphRect.height

            pygame.draw.line(surface, grid,
                (graphRect.left, y),
                (graphRect.right, y))

            value = minVal + t * rangeVal

            label = font.render(f"{value:.1f}", True, textColor)
            surface.blit(label, (rect.right + 5, y - 8))

        # Build graph points
        points = []
        for i, value in enumerate(self.stockHistory):

            t = i / (len(self.stockHistory) - 1)

            x = graphRect.left + t * graphRect.width

            normalized = (value - minVal) / rangeVal

            y = graphRect.bottom - normalized * graphRect.height

            points.append((x, y))

        # Fill area under curve
        fillPoints = points.copy()
        fillPoints.append((points[-1][0], graphRect.bottom))
        fillPoints.append((points[0][0], graphRect.bottom))

        pygame.draw.polygon(surface, (0,220,120), fillPoints)

        # Draw main line
        pygame.draw.lines(surface, lineColor, False, points, 2)

        # Draw axes
        pygame.draw.line(surface, border,
            (graphRect.left, graphRect.bottom),
            (graphRect.right, graphRect.bottom), 2)

        pygame.draw.line(surface, border,
            (graphRect.left, graphRect.top),
            (graphRect.left, graphRect.bottom), 2)

        # Draw latest price label
        latest = self.stockHistory[-1]
        label = font.render(f"${latest:.2f}", True, (255,255,255))
        surface.blit(label, (rect.x, rect.y - 18))


