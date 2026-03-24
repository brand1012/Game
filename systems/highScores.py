import json

def loadHighScores(path="highscores.json"):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except Exception:
        return {}


def saveHighScores(highScores, path="highscores.json"):
    with open(path, "w") as file:
        json.dump(highScores, file)
