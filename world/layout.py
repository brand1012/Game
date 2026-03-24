from world.zones import Zone

def createZones():
    return [
        Zone((200, 25), (600, 100), "Semi Unloading Dock", (180, 220, 255)),
        Zone((200, 150), (600, 150), "Sorting Area", (180, 255, 180)),
        Zone((350, 325), (300, 200), "Storage", (255, 220, 180)),
        Zone((200, 325), (125, 200), "Van Prep", (255, 180, 255)),
        Zone((675, 325), (125, 200), "Van Prep", (255, 180, 255)),
        Zone((200, 550), (600, 100), "Offices", (220, 220, 220)),
        Zone((50, 25), (100, 625), "Vehicle Lane", (32, 32, 36), showLabel=False),
        Zone((850, 25), (100, 625), "Vehicle Lane", (32, 32, 36), showLabel=False),
    ]
