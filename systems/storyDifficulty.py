"""
Story mode difficulty tuning.
"""

STORY_ACTIVITY_DIFFICULTY = {
    "sorting": [
        {"timer": 15.0, "successThreshold": 5},
        {"timer": 14.5, "successThreshold": 5},
        {"timer": 14.0, "successThreshold": 6},
        {"timer": 13.0, "successThreshold": 7},
        {"timer": 12.0, "successThreshold": 7},
        {"timer": 11.0, "successThreshold": 8},
        {"timer": 10.0, "successThreshold": 9},
    ],
    "semiUnloading": [
        {"roundTime": 45.0, "manifestCount": 5},
        {"roundTime": 43.5, "manifestCount": 5},
        {"roundTime": 42.0, "manifestCount": 6},
        {"roundTime": 40.0, "manifestCount": 6},
        {"roundTime": 38.0, "manifestCount": 7},
        {"roundTime": 36.5, "manifestCount": 7},
        {"roundTime": 35.0, "manifestCount": 8},
    ],
    "conveyorRouting": [
        {"roundTime": 28.0, "spawnInterval": 1.35, "boxSpeed": 60.0, "successTarget": 8},
        {"roundTime": 27.0, "spawnInterval": 1.25, "boxSpeed": 66.0, "successTarget": 8},
        {"roundTime": 26.0, "spawnInterval": 1.15, "boxSpeed": 72.0, "successTarget": 9},
        {"roundTime": 24.5, "spawnInterval": 1.05, "boxSpeed": 78.0, "successTarget": 9},
        {"roundTime": 23.0, "spawnInterval": 0.95, "boxSpeed": 84.0, "successTarget": 10},
        {"roundTime": 21.5, "spawnInterval": 0.87, "boxSpeed": 90.0, "successTarget": 10},
        {"roundTime": 20.0, "spawnInterval": 0.80, "boxSpeed": 96.0, "successTarget": 11},
    ],
    "spillCleanup": [
        {"roundTime": 18.0, "spillCount": 8},
        {"roundTime": 17.0, "spillCount": 8},
        {"roundTime": 16.0, "spillCount": 9},
        {"roundTime": 15.0, "spillCount": 9},
        {"roundTime": 14.0, "spillCount": 10},
        {"roundTime": 13.0, "spillCount": 10},
        {"roundTime": 12.0, "spillCount": 11},
    ],
    "urgentUnload": [
        {"roundTime": 38.0, "manifestCount": 4, "moneyPerDelivered": 10},
        {"roundTime": 37.0, "manifestCount": 4, "moneyPerDelivered": 10},
        {"roundTime": 36.0, "manifestCount": 5, "moneyPerDelivered": 10},
        {"roundTime": 34.5, "manifestCount": 5, "moneyPerDelivered": 10},
        {"roundTime": 33.0, "manifestCount": 6, "moneyPerDelivered": 10},
        {"roundTime": 31.5, "manifestCount": 6, "moneyPerDelivered": 10},
        {"roundTime": 30.0, "manifestCount": 7, "moneyPerDelivered": 10},
    ],
    "manifestMismatch": [
        {"timer": 18.0, "successThreshold": 4, "scoreMoneyFactor": 4},
        {"timer": 17.5, "successThreshold": 4, "scoreMoneyFactor": 4},
        {"timer": 17.0, "successThreshold": 5, "scoreMoneyFactor": 4},
        {"timer": 16.5, "successThreshold": 5, "scoreMoneyFactor": 4},
        {"timer": 16.0, "successThreshold": 6, "scoreMoneyFactor": 4},
        {"timer": 15.5, "successThreshold": 6, "scoreMoneyFactor": 4},
        {"timer": 15.0, "successThreshold": 7, "scoreMoneyFactor": 4},
    ],
    "conveyorOverflow": [
        {"roundTime": 26.0, "successTarget": 7, "maxBacklog": 5},
        {"roundTime": 25.0, "successTarget": 7, "maxBacklog": 5},
        {"roundTime": 24.0, "successTarget": 8, "maxBacklog": 5},
        {"roundTime": 22.5, "successTarget": 8, "maxBacklog": 4},
        {"roundTime": 21.0, "successTarget": 9, "maxBacklog": 4},
        {"roundTime": 19.5, "successTarget": 9, "maxBacklog": 4},
        {"roundTime": 18.0, "successTarget": 10, "maxBacklog": 3},
    ],
    "spillCleanupEmergency": [
        {"roundTime": 15.0, "spillCount": 11, "moneyReward": 10, "cursorSpeed": 105},
        {"roundTime": 14.5, "spillCount": 11, "moneyReward": 10, "cursorSpeed": 100},
        {"roundTime": 14.0, "spillCount": 12, "moneyReward": 10, "cursorSpeed": 95},
        {"roundTime": 13.5, "spillCount": 13, "moneyReward": 10, "cursorSpeed": 90},
        {"roundTime": 13.0, "spillCount": 13, "moneyReward": 10, "cursorSpeed": 85},
        {"roundTime": 12.5, "spillCount": 14, "moneyReward": 10, "cursorSpeed": 80},
        {"roundTime": 12.0, "spillCount": 15, "moneyReward": 10, "cursorSpeed": 75},
    ],
}


def getStoryDifficultyTierIndex(dayNumber):
    day = int(dayNumber)
    difficulty = 0

    if day >= 3:
        difficulty = 1
    if day >= 5:
        difficulty = 2
    if day >= 7:
        difficulty = 3
    if day >= 9:
        difficulty = 4
    if day >= 11:
        difficulty = 5
    if day >= 13:
        difficulty = 6

    maxTierIndex = max(0, len(STORY_ACTIVITY_DIFFICULTY["sorting"]) - 1)
    return min(maxTierIndex, difficulty)


def getStoryActivityDifficulty(activityId, dayNumber, isEmergency=False):
    configKey = activityId
    if activityId == "spillCleanup" and isEmergency:
        configKey = "spillCleanupEmergency"

    difficultyTiers = STORY_ACTIVITY_DIFFICULTY.get(configKey, [])
    if not difficultyTiers:
        return {}

    tierIndex = min(getStoryDifficultyTierIndex(dayNumber), len(difficultyTiers) - 1)
    return dict(difficultyTiers[tierIndex])
