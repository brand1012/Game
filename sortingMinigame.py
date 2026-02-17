import pygame
import random

class SortingMinigame:

    def __init__(self, game):

        self.game = game

        self.timer = 10
        self.score = 1

        self.colors = [
            ("RED", (255,0,0), pygame.K_a),
            ("GREEN", (0,255,0), pygame.K_s),
            ("BLUE", (0,0,255), pygame.K_d)
        ]

        self.current = random.choice(self.colors)

        self.font = game.myFont

    def update(self, dt):

        self.timer -= dt

        if self.timer <= 0:

            print("Final score:", self.score)

            moneyEarned = max(0, self.score * 5)

            self.game.money += moneyEarned
            self.game.packagesShipped += max(0, self.score)

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


    def handleEvent(self, event):

        if event.type == pygame.KEYDOWN:

            expectedKey = self.current[2]

            if event.key == expectedKey:
                self.score += 1
            else:
                self.score -= 1

            self.current = random.choice(self.colors)

    def draw(self, surface):

        surface.fill((20,20,20))

        # draw package box
        pygame.draw.rect(surface, self.current[1], (150, 60, 100, 80))

        # instructions
        text = self.font.render(
            "A=Red S=Green D=Blue", True, (255,255,255))
        surface.blit(text, (110, 20))

        # score
        scoreText = self.font.render(
            f"Score: {self.score}", True, (255,255,255))
        surface.blit(scoreText, (10, 10))

        # timer
        timerText = self.font.render(
            f"Time: {int(self.timer)}", True, (255,255,255))
        surface.blit(timerText, (300, 10))
