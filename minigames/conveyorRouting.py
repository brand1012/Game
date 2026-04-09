import random

import pygame

import systems.highScores as highScores


class ConveyorRoutingMinigame:
    HUD_HEIGHT = 34

    CATEGORY_INFO = {
        "Crated": {"color": (166, 104, 66), "lane": "crate"},
        "Metal": {"color": (92, 156, 224), "lane": "metal"},
        "Boxed": {"color": (104, 196, 112), "lane": "boxed"},
    }

    LANE_LABELS = {
        "crate": "CRATED",
        "metal": "METAL",
        "boxed": "BOXED",
    }

    def __init__(self, game, settings=None):
        self.game = game
        self.settings = settings or {}
        self.activityId = self.settings.get("activityId", game.currentMinigameType)
        self.quotaKey = self.settings.get("quotaKey", "conveyorRouting")
        self.dayProgressDelta = self.settings.get("dayProgressDelta", 0.18)
        self.isEmergency = self.settings.get("isEmergency", False)
        self.recordHighScore = self.settings.get("recordHighScore", True)
        self.resultLabel = self.settings.get("resultLabel", "CONVEYOR ROUTING COMPLETE")
        self.font = game.myFont
        self.smallFont = game.infoFont

        self.roundTime = float(self.settings.get("roundTime", 28.0))
        self.spawnInterval = float(self.settings.get("spawnInterval", 1.35))
        self.boxSpeed = float(self.settings.get("boxSpeed", 60.0))
        self.queueLength = int(self.settings.get("queueLength", 4))
        self.moneyPerCorrect = int(self.settings.get("moneyPerCorrect", 6))
        self.maxBacklog = int(self.settings.get("maxBacklog", 6))
        self.successTarget = int(self.settings.get("successTarget", max(6, self.queueLength * 2)))

        self.timer = self.roundTime
        self.spawnTimer = 0.0
        self.handled = 0
        self.correct = 0
        self.wrong = 0
        self.backlog = 0
        self.backlogBursts = 0
        self.peakBacklog = 0
        self.feedbackText = ""
        self.feedbackColor = (255, 255, 255)
        self.feedbackTimer = 0.0

        self.gateOneDivert = False
        self.gateTwoDivert = True

        self.playRect = pygame.Rect(0, self.HUD_HEIGHT, 400, 200 - self.HUD_HEIGHT)
        self.mainBeltRect = pygame.Rect(18, 56, 302, 28)
        self.gateOneX = 132
        self.gateTwoX = 230
        self.boxedDropX = 304

        self.laneTargets = {
            "crate": {"centerX": 86, "boxY": 132, "rect": pygame.Rect(26, 148, 88, 34)},
            "metal": {"centerX": 200, "boxY": 132, "rect": pygame.Rect(156, 148, 88, 34)},
            "boxed": {"centerX": 314, "boxY": 132, "rect": pygame.Rect(286, 148, 88, 34)},
        }

        self.beltFrames = self.buildBeltFrames()
        self.verticalBeltFrames = [pygame.transform.rotate(frame, -90) for frame in self.beltFrames]
        self.boxImage = pygame.transform.smoothscale(
            game.spriteManager.getSprite("kenney_car-kit_3.0/Previews/box.png"),
            (22, 22),
        )
        self.boxes = []
        self.random = random.Random(self.settings.get("seed", self.game.campaign.dayNumber if self.game.campaign else 0))

    def buildBeltFrames(self):
        frameRects = [(0, 0, 49, 15), (49, 0, 49, 15), (98, 0, 49, 15)]
        return [
            pygame.transform.smoothscale(
                self.game.spriteManager.getSprite("Conveyor Belts sprite sheet.png", rect),
                (74, 24),
            )
            for rect in frameRects
        ]

    def setFeedback(self, text, color, duration=0.55):
        self.feedbackText = text
        self.feedbackColor = color
        self.feedbackTimer = duration

    def spawnBox(self):
        category = self.random.choice(list(self.CATEGORY_INFO.keys()))
        rect = self.boxImage.get_rect(center=(-12, self.mainBeltRect.centery))
        self.boxes.append(
            {
                "rect": rect,
                "position": [float(rect.x), float(rect.y)],
                "category": category,
                "lane": None,
                "laneKey": None,
                "gateOneProcessed": False,
                "gateTwoProcessed": False,
            }
        )

    def routeToLane(self, box, laneKey):
        box["lane"] = "branch"
        box["laneKey"] = laneKey

    def handleMistake(self, message):
        self.wrong += 1
        self.backlog = min(self.maxBacklog, self.backlog + 2)
        self.peakBacklog = max(self.peakBacklog, self.backlog)
        self.setFeedback(message, (255, 120, 120))

        if self.backlog >= self.maxBacklog:
            self.backlogBursts += 1
            self.backlog = max(2, self.maxBacklog - 2)
            self.setFeedback("BACKLOG SPIKE", (255, 172, 110), duration=0.8)

    def resolveBox(self, box):
        self.handled += 1
        laneKey = box["laneKey"]
        category = box["category"]
        correctLane = self.CATEGORY_INFO[category]["lane"]
        if laneKey == correctLane:
            self.correct += 1
            self.backlog = max(0, self.backlog - 1)
            self.setFeedback(category.upper() + " ROUTED", (120, 255, 150), duration=0.4)
        else:
            self.handleMistake("WRONG LANE FOR " + category.upper())

    def updateMainBox(self, box, dt):
        box["position"][0] += self.boxSpeed * dt
        box["rect"].x = int(round(box["position"][0]))

        if not box["gateOneProcessed"] and box["rect"].centerx >= self.gateOneX:
            box["gateOneProcessed"] = True
            if self.gateOneDivert:
                self.routeToLane(box, "crate")
                return

        if not box["gateTwoProcessed"] and box["rect"].centerx >= self.gateTwoX:
            box["gateTwoProcessed"] = True
            if self.gateTwoDivert:
                self.routeToLane(box, "metal")
                return

        if box["rect"].centerx >= self.boxedDropX:
            self.routeToLane(box, "boxed")

    def updateBranchBox(self, box, dt):
        laneKey = box["laneKey"]
        lane = self.laneTargets[laneKey]
        currentX = box["rect"].centerx
        targetX = lane["centerX"]
        moveStep = self.boxSpeed * 0.95 * dt

        if abs(targetX - currentX) <= moveStep:
            box["position"][0] = float(targetX - (box["rect"].width / 2))
        elif currentX < targetX:
            box["position"][0] += moveStep
        else:
            box["position"][0] -= moveStep

        box["position"][1] += self.boxSpeed * 0.8 * dt
        box["rect"].x = int(round(box["position"][0]))
        box["rect"].y = int(round(box["position"][1]))
        if box["rect"].centery >= lane["boxY"]:
            self.resolveBox(box)
            return False
        return True

    def update(self, dt):
        if self.correct >= self.successTarget:
            self.finishRound()
            return

        self.timer = max(0.0, self.timer - dt)
        self.spawnTimer -= dt

        if self.spawnTimer <= 0 and len(self.boxes) < self.queueLength:
            self.spawnBox()
            self.spawnTimer = self.spawnInterval

        remaining = []
        for box in self.boxes:
            if box["lane"] == "branch":
                if self.updateBranchBox(box, dt):
                    remaining.append(box)
                elif self.correct >= self.successTarget:
                    self.finishRound()
                    return
                continue

            self.updateMainBox(box, dt)
            if box["lane"] == "branch":
                if self.updateBranchBox(box, dt):
                    remaining.append(box)
                elif self.correct >= self.successTarget:
                    self.finishRound()
                    return
            elif box["rect"].left > self.playRect.right:
                self.handleMistake("BOX PASSED THE SORTER")
            else:
                remaining.append(box)

        self.boxes = remaining

        if self.correct >= self.successTarget:
            self.finishRound()
            return

        if self.feedbackTimer > 0:
            self.feedbackTimer = max(0.0, self.feedbackTimer - dt)

        if self.timer <= 0:
            self.finishRound()

    def finishRound(self):
        score = max(0, (self.correct * 110) - (self.wrong * 35) - (self.backlogBursts * 40) + int(self.timer) * 4)
        moneyEarned = max(0, self.correct * self.moneyPerCorrect)
        self.game.money += moneyEarned
        self.game.packagesShipped += self.correct

        previousHigh = self.game.highScores.get(self.activityId, 0)
        isNewHigh = score > previousHigh

        if isNewHigh and self.recordHighScore:
            self.game.highScores[self.activityId] = score
            highScores.saveHighScores(self.game.highScores, "highscores.json")

        success = self.correct >= self.successTarget and self.peakBacklog < self.maxBacklog
        self.game.resultsData = {
            "score": score,
            "money": moneyEarned,
            "highScore": self.game.highScores.get(self.activityId, 0),
            "isNewHigh": isNewHigh and self.recordHighScore,
            "type": self.activityId,
            "activityId": self.activityId,
            "quotaKey": self.quotaKey,
            "dayProgressDelta": self.dayProgressDelta,
            "isEmergency": self.isEmergency,
            "packages": self.correct,
            "success": success,
            "resultLabel": self.resultLabel,
            "safetyDelta": self.correct // 4 - self.wrong,
        }
        self.game.state = "results"

    def handleEvent(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_1:
            self.gateOneDivert = not self.gateOneDivert
            text = "GATE 1 -> CRATED" if self.gateOneDivert else "GATE 1 -> PASS"
            self.setFeedback(text, (160, 210, 255), duration=0.35)
        elif event.key == pygame.K_2:
            self.gateTwoDivert = not self.gateTwoDivert
            text = "GATE 2 -> METAL" if self.gateTwoDivert else "GATE 2 -> BOXED"
            self.setFeedback(text, (160, 210, 255), duration=0.35)

    def drawBelts(self, surface):
        frame = self.beltFrames[int((self.roundTime - self.timer) * 8) % len(self.beltFrames)]
        verticalFrame = self.verticalBeltFrames[int((self.roundTime - self.timer) * 8) % len(self.verticalBeltFrames)]

        for x in (18, 90, 162, 234):
            surface.blit(frame, (x, self.mainBeltRect.y))

        surface.blit(verticalFrame, (74, 74))
        surface.blit(verticalFrame, (188, 74))
        surface.blit(verticalFrame, (302, 74))

        pygame.draw.line(surface, (88, 88, 94), (self.gateOneX, 68), (74, 112), 3)
        pygame.draw.line(surface, (88, 88, 94), (self.gateTwoX, 68), (188, 112), 3)
        pygame.draw.line(surface, (88, 88, 94), (self.boxedDropX, 68), (302, 112), 3)

    def drawGate(self, surface, x, label, active, targetText):
        color = (122, 240, 152) if active else (236, 196, 72)
        stateText = targetText if active else "PASS"
        pygame.draw.rect(surface, (38, 38, 44), pygame.Rect(x - 16, 42, 32, 12), border_radius=4)
        pygame.draw.rect(surface, color, pygame.Rect(x - 14, 44, 28, 8), border_radius=4)
        gateLabel = self.smallFont.render(label, True, (230, 230, 230))
        gateState = self.smallFont.render(stateText, True, color)
        surface.blit(gateLabel, (x - gateLabel.get_width() // 2, 90))
        surface.blit(gateState, (x - gateState.get_width() // 2, 102))

    def drawLanes(self, surface):
        for laneKey, lane in self.laneTargets.items():
            info = next(info for name, info in self.CATEGORY_INFO.items() if info["lane"] == laneKey)
            rect = lane["rect"]
            pygame.draw.rect(surface, (38, 38, 44), rect, border_radius=8)
            pygame.draw.rect(surface, info["color"], rect, 3, border_radius=8)
            label = self.smallFont.render(self.LANE_LABELS[laneKey], True, (255, 255, 255))
            labelX = rect.x + (rect.width - label.get_width()) // 2
            surface.blit(label, (labelX, rect.y + 10))

    def drawBoxes(self, surface):
        for box in self.boxes:
            surface.blit(self.boxImage, box["rect"].topleft)
            color = self.CATEGORY_INFO[box["category"]]["color"]
            tagRect = pygame.Rect(box["rect"].x + 4, box["rect"].y + 4, 14, 8)
            pygame.draw.rect(surface, color, tagRect, border_radius=3)
            pygame.draw.rect(surface, (32, 32, 32), tagRect, 1, border_radius=3)

    def drawHud(self, surface):
        pygame.draw.rect(surface, (18, 18, 22), pygame.Rect(0, 0, 400, self.HUD_HEIGHT))
        pygame.draw.line(surface, (58, 58, 64), (0, self.HUD_HEIGHT - 1), (400, self.HUD_HEIGHT - 1), 1)

        title = self.font.render("CONVEYOR ROUTING", True, (255, 255, 255))
        surface.blit(title, (10, 4))

        instructions = self.smallFont.render(
            "1 toggle crate divert   2 toggle metal divert",
            True,
            (220, 220, 220),
        )
        surface.blit(instructions, (10, 19))

        statusText = self.smallFont.render(
            "Handled {0}/{1}   Backlog {2}/{3}".format(self.correct, self.successTarget, self.backlog, self.maxBacklog),
            True,
            (255, 255, 255),
        )
        surface.blit(statusText, (10, 40))

        timerText = self.smallFont.render("Time: {0}".format(int(self.timer)), True, (255, 255, 255))
        surface.blit(timerText, (330, 40))

        if self.feedbackTimer > 0:
            feedback = self.smallFont.render(self.feedbackText, True, self.feedbackColor)
            surface.blit(feedback, (10, 54))

    def draw(self, surface):
        surface.fill((24, 24, 28))
        pygame.draw.rect(surface, (32, 32, 36), self.playRect)
        self.drawBelts(surface)
        self.drawGate(surface, self.gateOneX, "GATE 1", self.gateOneDivert, "CRATE")
        self.drawGate(surface, self.gateTwoX, "GATE 2", self.gateTwoDivert, "METAL")
        self.drawLanes(surface)
        self.drawBoxes(surface)
        self.drawHud(surface)
