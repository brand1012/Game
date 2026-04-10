import pygame

import minigames.registry as activityRegistry
import systems.campaign as campaign
import systems.storyContent as storyContent
import ui.textLayout as textLayout


def drawBriefingScreen(game, surface):
    beat = storyContent.get_day_beat(game.campaign.dayNumber)
    surface.fill((24, 30, 38))

    title = game.myFont.render(
        "DAY {0}: {1}".format(game.campaign.dayNumber, beat["title"]),
        True,
        (255, 255, 255),
    )
    surface.blit(title, (18, 14))

    speaker = game.infoFont.render(
        "{0} - {1}".format(beat["speaker"], campaign.getDayPhase(game.campaign.dayProgress)),
        True,
        (255, 208, 120),
    )
    surface.blit(speaker, (18, 32))

    textLayout.drawWrappedText(
        surface,
        game.infoFont,
        beat["summary"],
        (220, 220, 220),
        (18, 48),
        364,
        lineHeight=13,
        maxLines=2,
    )

    quotaBox = pygame.Rect(18, 76, 170, 86)
    noteBox = pygame.Rect(204, 76, 178, 86)
    pygame.draw.rect(surface, (34, 40, 48), quotaBox, border_radius=12)
    pygame.draw.rect(surface, (34, 40, 48), noteBox, border_radius=12)
    pygame.draw.rect(surface, (98, 112, 128), quotaBox, 2, border_radius=12)
    pygame.draw.rect(surface, (98, 112, 128), noteBox, 2, border_radius=12)

    quotaTitle = game.infoFont.render("SHIFT TARGETS", True, (255, 255, 255))
    surface.blit(quotaTitle, (30, 82))
    quotas = [
        "{0}: {1}".format(activityRegistry.getQuotaLabel(quotaKey), required)
        for quotaKey, required in campaign.iterActivityQuotaItems(beat["quota"])
    ]
    quotas.append("Package target: {0}".format(beat["quota"]["packageTarget"]))
    for index, line in enumerate(quotas):
        text = game.infoFont.render(line, True, (230, 230, 230))
        surface.blit(text, (30, 98 + index * 15))

    noteTitle = game.infoFont.render("FLOOR TALK", True, (255, 255, 255))
    surface.blit(noteTitle, (216, 86))

    textY = 102
    lineHeight = 13
    maxNoteLines = 4
    usedLines = 0
    for line in beat["dialogue"]:
        remainingLines = maxNoteLines - usedLines
        if remainingLines <= 0:
            break

        wrappedLines = textLayout.wrapText(game.infoFont, line, 154)
        wrappedLines = textLayout.trimWrappedLines(game.infoFont, wrappedLines, 154, remainingLines)
        for wrappedLine in wrappedLines:
            text = game.infoFont.render(wrappedLine, True, (230, 230, 230))
            surface.blit(text, (216, textY))
            textY += lineHeight
        usedLines += len(wrappedLines)
        if usedLines < maxNoteLines:
            textY += 1

    footer = game.infoFont.render(
        "Enter start shift  B back to warehouse  S company pressure",
        True,
        (200, 200, 200),
    )
    surface.blit(footer, (36, 178))
