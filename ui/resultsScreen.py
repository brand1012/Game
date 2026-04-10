import ui.textLayout as textLayout


def drawResults(game, surface):
    surface.fill((30, 30, 30))

    resultType = game.resultsData.get("type")
    titleText = game.resultsData.get("resultLabel")
    if not titleText:
        titleText = "DOCK SHIFT COMPLETE" if resultType == "semiUnloading" else "SHIFT COMPLETE"
    title = game.myFont.render(titleText, True, (255, 255, 255))
    surface.blit(title, ((surface.get_width() - title.get_width()) // 2, 30))

    success = bool(game.resultsData.get("success"))
    outcomeText = game.resultsData.get("outcomeLabel", "Run complete" if success else "Run failed")
    outcomeColor = (122, 240, 152) if success else (255, 124, 124)
    outcomeLabel = game.infoFont.render(outcomeText, True, outcomeColor)
    surface.blit(outcomeLabel, ((surface.get_width() - outcomeLabel.get_width()) // 2, 52))

    detailLines = [
        "Score: {0}".format(game.resultsData["score"]),
    ]

    moneyAmount = int(game.resultsData.get("money", 0))
    if moneyAmount >= 0:
        detailLines.append("Money change: ${0}".format(moneyAmount))
    else:
        detailLines.append("Money change: -${0}".format(abs(moneyAmount)))

    moneyPenalty = int(game.resultsData.get("moneyPenalty", 0))
    if moneyPenalty > 0:
        detailLines.append("Missed freight penalty: -${0}".format(moneyPenalty))

    packages = game.resultsData.get("packages")
    detailLines.append("Handled: {0}".format(packages))
    detailLines.append("Quota credit: {0}".format("Yes" if game.resultsData.get("countsForQuota", True) else "No"))

    highText = game.infoFont.render(f"High Score: {game.resultsData['highScore']}", True, (255, 255, 255))
    if game.resultsData.get("highScore"):
        detailLines.append("High Score: {0}".format(game.resultsData["highScore"]))

    if game.resultsData.get("isNewHigh"):
        detailLines.append("NEW HIGH SCORE!")

    for index, line in enumerate(detailLines):
        text = game.infoFont.render(line, True, (220, 220, 220))
        surface.blit(text, (106, 72 + index * 13))

    summaryText = game.resultsData.get("summaryText", "")
    if summaryText:
        textLayout.drawWrappedText(
            surface,
            game.infoFont,
            summaryText,
            (214, 214, 214),
            (30, 154),
            340,
            lineHeight=12,
            maxLines=2,
        )

    continueText = game.myFont.render("Press SPACE or ENTER", True, (200, 200, 200))
    surface.blit(continueText, (106, 174))
