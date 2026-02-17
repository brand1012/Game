import pygame
from vector import vec, pyVec
from drawable import drawable, mobile, wall, kirby
from spriteManager import SpriteManager
from zone import Zone
from sortingMinigame import SortingMinigame
import json

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
        self.floor = self.createPlaceholder(self.WORLD_SIZE, (240,240,240))

        self.dragging = False
        self.dragOffset = vec(0, 0)

        brick = self.spriteManager.getSprite("brick.png")

        self.baseWorkerCost = 50
        self.baseVanCost = 150
        self.baseCapacityCost = 100
        self.costGrowth = 1.15

        self.state = "warehouse"
        self.currentMinigame = None
        self.highScores = self.loadHighScores()

        self.workers = 1
        self.vans = 1
        self.vanCapacity = 1
        self.contractMultiplier = 1

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
                size=(500, 100),
                name="Offices",
                color=(220, 220, 220)
            ),

            # Vehicle lane (left)
            Zone(
                position=(50, 25),
                size=(100, 625),
                name="Vehicle Lane",
                color=(200,200,200)
            ),

            # Vehicle lane (right)
            Zone(
                position=(850, 25),
                size=(100, 625),
                name="Vehicle Lane",
                color=(200,200,200)
            ),

            # Upgrade station
            Zone(
                position=(700, 550),
                size=(100, 100),
                name="Upgrade Station",
                color=(200, 255, 200)
            )

        ]

        self.walls = []

        # ----- UI / Tycoon Stats -----
        self.money = 0
        self.packagesShipped = 0
        self.showInteractPrompt = False

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
        surface.fill((255,255,255))
        surface.blit(self.floor, -drawable.CAMERA_OFFSET)

        for zone in self.zones:
            zone.draw(surface)

        self.kirby.draw(surface)

        self.drawUI(surface)
    
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

        pygame.transform.scale(surface, self.UPSCALED, self.screen)
        pygame.display.flip()

    def updateWarehouse(self, seconds):
        income = self.getIncomePerSecond() * seconds
        self.money += income

        packages = self.getPackagesDeliveredPerSecond() * seconds
        self.packagesShipped += packages

        self.kirby.update(seconds, self.walls)

        self.showInteractPrompt = False
        self.currentZone = None

        for zone in self.zones:
            if zone.rect.colliderect(self.kirby.rect):
                self.showInteractPrompt = True
                self.currentZone = zone
                break

        drawable.CAMERA_OFFSET = (
            self.kirby.position +
            vec(*self.kirby.rect.size) / 2 -
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
        # movement keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.kirby.velocity[0] = 50
            if event.key == pygame.K_LEFT:
                self.kirby.velocity[0] = -50
            if event.key == pygame.K_UP:
                self.kirby.velocity[1] = -50
            if event.key == pygame.K_DOWN:
                self.kirby.velocity[1] = 50

            # interact with zone
            if event.key == pygame.K_e and self.currentZone:
                zoneName = self.currentZone.name
                if zoneName == "Sorting Area":
                    self.startMinigame("sorting")
                if zoneName == "Upgrade Station":
                    self.state = "upgrade"
                else:
                    self.money += 1
                    self.packagesShipped += 1
            
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
        # release keys
        if event.type == pygame.KEYUP:
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

        drawable.CAMERA_OFFSET = self.kirby.position + vec(*self.kirby.rect.size) / 2 - vec(*self.RESOLUTION) / 2

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


