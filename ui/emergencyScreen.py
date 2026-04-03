import pygame

import minigames.registry as activityRegistry


def drawEmergencyScreen(game, surface):
    emergency = game.currentEmergencyDef or {}
    surface.fill((38, 20, 20))

    title = game.myFont.render(emergency.get("title", "EMERGENCY"), True, (255, 255, 255))
    surface.blit(title, (90, 16))

    speaker = emergency.get("speaker", "")
    if speaker:
        speakerText = game.infoFont.render(speaker.upper(), True, (255, 176, 132))
        surface.blit(speakerText, (18, 38))

    summary = emergency.get("summary", "")
    summaryText = game.infoFont.render(summary, True, (236, 228, 228))
    surface.blit(summaryText, (18, 56))

    box = pygame.Rect(18, 82, 364, 64)
    pygame.draw.rect(surface, (58, 28, 28), box, border_radius=12)
    pygame.draw.rect(surface, (122, 72, 72), box, 2, border_radius=12)

    lines = [
        "Emergency minigame: {0}".format(activityRegistry.getQuotaLabel(emergency.get("activityId", ""))),
        "Success keeps pressure down and protects safety reputation.",
        "Failure adds stress and tomorrow gets sharper.",
    ]
    for index, line in enumerate(lines):
        text = game.infoFont.render(line, True, (245, 236, 236))
        surface.blit(text, (30, 96 + index * 16))

    footer = game.infoFont.render("Press Enter to respond", True, (240, 220, 220))
    surface.blit(footer, (126, 178))
