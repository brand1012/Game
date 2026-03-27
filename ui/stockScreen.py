import pygame


def drawStockGraph(game, surface):
    surface.fill((17, 22, 28))

    title = game.myFont.render("STOCK TRACKER", True, (255, 255, 255))
    surface.blit(title, (12, 10))

    currentValue = game.stockHistory[-1] if game.stockHistory else game.stockValue
    currentLabel = game.infoFont.render(
        f"Current value: ${currentValue:.2f}",
        True,
        (210, 230, 216),
    )
    surface.blit(
        currentLabel,
        (surface.get_width() - currentLabel.get_width() - 12, 14),
    )

    rect = pygame.Rect(50, 48, 300, 102)

    bg = (24, 30, 38)
    border = (214, 220, 226)
    grid = (60, 68, 78)
    fillColor = (18, 110, 70)
    lineColor = (74, 238, 153)
    textColor = (236, 236, 236)

    font = pygame.font.SysFont(None, 16)

    pygame.draw.rect(surface, bg, rect)
    pygame.draw.rect(surface, border, rect, 2)

    if len(game.stockHistory) < 2:
        closeHint = game.infoFont.render("Press S to close", True, (200, 200, 200))
        surface.blit(
            closeHint,
            (surface.get_width() - closeHint.get_width() - 12, 176),
        )
        return

    pad = 10
    graphRect = rect.inflate(-pad * 2, -pad * 2)

    minVal = min(game.stockHistory)
    maxVal = max(game.stockHistory)
    margin = (maxVal - minVal) * 0.1
    if margin == 0:
        margin = 1

    minVal -= margin
    maxVal += margin
    rangeVal = maxVal - minVal

    for index in range(5):
        t = index / 4
        y = graphRect.bottom - t * graphRect.height
        pygame.draw.line(surface, grid, (graphRect.left, y), (graphRect.right, y))
        value = minVal + t * rangeVal
        label = font.render(f"{value:.1f}", True, textColor)
        surface.blit(label, (rect.right + 5, y - 8))

    points = []
    for index, value in enumerate(game.stockHistory):
        t = index / (len(game.stockHistory) - 1)
        x = graphRect.left + t * graphRect.width
        normalized = (value - minVal) / rangeVal
        y = graphRect.bottom - normalized * graphRect.height
        points.append((x, y))

    fillPoints = points.copy()
    fillPoints.append((points[-1][0], graphRect.bottom))
    fillPoints.append((points[0][0], graphRect.bottom))

    pygame.draw.polygon(surface, fillColor, fillPoints)
    pygame.draw.lines(surface, lineColor, False, points, 2)
    pygame.draw.line(
        surface,
        border,
        (graphRect.left, graphRect.bottom),
        (graphRect.right, graphRect.bottom),
        2,
    )
    pygame.draw.line(
        surface,
        border,
        (graphRect.left, graphRect.top),
        (graphRect.left, graphRect.bottom),
        2,
    )

    latest = game.stockHistory[-1]
    label = font.render(f"Latest: ${latest:.2f}", True, (255, 255, 255))
    surface.blit(label, (rect.x, rect.y - 18))

    footer = game.infoFont.render(
        "Track your warehouse performance over time.",
        True,
        (190, 190, 190),
    )
    surface.blit(footer, (12, 176))
    closeHint = game.infoFont.render("Press S to close", True, (200, 200, 200))
    surface.blit(
        closeHint,
        (surface.get_width() - closeHint.get_width() - 12, 176),
    )
