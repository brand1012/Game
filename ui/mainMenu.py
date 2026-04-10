import pygame


def drawMainMenu(game, surface):
    surface.fill((16, 20, 27))

    title = game.myFont.render("SHIFT MANAGER", True, (255, 255, 255))
    subtitle = game.infoFont.render("Story campaign and practice warehouse shift", True, (198, 208, 220))
    surface.blit(title, (130, 16))
    surface.blit(subtitle, (58, 36))

    card = pygame.Rect(44, 56, 312, 104)
    pygame.draw.rect(surface, (28, 35, 45), card, border_radius=12)
    pygame.draw.rect(surface, (86, 101, 120), card, 2, border_radius=12)

    options = game.getMainMenuOptions()
    for index, (labelText, _) in enumerate(options):
        y = 68 + index * 20
        selected = index == game.mainMenuIndex
        color = (255, 220, 124) if selected else (236, 236, 236)
        prefix = "> " if selected else "  "
        label = game.myFont.render(prefix + labelText, True, color)
        surface.blit(label, (62, y))

    footer = game.infoFont.render(
        "Up/Down choose  Enter confirm  ESC quits",
        True,
        (190, 196, 205),
    )
    surface.blit(footer, (84, 176))


def drawContinueMenu(game, surface):
    surface.fill((16, 20, 27))

    title = game.myFont.render("CONTINUE STORY", True, (255, 255, 255))
    subtitle = game.infoFont.render("Choose which day to resume", True, (198, 208, 220))
    surface.blit(title, (113, 16))
    surface.blit(subtitle, (101, 36))

    card = pygame.Rect(32, 56, 336, 112)
    pygame.draw.rect(surface, (28, 35, 45), card, border_radius=12)
    pygame.draw.rect(surface, (86, 101, 120), card, 2, border_radius=12)

    options = game.continueOptions
    maxVisible = 6
    startIndex = 0
    if len(options) > maxVisible:
        startIndex = max(0, game.continueMenuIndex - (maxVisible // 2))
        startIndex = min(startIndex, len(options) - maxVisible)

    visibleOptions = options[startIndex:startIndex + maxVisible]

    for offset, option in enumerate(visibleOptions):
        optionIndex = startIndex + offset
        y = 66 + offset * 16
        selected = optionIndex == game.continueMenuIndex
        color = (255, 220, 124) if selected else (236, 236, 236)
        prefix = "> " if selected else "  "
        labelText = "{0}Day {1}: {2}".format(prefix, option["dayNumber"], option["title"])
        label = game.infoFont.render(labelText, True, color)
        surface.blit(label, (44, y))

        detail = game.infoFont.render(option["detail"], True, (170, 184, 200))
        surface.blit(detail, (308 - detail.get_width() // 2, y))

    footer = game.infoFont.render(
        "Up/Down choose  Enter load  Backspace back",
        True,
        (190, 196, 205),
    )
    surface.blit(footer, (60, 176))
