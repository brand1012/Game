import pygame


HOME_ITEMS = [
    ("rent", "Rent"),
    ("groceries", "Groceries"),
    ("medicine", "Medicine"),
    ("school", "School"),
    ("savings", "Savings"),
    ("sleep", "Sleep"),
]


def drawHomeScreen(game, surface):
    household = game.household
    surface.fill((27, 22, 26))

    title = game.myFont.render("HOME BUDGET", True, (255, 255, 255))
    surface.blit(title, (136, 14))

    cashText = game.infoFont.render(
        "Cash on hand: ${0}   Savings: ${1}".format(household.moneyOnHand, household.savings),
        True,
        (226, 226, 226),
    )
    surface.blit(cashText, (82, 34))

    statusText = game.infoFont.render(
        "Household stability: {0}   Stress: {1}".format(household.householdStability, household.stress),
        True,
        (224, 206, 168),
    )
    surface.blit(statusText, (66, 50))

    box = pygame.Rect(24, 70, 352, 96)
    pygame.draw.rect(surface, (39, 33, 38), box, border_radius=12)
    pygame.draw.rect(surface, (112, 96, 106), box, 2, border_radius=12)

    values = {
        "rent": household.rentDue,
        "groceries": household.groceriesNeed,
        "medicine": household.medicineNeed,
        "school": household.schoolDue,
        "savings": household.savings,
    }

    for index, (key, label) in enumerate(HOME_ITEMS):
        y = 80 + index * 14
        selected = index == game.homeMenuIndex
        color = (255, 220, 118) if selected else (240, 240, 240)
        if key == "sleep":
            textValue = "Finish day"
        elif key == "savings":
            textValue = "Balance ${0}".format(values[key])
        else:
            textValue = "Due ${0}".format(values[key])
        line = "{0} {1}: {2}".format(">" if selected else " ", label, textValue)
        text = game.infoFont.render(line, True, color)
        surface.blit(text, (36, y))

    message = household.lastMessage
    messageText = game.infoFont.render(message, True, (214, 198, 198))
    surface.blit(messageText, (22, 176))

    footer = game.infoFont.render(
        "Bills L/R pay $10  Savings R deposits $10  Enter sleep",
        True,
        (205, 205, 205),
    )
    surface.blit(footer, (42, 188))
