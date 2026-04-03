import pygame


def drawDialogueScreen(game, surface):
    data = game.dialogueData or {}
    surface.fill((22, 24, 30))

    title = game.myFont.render(data.get("title", "SHIFT NOTE"), True, (255, 255, 255))
    surface.blit(title, (18, 16))

    speaker = data.get("speaker", "")
    if speaker:
        speakerText = game.infoFont.render(speaker.upper(), True, (255, 210, 118))
        surface.blit(speakerText, (18, 36))

    summary = data.get("summary")
    if summary:
        summaryText = game.infoFont.render(summary, True, (212, 212, 212))
        surface.blit(summaryText, (18, 54))

    lines = data.get("lines", [])
    card = pygame.Rect(16, 72, 368, 92)
    pygame.draw.rect(surface, (36, 39, 48), card, border_radius=12)
    pygame.draw.rect(surface, (92, 102, 118), card, 2, border_radius=12)

    for index, line in enumerate(lines[:5]):
        text = game.infoFont.render(line, True, (240, 240, 240))
        surface.blit(text, (28, 84 + index * 16))

    prompt = game.infoFont.render(data.get("prompt", "Press Enter to continue"), True, (210, 210, 210))
    surface.blit(prompt, (surface.get_width() - prompt.get_width() - 14, 178))
