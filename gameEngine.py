import os

import pygame

import assets.spriteManager as spriteManager
import minigames.registry as activityRegistry
import systems.campaign as campaign
import systems.economy as economy
import systems.highScores as highScores
import systems.saveData as saveData
import systems.storyContent as storyContent
import systems.storyDifficulty as storyDifficulty
import ui.briefingScreen as briefingScreen
import ui.daySummaryScreen as daySummaryScreen
import ui.dialogueScreen as dialogueScreen
import ui.emergencyScreen as emergencyScreen
import ui.homeScreen as homeScreen
import ui.infoScreen as infoScreen
import ui.mainMenu as mainMenu
import ui.resultsScreen as resultsScreen
import ui.stockScreen as stockScreen
import ui.upgradeScreen as upgradeScreen
import ui.warehouse as warehouse
import world.floor as floor
import world.layout as layout
import world.zoneBuilders.loadingDock as loadingDock
import world.zoneBuilders.offices as offices
import world.zoneBuilders.sortingArea as sortingArea
import world.zoneBuilders.storage as storage
import world.zoneBuilders.vanPrep as vanPrep
import world.zoneBuilders.vehicleLanes as vehicleLanes

from characters.drawable import Drawable
from characters.player import Player
from characters.props import AnimatedProp, LoopingProp, Prop
from characters.vehicles import LaneVehicle
from utils.vector import vec


VALID_STORY_SAVE_PHASES = {"briefing", "warehouse", "daySummary", "home"}


class GameEngine(object):
    def __init__(self):
        os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
        pygame.init()

        self.RESOLUTION = (400, 200)
        self.WORLD_SIZE = (1000, 700)

        monitorResolution = self.getMonitorResolution()
        self.screen = pygame.display.set_mode(list(monitorResolution), pygame.NOFRAME)
        self.UPSCALED = list(self.screen.get_size())
        self.drawSurface = pygame.Surface(list(self.RESOLUTION))

        self.myFont = pygame.font.SysFont("Arial", 16)
        self.infoFont = pygame.font.SysFont("Arial", 12)
        self.uiFont = pygame.font.SysFont("Arial", 10, bold=True)

        self.spriteManager = spriteManager.SpriteManager()
        self.player = Player(vec(500, 600), self.spriteManager, self.WORLD_SIZE)
        self.floor = floor.buildFloor(self)

        self.baseWorkerCost = 10
        self.baseCapacityCost = 50
        self.baseVanCost = 200
        self.costGrowth = 1.5

        self.highScores = highScores.loadHighScores("highscores.json")
        self.zones = layout.createZones()

        self.worldProps = []
        self.laneVehicles = []
        self.vehicleWaves = []
        self.semiTruckRigs = []
        self.semiTruckWaves = []
        self.walls = []
        self.sortingPallets = []
        self.loadingDockForklifts = []
        self.spillCleanupControls = []
        self.storageControls = []
        self.upgradeDesks = []

        self.gameClock = pygame.time.Clock()
        self.mainMenuIndex = 0
        self.continueMenuIndex = 0
        self.continueOptions = []
        self.homeMenuIndex = 0
        self.homePaymentStep = 10
        self.canContinueStory = False

        self.mode = None
        self.state = "mainMenu"
        self.currentMinigame = None
        self.currentMinigameType = None
        self.resultsData = None
        self.currentEmergencyDef = None
        self.currentEmergencyOutcome = None
        self.daySummaryData = None
        self.dialogueData = None
        self.dialogueAction = ""
        self.campaign = None
        self.household = None

        self.resetRuntimeState()
        self.refreshContinueOption()

    def getMonitorResolution(self):
        desktopSizes = pygame.display.get_desktop_sizes()
        if desktopSizes:
            monitorWidth, monitorHeight = desktopSizes[0]
            return [int(monitorWidth), int(monitorHeight)]

        displayInfo = pygame.display.Info()
        monitorWidth = int(displayInfo.current_w)
        monitorHeight = int(displayInfo.current_h)

        if monitorWidth <= 0 or monitorHeight <= 0:
            return [self.RESOLUTION[0] * 3, self.RESOLUTION[1] * 3]

        return [monitorWidth, monitorHeight]

    def getRenderPosition(self, position):
        scaleX = self.UPSCALED[0] / self.RESOLUTION[0]
        scaleY = self.UPSCALED[1] / self.RESOLUTION[1]
        return (int(position[0] / scaleX), int(position[1] / scaleY))

    def refreshContinueOption(self):
        savePayload = saveData.loadGame()
        self.canContinueStory = self.isValidStorySaveData(savePayload)

    def getPhaseLabel(self, phase):
        if phase == "warehouse":
            return "In Shift"
        if phase == "daySummary":
            return "Summary"
        if phase == "home":
            return "Home"
        return "Briefing"

    def buildContinueOptions(self, savePayload):
        options = []
        snapshotsByDay = {}

        for snapshot in savePayload.get("daySnapshots", []):
            if not self.isValidStorySaveData(snapshot):
                continue
            snapshotCampaign = snapshot.get("campaign", {})
            snapshotDay = int(snapshotCampaign.get("dayNumber", 0))
            snapshotsByDay[snapshotDay] = snapshot

        currentCampaign = savePayload.get("campaign", {})
        currentDay = int(currentCampaign.get("dayNumber", 0))
        currentPhase = currentCampaign.get("phase", "briefing")

        if currentDay > 0 and self.isValidStorySaveData(savePayload) and currentDay not in snapshotsByDay:
            snapshotsByDay[currentDay] = savePayload

        for dayNumber in sorted(snapshotsByDay.keys()):
            optionPayload = snapshotsByDay[dayNumber]
            detail = "Start of day"
            if dayNumber == currentDay and currentPhase != "briefing":
                optionPayload = savePayload
                detail = self.getPhaseLabel(currentPhase)

            options.append(
                {
                    "dayNumber": dayNumber,
                    "title": storyContent.get_day_beat(dayNumber)["title"],
                    "detail": detail,
                    "payload": optionPayload,
                }
            )

        return options

    def openContinueMenu(self):
        savePayload = saveData.loadGame()
        if not self.isValidStorySaveData(savePayload):
            self.refreshContinueOption()
            return

        self.continueOptions = self.buildContinueOptions(savePayload)
        if not self.continueOptions:
            self.refreshContinueOption()
            return

        self.continueMenuIndex = len(self.continueOptions) - 1
        self.state = "continueMenu"

    def isValidStorySaveData(self, savePayload):
        if not savePayload or savePayload.get("mode") != "story":
            return False

        campaignData = savePayload.get("campaign")
        householdData = savePayload.get("household")
        if not campaignData or not householdData:
            return False

        return campaignData.get("phase") in VALID_STORY_SAVE_PHASES

    def getMainMenuOptions(self):
        continueLabel = "Continue" if self.canContinueStory else "Continue (No Save)"
        storyLabel = "Restart Campaign" if self.canContinueStory else "Start Campaign"
        return [
            (continueLabel, "continue"),
            (storyLabel, "story"),
            ("Practice Shift", "practice"),
            ("Quit", "quit"),
        ]

    def autosaveStory(self):
        if self.mode != "story" or not self.campaign or not self.household:
            return

        if self.campaign.phase not in VALID_STORY_SAVE_PHASES:
            return

        saveData.saveGame(self)
        self.refreshContinueOption()

    def resetRuntimeState(self):
        self.workers = 1
        self.vans = 1
        self.vanCapacity = 1
        self.contractMultiplier = 1
        self.stockValue = 100
        self.stockHistory = [self.stockValue]
        self.stockTimer = 0
        self.trafficWaveVehicleCount = 4

        self.money = 0
        self.packagesShipped = 0
        self.showInteractPrompt = False
        self.currentInteraction = None

        self.currentMinigame = None
        self.currentMinigameType = None
        self.resultsData = None
        self.currentEmergencyDef = None
        self.currentEmergencyOutcome = None
        self.daySummaryData = None
        self.dialogueData = None
        self.dialogueAction = ""

        officeSpawn = self.getOfficeRespawnPosition()
        self.player.setRespawnPosition(officeSpawn)
        self.player.placeAt(officeSpawn)
        self.buildWorldProps()
        self.centerCameraOnPlayer()
        self.clampCamera()

    def startPracticeShift(self):
        self.mode = "practice"
        self.resetRuntimeState()
        self.campaign = None
        self.household = None
        self.mainMenuIndex = 0
        self.state = "warehouse"

    def startStoryCampaign(self):
        self.mode = "story"
        self.resetRuntimeState()
        self.campaign = campaign.createCampaignState()
        self.household = campaign.createHouseholdState(self.money)
        self.mainMenuIndex = 0
        self.applyStoryDaySetup()
        self.autosaveStory()
        self.showBeatDialogue()

    def continueStoryCampaign(self, savePayload=None):
        if savePayload is None:
            savePayload = saveData.loadGame()
        if not self.isValidStorySaveData(savePayload):
            self.refreshContinueOption()
            return

        self.continueOptions = []
        self.continueMenuIndex = 0
        self.mode = "story"
        self.resetRuntimeState()

        self.money = float(savePayload.get("money", 0))
        self.packagesShipped = float(savePayload.get("packagesShipped", 0))
        self.workers = int(savePayload.get("workers", self.workers))
        self.vans = int(savePayload.get("vans", self.vans))
        self.vanCapacity = int(savePayload.get("vanCapacity", self.vanCapacity))
        self.contractMultiplier = float(savePayload.get("contractMultiplier", self.contractMultiplier))
        self.stockValue = float(savePayload.get("stockValue", self.stockValue))
        self.stockHistory = list(savePayload.get("stockHistory", [self.stockValue])) or [self.stockValue]
        self.highScores = dict(savePayload.get("highScores", self.highScores))

        self.campaign = campaign.campaignFromDict(savePayload["campaign"])
        self.household = campaign.householdFromDict(savePayload["household"])

        phase = self.campaign.phase
        self.applyStoryDaySetup()

        if phase == "warehouse":
            self.state = "warehouse"
        elif phase == "daySummary":
            self.daySummaryData = dict(self.campaign.currentSummary)
            if not self.daySummaryData:
                beat = storyContent.get_day_beat(self.campaign.dayNumber)
                self.daySummaryData = campaign.buildDaySummary(self.campaign, beat)
            self.currentEmergencyOutcome = self.daySummaryData.get("emergencyOutcome")
            self.state = "daySummary"
        elif phase == "home":
            self.state = "home"
            self.homeMenuIndex = 0
        else:
            self.campaign.phase = "briefing"
            self.state = "briefing"

        self.autosaveStory()

    def addStoryPressureBoost(self, beat):
        boost = float(beat.get("pressureBoost", 0.0))
        if boost <= 0:
            return

        self.stockValue += boost
        self.stockHistory.append(self.stockValue)
        if len(self.stockHistory) > 200:
            self.stockHistory.pop(0)

    def applyStoryDaySetup(self):
        beat = campaign.syncDailyQuotaToBeat(self.campaign)
        self.contractMultiplier = float(beat.get("contractMultiplier", self.contractMultiplier))
        self.trafficWaveVehicleCount = int(beat.get("trafficCount", self.trafficWaveVehicleCount))

        self.currentMinigame = None
        self.currentMinigameType = None
        self.resultsData = None
        self.currentEmergencyDef = None
        self.currentEmergencyOutcome = None
        self.daySummaryData = dict(self.campaign.currentSummary)
        self.dialogueData = None
        self.dialogueAction = ""

        officeSpawn = self.getOfficeRespawnPosition()
        self.player.setRespawnPosition(officeSpawn)
        self.player.placeAt(officeSpawn)
        self.buildWorldProps()
        self.centerCameraOnPlayer()
        self.clampCamera()

        return beat

    def showBeatDialogue(self):
        beat = storyContent.get_day_beat(self.campaign.dayNumber)
        self.campaign.phase = "briefing"
        self.queueDialogue(
            title="DAY {0}: {1}".format(self.campaign.dayNumber, beat["title"]),
            speaker=beat["speaker"],
            summary=beat["summary"],
            lines=beat["dialogue"],
            prompt="Press Enter for briefing",
            action="briefing",
        )

    def queueDialogue(self, title, speaker, summary, lines, prompt, action):
        self.dialogueData = {
            "title": title,
            "speaker": speaker,
            "summary": summary,
            "lines": list(lines),
            "prompt": prompt,
        }
        self.dialogueAction = action
        self.state = "dialogue"

    def resolveDialogue(self):
        action = self.dialogueAction
        self.dialogueData = None
        self.dialogueAction = ""

        if action == "briefing":
            self.enterBriefing()
        elif action == "mainMenu":
            self.finishStoryEnding()

    def enterBriefing(self):
        self.campaign.phase = "briefing"
        self.state = "briefing"
        self.autosaveStory()

    def beginShift(self):
        self.campaign.phase = "warehouse"
        self.campaign.dayStartMoney = int(self.money)
        self.daySummaryData = None
        self.currentEmergencyDef = None
        self.currentEmergencyOutcome = None
        self.state = "warehouse"
        self.autosaveStory()

    def enterEmergency(self):
        if not self.campaign.pendingEmergencyId:
            self.openDaySummary()
            return

        emergencyDef = storyContent.get_emergency_def(self.campaign.pendingEmergencyId)
        if not emergencyDef:
            self.openDaySummary()
            return

        self.currentEmergencyDef = emergencyDef
        self.campaign.phase = "emergency"
        self.state = "emergency"

    def launchEmergencyMinigame(self):
        if not self.currentEmergencyDef:
            return

        activityId = self.currentEmergencyDef.get("activityId")
        activityConfig = self.getStoryActivityConfig(activityId)
        self.startActivity(activityId, activityConfig)

    def openDaySummary(self):
        beat = storyContent.get_day_beat(self.campaign.dayNumber)
        self.currentEmergencyDef = None
        self.campaign.payToday = max(0, int(self.money) - int(self.campaign.dayStartMoney))
        self.daySummaryData = campaign.buildDaySummary(
            self.campaign,
            beat,
            emergencyOutcome=self.currentEmergencyOutcome,
        )
        self.campaign.phase = "daySummary"
        self.state = "daySummary"
        self.autosaveStory()

    def openStockScreen(self):
        self.state = "stock"

    def openHomeScreen(self):
        campaign.applyBillsForDay(self.household, self.campaign.dayNumber)
        if self.campaign.phase != "home":
            self.household.moneyOnHand += campaign.getTakeHomePay(self.campaign)
        self.homeMenuIndex = 0
        self.campaign.phase = "home"
        self.state = "home"
        self.autosaveStory()

    def finishHomePhase(self):
        campaign.finalizeHomePhase(self.household)

        if self.campaign.dayNumber >= storyContent.CAMPAIGN_LENGTH:
            endingId = campaign.resolveEnding(self.campaign, self.household)
            endingDef = storyContent.ENDING_DEFS[endingId]
            self.campaign.currentEndingId = endingId
            saveData.deleteSave()
            self.refreshContinueOption()
            self.queueDialogue(
                title=endingDef["title"],
                speaker="Shift Record",
                summary=endingDef["summary"],
                lines=endingDef["lines"],
                prompt="Press Enter for main menu",
                action="mainMenu",
            )
            return

        nextDay = self.campaign.dayNumber + 1
        nextBeat = campaign.prepareDay(self.campaign, nextDay)
        self.addStoryPressureBoost(nextBeat)
        self.applyStoryDaySetup()
        self.autosaveStory()
        self.showBeatDialogue()

    def finishStoryEnding(self):
        self.returnToMenu()

    def finishShift(self):
        if self.campaign.pendingEmergencyId and not self.campaign.emergencyResolved:
            self.enterEmergency()
        else:
            self.openDaySummary()

    def resolveEmergencyOutcome(self, resultData):
        emergencyDef = self.currentEmergencyDef or storyContent.get_emergency_def(self.campaign.pendingEmergencyId)
        if not emergencyDef:
            self.openDaySummary()
            return

        if resultData.get("success"):
            self.money += int(emergencyDef.get("moneyBonus", 0))
            self.campaign.safetyReputation += int(emergencyDef.get("safetyDeltaOnSuccess", 0))
            self.currentEmergencyOutcome = emergencyDef.get("successText", "The emergency was handled.")
        else:
            self.household.stress += int(emergencyDef.get("stressDeltaOnFail", 0))
            campaign.recalculateHousehold(self.household)
            self.campaign.safetyReputation += int(emergencyDef.get("safetyDeltaOnFail", 0))
            self.currentEmergencyOutcome = emergencyDef.get("failureText", "The emergency slipped into tomorrow.")

        self.openDaySummary()

    def getStoryActivityConfig(self, activityId):
        dayNumber = self.campaign.dayNumber if self.campaign else 1
        config = storyDifficulty.getStoryActivityDifficulty(
            activityId,
            dayNumber,
            isEmergency=bool(self.currentEmergencyDef),
        )

        if activityId == "sorting":
            config.update({
                "title": "SORT THE FLOOR FREIGHT",
                "resultLabel": "SHIFT TASK COMPLETE",
            })
        elif activityId == "semiUnloading":
            config.update({
                "title": "CLEAR THE DOCK TRAILER",
                "resultLabel": "DOCK TASK COMPLETE",
            })
        elif activityId == "conveyorRouting":
            config.update({
                "resultLabel": "ROUTING TASK COMPLETE",
            })

        if not self.currentEmergencyDef:
            return config

        emergencySummary = self.currentEmergencyDef.get("summary", "")
        config.update({
            "isEmergency": True,
            "quotaKey": "emergencies",
            "recordHighScore": False,
            "title": self.currentEmergencyDef.get("title", "").upper(),
            "instructions": emergencySummary,
            "resultLabel": "EMERGENCY RESPONSE COMPLETE",
        })

        return config

    def returnToMenu(self):
        self.mode = None
        self.campaign = None
        self.household = None
        self.currentEmergencyDef = None
        self.currentEmergencyOutcome = None
        self.daySummaryData = None
        self.dialogueData = None
        self.dialogueAction = ""
        self.currentMinigame = None
        self.currentMinigameType = None
        self.resultsData = None
        self.mainMenuIndex = 0
        self.continueMenuIndex = 0
        self.continueOptions = []
        self.state = "mainMenu"
        self.refreshContinueOption()

    def draw(self, surface):
        if self.state == "mainMenu":
            mainMenu.drawMainMenu(self, surface)
        elif self.state == "continueMenu":
            mainMenu.drawContinueMenu(self, surface)
        elif self.state == "briefing":
            briefingScreen.drawBriefingScreen(self, surface)
        elif self.state == "dialogue":
            dialogueScreen.drawDialogueScreen(self, surface)
        elif self.state == "warehouse":
            warehouse.drawWarehouse(self, surface)
        elif self.state == "minigame":
            self.currentMinigame.draw(surface)
        elif self.state == "results":
            resultsScreen.drawResults(self, surface)
        elif self.state == "upgrade":
            upgradeScreen.drawUpgradeScreen(self, surface)
        elif self.state == "info":
            infoScreen.drawInfoScreen(self, surface)
        elif self.state == "stock":
            stockScreen.drawStockGraph(self, surface)
        elif self.state == "emergency":
            emergencyScreen.drawEmergencyScreen(self, surface)
        elif self.state == "daySummary":
            daySummaryScreen.drawDaySummary(self, surface)
        elif self.state == "home":
            homeScreen.drawHomeScreen(self, surface)

        pygame.transform.scale(surface, self.UPSCALED, self.screen)
        pygame.display.flip()

    def updateWarehouse(self, seconds):
        self.money += economy.getIncomePerSecond(self) * seconds
        self.packagesShipped += economy.getPackagesDeliveredPerSecond(self) * seconds
        economy.updateStockHistory(self, seconds)

        activeVehicleWalls = [vehicle for vehicle in self.laneVehicles if vehicle.active and vehicle.rect]
        activeSemiWalls = [rig for rig in self.semiTruckRigs if rig.active and getattr(rig, "rect", None)]
        collisionWalls = self.walls + activeVehicleWalls + activeSemiWalls

        for worldProp in self.worldProps:
            worldProp.update(seconds)
        for vehicleWave in self.vehicleWaves:
            vehicleWave.update(seconds)
        for semiTruckWave in self.semiTruckWaves:
            semiTruckWave.update(seconds)

        self.player.update(seconds, collisionWalls)
        self.updateTrafficHazards()

        if self.player.isMelting():
            self.showInteractPrompt = False
            self.currentInteraction = None
        else:
            self.updateInteractionPrompt()

        self.centerCameraOnPlayer()
        self.clampCamera()

        if self.mode == "story" and self.campaign:
            campaign.recordAmbientTime(self.campaign, seconds)
            if campaign.isShiftComplete(self.campaign):
                self.finishShift()

    def update(self, seconds):
        if self.state == "warehouse":
            self.updateWarehouse(seconds)
        elif self.state == "minigame" and self.currentMinigame:
            self.currentMinigame.update(seconds)

    def applyResultsAndContinue(self):
        resultData = self.resultsData or {}
        self.currentMinigame = None
        self.currentMinigameType = None
        self.resultsData = None

        if self.mode != "story" or not self.campaign:
            self.state = "warehouse"
            return

        campaign.registerActivityResult(self.campaign, resultData)
        campaign.advanceDayProgress(self.campaign, float(resultData.get("dayProgressDelta", 0.0)))

        if not resultData.get("isEmergency"):
            self.campaign.safetyReputation += int(resultData.get("safetyDelta", 0))

        if resultData.get("isEmergency"):
            self.resolveEmergencyOutcome(resultData)
            return

        if campaign.isShiftComplete(self.campaign):
            self.finishShift()
        else:
            self.campaign.phase = "warehouse"
            self.state = "warehouse"

    def clampCamera(self):
        maxX = self.WORLD_SIZE[0] - self.RESOLUTION[0]
        maxY = self.WORLD_SIZE[1] - self.RESOLUTION[1]
        Drawable.CAMERA_OFFSET[0] = max(0, min(Drawable.CAMERA_OFFSET[0], maxX))
        Drawable.CAMERA_OFFSET[1] = max(0, min(Drawable.CAMERA_OFFSET[1], maxY))

    def handleMainMenuEvent(self, event):
        options = self.getMainMenuOptions()
        if event.key == pygame.K_UP:
            self.mainMenuIndex = (self.mainMenuIndex - 1) % len(options)
        elif event.key == pygame.K_DOWN:
            self.mainMenuIndex = (self.mainMenuIndex + 1) % len(options)
        elif event.key == pygame.K_RETURN:
            action = options[self.mainMenuIndex][1]
            if action == "story":
                self.startStoryCampaign()
            elif action == "practice":
                self.startPracticeShift()
            elif action == "continue":
                self.openContinueMenu()
            else:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handleContinueMenuEvent(self, event):
        if not self.continueOptions:
            self.returnToMenu()
            return

        if event.key == pygame.K_UP:
            self.continueMenuIndex = (self.continueMenuIndex - 1) % len(self.continueOptions)
        elif event.key == pygame.K_DOWN:
            self.continueMenuIndex = (self.continueMenuIndex + 1) % len(self.continueOptions)
        elif event.key == pygame.K_BACKSPACE:
            self.state = "mainMenu"
        elif event.key == pygame.K_RETURN:
            selected = self.continueOptions[self.continueMenuIndex]
            self.continueStoryCampaign(selected["payload"])

    def handleHomeEvent(self, event):
        homeItems = homeScreen.HOME_ITEMS
        if event.key == pygame.K_UP:
            self.homeMenuIndex = (self.homeMenuIndex - 1) % len(homeItems)
            return True
        if event.key == pygame.K_DOWN:
            self.homeMenuIndex = (self.homeMenuIndex + 1) % len(homeItems)
            return True

        selectedKey, selectedLabel = homeItems[self.homeMenuIndex]

        if event.key in (pygame.K_LEFT, pygame.K_RIGHT) and selectedKey != "sleep":
            if selectedKey == "savings" and event.key != pygame.K_RIGHT:
                self.household.lastMessage = "Savings only accepts deposits here."
                return True

            payment = campaign.payBill(self.household, selectedKey, self.homePaymentStep)
            paid = payment["paid"]
            if paid > 0:
                if selectedKey == "savings":
                    self.household.lastMessage = "Moved ${0} into savings".format(paid)
                elif payment["fromSavings"] > 0:
                    self.household.lastMessage = "Paid ${0} toward {1} (${2} from savings)".format(
                        paid,
                        selectedLabel,
                        payment["fromSavings"],
                    )
                else:
                    self.household.lastMessage = "Paid ${0} toward {1}".format(paid, selectedLabel)
            else:
                if selectedKey == "savings":
                    self.household.lastMessage = "Not enough cash to add to savings"
                else:
                    self.household.lastMessage = "Not enough cash or savings for {0}".format(selectedLabel.lower())
            return True

        if event.key == pygame.K_RETURN and selectedKey == "sleep":
            self.finishHomePhase()
            return True

        return False

    def handleWarehouseHotkeys(self, event):
        if event.key == pygame.K_i:
            self.state = "info" if self.state == "warehouse" else "warehouse"
            return True
        if event.key == pygame.K_s:
            self.state = "stock" if self.state == "warehouse" else "warehouse"
            return True
        if self.mode == "story" and event.key == pygame.K_b:
            if self.state == "warehouse":
                self.state = "briefing"
                return True
            if self.state == "briefing":
                self.state = "warehouse"
                return True
        return False

    def handleEvent(self, event):
        if self.state == "minigame" and self.currentMinigame:
            self.currentMinigame.handleEvent(event)
            return

        if event.type == pygame.KEYDOWN:
            if self.state == "mainMenu":
                self.handleMainMenuEvent(event)
                return

            if self.state == "continueMenu":
                self.handleContinueMenuEvent(event)
                return

            if self.state == "dialogue" and event.key == pygame.K_RETURN:
                self.resolveDialogue()
                return

            if self.state == "briefing":
                if event.key == pygame.K_RETURN:
                    self.beginShift()
                    return
                if event.key == pygame.K_b:
                    self.state = "warehouse"
                    return
                if event.key == pygame.K_s:
                    self.state = "stock"
                    return

            if self.state == "emergency" and event.key == pygame.K_RETURN:
                self.launchEmergencyMinigame()
                return

            if self.state == "daySummary" and event.key == pygame.K_RETURN:
                self.openStockScreen()
                return

            if self.state == "stock" and self.mode == "story" and self.campaign and self.campaign.phase == "daySummary":
                if event.key in (pygame.K_RETURN, pygame.K_s):
                    self.openHomeScreen()
                return

            if self.state == "home" and self.handleHomeEvent(event):
                return

            if self.state == "results" and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.applyResultsAndContinue()
                return

            if self.state == "upgrade":
                if event.key == pygame.K_BACKSPACE:
                    self.state = "warehouse"
                elif event.key == pygame.K_1:
                    self.purchaseUpgrade("+1 Extra Worker")
                elif event.key == pygame.K_2:
                    self.purchaseUpgrade("+2 Van Capacity")
                elif event.key == pygame.K_3:
                    self.purchaseUpgrade("+1 Extra Van")
                return

            if self.state in ("warehouse", "info", "stock") and self.handleWarehouseHotkeys(event):
                return

            if self.state == "warehouse" and event.key == pygame.K_e and self.currentInteraction:
                if self.currentInteraction == "sorting":
                    storyConfig = self.getStoryActivityConfig("sorting") if self.mode == "story" else None
                    self.startActivity("sorting", storyConfig)
                elif self.currentInteraction == "semiUnloading":
                    storyConfig = self.getStoryActivityConfig("semiUnloading") if self.mode == "story" else None
                    self.startActivity("semiUnloading", storyConfig)
                elif self.currentInteraction == "conveyorRouting":
                    storyConfig = self.getStoryActivityConfig("conveyorRouting") if self.mode == "story" else None
                    self.startActivity("conveyorRouting", storyConfig)
                elif self.currentInteraction == "spillCleanup" and self.mode != "story":
                    self.startActivity("spillCleanup")
                elif self.currentInteraction == "upgrade":
                    self.state = "upgrade"

        if self.state == "warehouse" and event.type == pygame.KEYUP:
            if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                self.player.velocity[0] = 0
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                self.player.velocity[1] = 0

        if event.type == pygame.MOUSEBUTTONUP:
            self.player.velocity[0] = 0
            self.player.velocity[1] = 0

    def buildActivity(self, activityId, overrides=None):
        return activityRegistry.buildActivity(self, activityId, overrides)

    def startActivity(self, activityId, overrides=None):
        self.currentMinigameType = activityId
        self.currentMinigame = self.buildActivity(activityId, overrides)
        self.state = "minigame"

    def centerCameraOnPlayer(self):
        Drawable.CAMERA_OFFSET = (
            self.player.position +
            vec(*self.player.image.get_size()) / 2 -
            vec(*self.RESOLUTION) / 2
        )

    def getOfficeRespawnPosition(self):
        officeZone = self.getZone("Offices")
        spriteWidth, spriteHeight = self.player.image.get_size()
        return vec(
            officeZone.position[0] + (officeZone.size[0] / 2) - (spriteWidth / 2),
            officeZone.position[1] + officeZone.size[1] - spriteHeight - 18,
        )

    def getZone(self, name, index=0):
        matches = [zone for zone in self.zones if zone.name == name]
        return matches[index]

    def getActiveTrafficHazards(self):
        return [
            vehicle
            for vehicle in self.laneVehicles
            if vehicle.rect and vehicle.isMoving()
        ]

    def updateTrafficHazards(self):
        if not self.player.canBeHitByTraffic():
            return

        impactRect = self.player.rect
        for hazard in self.getActiveTrafficHazards():
            if hazard.isForwardImpact(impactRect):
                self.player.startTrafficMeltdown(self.getOfficeRespawnPosition())
                self.showInteractPrompt = False
                self.currentInteraction = None
                return

    def addWorldProp(self, position, fileName, size, collisionSize=None, collisionOffset=(0, 0)):
        image = pygame.transform.smoothscale(self.spriteManager.getSprite(fileName), size)
        worldProp = Prop(position, image, collisionSize, collisionOffset)
        self.worldProps.append(worldProp)

        if worldProp.rect:
            self.walls.append(worldProp)

        return worldProp

    def addAnimatedWorldPropRects(
        self,
        position,
        fileName,
        rects,
        size,
        framesPerSecond=6,
        collisionSize=None,
        collisionOffset=(0, 0)
    ):
        frames = [
            pygame.transform.smoothscale(self.spriteManager.getSprite(fileName, rect), size)
            for rect in rects
        ]
        worldProp = AnimatedProp(
            position,
            frames,
            framesPerSecond=framesPerSecond,
            collisionSize=collisionSize,
            collisionOffset=collisionOffset
        )
        self.worldProps.append(worldProp)

        if worldProp.rect:
            self.walls.append(worldProp)

        return worldProp

    def addLoopingWorldProp(self, position, fileName, size, speed, loopStartX, loopEndX):
        image = pygame.transform.smoothscale(self.spriteManager.getSprite(fileName), size)
        worldProp = LoopingProp(position, image, speed, loopStartX, loopEndX)
        self.worldProps.append(worldProp)
        return worldProp

    def addLaneVehicle(
        self,
        position,
        fileName,
        size,
        velocity,
        resetY,
        stopY=None,
        pauseDuration=0,
        startDelay=0,
        collisionSize=None,
        collisionOffset=(0, 0)
    ):
        image = pygame.transform.smoothscale(self.spriteManager.getSprite(fileName), size)
        vehicle = LaneVehicle(
            position,
            image,
            velocity,
            resetY,
            stopY=stopY,
            pauseDuration=pauseDuration,
            startDelay=startDelay,
            collisionSize=collisionSize,
            collisionOffset=collisionOffset
        )
        self.laneVehicles.append(vehicle)
        return vehicle

    def buildWorldProps(self):
        self.worldProps = []
        self.laneVehicles = []
        self.vehicleWaves = []
        self.semiTruckRigs = []
        self.semiTruckWaves = []
        self.walls = []
        self.sortingPallets = []
        self.loadingDockForklifts = []
        self.spillCleanupControls = []
        self.storageControls = []
        self.upgradeDesks = []

        loadingDock.buildLoadingDock(self, self.getZone("Semi Unloading Dock"))
        sortingArea.buildSortingZone(self, self.getZone("Sorting Area"))
        storage.buildStorageZone(self, self.getZone("Storage"))
        vanPrep.buildVanPrep(self, self.getZone("Van Prep", 0), self.getZone("Van Prep", 1))
        offices.buildOfficeZone(self, self.getZone("Offices"))
        vehicleLanes.buildVehicleTraffic(self, self.getZone("Vehicle Lane", 0), self.getZone("Vehicle Lane", 1))

    def updateInteractionPrompt(self):
        self.showInteractPrompt = False
        self.currentInteraction = None
        interactionRect = self.player.interactionRect

        if self.isSemiReadyForUnload():
            for forklift in self.loadingDockForklifts:
                targetRect = getattr(forklift, "interactionRect", forklift.rect)
                if targetRect and interactionRect.colliderect(targetRect):
                    self.showInteractPrompt = True
                    self.currentInteraction = "semiUnloading"
                    return

        if self.mode != "story":
            for control in self.spillCleanupControls:
                targetRect = getattr(control, "interactionRect", control.rect)
                if targetRect and interactionRect.colliderect(targetRect):
                    self.showInteractPrompt = True
                    self.currentInteraction = "spillCleanup"
                    return

        sortingZone = self.getZone("Sorting Area")
        if sortingZone.rect.colliderect(interactionRect):
            for pallet in self.sortingPallets:
                if pallet.rect and interactionRect.colliderect(pallet.rect):
                    self.showInteractPrompt = True
                    self.currentInteraction = "sorting"
                    return

        for control in self.storageControls:
            targetRect = getattr(control, "interactionRect", control.rect)
            if targetRect and interactionRect.colliderect(targetRect):
                self.showInteractPrompt = True
                self.currentInteraction = "conveyorRouting"
                return

        for desk in self.upgradeDesks:
            if desk.rect and interactionRect.colliderect(desk.rect):
                self.showInteractPrompt = True
                self.currentInteraction = "upgrade"
                return

    def purchaseUpgrade(self, name):
        economy.purchaseUpgrade(self, name)

    def isSemiReadyForUnload(self):
        for rig in self.semiTruckRigs:
            if rig.active and rig.startDelay <= 0 and getattr(rig, "pauseTimer", 0) > 0:
                return True
        return False


gameEngine = GameEngine
