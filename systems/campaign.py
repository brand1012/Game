import systems.storyContent as storyContent


DAY_PHASES = (
    (0.25, "Morning"),
    (0.55, "Midday"),
    (0.82, "Dusk"),
    (1.01, "Night"),
)


DAY_TINTS = {
    "Morning": (255, 232, 208, 18),
    "Midday": (255, 255, 255, 0),
    "Dusk": (234, 190, 154, 38),
    "Night": (72, 102, 145, 88),
}


NON_ACTIVITY_QUOTA_KEYS = {"packageTarget"}
TAKE_HOME_PAY_RATIO = 0.2


class CampaignState(object):
    def __init__(
        self,
        dayNumber=1,
        phase="briefing",
        dayProgress=0.0,
        dailyQuota=None,
        completedJobs=None,
        storyBeatId="",
        pendingEmergencyId=None,
        safetyReputation=0,
        totalPerformance=0,
        storyFlags=None,
        payToday=0,
        dayStartMoney=0,
        currentEndingId=None,
        currentSummary=None,
        emergencyResolved=False,
    ):
        self.dayNumber = int(dayNumber)
        self.phase = phase
        self.dayProgress = float(dayProgress)

        self.dailyQuota = {}
        if dailyQuota:
            for key in dailyQuota:
                self.dailyQuota[key] = dailyQuota[key]

        self.completedJobs = {}
        if completedJobs:
            for key in completedJobs:
                self.completedJobs[key] = completedJobs[key]

        self.storyBeatId = storyBeatId
        self.pendingEmergencyId = pendingEmergencyId
        self.safetyReputation = int(safetyReputation)
        self.totalPerformance = int(totalPerformance)

        self.storyFlags = []
        if storyFlags:
            for flag in storyFlags:
                self.storyFlags.append(flag)

        self.payToday = int(payToday)
        self.dayStartMoney = int(dayStartMoney)
        self.currentEndingId = currentEndingId

        self.currentSummary = {}
        if currentSummary:
            for key in currentSummary:
                self.currentSummary[key] = currentSummary[key]

        self.emergencyResolved = bool(emergencyResolved)


class HouseholdState(object):
    def __init__(
        self,
        moneyOnHand=0,
        rentDue=0,
        groceriesNeed=0,
        medicineNeed=0,
        schoolDue=0,
        savings=0,
        stress=8,
        householdStability=72,
        lateBills=None,
        billsAppliedThroughDay=0,
        lastMessage="Your phone is full of reminders you can not ignore forever.",
    ):
        self.moneyOnHand = int(moneyOnHand)
        self.rentDue = int(rentDue)
        self.groceriesNeed = int(groceriesNeed)
        self.medicineNeed = int(medicineNeed)
        self.schoolDue = int(schoolDue)
        self.savings = int(savings)
        self.stress = int(stress)
        self.householdStability = int(householdStability)

        self.lateBills = []
        if lateBills:
            for bill in lateBills:
                self.lateBills.append(bill)

        self.billsAppliedThroughDay = int(billsAppliedThroughDay)
        self.lastMessage = lastMessage


def campaignToDict(campaign):
    if not campaign:
        return None

    dailyQuota = {}
    for key in campaign.dailyQuota:
        dailyQuota[key] = campaign.dailyQuota[key]

    completedJobs = {}
    for key in campaign.completedJobs:
        completedJobs[key] = campaign.completedJobs[key]

    storyFlags = []
    for flag in campaign.storyFlags:
        storyFlags.append(flag)

    currentSummary = {}
    for key in campaign.currentSummary:
        currentSummary[key] = campaign.currentSummary[key]

    return {
        "dayNumber": campaign.dayNumber,
        "phase": campaign.phase,
        "dayProgress": campaign.dayProgress,
        "dailyQuota": dailyQuota,
        "completedJobs": completedJobs,
        "storyBeatId": campaign.storyBeatId,
        "pendingEmergencyId": campaign.pendingEmergencyId,
        "safetyReputation": campaign.safetyReputation,
        "totalPerformance": campaign.totalPerformance,
        "storyFlags": storyFlags,
        "payToday": campaign.payToday,
        "dayStartMoney": campaign.dayStartMoney,
        "currentEndingId": campaign.currentEndingId,
        "currentSummary": currentSummary,
        "emergencyResolved": campaign.emergencyResolved,
    }


def campaignFromDict(data):
    if not data:
        return None

    return CampaignState(
        dayNumber=data.get("dayNumber", 1),
        phase=data.get("phase", "briefing"),
        dayProgress=data.get("dayProgress", 0.0),
        dailyQuota=data.get("dailyQuota", {}),
        completedJobs=data.get("completedJobs", {}),
        storyBeatId=data.get("storyBeatId", ""),
        pendingEmergencyId=data.get("pendingEmergencyId"),
        safetyReputation=data.get("safetyReputation", 0),
        totalPerformance=data.get("totalPerformance", 0),
        storyFlags=data.get("storyFlags", []),
        payToday=data.get("payToday", 0),
        dayStartMoney=data.get("dayStartMoney", 0),
        currentEndingId=data.get("currentEndingId"),
        currentSummary=data.get("currentSummary", {}),
        emergencyResolved=data.get("emergencyResolved", False),
    )


def householdToDict(household):
    if not household:
        return None

    lateBills = []
    for bill in household.lateBills:
        lateBills.append(bill)

    return {
        "moneyOnHand": household.moneyOnHand,
        "rentDue": household.rentDue,
        "groceriesNeed": household.groceriesNeed,
        "medicineNeed": household.medicineNeed,
        "schoolDue": household.schoolDue,
        "savings": household.savings,
        "stress": household.stress,
        "householdStability": household.householdStability,
        "lateBills": lateBills,
        "billsAppliedThroughDay": household.billsAppliedThroughDay,
        "lastMessage": household.lastMessage,
    }


def householdFromDict(data):
    if not data:
        return None

    return HouseholdState(
        moneyOnHand=data.get("moneyOnHand", 0),
        rentDue=data.get("rentDue", 0),
        groceriesNeed=data.get("groceriesNeed", 0),
        medicineNeed=data.get("medicineNeed", 0),
        schoolDue=data.get("schoolDue", 0),
        savings=data.get("savings", 0),
        stress=data.get("stress", 8),
        householdStability=data.get("householdStability", 72),
        lateBills=data.get("lateBills", []),
        billsAppliedThroughDay=data.get("billsAppliedThroughDay", 0),
        lastMessage=data.get(
            "lastMessage",
            "Your phone is full of reminders you can not ignore forever.",
        ),
    )


def createCampaignState():
    campaign = CampaignState()
    prepareDay(campaign, 1)
    return campaign


def createHouseholdState(startingMoney=0):
    household = HouseholdState(moneyOnHand=int(startingMoney))
    recalculateHousehold(household)
    return household


def iterActivityQuotaItems(quota):
    quotaItems = []
    for key in quota:
        value = quota[key]
        if key in NON_ACTIVITY_QUOTA_KEYS or value <= 0:
            continue
        quotaItems.append((key, value))
    return quotaItems


def prepareDay(campaign, dayNumber):
    beat = storyContent.get_day_beat(dayNumber)
    campaign.dayNumber = dayNumber
    campaign.phase = "briefing"
    campaign.dayProgress = 0.0

    campaign.dailyQuota = {}
    for key in beat["quota"]:
        campaign.dailyQuota[key] = beat["quota"][key]

    campaign.completedJobs = {}
    quotaItems = iterActivityQuotaItems(campaign.dailyQuota)
    for key, required in quotaItems:
        campaign.completedJobs[key] = 0
    campaign.completedJobs["emergencies"] = 0

    campaign.storyBeatId = beat["storyBeatId"]
    campaign.pendingEmergencyId = beat["emergencyId"]
    campaign.payToday = 0
    campaign.currentSummary = {}
    campaign.emergencyResolved = False
    return beat


def syncDailyQuotaToBeat(campaign):
    beat = storyContent.get_day_beat(campaign.dayNumber)

    canonicalQuota = {}
    for key in beat["quota"]:
        canonicalQuota[key] = beat["quota"][key]

    existingProgress = {}
    for key in campaign.completedJobs:
        existingProgress[key] = campaign.completedJobs[key]

    campaign.dailyQuota = canonicalQuota
    campaign.completedJobs = {}

    quotaItems = iterActivityQuotaItems(canonicalQuota)
    for key, required in quotaItems:
        campaign.completedJobs[key] = int(existingProgress.get(key, 0))

    campaign.completedJobs["emergencies"] = int(existingProgress.get("emergencies", 0))
    return beat


def getDayPhase(progress):
    for limit, label in DAY_PHASES:
        if progress < limit:
            return label
    return "Night"


def getTintForProgress(progress):
    return DAY_TINTS[getDayPhase(progress)]


def advanceDayProgress(campaign, amount):
    campaign.dayProgress = max(0.0, min(1.0, campaign.dayProgress + amount))
    return campaign.dayProgress


def recordAmbientTime(campaign, seconds):
    advanceDayProgress(campaign, seconds * 0.0025)


def getTakeHomePay(campaign):
    if not campaign:
        return 0
    return int(max(0, campaign.payToday) * TAKE_HOME_PAY_RATIO)


def getQuotaCompletion(campaign):
    totalRequired = 0
    totalDone = 0

    quotaItems = iterActivityQuotaItems(campaign.dailyQuota)
    for key, required in quotaItems:
        totalRequired += required
        totalDone += min(required, campaign.completedJobs.get(key, 0))

    if totalRequired <= 0:
        return 1.0
    return totalDone / float(totalRequired)


def isShiftComplete(campaign):
    return campaign.dayProgress >= 1.0 or getQuotaCompletion(campaign) >= 1.0


def registerActivityResult(campaign, resultData):
    activityId = resultData.get("activityId")
    quotaKey = resultData.get("quotaKey")
    if quotaKey:
        campaign.completedJobs[quotaKey] = campaign.completedJobs.get(quotaKey, 0) + 1
    if resultData.get("isEmergency"):
        campaign.completedJobs["emergencies"] = campaign.completedJobs.get("emergencies", 0) + 1
        campaign.emergencyResolved = True
    campaign.totalPerformance += int(resultData.get("score", 0))
    campaign.payToday += int(resultData.get("money", 0))
    return activityId


def buildDaySummary(campaign, beat, emergencyOutcome=None):
    quotaMet = getQuotaCompletion(campaign) >= 1.0
    quotaProgress = []

    quotaItems = iterActivityQuotaItems(campaign.dailyQuota)
    for key, required in quotaItems:
        quotaProgress.append(
            {
                "key": key,
                "done": campaign.completedJobs.get(key, 0),
                "required": required,
            }
        )

    summary = {
        "dayNumber": campaign.dayNumber,
        "title": beat["title"],
        "quotaMet": quotaMet,
        "quotaProgress": quotaProgress,
        "packageTarget": campaign.dailyQuota.get("packageTarget", 0),
        "payToday": campaign.payToday,
        "takeHomePay": getTakeHomePay(campaign),
        "emergencyOutcome": emergencyOutcome,
    }
    campaign.currentSummary = summary
    return summary


def applyBillsForDay(household, dayNumber):
    if dayNumber <= household.billsAppliedThroughDay:
        return

    for billKey, definition in storyContent.BILL_DEFS.items():
        if dayNumber in definition["dueDays"]:
            if billKey == "rent":
                household.rentDue += definition["amount"]
            elif billKey == "groceries":
                household.groceriesNeed += definition["amount"]
            elif billKey == "medicine":
                household.medicineNeed += definition["amount"]
            elif billKey == "school":
                household.schoolDue += definition["amount"]

    household.billsAppliedThroughDay = dayNumber
    recalculateHousehold(household)


def getOutstandingBills(household):
    return {
        "rent": household.rentDue,
        "groceries": household.groceriesNeed,
        "medicine": household.medicineNeed,
        "school": household.schoolDue,
    }


def payBill(household, billKey, amount):
    amount = max(0, int(amount))
    result = {
        "paid": 0,
        "fromCash": 0,
        "fromSavings": 0,
    }
    if amount == 0:
        return result

    if billKey == "rent":
        due = household.rentDue
    elif billKey == "groceries":
        due = household.groceriesNeed
    elif billKey == "medicine":
        due = household.medicineNeed
    elif billKey == "school":
        due = household.schoolDue
    elif billKey == "savings":
        due = household.moneyOnHand
    else:
        return result

    if billKey == "savings":
        payment = min(amount, due)
        household.moneyOnHand -= payment
        household.savings += payment
        result["paid"] = payment
        result["fromCash"] = payment
        recalculateHousehold(household)
        return result

    paymentTarget = min(amount, due)
    cashPayment = min(paymentTarget, household.moneyOnHand)
    household.moneyOnHand -= cashPayment

    savingsPayment = min(paymentTarget - cashPayment, household.savings)
    household.savings -= savingsPayment

    payment = cashPayment + savingsPayment
    result["paid"] = payment
    result["fromCash"] = cashPayment
    result["fromSavings"] = savingsPayment

    if billKey == "rent":
        household.rentDue -= payment
    elif billKey == "groceries":
        household.groceriesNeed -= payment
    elif billKey == "medicine":
        household.medicineNeed -= payment
    elif billKey == "school":
        household.schoolDue -= payment

    recalculateHousehold(household)
    return result


def recalculateHousehold(household):
    outstanding = (
        household.rentDue
        + household.groceriesNeed
        + household.medicineNeed
        + household.schoolDue
    )
    savingsBuffer = min(30, household.savings // 3)
    household.householdStability = max(
        0,
        min(100, 82 - household.stress - (outstanding // 4) + savingsBuffer),
    )


def finalizeHomePhase(household):
    lateBills = []

    for billKey, definition in storyContent.BILL_DEFS.items():
        remaining = 0
        if billKey == "rent":
            remaining = household.rentDue
        elif billKey == "groceries":
            remaining = household.groceriesNeed
        elif billKey == "medicine":
            remaining = household.medicineNeed
        elif billKey == "school":
            remaining = household.schoolDue

        if remaining > 0:
            lateBills.append(definition["lateLabel"])
            household.stress += definition["stressPenalty"]
            household.householdStability = max(
                0,
                household.householdStability - definition["stabilityPenalty"],
            )

    if not lateBills:
        household.stress = max(0, household.stress - 4)
        household.lastMessage = "Home is still tight, but tonight it can breathe."
    else:
        household.lastMessage = lateBills[0]

    household.lateBills = lateBills
    recalculateHousehold(household)


def resolveEnding(campaign, household):
    if household.householdStability >= 62 and campaign.safetyReputation <= 2 and campaign.totalPerformance >= 1800:
        return "secure_but_complicit"
    if household.householdStability >= 45 and campaign.safetyReputation >= 6:
        return "hard_won_solidarity"
    return "burnout_or_eviction"
