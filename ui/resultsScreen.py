def drawResults(game, surface):
    surface.fill((30, 30, 30))

    resultType = game.resultsData.get("type")
    titleText = game.resultsData.get("resultLabel")
    if not titleText:
        titleText = "DOCK SHIFT COMPLETE" if resultType == "semiUnloading" else "SHIFT COMPLETE"
    title = game.myFont.render(titleText, True, (255, 255, 255))
    surface.blit(title, ((surface.get_width() - title.get_width()) // 2, 30))

    scoreText = game.myFont.render(f"Score: {game.resultsData['score']}", True, (255, 255, 255))
    surface.blit(scoreText, (140, 70))

    moneyText = game.myFont.render(f"Money earned: ${game.resultsData['money']}", True, (255, 255, 255))
    surface.blit(moneyText, (140, 100))

    highText = game.myFont.render(f"High Score: {game.resultsData['highScore']}", True, (255, 255, 255))
    if game.resultsData.get("highScore"):
        surface.blit(highText, (140, 130))

    packages = game.resultsData.get("packages")
    packageText = game.infoFont.render(f"Handled: {packages}", True, (220, 220, 220))
    surface.blit(packageText, (142, 148))

    if game.resultsData.get("isNewHigh"):
        newHighText = game.infoFont.render("NEW HIGH SCORE!", True, (255, 220, 110))
        surface.blit(newHighText, (142, 162))

    continueText = game.myFont.render("Press SPACE or ENTER", True, (200, 200, 200))
    surface.blit(continueText, (106, 174))
