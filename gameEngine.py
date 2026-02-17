import pygame
from vector import vec, pyVec
from drawable import drawable, mobile, wall, kirby
from spriteManager import SpriteManager

class gameEngine(object):
    def __init__(self):
        pygame.init()
        
        self.RESOLUTION = (400, 200)
        self.WORLD_SIZE = (800, 400)
        self.SCALE = 3
        self.UPSCALED = [int(x * self.SCALE) for x in self.RESOLUTION]

        self.screen = pygame.display.set_mode(list(self.UPSCALED))
        self.drawSurface = pygame.Surface(list(self.RESOLUTION))

        self.myFont = pygame.font.SysFont("Arial", 16)

        self.spriteManager = SpriteManager()

        self.kirby = kirby(vec(60, 100), self.spriteManager, self.WORLD_SIZE)
        self.rose = mobile(vec(200, 100), self.spriteManager.getSprite("rose.png", (4,0)), self.WORLD_SIZE)
        self.background = mobile(vec(0, 0), self.spriteManager.getSprite("background.png"), self.WORLD_SIZE)

        self.dragging = False
        self.dragOffset = vec(0, 0)

        brick = self.spriteManager.getSprite("brick.png")
        self.walls = [
            wall(vec(50, 120), brick),
            wall(vec(66, 120), brick),
            wall(vec(82, 120), brick),
            wall(vec(98, 120), brick),
            wall(vec(104, 120), brick),

            wall(vec(104, 104), brick),
            wall(vec(104, 88), brick),
        ]

        # ----- UI / Tycoon Stats -----
        self.money = 0
        self.packagesShipped = 0
        self.showInteractPrompt = False

        self.uiFont = pygame.font.SysFont("Arial", 20, bold=True)

        self.gameClock = pygame.time.Clock()
    
    def draw(self, surface):
        surface.fill((255,255,255))
        self.background.draw(surface)

        self.kirby.draw(surface)
        self.rose.draw(surface)

        for wall in self.walls:
            wall.draw(surface)

        self.drawUI(surface)

        pygame.transform.scale(surface, self.UPSCALED, self.screen)
        pygame.display.flip()

    def update(self, seconds):
        if self.dragging:
            mouse = vec(*pygame.mouse.get_pos()) / self.SCALE
            target = mouse - self.dragOffset
            direction = target - self.kirby.position
            self.kirby.velocity = direction * 10 # adjust for speed

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
        panelRect = pygame.Rect(5, 5, 180, 60)
        pygame.draw.rect(surface, (220,220,220), panelRect)
        pygame.draw.rect(surface, (0,0,0), panelRect, 2)

        # Money
        moneyText = self.uiFont.render(f"Money: ${self.money}", True, (0,0,0))
        surface.blit(moneyText, (10, 10))

        # Packages shipped
        packageText = self.uiFont.render(f"Packages: {self.packagesShipped}", True, (0,0,0))
        surface.blit(packageText, (10, 35))

        # Interaction prompt
        if self.showInteractPrompt:
            prompt = self.uiFont.render("Press E to interact", True, (0,0,0))

            x = (self.RESOLUTION[0] - prompt.get_width()) // 2
            y = self.RESOLUTION[1] - 30

            surface.blit(prompt, (x, y))



