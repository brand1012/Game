import pygame
from vector import vec, pyVec
from drawable import drawable, mobile, wall, kirby
from spriteManager import SpriteManager
from zone import Zone

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

        self.spriteManager = SpriteManager()

        self.kirby = kirby(vec(500, 600), self.spriteManager, self.WORLD_SIZE)
        self.floor = self.createPlaceholder(self.WORLD_SIZE, (240,240,240))

        self.dragging = False
        self.dragOffset = vec(0, 0)

        brick = self.spriteManager.getSprite("brick.png")

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
                color=(200,200,200)
            ),

            # Vehicle lane (right)
            Zone(
                position=(850, 25),
                size=(100, 625),
                name="Vehicle Lane",
                color=(200,200,200)
            )
        ]

        self.walls = []


        # ----- UI / Tycoon Stats -----
        self.money = 0
        self.packagesShipped = 0
        self.showInteractPrompt = False

        self.uiFont = pygame.font.SysFont("Arial", 10, bold=True)

        self.gameClock = pygame.time.Clock()
    
    def draw(self, surface):
        surface.fill((255,255,255))
        surface.blit(self.floor, -drawable.CAMERA_OFFSET)

        for zone in self.zones:
            zone.draw(surface)

        self.kirby.draw(surface)

        self.drawUI(surface)

        pygame.transform.scale(surface, self.UPSCALED, self.screen)
        pygame.display.flip()

    def update(self, seconds):
        if self.dragging:
            mouse = vec(*pygame.mouse.get_pos()) / self.SCALE
            target = mouse - self.dragOffset
            direction = target - self.kirby.position
            self.kirby.velocity = direction * 10 # movement speed

        self.kirby.update(seconds, self.walls)

        drawable.CAMERA_OFFSET = (
            self.kirby.position +
            vec(*self.kirby.rect.size) / 2 -
            vec(*self.RESOLUTION) / 2
        )
        self.clampCamera()

    def clampCamera(self):
        maxX = self.WORLD_SIZE[0] - self.RESOLUTION[0]
        maxY = self.WORLD_SIZE[1] - self.RESOLUTION[1]

        drawable.CAMERA_OFFSET[0] = max(0, min(drawable.CAMERA_OFFSET[0], maxX))
        drawable.CAMERA_OFFSET[1] = max(0, min(drawable.CAMERA_OFFSET[1], maxY))

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.kirby.velocity[0] = 50
            if event.key == pygame.K_LEFT:
                self.kirby.velocity[0] = -50
            if event.key == pygame.K_UP:
                self.kirby.velocity[1] = -50
            if event.key == pygame.K_DOWN:
                self.kirby.velocity[1] = 50
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                self.kirby.velocity[0] = 0
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                self.kirby.velocity[1] = 0
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

        drawable.CAMERA_OFFSET = self.kirby.position + vec(*self.kirby.rect.size) / 2 - vec(*self.RESOLUTION) / 2

    def drawUI(self, surface):

        # Background panel
        panelRect = pygame.Rect(5, 5, 90, 30)
        pygame.draw.rect(surface, (220,220,220), panelRect)
        pygame.draw.rect(surface, (0,0,0), panelRect, 2)

        # Money
        moneyText = self.uiFont.render(f"Money: ${self.money}", True, (0,0,0))
        surface.blit(moneyText, (10, 8))

        # Packages shipped
        packageText = self.uiFont.render(f"Packages: {self.packagesShipped}", True, (0,0,0))
        surface.blit(packageText, (10, 20))

        # Interaction prompt
        if self.showInteractPrompt:
            prompt = self.uiFont.render("Press E to interact", True, (0,0,0))

            x = (self.RESOLUTION[0] - prompt.get_width()) // 2
            y = self.RESOLUTION[1] - 30

            surface.blit(prompt, (x, y))
    
    def createPlaceholder(self, size, color):

        surf = pygame.Surface(size)
        surf.fill(color)

        pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)

        return surf



