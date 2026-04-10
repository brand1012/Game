import pygame

import minigames.registry as activityRegistry
import ui.textLayout as textLayout


def drawDaySummary(game, surface):
    summary = game.daySummaryData or {}
    surface.fill((25, 27, 33))

    title = game.myFont.render(
        "DAY {0} WRAP-UP".format(summary.get("dayNumber", game.campaign.dayNumber if game.campaign else 0)),
        True,
        (255, 255, 255),
    )
    surface.blit(title, (120, 18))

    quotaText = "Quota met" if summary.get("quotaMet") else "Quota missed"
    quotaColor = (122, 240, 152) if summary.get("quotaMet") else (255, 124, 124)
    quotaLabel = game.myFont.render(quotaText, True, quotaColor)
    surface.blit(quotaLabel, (146, 42))

    card = pygame.Rect(24, 70, 352, 90)
    pygame.draw.rect(surface, (34, 36, 44), card, border_radius=12)
    pygame.draw.rect(surface, (86, 94, 112), card, 2, border_radius=12)

    lines = [
        "{0}: {1}/{2}".format(
            activityRegistry.getQuotaLabel(item["key"]),
            item["done"],
            item["required"],
        )
        for item in summary.get("quotaProgress", [])
    ]
    lines.append("Business income: ${0}".format(int(summary.get("payToday", 0))))
    lines.append("Take-home pay: ${0}".format(int(summary.get("takeHomePay", 0))))
    if summary.get("quotaStressPenalty", 0):
        lines.append("Missed quota stress: +{0}".format(int(summary.get("quotaStressPenalty", 0))))

    emergencyOutcome = summary.get("emergencyOutcome")
    if emergencyOutcome:
        lines.append("Emergency: " + emergencyOutcome)

    textY = 80
    lineHeight = 13
    maxLines = max(1, (card.height - 16) // lineHeight)
    usedLines = 0
    for line in lines:
        remainingLines = maxLines - usedLines
        if remainingLines <= 0:
            break

        wrappedLines = textLayout.wrapText(game.infoFont, line, 324)
        wrappedLines = textLayout.trimWrappedLines(game.infoFont, wrappedLines, 324, remainingLines)
        for wrappedLine in wrappedLines:
            text = game.infoFont.render(wrappedLine, True, (230, 230, 230))
            surface.blit(text, (38, textY))
            textY += lineHeight
        usedLines += len(wrappedLines)

    footer = game.infoFont.render("Press Enter for company pressure", True, (205, 205, 205))
    surface.blit(footer, (124, 176))
