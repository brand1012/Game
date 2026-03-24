from systems.traffic import VehicleWave

def buildVehicleTraffic(game, leftLane, rightLane):
    def addLaneColumnTraffic(lane, specs):
        laneVehicles = []
        laneXOffset = -3 if lane.position[0] > game.WORLD_SIZE[0] / 2 else 0
        leftColumnX = lane.position[0] - 10 + laneXOffset
        rightColumnX = lane.position[0] + 46 + laneXOffset

        for spec in specs:
            columnX = leftColumnX if spec["column"] == "left" else rightColumnX
            vehicleX = columnX + spec.get("xOffset", 0)
            laneVehicles.append(
                game.addLaneVehicle(
                    position=(vehicleX, lane.position[1] + spec["spawnY"]),
                    fileName=spec["fileName"],
                    size=spec["size"],
                    velocity=(0, spec["speed"]),
                    resetY=(lane.position[1] + spec["spawnY"], lane.position[1] + lane.size[1] + 48),
                    stopY=lane.position[1] + spec["stopY"],
                    pauseDuration=spec["pauseDuration"],
                    startDelay=spec["startDelay"],
                    collisionSize=spec["collisionSize"],
                    collisionOffset=spec["collisionOffset"],
                )
            )

        game.vehicleWaves.append(VehicleWave(laneVehicles, restartDelay=5.0))

    trafficSpecTemplates = [
        {"column": "left", "fileName": "BOX TRUCK TOPDOWN/Blue/MOVE/SOUTH/SEPARATED/Blue_BOXTRUCK_CLEAN_SOUTH_000.png", "size": (80, 80), "xOffset": -6, "speed": 34, "spawnY": -90, "stopY": 438, "pauseDuration": 10.0, "startDelay": 0.0, "collisionSize": (34, 64), "collisionOffset": (23, 10)},
        {"column": "right", "fileName": "VAN TOP DOWN/Yellow/MOVE/SOUTH/SEPARATED/Yellow_VAN_CLEAN_SOUTH_000.png", "size": (68, 68), "speed": 32, "spawnY": -150, "stopY": 368, "pauseDuration": 10.0, "startDelay": 0.55, "collisionSize": (34, 52), "collisionOffset": (17, 10)},
        {"column": "left", "fileName": "VAN TOP DOWN/White/MOVE/SOUTH/SEPARATED/White_VAN_CLEAN_SOUTH_000.png", "size": (68, 68), "speed": 31, "spawnY": -220, "stopY": 298, "pauseDuration": 10.0, "startDelay": 1.15, "collisionSize": (34, 52), "collisionOffset": (17, 10)},
        {"column": "right", "fileName": "BOX TRUCK TOPDOWN/Red/MOVE/SOUTH/SEPARATED/Red_BOXTRUCK_CLEAN_SOUTH_000.png", "size": (80, 80), "xOffset": -6, "speed": 33, "spawnY": -300, "stopY": 228, "pauseDuration": 10.0, "startDelay": 1.8, "collisionSize": (34, 64), "collisionOffset": (23, 10)},
    ]

    trafficSpecs = trafficSpecTemplates[: max(1, min(game.trafficWaveVehicleCount, len(trafficSpecTemplates)))]

    addLaneColumnTraffic(leftLane, trafficSpecs)
    addLaneColumnTraffic(rightLane, trafficSpecs)
