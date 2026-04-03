"""
Central lookup for minigame activity ids and labels.

The game engine uses this module to build the right minigame from an activity id,
and the UI reuses the same labels so gameplay and presentation stay in sync.
"""

from minigames.conveyorRouting import ConveyorRoutingMinigame
from minigames.semiUnloading import SemiUnloadingMinigame
from minigames.sorting import SortingMinigame
from minigames.spillCleanup import SpillCleanupMinigame


QUOTA_LABELS = {
    "packageTarget": "Package target",
    "sorting": "Sorting Run",
    "semiUnloading": "Dock Unload",
    "conveyorRouting": "Conveyor Routing",
    "spillCleanup": "Spill Cleanup",
    "urgentUnload": "Urgent Unload",
    "manifestMismatch": "Manifest Mismatch",
    "conveyorOverflow": "Conveyor Overflow",
}


def getQuotaLabel(quotaKey):
    return QUOTA_LABELS.get(quotaKey, quotaKey)


def buildActivity(game, activityId, overrides=None):
    settings = {}

    if activityId == "sorting":
        settings["activityId"] = "sorting"
        settings["quotaKey"] = "sorting"
        factory = SortingMinigame
    elif activityId == "semiUnloading":
        settings["activityId"] = "semiUnloading"
        settings["quotaKey"] = "semiUnloading"
        factory = SemiUnloadingMinigame
    elif activityId == "conveyorRouting":
        settings["activityId"] = "conveyorRouting"
        settings["quotaKey"] = "conveyorRouting"
        factory = ConveyorRoutingMinigame
    elif activityId == "spillCleanup":
        settings["activityId"] = "spillCleanup"
        settings["quotaKey"] = "spillCleanup"
        settings["isEmergency"] = False
        settings["recordHighScore"] = True
        factory = SpillCleanupMinigame
    elif activityId == "urgentUnload":
        settings["activityId"] = "urgentUnload"
        settings["quotaKey"] = "emergencies"
        settings["isEmergency"] = True
        settings["recordHighScore"] = False
        settings["resultLabel"] = "EMERGENCY RESPONSE COMPLETE"
        factory = SemiUnloadingMinigame
    elif activityId == "manifestMismatch":
        settings["activityId"] = "manifestMismatch"
        settings["quotaKey"] = "emergencies"
        settings["isEmergency"] = True
        settings["recordHighScore"] = False
        settings["resultLabel"] = "EMERGENCY RESPONSE COMPLETE"
        factory = SortingMinigame
    elif activityId == "conveyorOverflow":
        settings["activityId"] = "conveyorOverflow"
        settings["quotaKey"] = "emergencies"
        settings["isEmergency"] = True
        settings["recordHighScore"] = False
        settings["resultLabel"] = "EMERGENCY RESPONSE COMPLETE"
        factory = ConveyorRoutingMinigame
    else:
        raise ValueError("Unknown activity id: {0}".format(activityId))

    if overrides:
        settings.update(overrides)
    return factory(game, settings=settings)
