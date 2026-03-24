import pygame


def drawStockGraph(game, surface):
    rect = pygame.Rect(50, 50, 300, 120)

    bg = (25, 25, 25)
    border = (200, 200, 200)
    grid = (60, 60, 60)
    lineColor = (0, 220, 120)
    textColor = (0, 0, 0)

    font = pygame.font.SysFont(None, 16)

    pygame.draw.rect(surface, bg, rect)
    pygame.draw.rect(surface, border, rect, 2)

    if len(game.stockHistory) < 2:
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

    pygame.draw.polygon(surface, (0, 220, 120), fillPoints)
    pygame.draw.lines(surface, lineColor, False, points, 2)
    pygame.draw.line(surface, border, (graphRect.left, graphRect.bottom), (graphRect.right, graphRect.bottom), 2)
    pygame.draw.line(surface, border, (graphRect.left, graphRect.top), (graphRect.left, graphRect.bottom), 2)

    latest = game.stockHistory[-1]
    label = font.render(f"${latest:.2f}", True, (255, 255, 255))
    surface.blit(label, (rect.x, rect.y - 18))
