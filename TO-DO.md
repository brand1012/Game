# 1) Refactor the classes; classes like drawable.py or gameEngine.py or kirbystates are too long and difficult to parse
# 2) Change anything named 'kirby' to 'manager' or something similar - ask peers for main character name ideas
# 3) Implement easter egg for when the main character gets hit by a car, he fades and then respawns in the office
4) Add more minigames
# 5) Add time-based crises
# 6) Add a day timer, so each day has a start and an end
# 7) Add game progress saving
# 8) Add a main menu
# 9) Make minigames progress in difficulty
# 10) Add NPCs?
11) have a day where you are too tired from the night before, so your vision is all messed up
12) fix text length in cutscenes, too long for the screen right now

FEEDBACK FROM PEER FEEDBACK DAY 2 (Mar 18):
# 1) Player needs to know how to access info screen and stock
2) Add doors
3) Make the walls look more 3d
4) Spend money on snacks from vending machine, i.e. buy a monster = walk faster

FEEDBACK FROM MILESTONE 2 MEETING (Mar 27):
# 1) Make the game resizable to screen? You can obtain the screen resolution from os, pygame.display.Info(). Set upscaled to be the resolution of the montitor


OTHER FEEDBACK
# 1) conveyor belt game, colors need to be more distinguishable (right now it has yellow and orange)
# 2) should be able to take money out of your savings
# 3) fix the conveyor belt game (it doesn't end when the quota is reached)
# 4) business money does not carry over from day to day
# 5) make the minigames harder as the days go on (i.e. conveyor belt becomes faster, quota gets larger, time limit is lower)
# 6) highscore doesnt update from campaign mode minigames

FEEDBACK FROM NIKOLA GAME TESTING
1. change home screen “warehouse shift” to game title (Shift Manager)
2. fix text overflow on campaign dialogue pages
3. show in upgrade screen the amount of money, current stats
4. have conveyor game punish for wrong packages (red popup on screen and make it restart from beginning?) or maybe if you fail enough then you lose the minigame
5. maybe have a brief tour at the beginning? boss showing you around the warehouse floor, showing where each task is
6. space doesnt show anywhere on the dock unload screen
7. the spill emergency minigame happens for the first time far too late
8. make popup on forklift when the semi isn’t there saying you need to wait for the semi
9. there isnt a fail screen when you fail the semi unloading task, you should lose money/packages
10. can i make the emergency minigames actually different? maybe for manifest mismatch the zones are just swapped!
11. household expenses should be higher, it should be hard to keep stability high…
12. have a completion quota/requirement for the sorting, but it goes the entire time
13. add energy drink/character upgrades?
14. missing the quota should increase stress
15. spill game needs to come up much earlier
16. sort failure should be a -2 points
17. spill cleanup is very fast
18. dock unload game takes too long
19. speed up/down is good but why is left/right so slow?
20. decrease the amount of dock unloads in the daily quotas
21. emergencies don’t scale based on the difficulty but they should
22. savegame.json should not be deleted upon game completion