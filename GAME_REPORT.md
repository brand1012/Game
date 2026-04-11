# Game Report

## Summary

Shift Manager is a 2D warehouse-management and arcade game built with Python and Pygame. The player explores a warehouse floor, starts tasks by walking to stations and pressing `E`, and completes fast minigames to keep the shift moving. In story mode, the game unfolds over a 14-day campaign about pressure, burnout, and survival: each day begins with a briefing, moves into warehouse work, can trigger an emergency, ends with a company-pressure summary, and then shifts to a home-budget screen where the player uses take-home pay to cover rent, groceries, medicine, school costs, and savings.

To play, the player moves with the arrow keys. `E` interacts with work stations in the warehouse. Different minigames use different controls: the sorting game uses drag-and-drop with the mouse, the dock-unloading game uses movement keys plus `Space` to operate the forklift, the conveyor-routing game uses `1` and `2` to control diverters, and the spill-cleanup game uses movement keys to sweep through spills before time runs out. The game also includes an info screen, a stock/company pressure graph, high scores, story saves, and a practice mode.

## Features

### Achieved Features from the Pitch

- Skill-based challenge levels: This was one of the most successfully realized parts of the pitch. The final build includes four warehouse-themed minigames/challenges: sorting pallets by type, unloading a semi with a forklift, routing packages across conveyor belts, and cleaning up spills before they become hazards. Each challenge has its own rules, timing, scoring, and success conditions.
- How these were programmed: Each minigame is implemented as its own class and loaded using a central framework. That made it possible to reuse the same launch/results flow while giving each minigame custom input and mechanics. For example, the sorting game maps freight sprites to categories and checks drag-and-drop collisions with labeled bays, the semi-unloading game uses forklift hitboxes, trailer slots, and wall collision penalties, and the conveyor game spawns boxes over time and routes them through diverters.
- Tycoon progression system: The game does connect work performance to money and progression. The player earns money and shipped-package totals through both passive warehouse income and minigame results, then spends business money on upgrades that improve warehouse output. The stock/company pressure graph also reinforces the idea that work performance affects the business over time.
- Upgrade system: While the final upgrade tree is simpler than the one in the pitch, it is functional. The player can buy extra workers, extra vans, and larger van capacity. These upgrades are tied to increasing costs, so progression still has the "money -> upgrades -> better output" loop described in the original proposal.
- Day/shift cycle system: This was achieved and expanded upon. Story mode includes daily briefings, shift quotas, day progress, emergencies, a day summary screen, a company pressure screen, and a home phase where the player manages bills, savings, stress, and household stability. This added a stronger ludonarrative than the original pitch.
- Dynamic difficulty scaling: This feature was implemented through day-based difficulty tables. As the campaign advances, timers get shorter, objectives get larger, and hazards become harder. The conveyor game speeds up, sorting requires more correct responses, the dock unload asks for more pallets, and emergency variants use harder settings.
- One-business-setting demo with 3-4 challenge types: The pitch said the demo would focus on one warehouse setting with 3-4 unique challenge types, and the final game meets that goal. The entire experience is built around the warehouse environment, with multiple activity zones and a consistent visual/gameplay theme.
- Story and tone: The pitch described a semi-satirical tone about hustle culture and burnout. The final version actually leans even harder into this idea through the story campaign, named coworkers and supervisors, emergencies, household bills, stress, and multiple endings based on performance and safety choices.

### Features Not Achieved or Only Partially Achieved

- Contract selection screen: The original pitch described each workday as choosing contracts and then completing them for different rewards. The final game does not have a separate contract-selection management screen. Instead, story mode assigns daily quotas automatically, and the player enters tasks by moving around the warehouse and interacting with stations. Building a full contract UI and balancing different reward structures would have added another major layer of systems design that I didn't think would be worth it for the minimal, if any, benefit to the player experience.
- Specific pancake/breakfast minigame: The pitch specifically mentioned a breakfast or pancake-catching challenge. That exact minigame was not implemented. The final set of tasks stayed focused on warehouse activities so the mechanics, art, and story all matched the same setting.
- Larger upgrade tree with automation, power-ups, and double contracts: The final upgrade system is much narrower than the pitch's original tree. Features like automation, power-ups, faster worker speed, and double contracts were not completed. A big setback was scope, because each of those upgrades would need balancing across several minigames and the economy system.
- Risk/reward contracts and randomized modifiers: These stretch goals were not implemented. The game uses authored story beats and scripted emergencies instead of randomized daily modifiers or contract tradeoffs. That was the safer choice for a solo project because it kept tuning and difficulty progression manageable.
- Multi-task challenges: The stretch idea of running two minigames at once was not achieved. That kind of mechanic would have required a much more complicated UI and game-state system, especially when the project already had several separate minigames and story screens.
- Active employee NPCs with buffs: The final game includes named characters in dialogue, but not roaming employee NPCs who actively change gameplay or give passive buffs. Implementing pathing, interaction logic, and meaningful buffs would have taken more time than was available.
- Original CEO framing: The pitch initially described the player as a CEO personally completing challenges. The final version shifted toward a worker or shift-level perspective with supervisors, coworkers, bills, and home-life stress. This was less of a failure and more of a design evolution, but it is still a clear change from the first pitch.

## Feedback

### Peer Feedback Assignment 1

The first round of feedback focused on structure, progression, and clarity. The main themes were adding more content, making the game feel more like a full day-by-day experience, improving usability, and polishing presentation. Suggestions included adding more minigames, time-based crises, a clear day timer, save functionality, a main menu, difficulty progression across days, possible NPCs, and fixing cutscene text that was too long for the screen.

This feedback had a big impact on the project's direction. The biggest changes I incorporated were the main menu and continue system, persistent story saves, a more complete day cycle, escalating difficulty, and improved dialogue and briefing text layout. In other words, peer feedback helped push the game from a collection of warehouse tasks into a more organized story campaign. Some feedback from this round remained incomplete, especially adding even more minigames and full NPC behavior, because those were larger scope additions.

### Peer Feedback Assignment 2

The second round of feedback was more focused on readability and communication with the player. Players wanted clearer directions for accessing the info and stock screens, better environmental clarity such as doors and stronger wall visuals, and extra interaction ideas like buying snacks from a vending machine for a speed boost.

The biggest change I clearly incorporated from this round was stronger UI signposting. The HUD now shows controls for the info screen, stock or company-pressure screen, and briefing screen, which directly addresses the problem of players not knowing how to access those menus. The overall flow of briefing, results, stock or company pressure, and home screens also makes the game easier to understand moment-to-moment. However, some of the other suggestions from this round were not fully completed. I did not finish a vending-machine power-up system, and the environmental suggestions like doors or more 3D wall styling were lower priority than finishing the campaign systems and minigames. Even so, the feedback helped me prioritize onboarding and readability, which made the final version easier to play.

### Overall Impact of Feedback

Across both peer feedback assignments, the most valuable outside input was not just "add more stuff," but "make the game easier to understand and easier to follow." That feedback changed the project in a real way. The final version is much more structured, has clearer interfaces, keeps progress between sessions, scales difficulty across the campaign, and communicates goals more directly. The feedback also helped me decide which ideas were core to the game and which ones were better left as future improvements once the main gameplay loop was working.
