import random

import pygame
import systems.highScores as highScores


class SpillCleanupMinigame:
    def __init__(self, game, settings=None):
        self.game = game
        self.settings = settings or {}
        self.activityId = self.settings.get("activityId", "spillCleanup")
        self.isEmergency = self.settings.get("isEmergency", True)
        self.quotaKey = self.settings.get("quotaKey", "emergencies" if self.isEmergency else "spillCleanup")
        self.dayProgressDelta = self.settings.get("dayProgressDelta", 0.1)
        self.recordHighScore = self.settings.get("recordHighScore", not self.isEmergency)
        self.resultLabel = self.settings.get("resultLabel", "SPILL CLEANUP COMPLETE")
        self.failureResultLabel = self.settings.get(
            "failureResultLabel",
            "EMERGENCY RESPONSE FAILED" if self.isEmergency else "SPILL CLEANUP FAILED",
        )
        self.font = game.myFont
        self.smallFont = game.infoFont
        self.timer = float(self.settings.get("roundTime", 18.0))
        self.totalSpills = int(self.settings.get("spillCount", 8))
        self.moneyReward = int(self.settings.get("moneyReward", 18))
        self.scorePerSpill = int(self.settings.get("scorePerSpill", 80))
        self.cursor = pygame.Rect(188, 120, 22, 22)
        self.speed = float(self.settings.get("cursorSpeed", 120))
        self.cleaned = 0
        self.feedbackText = ""
        self.feedbackTimer = 0.0
        self.spills = self.buildSpills(self.totalSpills)

    def buildSpills(self, count):
        random.seed(self.settings.get("seed", self.game.campaign.dayNumber if self.game.campaign else 0))
        spills = []
        for _ in range(count):
            width = random.randint(18, 34)
            height = random.randint(12, 24)
            x = random.randint(24, 400 - width - 24)
            y = random.randint(48, 200 - height - 20)
            spills.append(pygame.Rect(x, y, width, height))
        return spills

    def finishRound(self):
        score = self.cleaned * self.scorePerSpill + int(max(0, self.timer) * 10)
        success = self.cleaned == self.totalSpills
        moneyEarned = self.moneyReward if success else max(0, self.cleaned * 2)
        self.game.money += moneyEarned
        previousHigh = self.game.highScores.get(self.activityId, 0)
        isNewHigh = score > previousHigh

        if isNewHigh and self.recordHighScore:
            self.game.highScores[self.activityId] = score
            highScores.saveHighScores(self.game.highScores, "highscores.json")

        if self.isEmergency:
            outcomeLabel = "Emergency handled" if success else "Emergency failed"
            summaryText = (
                "The spill was cleared before the lane turned into a hazard."
                if success
                else "The cleanup ran out of time and slick patches were still on the floor."
            )
        elif self.game.mode == "story":
            outcomeLabel = "Quota credit earned" if success else "No quota credit"
            summaryText = (
                "This cleanup run counts toward the day's quota."
                if success
                else "The cleanup fell short and does not count toward quota."
            )
        else:
            outcomeLabel = "Run complete" if success else "Run failed"
            summaryText = "Cut a clean path through every spill before time runs out."

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
            "packages": self.cleaned,
            "success": success,
            "resultLabel": self.resultLabel if success else self.failureResultLabel,
            "outcomeLabel": outcomeLabel,
            "summaryText": summaryText,
            "moneyPenalty": 0,
            "countsForQuota": success,
            "safetyDelta": self.cleaned // 3,
        }
        self.game.state = "results"

    def update(self, dt):
        self.timer = max(0.0, self.timer - dt)
        keys = pygame.key.get_pressed()
        moveX = 0
        moveY = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            moveX -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            moveX += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            moveY -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            moveY += self.speed

        self.cursor.x += int(moveX * dt)
        self.cursor.y += int(moveY * dt)
        self.cursor.clamp_ip(pygame.Rect(0, 36, 400, 164))

        cleanedAny = False
        remaining = []
        for spill in self.spills:
            if self.cursor.colliderect(spill):
                cleanedAny = True
                self.cleaned += 1
            else:
                remaining.append(spill)
        self.spills = remaining

        if cleanedAny:
            self.feedbackText = "Spill cleared"
            self.feedbackTimer = 0.35

        if self.feedbackTimer > 0:
            self.feedbackTimer = max(0.0, self.feedbackTimer - dt)

        if self.timer <= 0 or not self.spills:
            self.finishRound()

    def handleEvent(self, event):
        return

    def draw(self, surface):
        surface.fill((28, 26, 32))
        title = self.font.render("SPILL CLEANUP", True, (255, 255, 255))
        surface.blit(title, (126, 8))

        instructions = self.smallFont.render(
            "Move through each spill before somebody slips",
            True,
            (220, 220, 220),
        )
        surface.blit(instructions, (78, 24))

        floorRect = pygame.Rect(18, 40, 364, 146)
        pygame.draw.rect(surface, (58, 58, 64), floorRect, border_radius=10)
        pygame.draw.rect(surface, (90, 90, 96), floorRect, width=2, border_radius=10)

        for spill in self.spills:
            pygame.draw.ellipse(surface, (52, 150, 201), spill)
            pygame.draw.ellipse(surface, (180, 228, 255), spill, 2)

        pygame.draw.rect(surface, (228, 214, 124), self.cursor, border_radius=5)
        pygame.draw.rect(surface, (33, 33, 33), self.cursor, 2, border_radius=5)

        cleanedText = self.smallFont.render(
            "Cleaned: {0}/{1}".format(self.cleaned, self.totalSpills),
            True,
            (255, 255, 255),
        )
        surface.blit(cleanedText, (14, 188))

        timerText = self.smallFont.render(
            "Time: {0}".format(int(self.timer)),
            True,
            (255, 255, 255),
        )
        surface.blit(timerText, (330, 188))

        if self.feedbackTimer > 0:
            feedback = self.smallFont.render(self.feedbackText, True, (130, 255, 170))
            surface.blit(feedback, (158, 188))
