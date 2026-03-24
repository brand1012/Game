def buildSortingZone(game, zone):
    palletSize = (22, 26)
    files = [
        "freight/Freight-5.png",
        "freight/Freight-6.png",
        "freight/Freight-7.png",
        "freight/Freight-8.png",
        "freight/Freight-9.png",
        "freight/Freight-10.png",
    ]

    sidePadding = 8
    columnGap = 0
    rowGap = 0
    topMargin = 8
    bottomMargin = 8
    columns = max(1, int((zone.size[0] - sidePadding * 2 + columnGap) / (palletSize[0] + columnGap)))
    totalWidth = columns * palletSize[0] + (columns - 1) * columnGap
    startX = zone.position[0] + (zone.size[0] - totalWidth) / 2
    walkwayColumns = 2
    aisleStart = max(1, (columns // 2) - (walkwayColumns // 2))
    aisleColumns = set(range(aisleStart, aisleStart + walkwayColumns))

    topPairStart = zone.position[1] + topMargin
    bottomPairStart = zone.position[1] + zone.size[1] - bottomMargin - (palletSize[1] * 2) - rowGap

    yPositions = [
        topPairStart,
        topPairStart + palletSize[1] + rowGap,
        bottomPairStart,
        bottomPairStart + palletSize[1] + rowGap,
    ]

    fileIndex = 0
    for y in yPositions:
        for col in range(columns):
            if col in aisleColumns:
                continue
            x = startX + col * (palletSize[0] + columnGap)
            fileName = files[fileIndex % len(files)]
            fileIndex += 1
            game.addWorldProp(
                position=(x, y),
                fileName=fileName,
                size=palletSize,
                collisionSize=palletSize,
            )
            game.sortingPallets.append(game.worldProps[-1])
