class VehicleWave:
    def __init__(self, vehicles, restartDelay=5.0):
        self.vehicles = vehicles
        self.restartDelay = restartDelay
        self.cooldownTimer = restartDelay
        self.waitingForRestart = False

    def update(self, seconds):
        anyActive = False
        allExited = True

        for vehicle in self.vehicles:
            vehicle.update(seconds)
            if vehicle.active:
                anyActive = True
            if not vehicle.hasExitedScreen:
                allExited = False

        if anyActive or not allExited:
            self.waitingForRestart = False
            self.cooldownTimer = self.restartDelay
            return

        if not self.waitingForRestart:
            self.waitingForRestart = True
            self.cooldownTimer = self.restartDelay

        self.cooldownTimer = max(0, self.cooldownTimer - seconds)
        if self.cooldownTimer == 0:
            for vehicle in self.vehicles:
                vehicle.restartWave()
            self.waitingForRestart = False
            self.cooldownTimer = self.restartDelay


class SemiTruckWave:
    def __init__(self, rigs, restartDelay=5.0):
        self.rigs = rigs
        self.restartDelay = restartDelay
        self.cooldownTimer = restartDelay
        self.waitingForRestart = False

    def update(self, seconds):
        anyActive = False
        allFinished = True

        for rig in self.rigs:
            rig.update(seconds)
            if rig.active:
                anyActive = True
            if not rig.finished:
                allFinished = False

        if anyActive or not allFinished:
            self.waitingForRestart = False
            self.cooldownTimer = self.restartDelay
            return

        if not self.waitingForRestart:
            self.waitingForRestart = True
            self.cooldownTimer = self.restartDelay

        self.cooldownTimer = max(0, self.cooldownTimer - seconds)
        if self.cooldownTimer == 0:
            for rig in self.rigs:
                rig.restart()
            self.waitingForRestart = False
            self.cooldownTimer = self.restartDelay
