from vector import pyVec, vec
import pygame
from kirbystates import IdleState, WalkState

class drawable(object):

    CAMERA_OFFSET = vec(0,0)

    def __init__(self, position, image):
        self.position = position
        self.image = image

    def draw(self, surface):
        surface.blit(self.image, pyVec(self.position) - drawable.CAMERA_OFFSET)

    def setPosition(self, newPosition):
        self.position = newPosition

    def update(self, seconds):
        pass

    def handleEvent(self, event):
        pass


class mobile(drawable):
    def __init__(self, position, image, bounds):
        super().__init__(position, image)
        self.velocity = vec(0,0)
        self.bounds = bounds # (width, height)
        self.rect = pygame.Rect(pyVec(position), image.get_size())

    def updateRect(self):
        self.rect.topleft = pyVec(self.position)

    def collisionDetection(self, dt, walls):
        # X axis
        self.position[0] += self.velocity[0] * dt
        self.updateRect()
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity[0] > 0:
                    self.rect.right = wall.rect.left
                elif self.velocity[0] < 0:
                    self.rect.left = wall.rect.right
                self.position[0] = self.rect.x

        # Y axis
        self.position[1] += self.velocity[1] * dt
        self.updateRect()
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity[1] > 0:
                    self.rect.bottom = wall.rect.top
                elif self.velocity[1] < 0:
                    self.rect.top = wall.rect.bottom
                self.position[1] = self.rect.y


    def update(self, dt, walls=None):
        if walls:
            self.collisionDetection(dt, walls)
        else:
            self.position += self.velocity * dt
            self.updateRect()

        w, h = self.bounds
        spriteWidth, spriteHeight = self.image.get_size()

        # Clamp X
        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] = 0
        elif self.position[0] > w - spriteWidth:
            self.position[0] = w - spriteWidth
            self.velocity[0] = 0

        # Clamp Y
        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity[1] = 0
        elif self.position[1] > h - spriteHeight:
            self.position[1] = h - spriteHeight
            self.velocity[1] = 0

        self.updateRect()


class wall(drawable):
    def __init__(self, position, image):
        super().__init__(position, image)
        self.rect = pygame.Rect(pyVec(position), image.get_size())

    def updateRect(self):
        self.rect.topleft = pyVec(self.position)

class kirby(drawable):
    def __init__(self, position, spriteManager, bounds):
        sheet = spriteManager.getSprite("Kirby.png")

        self.animations = {
            "idle": self.sliceRow(sheet, row=0, cols=2),
            "walk": self.sliceRow(sheet, row=1, cols=4),
        }

        self.stateName = "idle"
        self.frame = 0
        self.timer = 0
        self.framesPerSecond = 10
        self.facing = "right"

        self.image = self.animations["idle"][0]
        super().__init__(position, self.image)

        self.velocity = vec(0, 0)
        self.bounds = bounds
        self.rect = pygame.Rect(pyVec(position), self.image.get_size())

        # --- Finite State Machine ---
        self.state = IdleState()
        self.state.enter(self)

    def getPosition(self):
        return self.position
    
    def getSize(self):
        return vec(*self.image.get_size())
    
    def setAnimation(self, name):
        if self.stateName != name:
            self.stateName = name
            self.frame = 0
            self.timer = 0
        self.image = self.animations[name][0]

    def changeState(self, newState):
        self.state.exit(self)
        self.state = newState
        self.state.enter(self)

    def sliceRow(self, sheet, row, cols):
        sheetWidth, sheetHeight = sheet.get_size()
        frameHeight = sheetHeight // 5   # 5 rows total
        frameWidth = sheetWidth // max(2, 4)  # 4 cols

        frames = []
        for col in range(cols):
            rect = pygame.Rect(col * frameWidth, row * frameHeight,
                               frameWidth, frameHeight)
            frames.append(sheet.subsurface(rect))
        return frames

    def updateRect(self):
        self.rect.topleft = pyVec(self.position)

    def collisionDetection(self, dt, walls):
        # X axis
        self.position[0] += self.velocity[0] * dt
        self.updateRect()
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity[0] > 0:
                    self.rect.right = wall.rect.left
                elif self.velocity[0] < 0:
                    self.rect.left = wall.rect.right
                self.position[0] = self.rect.x

        # Y axis
        self.position[1] += self.velocity[1] * dt
        self.updateRect()
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity[1] > 0:
                    self.rect.bottom = wall.rect.top
                elif self.velocity[1] < 0:
                    self.rect.top = wall.rect.bottom
                self.position[1] = self.rect.y

    def updateAnimation(self, dt):
        frames = self.animations[self.stateName]

        self.timer += dt
        if self.timer >= 1 / self.framesPerSecond:
            self.timer -= 1 / self.framesPerSecond
            self.frame = (self.frame + 1) % len(frames)

        self.image = frames[self.frame]

    def update(self, dt, walls=None):
        self.state.update(self, dt)

        if walls:
            self.collisionDetection(dt, walls)
        else:
            self.position += self.velocity * dt
            self.updateRect()

        w, h = self.bounds
        spriteWidth, spriteHeight = self.image.get_size()

        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] = 0
        elif self.position[0] > w - spriteWidth:
            self.position[0] = w - spriteWidth
            self.velocity[0] = 0

        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity[1] = 0
        elif self.position[1] > h - spriteHeight:
            self.position[1] = h - spriteHeight
            self.velocity[1] = 0

        self.updateRect()
        self.updateAnimation(dt)

    def draw(self, surface):
        image = self.image
        if self.facing == "left":
            image = pygame.transform.flip(self.image, True, False)
        surface.blit(image, pyVec(self.position) - drawable.CAMERA_OFFSET)