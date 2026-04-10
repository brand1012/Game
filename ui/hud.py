import pygame

import minigames.registry as activityRegistry
import systems.campaign as campaign


COMPACT_QUOTA_LABELS = {
    "sorting": "Sort",
    "semiUnloading": "Dock",
    "conveyorRouting": "Route",
    "spillCleanup": "Spill",
    "urgentUnload": "Urgent",
    "manifestMismatch": "Manifest",
    "conveyorOverflow": "Overflow",
}


def getCompactQuotaLabel(quotaKey):
    label = activityRegistry.getQuotaLabel(quotaKey)
    return COMPACT_QUOTA_LABELS.get(quotaKey, label.split()[0])


def drawStoryPanel(game, surface):
    panelRect = pygame.Rect(214, 5, 181, 52)
    storyFont = pygame.font.SysFont("Arial", 9, bold=True)
    dividerX = panelRect.x + 84
    leftX = panelRect.x + 6
    rightX = dividerX + 6
    lineY = panelRect.y + 7
    lineGap = 12

    pygame.draw.rect(surface, (236, 236, 236), panelRect)
    pygame.draw.rect(surface, (0, 0, 0), panelRect, 2)
    pygame.draw.line(
        surface,
        (176, 176, 176),
        (dividerX, panelRect.y + 5),
        (dividerX, panelRect.bottom - 5),
    )

    phase = campaign.getDayPhase(game.campaign.dayProgress)
    quotaPercent = int(campaign.getQuotaCompletion(game.campaign) * 100)
    timePercent = int(game.campaign.dayProgress * 100)

    leftLines = [
        "Day {0} {1}".format(game.campaign.dayNumber, phase),
        "Quota {0}%".format(quotaPercent),
        "Time {0}%".format(timePercent),
    ]
    for index, line in enumerate(leftLines):
        label = storyFont.render(line, True, (0, 0, 0))
        surface.blit(label, (leftX, lineY + index * lineGap))

    quotaItems = list(campaign.iterActivityQuotaItems(game.campaign.dailyQuota))
    pendingLines = []
    for quotaKey, required in quotaItems:
        done = game.campaign.completedJobs.get(quotaKey, 0)
        if done < required:
            pendingLines.append(
                "{0} {1}/{2}".format(getCompactQuotaLabel(quotaKey), done, required)
            )

    if not pendingLines:
        pendingLines.append("Runs done")

    for index, line in enumerate(pendingLines[:3]):
        label = storyFont.render(line, True, (0, 0, 0))
        surface.blit(label, (rightX, lineY + index * lineGap))


def drawUI(game, surface):
    statsPanelRect = pygame.Rect(5, 5, 126, 34)
    controlsPanelRect = pygame.Rect(136, 5, 72, 34)
    controlFont = pygame.font.SysFont("Arial", 9, bold=True)

    pygame.draw.rect(surface, (236, 236, 236), statsPanelRect)
    pygame.draw.rect(surface, (0, 0, 0), statsPanelRect, 2)
    pygame.draw.rect(surface, (236, 236, 236), controlsPanelRect)
    pygame.draw.rect(surface, (0, 0, 0), controlsPanelRect, 2)

    moneyText = game.uiFont.render("Money: ${0}".format(int(game.money)), True, (0, 0, 0))
    surface.blit(moneyText, (10, 8))

    packageText = game.uiFont.render(
        "Packages: {0}".format(int(game.packagesShipped)),
        True,
        (0, 0, 0),
    )
    surface.blit(packageText, (10, 21))

    infoHint = controlFont.render("I Info", True, (0, 0, 0))
    stockHint = controlFont.render("S Stock", True, (0, 0, 0))
    surface.blit(infoHint, (141, 8))
    surface.blit(stockHint, (141, 17))

    if game.mode == "story" and game.campaign:
        briefingHint = controlFont.render("B Brief", True, (0, 0, 0))
        surface.blit(briefingHint, (141, 26))
        drawStoryPanel(game, surface)

    if game.showInteractPrompt and game.interactPromptText:
        prompt = game.uiFont.render(game.interactPromptText, True, (0, 0, 0))
        x = (game.RESOLUTION[0] - prompt.get_width()) // 2
        y = game.RESOLUTION[1] - 30
        surface.blit(prompt, (x, y))
