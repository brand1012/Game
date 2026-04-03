import json
import os

import systems.campaign as campaign


SAVE_PATH = "savegame.json"


def hasSave(path=SAVE_PATH):
    return os.path.exists(path)


def loadGame(path=SAVE_PATH):
    if not hasSave(path):
        return None

    try:
        with open(path, "r") as saveFile:
            return json.load(saveFile)
    except Exception:
        return None


def buildSavePayload(game):
    return {
        "mode": game.mode,
        "money": game.money,
        "packagesShipped": game.packagesShipped,
        "workers": game.workers,
        "vans": game.vans,
        "vanCapacity": game.vanCapacity,
        "contractMultiplier": game.contractMultiplier,
        "stockValue": game.stockValue,
        "stockHistory": list(game.stockHistory),
        "highScores": dict(game.highScores),
        "campaign": campaign.campaignToDict(game.campaign),
        "household": campaign.householdToDict(game.household),
    }


def saveGame(game, path=SAVE_PATH):
    payload = buildSavePayload(game)

    existingSave = loadGame(path)
    daySnapshots = []
    if existingSave:
        for snapshot in existingSave.get("daySnapshots", []):
            daySnapshots.append(snapshot)

    if game.mode == "story" and game.campaign:
        currentDay = int(game.campaign.dayNumber)
        keptSnapshots = []
        for snapshot in daySnapshots:
            snapshotCampaign = snapshot.get("campaign", {})
            snapshotDay = int(snapshotCampaign.get("dayNumber", 0))
            if snapshotDay <= currentDay:
                keptSnapshots.append(snapshot)
        daySnapshots = keptSnapshots

        if game.campaign.phase == "briefing":
            snapshotSaved = False
            snapshotPayload = buildSavePayload(game)
            for index, snapshot in enumerate(daySnapshots):
                snapshotCampaign = snapshot.get("campaign", {})
                snapshotDay = int(snapshotCampaign.get("dayNumber", 0))
                if snapshotDay == currentDay:
                    daySnapshots[index] = snapshotPayload
                    snapshotSaved = True
                    break
            if not snapshotSaved:
                daySnapshots.append(snapshotPayload)

        daySnapshots.sort(key=lambda snapshot: int(snapshot.get("campaign", {}).get("dayNumber", 0)))
        payload["daySnapshots"] = daySnapshots

    with open(path, "w") as saveFile:
        json.dump(payload, saveFile, indent=2)


def deleteSave(path=SAVE_PATH):
    if hasSave(path):
        os.remove(path)
