import pygame

import minigames.registry as activityRegistry


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

    emergencyOutcome = summary.get("emergencyOutcome")
    if emergencyOutcome:
        lines.append("Emergency: " + emergencyOutcome)

    for index, line in enumerate(lines):
        text = game.infoFont.render(line, True, (230, 230, 230))
        surface.blit(text, (104, 78 + index * 18))

    footer = game.infoFont.render("Press Enter for company pressure", True, (205, 205, 205))
    surface.blit(footer, (124, 176))
