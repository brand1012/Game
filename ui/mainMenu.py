import pygame


def drawMainMenu(game, surface):
    surface.fill((16, 20, 27))

    title = game.myFont.render("WAREHOUSE SHIFT", True, (255, 255, 255))
    subtitle = game.infoFont.render("Practice warehouse hub", True, (198, 208, 220))
    surface.blit(title, (125, 18))
    surface.blit(subtitle, (132, 38))

    card = pygame.Rect(52, 58, 296, 86)
    pygame.draw.rect(surface, (28, 35, 45), card, border_radius=12)
    pygame.draw.rect(surface, (86, 101, 120), card, 2, border_radius=12)

    options = [
        "Practice Shift",
        "Quit",
    ]

    for index, option in enumerate(options):
        y = 72 + index * 22
        selected = index == game.mainMenuIndex
        color = (255, 220, 124) if selected else (236, 236, 236)
        prefix = "> " if selected else "  "
        label = game.myFont.render(prefix + option, True, color)
        surface.blit(label, (74, y))

    footer = game.infoFont.render(
        "Up/Down choose  Enter confirm  ESC quits",
        True,
        (190, 196, 205),
    )
    surface.blit(footer, (84, 176))
