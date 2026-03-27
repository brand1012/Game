def drawResults(game, surface):
    surface.fill((30, 30, 30))

    title = game.myFont.render("SHIFT COMPLETE", True, (255, 255, 255))
    surface.blit(title, (140, 30))

    scoreText = game.myFont.render(f"Score: {game.resultsData['score']}", True, (255, 255, 255))
    surface.blit(scoreText, (140, 70))

    moneyText = game.myFont.render(f"Money earned: ${game.resultsData['money']}", True, (255, 255, 255))
    surface.blit(moneyText, (140, 100))

    highText = game.myFont.render(f"High Score: {game.resultsData['highScore']}", True, (255, 255, 255))
    surface.blit(highText, (140, 130))

    if game.resultsData.get("isNewHigh"):
        newHighText = game.infoFont.render("NEW HIGH SCORE!", True, (255, 220, 110))
        surface.blit(newHighText, (142, 154))

    continueText = game.myFont.render("Press SPACE to continue", True, (200, 200, 200))
    surface.blit(continueText, (120, 174))
