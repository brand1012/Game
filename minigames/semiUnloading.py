import random

import pygame

import systems.highScores as highScores

from assets.warehouseSprites import loadForkliftSprite


class SemiUnloadingMinigame:
    HUD_HEIGHT = 32
    ROUND_TIME = 45.0
    MANIFEST_COUNT = 6
    EMPTY_SPEED = 72
    LOADED_SPEED = 58
    COLLISION_COOLDOWN = 0.25

    def __init__(self, game):
        self.game = game
        self.font = game.myFont
        self.smallFont = game.infoFont

        self.timer = self.ROUND_TIME
        self.delivered = 0
        self.collisions = 0

        self.feedbackText = ""
        self.feedbackColor = (255, 255, 255)
        self.feedbackTimer = 0.0
        self.flashColor = None
        self.flashTimer = 0.0
        self.collisionPenaltyCooldown = 0.0

        self.categories = [
            {"name": "Crated", "color": (195, 155, 90), "fileNames": ["freight/Freight-5.png", "freight/Freight-10.png"]},
            {"name": "Metal", "color": (145, 170, 210), "fileNames": ["freight/Freight-8.png", "freight/Freight-9.png"]},
            {"name": "Boxed", "color": (225, 210, 135), "fileNames": ["freight/Freight-6.png", "freight/Freight-7.png"]},
        ]
        self.spriteToCategory = {}
        for category in self.categories:
            for fileName in category["fileNames"]:
                self.spriteToCategory[fileName] = category["name"]

        self.playRect = pygame.Rect(0, self.HUD_HEIGHT, 400, 200 - self.HUD_HEIGHT)
        self.trailerRect = pygame.Rect(158, 40, 84, 82)
        self.trailerInteriorRect = pygame.Rect(168, 49, 64, 60)
        self.trailerOpeningRect = pygame.Rect(176, 108, 48, 14)
        self.trailerWallRects = [
            pygame.Rect(self.trailerRect.left, self.trailerRect.top, 9, self.trailerRect.height),
            pygame.Rect(self.trailerRect.right - 9, self.trailerRect.top, 9, self.trailerRect.height),
            pygame.Rect(self.trailerRect.left, self.trailerRect.top, self.trailerRect.width, 9),
            pygame.Rect(self.trailerRect.left, self.trailerRect.bottom - 9, 18, 9),
            pygame.Rect(self.trailerRect.right - 18, self.trailerRect.bottom - 9, 18, 9),
        ]
        self.trailerSlotRects = [
            pygame.Rect(177, 53, 46, 16),
            pygame.Rect(177, 74, 46, 16),
            pygame.Rect(177, 95, 46, 16),
        ]

        self.dropBays = [
            {"name": "Crated", "rect": pygame.Rect(14, 154, 112, 30), "cooldown": 0.0, "color": (195, 155, 90)},
            {"name": "Metal", "rect": pygame.Rect(144, 154, 112, 30), "cooldown": 0.0, "color": (145, 170, 210)},
            {"name": "Boxed", "rect": pygame.Rect(274, 154, 112, 30), "cooldown": 0.0, "color": (225, 210, 135)},
        ]
        self.dividerRects = [
            pygame.Rect(132, 150, 8, 38),
            pygame.Rect(262, 150, 8, 38),
        ]
        self.cones = [
            {"image": None, "rect": pygame.Rect(146, 114, 14, 18)},
            {"image": None, "rect": pygame.Rect(240, 114, 14, 18)},
        ]
        self.boundaryWalls = [
            pygame.Rect(0, self.HUD_HEIGHT, 400, 4),
            pygame.Rect(0, 196, 400, 4),
            pygame.Rect(0, self.HUD_HEIGHT, 4, 168),
            pygame.Rect(396, self.HUD_HEIGHT, 4, 168),
        ]

        self.forkliftSize = (36, 36)
        self.forkliftPosition = [182.0, 118.0]
        self.facing = "up"
        self.visualFacing = "right"
        self.forkliftImages = self.buildForkliftImages()
        self.forkliftBodyInset = pygame.Rect(9, 10, 18, 18)
        self.coneImage = pygame.transform.smoothscale(
            game.spriteManager.getSprite("kenney_car-kit_3.0/Previews/cone.png"),
            (14, 18),
        )
        for cone in self.cones:
            cone["image"] = self.coneImage

        trailerSurface = game.spriteManager.getSprite("2D_TOPDOWN_PIXELART_CARS.png", (172, 0, 36, 96))
        self.trailerImage = pygame.transform.smoothscale(trailerSurface, self.trailerRect.size)

        self.palletPreviewSize = (28, 22)
        self.palletCarrySize = (22, 16)
        self.palletSurfaces = {}
        self.palletCarrySurfaces = {}
        for fileName in self.spriteToCategory:
            self.palletSurfaces[fileName] = pygame.transform.smoothscale(
                game.spriteManager.getSprite(fileName),
                self.palletPreviewSize,
            )
            self.palletCarrySurfaces[fileName] = pygame.transform.smoothscale(
                game.spriteManager.getSprite(fileName),
                self.palletCarrySize,
            )

        self.manifest = [random.choice(list(self.spriteToCategory.keys())) for _ in range(self.MANIFEST_COUNT)]
        self.spawnIndex = 0
        self.trailerSlots = [None, None, None]
        self.carrying = None
        self.fillTrailerSlots()

    def buildForkliftImages(self):
        base = loadForkliftSprite(self.game.spriteManager, self.forkliftSize)
        return {
            "right": base,
            "left": pygame.transform.flip(base, True, False),
        }

    def getForkliftDrawRect(self):
        return pygame.Rect(
            int(round(self.forkliftPosition[0])),
            int(round(self.forkliftPosition[1])),
            self.forkliftSize[0],
            self.forkliftSize[1],
        )

    def getForkliftBodyRect(self):
        drawRect = self.getForkliftDrawRect()
        return pygame.Rect(
            drawRect.x + self.forkliftBodyInset.x,
            drawRect.y + self.forkliftBodyInset.y,
            self.forkliftBodyInset.width,
            self.forkliftBodyInset.height,
        )

    def getForkHitbox(self):
        drawRect = self.getForkliftDrawRect()
        if self.facing == "up":
            return pygame.Rect(drawRect.x + 10, drawRect.y + 1, 16, 12)
        if self.facing == "down":
            return pygame.Rect(drawRect.x + 10, drawRect.bottom - 13, 16, 12)
        if self.facing == "left":
            return pygame.Rect(drawRect.x + 1, drawRect.y + 10, 12, 16)
        return pygame.Rect(drawRect.right - 13, drawRect.y + 10, 12, 16)

    def getCarriedPalletRect(self):
        drawRect = self.getForkliftDrawRect()
        carryWidth, carryHeight = self.palletCarrySize
        palletY = drawRect.bottom - carryHeight - 9
        if self.visualFacing == "left":
            return pygame.Rect(
                drawRect.x + 2,
                palletY,
                carryWidth,
                carryHeight,
            )
        return pygame.Rect(
            drawRect.right - carryWidth - 2,
            palletY,
            carryWidth,
            carryHeight,
        )

    def fillTrailerSlots(self):
        for slotIndex in range(len(self.trailerSlots)):
            if self.trailerSlots[slotIndex] is None and self.spawnIndex < len(self.manifest):
                fileName = self.manifest[self.spawnIndex]
                self.spawnIndex += 1
                self.trailerSlots[slotIndex] = {
                    "fileName": fileName,
                    "category": self.spriteToCategory[fileName],
                    "rect": self.trailerSlotRects[slotIndex].copy(),
                }

    def getDisplayScore(self):
        return max(0, (self.delivered * 100) - (self.collisions * 10))

    def getFinalScore(self):
        return max(0, (self.delivered * 100) + int(max(0, self.timer)) * 2 - (self.collisions * 10))

    def setFeedback(self, text, color, timer=0.8):
        self.feedbackText = text
        self.feedbackColor = color
        self.feedbackTimer = timer

    def triggerFlash(self, color, timer=0.18):
        self.flashColor = color
        self.flashTimer = timer

    def addCollisionPenalty(self):
        if self.collisionPenaltyCooldown > 0:
            return

        self.collisions += 1
        self.collisionPenaltyCooldown = self.COLLISION_COOLDOWN
        self.setFeedback("WATCH THE DOCK WALLS", (255, 120, 120))
        self.triggerFlash((255, 75, 75))

    def getCollisionRects(self):
        coneRects = [cone["rect"] for cone in self.cones]
        return self.boundaryWalls + self.trailerWallRects + coneRects

    def collidesWithWalls(self):
        bodyRect = self.getForkliftBodyRect()
        for wallRect in self.getCollisionRects():
            if bodyRect.colliderect(wallRect):
                return True
        return False

    def moveForklift(self, dt):
        keys = pygame.key.get_pressed()
        speed = self.LOADED_SPEED if self.carrying else self.EMPTY_SPEED
        moveX = 0
        moveY = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            moveX = -speed
            self.facing = "left"
            self.visualFacing = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            moveX = speed
            self.facing = "right"
            self.visualFacing = "right"
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            moveY = -speed
            self.facing = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            moveY = speed
            self.facing = "down"

        collided = False

        if moveX != 0:
            originalX = self.forkliftPosition[0]
            self.forkliftPosition[0] += moveX * dt
            if self.collidesWithWalls():
                self.forkliftPosition[0] = originalX
                collided = True

        if moveY != 0:
            originalY = self.forkliftPosition[1]
            self.forkliftPosition[1] += moveY * dt
            if self.collidesWithWalls():
                self.forkliftPosition[1] = originalY
                collided = True

        if collided:
            self.addCollisionPenalty()

    def handleAction(self):
        if self.carrying:
            carriedRect = self.getCarriedPalletRect()
            matchedBay = None
            for bay in self.dropBays:
                if bay["cooldown"] > 0:
                    continue

                bayTargetRect = bay["rect"].inflate(-10, -8)
                if bayTargetRect.collidepoint(carriedRect.center):
                    matchedBay = bay
                    break

            if matchedBay and matchedBay["name"] == self.carrying["category"]:
                self.delivered += 1
                matchedBay["cooldown"] = 0.35
                self.carrying = None
                self.setFeedback("PALLET UNLOADED", (120, 255, 150))
                self.triggerFlash((70, 220, 120))
                if self.delivered >= self.MANIFEST_COUNT:
                    self.finishRound()
                return

            if matchedBay:
                self.setFeedback("WRONG BAY FOR {0}".format(self.carrying["category"].upper()), (255, 120, 120))
                self.triggerFlash((255, 75, 75))
                return

            self.setFeedback("LINE UP WITH A MATCHING BAY", (255, 120, 120))
            self.triggerFlash((255, 75, 75))
            return

        forkHitbox = self.getForkHitbox()
        for slotIndex, slot in enumerate(self.trailerSlots):
            if slot and forkHitbox.colliderect(slot["rect"]):
                self.carrying = {
                    "fileName": slot["fileName"],
                    "category": slot["category"],
                }
                self.trailerSlots[slotIndex] = None
                self.fillTrailerSlots()
                self.setFeedback("{0} PALLET SECURED".format(self.carrying["category"].upper()), (120, 220, 255))
                self.triggerFlash((90, 160, 255), timer=0.14)
                return

        self.setFeedback("ALIGN WITH A TRAILER PALLET", (255, 220, 120))

    def finishRound(self):
        finalScore = self.getFinalScore()
        moneyEarned = self.delivered * 12
        self.game.money += moneyEarned
        self.game.packagesShipped += self.delivered

        gameType = self.game.currentMinigameType
        previousHigh = self.game.highScores.get(gameType, 0)
        isNewHigh = finalScore > previousHigh

        if isNewHigh:
            self.game.highScores[gameType] = finalScore
            highScores.saveHighScores(self.game.highScores, "highscores.json")

        self.game.resultsData = {
            "score": finalScore,
            "money": moneyEarned,
            "highScore": self.game.highScores.get(gameType, 0),
            "isNewHigh": isNewHigh,
            "type": gameType,
        }
        self.game.state = "results"

    def update(self, dt):
        self.timer = max(0, self.timer - dt)
        self.moveForklift(dt)

        if self.feedbackTimer > 0:
            self.feedbackTimer = max(0, self.feedbackTimer - dt)
        if self.flashTimer > 0:
            self.flashTimer = max(0, self.flashTimer - dt)
        if self.collisionPenaltyCooldown > 0:
            self.collisionPenaltyCooldown = max(0, self.collisionPenaltyCooldown - dt)

        for bay in self.dropBays:
            if bay["cooldown"] > 0:
                bay["cooldown"] = max(0, bay["cooldown"] - dt)

        if self.timer == 0:
            self.finishRound()

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.handleAction()

    def drawPlayfield(self, surface):
        surface.fill((26, 26, 30))
        pygame.draw.rect(surface, (34, 34, 40), self.playRect)

        laneRect = pygame.Rect(166, 118, 68, 32)
        pygame.draw.rect(surface, (44, 44, 50), laneRect, border_radius=6)

        stripeY = 138
        for stripeX in (24, 70, 116, 262, 308, 354):
            pygame.draw.rect(surface, (236, 196, 72), pygame.Rect(stripeX, stripeY, 28, 6), border_radius=3)

        for dividerRect in self.dividerRects:
            pygame.draw.rect(surface, (36, 36, 40), dividerRect.inflate(2, 2), border_radius=3)
            pygame.draw.rect(surface, (164, 166, 176), dividerRect, border_radius=3)
            pygame.draw.rect(surface, (236, 196, 72), pygame.Rect(dividerRect.x, dividerRect.y + 6, dividerRect.width, 6), border_radius=2)

        for bayIndex, bay in enumerate(self.dropBays):
            bayRect = bay["rect"]
            carryingRect = self.getCarriedPalletRect() if self.carrying else None
            isHoveringTarget = (
                self.carrying is not None
                and carryingRect is not None
                and bayRect.inflate(-10, -8).collidepoint(carryingRect.center)
            )
            isValidTarget = (
                isHoveringTarget
                and bay["cooldown"] == 0
                and bay["name"] == self.carrying["category"]
            )
            isWrongTarget = isHoveringTarget and bay["cooldown"] == 0 and bay["name"] != self.carrying["category"]

            bayFill = (44, 44, 50)
            bayOutline = bay["color"]
            if bay["cooldown"] > 0:
                bayFill = (74, 108, 82)
                bayOutline = (155, 255, 175)
            elif isValidTarget:
                bayFill = (60, 92, 72)
                bayOutline = (120, 255, 150)
            elif isWrongTarget:
                bayFill = (88, 54, 56)
                bayOutline = (255, 120, 120)

            pygame.draw.rect(surface, bayFill, bayRect, border_radius=8)
            pygame.draw.rect(surface, bayOutline, bayRect, width=3, border_radius=8)

            bayLabel = self.smallFont.render("BAY {0}".format(bayIndex + 1), True, (220, 220, 220))
            bayLabelX = bayRect.x + (bayRect.width - bayLabel.get_width()) // 2
            surface.blit(bayLabel, (bayLabelX, bayRect.y + 4))

            typeLabel = self.smallFont.render(bay["name"], True, (255, 255, 255))
            typeLabelX = bayRect.x + (bayRect.width - typeLabel.get_width()) // 2
            surface.blit(typeLabel, (typeLabelX, bayRect.y + 15))

    def drawTrailer(self, surface):
        shadowRect = self.trailerRect.inflate(8, 8)
        pygame.draw.rect(surface, (18, 18, 22), shadowRect, border_radius=12)
        surface.blit(self.trailerImage, self.trailerRect.topleft)
        pygame.draw.rect(surface, (26, 26, 30), self.trailerInteriorRect, border_radius=6)
        pygame.draw.rect(surface, (196, 196, 204), self.trailerInteriorRect, width=2, border_radius=6)
        pygame.draw.rect(surface, (224, 224, 230), self.trailerOpeningRect, width=2, border_radius=4)

        for slot in self.trailerSlots:
            if not slot:
                continue

            slotRect = slot["rect"]
            pygame.draw.rect(surface, (44, 44, 50), slotRect.inflate(8, 6), border_radius=6)
            palletSurface = self.palletSurfaces[slot["fileName"]]
            palletRect = palletSurface.get_rect(center=slotRect.center)
            surface.blit(palletSurface, palletRect.topleft)

        for cone in self.cones:
            surface.blit(cone["image"], cone["rect"].topleft)

    def drawForklift(self, surface):
        drawRect = self.getForkliftDrawRect()
        image = self.forkliftImages[self.visualFacing]
        imageRect = image.get_rect(center=drawRect.center)
        surface.blit(image, imageRect.topleft)

        if self.carrying:
            palletRect = self.getCarriedPalletRect()
            palletSurface = self.palletCarrySurfaces[self.carrying["fileName"]]
            surface.blit(palletSurface, palletRect.topleft)

    def drawHud(self, surface):
        pygame.draw.rect(surface, (18, 18, 22), pygame.Rect(0, 0, 400, self.HUD_HEIGHT))
        pygame.draw.line(surface, (58, 58, 64), (0, self.HUD_HEIGHT - 1), (400, self.HUD_HEIGHT - 1), 1)

        title = self.font.render("UNLOAD THE SEMI", True, (255, 255, 255))
        surface.blit(title, (10, 4))

        instructions = self.smallFont.render(
            "WASD / Arrows move   SPACE unload to the matching bay",
            True,
            (220, 220, 220),
        )
        surface.blit(instructions, (10, 19))

        palletText = self.smallFont.render(
            "Pallets: {0}/{1}".format(self.delivered, self.MANIFEST_COUNT),
            True,
            (255, 255, 255),
        )
        surface.blit(palletText, (10, 40))

        scoreText = self.smallFont.render(
            "Score: {0}".format(self.getDisplayScore()),
            True,
            (255, 255, 255),
        )
        surface.blit(scoreText, (10, 54))

        timeText = self.smallFont.render("Time: {0}".format(int(self.timer)), True, (255, 255, 255))
        surface.blit(timeText, (320, 40))

        collisionText = self.smallFont.render(
            "Hits: {0}".format(self.collisions),
            True,
            (215, 215, 215),
        )
        surface.blit(collisionText, (316, 68))

        if self.feedbackTimer > 0:
            feedback = self.smallFont.render(self.feedbackText, True, self.feedbackColor)
            surface.blit(feedback, (10, 68))

    def draw(self, surface):
        self.drawPlayfield(surface)
        self.drawTrailer(surface)
        self.drawForklift(surface)
        self.drawHud(surface)

        if self.flashTimer > 0 and self.flashColor:
            flashSurface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            alpha = int(70 * (self.flashTimer / 0.18))
            flashSurface.fill((*self.flashColor, max(0, min(120, alpha))))
            surface.blit(flashSurface, (0, 0))
