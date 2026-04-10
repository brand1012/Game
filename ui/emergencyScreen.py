import pygame

import minigames.registry as activityRegistry
import ui.textLayout as textLayout


def drawEmergencyScreen(game, surface):
    emergency = game.currentEmergencyDef or {}
    surface.fill((38, 20, 20))

    title = game.myFont.render(emergency.get("title", "EMERGENCY"), True, (255, 255, 255))
    surface.blit(title, (90, 16))

    speaker = emergency.get("speaker", "")
    currentY = 38
    if speaker:
        speakerText = game.infoFont.render(speaker.upper(), True, (255, 176, 132))
        surface.blit(speakerText, (18, currentY))
        currentY += 16

    summary = emergency.get("summary", "")
    currentY = textLayout.drawWrappedText(
        surface,
        game.infoFont,
        summary,
        (236, 228, 228),
        (18, currentY),
        364,
        lineHeight=13,
        maxLines=2,
    )
    currentY += 4

    box = pygame.Rect(18, max(82, currentY), 364, 70)
    pygame.draw.rect(surface, (58, 28, 28), box, border_radius=12)
    pygame.draw.rect(surface, (122, 72, 72), box, 2, border_radius=12)

    lines = [
        "Emergency minigame: {0}".format(activityRegistry.getQuotaLabel(emergency.get("activityId", ""))),
        "Success keeps pressure down and protects safety reputation.",
        "Failure adds stress and tomorrow gets sharper.",
    ]
    textY = box.y + 10
    lineHeight = 13
    maxLines = max(1, (box.height - 18) // lineHeight)
    usedLines = 0
    for line in lines:
        remainingLines = maxLines - usedLines
        if remainingLines <= 0:
            break

        wrappedLines = textLayout.wrapText(game.infoFont, line, 340)
        wrappedLines = textLayout.trimWrappedLines(game.infoFont, wrappedLines, 340, remainingLines)
        for wrappedLine in wrappedLines:
            text = game.infoFont.render(wrappedLine, True, (245, 236, 236))
            surface.blit(text, (30, textY))
            textY += lineHeight
        usedLines += len(wrappedLines)

    footer = game.infoFont.render("Press Enter to respond", True, (240, 220, 220))
    surface.blit(footer, (126, 178))
