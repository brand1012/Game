import pygame

import minigames.registry as activityRegistry
import systems.campaign as campaign
import systems.storyContent as storyContent


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

    summary = game.infoFont.render(beat["summary"], True, (220, 220, 220))
    surface.blit(summary, (18, 50))

    quotaBox = pygame.Rect(18, 72, 170, 84)
    noteBox = pygame.Rect(204, 72, 178, 84)
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
        surface.blit(text, (30, 100 + index * 16))

    noteTitle = game.infoFont.render("FLOOR TALK", True, (255, 255, 255))
    surface.blit(noteTitle, (216, 82))
    for index, line in enumerate(beat["dialogue"][:3]):
        text = game.infoFont.render(line, True, (230, 230, 230))
        surface.blit(text, (216, 100 + index * 16))

    footer = game.infoFont.render(
        "Enter start shift  B back to warehouse  S company pressure",
        True,
        (200, 200, 200),
    )
    surface.blit(footer, (36, 178))
