import pygame

import ui.textLayout as textLayout


def drawDialogueScreen(game, surface):
    data = game.dialogueData or {}
    surface.fill((22, 24, 30))

    title = game.myFont.render(data.get("title", "SHIFT NOTE"), True, (255, 255, 255))
    surface.blit(title, (18, 16))

    currentY = 36
    speaker = data.get("speaker", "")
    if speaker:
        speakerText = game.infoFont.render(speaker.upper(), True, (255, 210, 118))
        surface.blit(speakerText, (18, currentY))
        currentY += 16

    summary = data.get("summary")
    if summary:
        currentY = textLayout.drawWrappedText(
            surface,
            game.infoFont,
            summary,
            (212, 212, 212),
            (18, currentY),
            364,
            lineHeight=13,
            maxLines=2,
        )
        currentY += 4

    lines = data.get("lines", [])
    cardTop = max(72, currentY)
    card = pygame.Rect(16, cardTop, 368, 94)
    pygame.draw.rect(surface, (36, 39, 48), card, border_radius=12)
    pygame.draw.rect(surface, (92, 102, 118), card, 2, border_radius=12)

    textY = card.y + 10
    lineHeight = 13
    maxCardLines = max(1, (card.height - 18) // lineHeight)
    usedLines = 0
    for line in lines:
        remainingLines = maxCardLines - usedLines
        if remainingLines <= 0:
            break

        wrappedLines = textLayout.wrapText(game.infoFont, line, 340)
        wrappedLines = textLayout.trimWrappedLines(game.infoFont, wrappedLines, 340, remainingLines)
        for wrappedLine in wrappedLines:
            text = game.infoFont.render(wrappedLine, True, (240, 240, 240))
            surface.blit(text, (28, textY))
            textY += lineHeight
        usedLines += len(wrappedLines)
        if usedLines < maxCardLines:
            textY += 1

    prompt = game.infoFont.render(data.get("prompt", "Press Enter to continue"), True, (210, 210, 210))
    surface.blit(prompt, (surface.get_width() - prompt.get_width() - 14, 178))
