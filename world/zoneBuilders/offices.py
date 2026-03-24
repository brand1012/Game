def buildOfficeZone(game, officeZone):
    officeX, officeY = officeZone.position
    brickTileSize = 20
    wallHeight = 40

    for x in range(0, officeZone.size[0], brickTileSize):
        for y in range(0, wallHeight, brickTileSize):
            game.addWorldProp(
                position=(officeX + x, officeY + y),
                fileName="brick.png",
                size=(brickTileSize, brickTileSize),
                collisionSize=(brickTileSize, brickTileSize),
            )

    def addOfficeProp(position, fileName, size, collisionSize=None, collisionOffset=(0, 0)):
        return game.addWorldProp(
            position=(officeX + position[0], officeY + position[1]),
            fileName=f"Office-Furniture-Pixel-Art/{fileName}",
            size=size,
            collisionSize=collisionSize,
            collisionOffset=collisionOffset,
        )

    addOfficeProp((60, 8), "Wall-Clock.png", (18, 18))
    addOfficeProp((196, 8), "Wall-Note.png", (18, 18))
    addOfficeProp((336, 8), "Wall-Graph.png", (18, 18))
    addOfficeProp((496, 8), "Wall-Shelf.png", (18, 18))

    rowBottom = 54
    addOfficeProp((18, rowBottom - 42), "Wide-Filing-Cabinet.png", (42, 42), collisionSize=(34, 14), collisionOffset=(4, 26))
    game.upgradeDesks.append(addOfficeProp((88, rowBottom - 40), "Desk.png", (40, 40), collisionSize=(34, 14), collisionOffset=(3, 25)))
    game.upgradeDesks.append(addOfficeProp((208, rowBottom - 40), "Desk.png", (40, 40), collisionSize=(34, 14), collisionOffset=(3, 25)))
    game.upgradeDesks.append(addOfficeProp((328, rowBottom - 40), "Desk.png", (40, 40), collisionSize=(34, 14), collisionOffset=(3, 25)))
    addOfficeProp((392, rowBottom - 40), "Printer-Furniture.png", (40, 40), collisionSize=(34, 14), collisionOffset=(3, 25))
    addOfficeProp((468, rowBottom - 42), "Vending-Machine.png", (42, 42), collisionSize=(24, 16), collisionOffset=(9, 24))
    addOfficeProp((474, rowBottom - 24), "Water-Dispenser.png", (24, 24), collisionSize=(14, 10), collisionOffset=(5, 14))
    addOfficeProp((516, rowBottom - 42), "Wide-Filing-Cabinet.png", (42, 42), collisionSize=(34, 14), collisionOffset=(4, 26))
    game.upgradeDesks.append(addOfficeProp((560, rowBottom - 40), "Desk.png", (40, 40), collisionSize=(34, 14), collisionOffset=(3, 25)))
