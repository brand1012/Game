def wrapText(font, text, maxWidth):
    if not text:
        return []

    wrappedLines = []
    paragraphs = str(text).split("\n")
    for paragraph in paragraphs:
        words = paragraph.split()
        if not words:
            wrappedLines.append("")
            continue

        currentLine = words[0]
        for word in words[1:]:
            candidate = currentLine + " " + word
            if font.size(candidate)[0] <= maxWidth:
                currentLine = candidate
            else:
                wrappedLines.append(currentLine)
                currentLine = word

        wrappedLines.append(currentLine)

    return wrappedLines


def fitLineWithEllipsis(font, text, maxWidth):
    if font.size(text)[0] <= maxWidth:
        return text

    ellipsis = "..."
    if font.size(ellipsis)[0] > maxWidth:
        return ""

    trimmed = text
    while trimmed and font.size(trimmed + ellipsis)[0] > maxWidth:
        trimmed = trimmed[:-1]

    return trimmed.rstrip() + ellipsis


def trimWrappedLines(font, lines, maxWidth, maxLines):
    if maxLines is None or len(lines) <= maxLines:
        return list(lines)

    trimmed = list(lines[:maxLines])
    trimmed[-1] = fitLineWithEllipsis(font, trimmed[-1], maxWidth)
    return trimmed


def drawWrappedText(surface, font, text, color, position, maxWidth, lineHeight=None, maxLines=None):
    wrappedLines = wrapText(font, text, maxWidth)
    wrappedLines = trimWrappedLines(font, wrappedLines, maxWidth, maxLines)

    if lineHeight is None:
        lineHeight = font.get_linesize()

    x, y = position
    currentY = y
    for line in wrappedLines:
        if line:
            textSurface = font.render(line, True, color)
            surface.blit(textSurface, (x, currentY))
        currentY += lineHeight

    return currentY
