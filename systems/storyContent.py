"""
Story campaign data for shift beats, emergencies, bills, and endings.

Campaign systems read from this module to set each day's quota/dialogue, apply
home-life pressure, and resolve emergency outcomes and ending states.
"""


CAMPAIGN_LENGTH = 14

NPCS = {
    "supervisor": {
        "name": "Nina Alvarez",
        "role": "Dock Supervisor",
        "color": (226, 136, 76),
    },
    "coworker": {
        "name": "Malik Reed",
        "role": "Friendly Coworker",
        "color": (88, 183, 136),
    },
    "veteran": {
        "name": "Jo Price",
        "role": "Veteran Picker",
        "color": (126, 154, 214),
    },
}


BILL_DEFS = {
    "rent": {
        "label": "Rent",
        "amount": 90,
        "dueDays": [4, 8, 12, 14],
        "stressPenalty": 12,
        "stabilityPenalty": 14,
        "lateLabel": "Rent fell behind",
    },
    "groceries": {
        "label": "Groceries",
        "amount": 12,
        "dueDays": list(range(1, CAMPAIGN_LENGTH + 1)),
        "stressPenalty": 3,
        "stabilityPenalty": 4,
        "lateLabel": "The pantry is running thin",
    },
    "medicine": {
        "label": "Medicine",
        "amount": 20,
        "dueDays": [3, 7, 11, 14],
        "stressPenalty": 9,
        "stabilityPenalty": 10,
        "lateLabel": "Medicine refill was missed",
    },
    "school": {
        "label": "School Costs",
        "amount": 24,
        "dueDays": [5, 10, 14],
        "stressPenalty": 7,
        "stabilityPenalty": 8,
        "lateLabel": "School balance is overdue",
    },
}


EMERGENCY_DEFS = {
    "urgent_dock_rush": {
        "id": "urgent_dock_rush",
        "activityId": "urgentUnload",
        "title": "Late Trailer Rush",
        "speaker": "Nina Alvarez",
        "summary": "A late trailer hit the bay after clock-out. Clear the hot freight before the route is missed.",
        "successText": "You cleared the late trailer and kept the route on schedule.",
        "failureText": "The trailer rolled into the night half-cleared. Dispatch filed the miss against the shift.",
        "moneyBonus": 18,
        "stressDeltaOnFail": 5,
        "safetyDeltaOnSuccess": 2,
        "safetyDeltaOnFail": -1,
    },
    "manifest_scramble": {
        "id": "manifest_scramble",
        "activityId": "manifestMismatch",
        "title": "Manifest Scramble",
        "speaker": "Malik Reed",
        "summary": "Labels and paperwork stopped matching. Sort the rush pallets before billing locks.",
        "successText": "You untangled the manifest mess before finance froze the shipment.",
        "failureText": "The wrong freight tags made it through and everyone hears about it tomorrow.",
        "moneyBonus": 14,
        "stressDeltaOnFail": 4,
        "safetyDeltaOnSuccess": 1,
        "safetyDeltaOnFail": -1,
    },
    "chemical_spill": {
        "id": "chemical_spill",
        "activityId": "spillCleanup",
        "title": "Chemical Spill",
        "speaker": "Jo Price",
        "summary": "A leaking pallet left slick trails near the sorting lane. Clean it before someone eats concrete.",
        "successText": "You got the spill handled before anyone slipped through it.",
        "failureText": "The spill lingered too long and the whole floor felt less safe because of it.",
        "moneyBonus": 12,
        "stressDeltaOnFail": 6,
        "safetyDeltaOnSuccess": 3,
        "safetyDeltaOnFail": -3,
    },
    "storm_backlog": {
        "id": "storm_backlog",
        "activityId": "urgentUnload",
        "title": "Storm Backlog",
        "speaker": "Nina Alvarez",
        "summary": "Rain stacked trailers outside all evening. The dock needs one more fast unload before they close the yard.",
        "successText": "You kept the weather backlog from swallowing tomorrow's first wave.",
        "failureText": "The backlog rolled over into tomorrow and management noticed immediately.",
        "moneyBonus": 20,
        "stressDeltaOnFail": 6,
        "safetyDeltaOnSuccess": 2,
        "safetyDeltaOnFail": -1,
    },
    "blind_relabel": {
        "id": "blind_relabel",
        "activityId": "manifestMismatch",
        "title": "Blind Relabel",
        "speaker": "Malik Reed",
        "summary": "Someone relabeled a whole batch with the wrong route codes. Fix the sort before vans leave.",
        "successText": "The relabel job got corrected before the wrong van doors shut.",
        "failureText": "Bad labels slipped through and the next morning starts with blame.",
        "moneyBonus": 16,
        "stressDeltaOnFail": 5,
        "safetyDeltaOnSuccess": 1,
        "safetyDeltaOnFail": -1,
    },
    "forklift_leak": {
        "id": "forklift_leak",
        "activityId": "spillCleanup",
        "title": "Forklift Leak",
        "speaker": "Jo Price",
        "summary": "A rough forklift left hydraulic streaks through the dock mouth. Clean it fast or someone will slide under a load.",
        "successText": "You cleaned the leak and kept the dock from turning into a lawsuit.",
        "failureText": "The leak sat too long and the floor felt one mistake away from disaster.",
        "moneyBonus": 15,
        "stressDeltaOnFail": 7,
        "safetyDeltaOnSuccess": 3,
        "safetyDeltaOnFail": -3,
    },
    "belt_overflow": {
        "id": "belt_overflow",
        "activityId": "conveyorOverflow",
        "title": "Belt Overflow",
        "speaker": "Malik Reed",
        "summary": "The storage belts kept running after the shift and now freight is stacking up faster than anyone can clear it by hand.",
        "successText": "You kept the storage line from swallowing tomorrow's first hour.",
        "failureText": "The belts backed up into a wall of missed freight and management will walk into it in the morning.",
        "moneyBonus": 18,
        "stressDeltaOnFail": 5,
        "safetyDeltaOnSuccess": 2,
        "safetyDeltaOnFail": -2,
    },
}


DAY_BEATS = {
    1: {
        "storyBeatId": "first_clock_in",
        "title": "First Shift",
        "speaker": "Nina Alvarez",
        "summary": "Clock in, learn the lanes, and prove you can keep up without getting lost.",
        "dialogue": [
            "Nina: Stay moving and ask questions later if you have to.",
            "Malik: You'll be fine. Just don't let the place convince you it's normal to sprint all day.",
        ],
        "quota": {"sorting": 1, "semiUnloading": 1, "packageTarget": 10},
        "trafficCount": 3,
        "contractMultiplier": 1.0,
        "pressureBoost": 0.0,
        "emergencyId": None,
    },
    2: {
        "storyBeatId": "tight_margin",
        "title": "Tight Margins",
        "speaker": "Malik Reed",
        "summary": "You are not new anymore, which mostly means nobody slows down for you.",
        "dialogue": [
            "Malik: The trick is pretending the pace is temporary.",
            "Nina: We are behind before lunch, so move like it.",
        ],
        "quota": {"sorting": 2, "semiUnloading": 1, "packageTarget": 14},
        "trafficCount": 4,
        "contractMultiplier": 1.05,
        "pressureBoost": 0.6,
        "emergencyId": None,
    },
    3: {
        "storyBeatId": "first_missed_refill",
        "title": "Refill Day",
        "speaker": "Jo Price",
        "summary": "The work gets faster right when home starts costing more.",
        "dialogue": [
            "Jo: Warehouse jobs always look simple until the bills show up at the same speed as the freight.",
            "Nina: End strong. Dispatch is nervous tonight.",
        ],
        "quota": {"sorting": 2, "semiUnloading": 1, "packageTarget": 16},
        "trafficCount": 4,
        "contractMultiplier": 1.1,
        "pressureBoost": 1.0,
        "emergencyId": "urgent_dock_rush",
    },
    4: {
        "storyBeatId": "rent_notice",
        "title": "Rent Notice",
        "speaker": "Nina Alvarez",
        "summary": "You need a clean day. Home cannot absorb another surprise right now.",
        "dialogue": [
            "Nina: Head office wants numbers, not excuses.",
            "Malik: Funny how those are always easier to say from a chair.",
        ],
        "quota": {"sorting": 2, "semiUnloading": 2, "packageTarget": 20},
        "trafficCount": 4,
        "contractMultiplier": 1.15,
        "pressureBoost": 1.2,
        "emergencyId": None,
    },
    5: {
        "storyBeatId": "storm_warning",
        "title": "Storm Warning",
        "speaker": "Malik Reed",
        "summary": "Weather is coming in and the dock already feels like it is racing the sky.",
        "dialogue": [
            "Malik: Half this place is one rainstorm away from a story nobody wants to tell.",
            "Jo: It gets loud before it gets dangerous. Listen for the change.",
        ],
        "quota": {"sorting": 2, "semiUnloading": 2, "packageTarget": 21},
        "trafficCount": 5,
        "contractMultiplier": 1.2,
        "pressureBoost": 1.6,
        "emergencyId": "storm_backlog",
    },
    6: {
        "storyBeatId": "paperwork_crack",
        "title": "Paperwork Crack",
        "speaker": "Nina Alvarez",
        "summary": "The numbers are rising faster than the paperwork keeping up with them.",
        "dialogue": [
            "Nina: If labels go bad, every mistake multiplies.",
            "Malik: Which is why they keep pretending labels are optional.",
        ],
        "quota": {"sorting": 3, "semiUnloading": 1, "packageTarget": 22},
        "trafficCount": 5,
        "contractMultiplier": 1.22,
        "pressureBoost": 1.8,
        "emergencyId": "manifest_scramble",
    },
    7: {
        "storyBeatId": "safety_meeting",
        "title": "Safety Meeting",
        "speaker": "Jo Price",
        "summary": "Management calls a safety meeting right before asking for a faster shift.",
        "dialogue": [
            "Jo: They only remember safety when there is paperwork attached to it.",
            "Nina: Keep your head clear tonight. We are stretched thin.",
        ],
        "quota": {"sorting": 3, "semiUnloading": 2, "packageTarget": 25},
        "trafficCount": 5,
        "contractMultiplier": 1.25,
        "pressureBoost": 2.0,
        "emergencyId": None,
    },
    8: {
        "storyBeatId": "route_codes_fail",
        "title": "Route Codes Fail",
        "speaker": "Malik Reed",
        "summary": "Mislabels keep showing up and nobody wants to admit where they started.",
        "dialogue": [
            "Malik: If it feels like the floor is covering for a bad decision, it probably is.",
            "Jo: Keep your eyes open after clock-out. The dangerous part likes to arrive late.",
        ],
        "quota": {"sorting": 3, "semiUnloading": 2, "packageTarget": 26},
        "trafficCount": 5,
        "contractMultiplier": 1.28,
        "pressureBoost": 2.2,
        "emergencyId": "blind_relabel",
    },
    9: {
        "storyBeatId": "fatigue_sets_in",
        "title": "Fatigue",
        "speaker": "Jo Price",
        "summary": "Everyone looks one bad hour away from making the mistake they cannot take back.",
        "dialogue": [
            "Jo: People do not break all at once. They fray in little places first.",
            "Nina: Numbers are up. So are expectations.",
        ],
        "quota": {"sorting": 3, "semiUnloading": 2, "packageTarget": 28},
        "trafficCount": 6,
        "contractMultiplier": 1.3,
        "pressureBoost": 2.4,
        "emergencyId": None,
    },
    10: {
        "storyBeatId": "hydraulic_streak",
        "title": "Hydraulic Streak",
        "speaker": "Jo Price",
        "summary": "The first real safety scare lands and everyone notices how little slack the building has left.",
        "dialogue": [
            "Jo: Remember the floor. If it gets slick, the whole place changes.",
            "Malik: They will ask who cleaned it before they ask why it leaked.",
        ],
        "quota": {"sorting": 3, "semiUnloading": 3, "packageTarget": 30},
        "trafficCount": 6,
        "contractMultiplier": 1.35,
        "pressureBoost": 2.7,
        "emergencyId": "forklift_leak",
    },
    11: {
        "storyBeatId": "discipline_talk",
        "title": "Discipline Talk",
        "speaker": "Nina Alvarez",
        "summary": "Management starts threatening write-ups while pretending morale is a personal responsibility.",
        "dialogue": [
            "Nina: Corporate is reading our floor like a chart now.",
            "Malik: Charts never have to carry wet boxes.",
        ],
        "quota": {"sorting": 4, "semiUnloading": 2, "packageTarget": 31},
        "trafficCount": 6,
        "contractMultiplier": 1.38,
        "pressureBoost": 3.0,
        "emergencyId": None,
    },
    12: {
        "storyBeatId": "double_shift_feel",
        "title": "Double Shift Feel",
        "speaker": "Malik Reed",
        "summary": "The day feels twice as long even before the night work starts piling up.",
        "dialogue": [
            "Malik: Funny how temporary crises keep ending up on the schedule.",
            "Jo: The building is telling us what management will not.",
        ],
        "quota": {"sorting": 4, "semiUnloading": 3, "packageTarget": 34},
        "trafficCount": 6,
        "contractMultiplier": 1.42,
        "pressureBoost": 3.4,
        "emergencyId": "belt_overflow",
    },
    13: {
        "storyBeatId": "walkout_whispers",
        "title": "Walkout Whispers",
        "speaker": "Jo Price",
        "summary": "People start talking about how many warnings it should take before someone says no.",
        "dialogue": [
            "Jo: A safe floor is never an accident. Neither is an unsafe one.",
            "Nina: Finish today. Tomorrow will already have enough teeth.",
        ],
        "quota": {"sorting": 4, "semiUnloading": 3, "packageTarget": 36},
        "trafficCount": 6,
        "contractMultiplier": 1.45,
        "pressureBoost": 3.8,
        "emergencyId": None,
    },
    14: {
        "storyBeatId": "final_breaking_point",
        "title": "Breaking Point",
        "speaker": "Nina Alvarez",
        "summary": "This is the day the safety crisis becomes impossible to ignore.",
        "dialogue": [
            "Nina: Whatever happens tonight, make sure it is something you can live with tomorrow.",
            "Malik: Get through the shift. Then decide what kind of ending you want.",
        ],
        "quota": {"sorting": 4, "semiUnloading": 3, "packageTarget": 38},
        "trafficCount": 6,
        "contractMultiplier": 1.5,
        "pressureBoost": 4.2,
        "emergencyId": "chemical_spill",
    },
}


ENDING_DEFS = {
    "secure_but_complicit": {
        "title": "Secure, But Complicit",
        "summary": "You kept the household stable and the numbers strong, but the warehouse learned it could keep asking for more.",
        "lines": [
            "The bills got paid.",
            "The floor stayed open.",
            "You leave with security, but not peace.",
        ],
    },
    "hard_won_solidarity": {
        "title": "Hard-Won Solidarity",
        "summary": "You protected the household and the people around you, even when that meant slowing the machine down.",
        "lines": [
            "The work never got kinder on its own.",
            "People did.",
            "That was enough to change what tomorrow could look like.",
        ],
    },
    "burnout_or_eviction": {
        "title": "Burnout Or Eviction Risk",
        "summary": "The pressure outran the paycheck. Home and work both demanded more than one person could safely give.",
        "lines": [
            "The numbers never stopped moving.",
            "You did.",
            "Now the next month starts with less room than the last.",
        ],
    },
}


def get_day_beat(dayNumber):
    sourceBeat = DAY_BEATS[max(1, min(CAMPAIGN_LENGTH, int(dayNumber)))]
    beat = {}

    for key in sourceBeat:
        value = sourceBeat[key]
        if key == "dialogue":
            beat[key] = list(value)
        elif key == "quota":
            quotaCopy = {}
            for quotaKey in value:
                quotaCopy[quotaKey] = value[quotaKey]
            beat[key] = quotaCopy
        else:
            beat[key] = value

    quota = beat.get("quota", {})
    if int(dayNumber) >= 5 and quota.get("sorting", 0) >= 2:
        quota["sorting"] -= 1
        quota["conveyorRouting"] = quota.get("conveyorRouting", 0) + 1
    beat["quota"] = quota
    return beat


def get_emergency_def(emergencyId):
    return EMERGENCY_DEFS.get(emergencyId)
