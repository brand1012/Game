import pygame
import random


class SortingMinigame:

    def __init__(self, game):

        self.game = game

        self.timer = 15
        self.score = 0

        self.font = game.myFont
        self.smallFont = game.infoFont
        self.palletSize = (78, 92)

        self.categories = [
            {
                "name": "Crated",
                "color": (195, 155, 90),
                "fileNames": ["freight/Freight-5.png", "freight/Freight-10.png"]
            },
            {
                "name": "Metal",
                "color": (145, 170, 210),
                "fileNames": ["freight/Freight-8.png", "freight/Freight-9.png"]
            },
            {
                "name": "Boxed",
                "color": (225, 210, 135),
                "fileNames": ["freight/Freight-6.png", "freight/Freight-7.png"]
            }
        ]

        self.spriteToCategory = {}
        self.previewSprites = {}
        for category in self.categories:
            for fileName in category["fileNames"]:
                self.spriteToCategory[fileName] = category["name"]
                self.previewSprites[fileName] = pygame.transform.smoothscale(
                    self.game.spriteManager.getSprite(fileName),
                    self.palletSize
                )

        self.dropZones = [
            {
                "name": "Crated",
                "rect": pygame.Rect(15, 138, 118, 48),
                "color": (195, 155, 90)
            },
            {
                "name": "Metal",
                "rect": pygame.Rect(141, 138, 118, 48),
                "color": (145, 170, 210)
            },
            {
                "name": "Boxed",
                "rect": pygame.Rect(267, 138, 118, 48),
                "color": (225, 210, 135)
            }
        ]

        self.feedbackTimer = 0
        self.feedbackColor = (255, 255, 255)
        self.feedbackText = ""

        self.dragging = False
        self.dragOffset = (0, 0)
        self.palletRect = pygame.Rect(161, 48, self.palletSize[0], self.palletSize[1])

        self.spawnNewPallet()

    def getScaledMousePos(self, pos):
        return (
            int(pos[0] / self.game.SCALE),
            int(pos[1] / self.game.SCALE)
        )

    def spawnNewPallet(self):
        fileName = random.choice(list(self.spriteToCategory.keys()))
        self.currentPallet = {
            "fileName": fileName,
            "category": self.spriteToCategory[fileName]
        }
        self.palletRect.topleft = (161, 48)
        self.dragging = False

    def finishRound(self):
        print("Final score:", self.score)

        moneyEarned = max(0, self.score * 5)
        delivered = max(0, self.score)

        self.game.money += moneyEarned
        self.game.packagesShipped += delivered

        gameType = self.game.currentMinigameType
        previousHigh = self.game.highScores.get(gameType, 0)
        isNewHigh = self.score > previousHigh

        if isNewHigh:
            self.game.highScores[gameType] = self.score
            self.game.saveHighScores()

        self.game.resultsData = {
            "score": self.score,
            "money": moneyEarned,
            "highScore": self.game.highScores.get(gameType, 0),
            "isNewHigh": isNewHigh,
            "type": gameType
        }

        self.game.state = "results"

    def update(self, dt):

        self.timer -= dt
        if self.feedbackTimer > 0:
            self.feedbackTimer = max(0, self.feedbackTimer - dt)

        if self.timer <= 0:
            self.finishRound()

    def handleDrop(self):
        matchedZone = None
        for zone in self.dropZones:
            if zone["rect"].colliderect(self.palletRect):
                matchedZone = zone
                break

        if matchedZone and matchedZone["name"] == self.currentPallet["category"]:
            self.score += 1
            self.feedbackText = "Correct"
            self.feedbackColor = (100, 255, 140)
            self.spawnNewPallet()
        else:
            self.score -= 1
            self.feedbackText = "Wrong Bay"
            self.feedbackColor = (255, 110, 110)
            self.palletRect.topleft = (161, 48)

        self.feedbackTimer = 0.6

    def handleEvent(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mousePos = self.getScaledMousePos(event.pos)
            if self.palletRect.collidepoint(mousePos):
                self.dragging = True
                self.dragOffset = (
                    mousePos[0] - self.palletRect.x,
                    mousePos[1] - self.palletRect.y
                )

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mousePos = self.getScaledMousePos(event.pos)
            self.palletRect.x = mousePos[0] - self.dragOffset[0]
            self.palletRect.y = mousePos[1] - self.dragOffset[1]

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging:
            self.dragging = False
            self.handleDrop()

    def drawDropZone(self, surface, zone):
        pygame.draw.rect(surface, (34, 34, 40), zone["rect"], border_radius=8)
        pygame.draw.rect(surface, zone["color"], zone["rect"], width=3, border_radius=8)

        label = self.smallFont.render(zone["name"], True, (255, 255, 255))
        labelX = zone["rect"].x + (zone["rect"].width - label.get_width()) // 2
        surface.blit(label, (labelX, zone["rect"].y + 16))

    def draw(self, surface):

        surface.fill((20, 20, 24))

        title = self.font.render("DRAG PALLETS TO THE RIGHT BAY", True, (255, 255, 255))
        surface.blit(title, (72, 10))

        instructions = self.smallFont.render(
            "Sort each pallet by freight type: Crated, Metal, or Boxed",
            True,
            (220, 220, 220)
        )
        surface.blit(instructions, (10, 28))

        targetText = self.smallFont.render(
            f"Current pallet belongs in: {self.currentPallet['category']}",
            True,
            (240, 240, 240)
        )
        surface.blit(targetText, (10, 44))

        for zone in self.dropZones:
            self.drawDropZone(surface, zone)

        palletSprite = self.previewSprites[self.currentPallet["fileName"]]
        surface.blit(palletSprite, self.palletRect.topleft)

        outlineColor = (255, 255, 255) if self.dragging else (120, 120, 130)
        pygame.draw.rect(surface, outlineColor, self.palletRect.inflate(6, 6), width=2, border_radius=8)

        if self.feedbackTimer > 0:
            feedback = self.font.render(self.feedbackText, True, self.feedbackColor)
            surface.blit(feedback, (145, 108))

        scoreText = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(scoreText, (10, 10))

        timerText = self.font.render(f"Time: {int(self.timer)}", True, (255, 255, 255))
        surface.blit(timerText, (302, 10))
