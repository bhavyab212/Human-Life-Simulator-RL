# Human Life Simulator — Expanded Design Document
## Every Edge Case, Variable, Action, and Human Scenario

---

## NEW VARIABLES TO ADD

### Core Stats (existing — kept)
- energy: 0–100
- happiness: 0–100
- health: 0–100
- academic_score: 0–100
- stress: 0–100
- social_bonds: 0–100
- money: 0–200
- sleep_debt: 0+
- hour_of_day: 0–23
- day_of_week: 0–6

---

### NEW Variables (add these)

**creativity: 0–100 (starts at 50)**
- Builds when doing personal projects, drawing, music, journaling
- Decays when only attending class and studying mechanically
- High creativity (>70) gives academic +5 bonus on essay-type work
- Very high creativity (>85) unlocks the `build_project` action
- Low creativity (<20) makes watch_netflix and scroll_phone give 0 happiness

**motivation: 0–100 (starts at 60)**
- The hidden multiplier most environments ignore
- High motivation (>70): study gives +1.5x academic gain
- Low motivation (<30): attend_class gives only 50% academic gain
- Hits 0: agent can only scroll_phone, eat_junk, sleep — all other actions locked
- Restored by: completing goals, socializing, exercise, achieving exam scores >70
- Destroyed by: repeated failure, burnout near-misses, isolation

**reputation: 0–100 (starts at 50)**
- How the student is perceived by peers and professors
- High reputation (>70): socializing gives +5 extra social_bonds
- High reputation (>80): professors give assignment extensions (deadline +24 steps once per episode)
- Low reputation (<30): group_study invitations stop coming
- Affected by: skipping class repeatedly, academic performance, social actions

**focus_level: 0–10 (starts at 5)**
- Tracks how deep into flow state the student currently is
- Each consecutive study/work action increases focus by 1
- Any interruption (scroll_phone, socialize, notification) resets focus to 0
- Focus > 7: study gives +2 bonus academic per step (flow state bonus)
- Focus = 10: "deep work mode" — study gives double gains for that step only

**loneliness_streak: int (starts at 0)**
- Counts consecutive hours with no social interaction
- Above 24 hours: happiness passive drain -1 per step
- Above 48 hours: health -0.5 per step (isolation physically harms)
- Above 72 hours: motivation drops to 20 regardless of other stats
- Reset by: any action involving another person

**caffeine_level: 0–100 (starts at 0)**
- Tracks coffee/energy drink consumption
- High caffeine (>60): energy +15 bonus but sleep quality halved when sleeping
- Very high caffeine (>80): stress +5 passive per step (anxiety)
- Caffeine above 90: heart palpitations — health -1 per step
- Decays naturally by 10 per step
- Caffeine crash: when caffeine drops from >70 to <30 in one step → energy -20

**assignment_queue: list of dicts**
- Tracks active assignments with due dates
- Each assignment has: name, due_step, difficulty (1–3), submitted (bool)
- Missing a deadline: academic -20, stress +15, reputation -10
- Submitting on time: academic +difficulty×5, reputation +5
- Submitting early: reputation +10, stress -5 (relief bonus)

**friendship_depth: dict {friend_id: 0–100}**
- Tracks quality of individual friendships, not just aggregate social_bonds
- 3 friends initialized: Friend A (depth 40), Friend B (depth 20), Friend C (depth 10)
- Deep friendship (>70): that friend can help you (see friend events)
- Shallow friendship (<20): socializing with that person gives only 30% normal gains
- Friendship decays 2 points per day without contact

**emotional_state: enum**
- Current dominant emotion: neutral, anxious, depressed, euphoric, focused, burnt_edge
- Transitions based on combinations of stats
- Each state modifies action outcomes differently (see emotional state section below)

**gut_health: 0–100 (starts at 70)**
- Separate from general health
- Affected by: eat_junk (-5), eat_healthy (+8), irregular meal timing (-3)
- Low gut health (<30): happiness passive drain -2 per step (gut-brain axis)
- Very low gut health (<15): concentration halved — study gains -50%
- Recovered only by: 3+ consecutive eat_healthy actions

**sleep_quality: 0–100 (starts at 70)**
- Not just duration — how good the sleep actually was
- Factors that reduce sleep quality: high caffeine, high stress, screen use before sleep
- High quality sleep (>70): sleep recovers +5 extra energy on top of normal
- Low quality sleep (<30): sleep debt still increases even after sleeping

**self_discipline: 0–100 (starts at 50)**
- Builds slowly through consistent good choices
- Decays through repeated avoidance behaviors
- High discipline (>75): procrastinate action is weakened — stress gain only +5 instead of +15
- High discipline (>90): agent can resist temptation actions (skip_class, procrastinate cost -1 extra reward)
- Low discipline (<25): after skip_class, next action is forced to be procrastinate or scroll_phone (momentum effect)

**environmental_noise: 0–10 (starts at 3)**
- How chaotic/noisy the student's environment is
- Increases: roommate conflict, party next door (random event), public spaces
- Decreases: library, late night alone, noise-canceling headphones (purchasable)
- Above 6: focus_level cannot exceed 4
- Above 8: study is completely ineffective (0 academic gain)

---

## NEW ACTIONS (add to the existing 14)

---

**15. build_personal_project**
- Requires: creativity > 85 OR motivation > 80
- Energy -12, Happiness +18, Academic +3, Creativity +15, Stress -5, Focus +2
- Does NOT count as studying but improves academic through applied learning
- If completed (3 consecutive build actions): reputation +20, motivation +30, unlocks `showcase_project`
- Real dilemma: working on your passion vs. studying for the exam that's in 48 steps

---

**16. group_study**
- Requires: at least one friendship_depth > 40
- Energy -8, Happiness +8, Academic +10, Social +8, Stress -3
- Better than solo study for academic per step AND social
- BUT: if environmental_noise > 5, group study gives only academic +3 (distracted group)
- If studying with a friend whose academic_score > yours by 20: you get +15 instead of +10 (learning from better peers)
- If everyone in group is low academic: you get academic +5 only (blind leading the blind)

---

**17. drink_coffee**
- Energy +20, Caffeine +30, Stress +5
- Instant energy but starts the caffeine clock
- Stacked with study: next study action gets focus_level +3 instantly
- Cannot sleep effectively for 6 steps after this action
- Third coffee in a day: health -5, gut_health -10

---

**18. journal / reflect**
- Energy -2, Happiness +8, Stress -10, Creativity +8, Motivation +10, Self_discipline +3
- The underrated action. No academic gain. No money. But resets emotional_state toward neutral
- If stress > 70 when journaling: unlocks insight — next study session gets +5 bonus academic
- If done before sleep: sleep_quality +20 for that sleep action

---

**19. take_a_walk**
- Energy -5, Happiness +10, Health +5, Stress -8, Creativity +5, Focus +1
- Low cost stress relief. No money needed. No social needed.
- If done when environmental_noise > 7: stress reduction doubles (-16 instead of -8)
- Consecutive walks (2+): motivation +5 each time (momentum)
- If done at hour_of_day between 6–8 (morning walk): sleep_quality +10 for next sleep

---

**20. attend_office_hours**
- Requires: reputation > 30
- Energy -5, Academic +15, Stress -5, Reputation +8
- Best academic gain per step — better than class
- But: available only between hour_of_day 14–17 (2pm–5pm)
- Only 2 per week allowed (professor availability)
- If reputation < 30: professor is too busy / doesn't know you → -1 reward

---

**21. help_a_friend**
- Requires: a friendship with depth > 30 AND energy > 30
- Energy -10, Happiness +15, Social +20, Friendship_depth[friend] +25, Stress -5
- Costs your time but builds deep bonds
- Deep friendship payoff: friend helps you later (see friend events)
- If you help a friend when YOU have an exam within 24 steps: -8 reward (sacrifice)
- But that friend's friendship_depth jumps to 80+ → they help you in a crisis later

---

**22. skip_class_and_self_study**
- Energy -5, Academic +6, Creativity +5, Happiness +5, Reputation -5, Stress +3
- The nuanced middle ground between attending and skipping entirely
- Student skips the class but works on their own — YouTube lectures, papers, projects
- Academic gain less than attend_class (+6 vs +12) but student learns what THEY want
- Creativity bonus reflects autonomous learning
- Reputation still takes a hit (professor notices absence)
- If done 3+ times: self_discipline +5 (proving you can study alone), but reputation -15 total

---

**23. cold_shower**
- Energy +15, Stress -12, Health +3, Caffeine -20
- Instant reset button. Free. Always available.
- No negative effects except a tiny happiness -2 (uncomfortable)
- Best when: caffeine crash incoming, stress spiking, energy low before a big step
- Consecutive days (3+): health +5 bonus (habit forming)

---

**24. cook_at_home**
- Energy -5, Health +15, Gut_health +10, Money -5, Happiness +10, Creativity +3
- Better than eat_healthy (which assumes takeout/cafe)
- Costs more time and slightly more focus but gut_health recovery is unique to this action
- If done with a friend (friendship_depth > 50 with anyone): social +10 bonus for free
- Unlocks if cook_at_home done 5 times: `meal_prep` action

---

**25. meal_prep**
- Requires: cook_at_home done 5+ times total
- One action that prepares food for the next 3 steps
- Those 3 steps automatically get eat_healthy benefits without spending an action
- Energy -15 (big upfront cost), Money -15, but saves time and money over next 3 steps
- Self_discipline +5 (planning ahead)

---

**26. call_family**
- Energy +5, Happiness +20, Stress -15, Loneliness_streak reset to 0, Money 0
- No cost. High emotional return.
- Available anytime but most effective when loneliness_streak > 24
- If done when stress > 80: stress -25 instead of -15 (parental support)
- If skipped for 4+ days: happiness passive drain -1 per step (guilt/distance)
- Does NOT increase social_bonds (family is separate from peer social)

---

**27. therapy_session / counseling**
- Requires: stress > 60 OR emotional_state == depressed
- Money -30 (or free if campus counseling — random event can unlock free sessions)
- Stress -30, Happiness +20, Motivation +25, Emotional_state → neutral
- Takes 2 steps (back-to-back; skipping the second step halves the effect)
- Reputation unaffected (private)
- One of the highest-impact actions in the game — but expensive and time-consuming

---

**28. doomscroll (extended)**
- Distinct from scroll_phone — this is 2+ hours of mindless consumption
- Energy +2, Happiness +3 → then happiness -8 (post-scroll regret)
- Stress +8, Self_discipline -5, Motivation -10, Focus reset to 0
- The trap: it FEELS like scroll_phone initially but the delayed effects are brutal
- If doomscroll happens 3+ days in a row: emotional_state → depressed

---

**29. all_nighter**
- One action that represents staying up all night
- Academic +20 (cramming), Stress +25, Energy -40, Sleep_debt +8, Health -5
- High risk high reward — only rational when exam is next step
- If health < 40 when attempting: energy crashes to 0 mid-way → all_nighter fails, get academic +7 only
- Sleep quality for next sleep -40 regardless (body remembers)
- If done before final exam: academic score captured is inflated by +10 but stress penalty carries forward

---

**30. take_exam** (triggered automatically but can also be chosen)
- Fires at step 72 and step 144 automatically
- If academic_score > 70: pass with bonus
- The agent's preparation across 72 steps is what matters
- But: if stress > 80 when exam fires → academic score used is academic_score × 0.7 (test anxiety penalty)
- If sleep_debt > 15 when exam fires → academic score used is academic_score × 0.6
- If motivation < 20 when exam fires → academic score used is academic_score × 0.5

---

**31. pull_a_prank / be_spontaneous**
- Random chaos action. Represents doing something unexpected.
- Happiness +25, Social +10, Reputation ±15 (random — could go either way)
- Stress -10 (fun releases pressure)
- Small chance (20%) of going viral in campus group chat → reputation +30
- Small chance (15%) of annoying the wrong person → friendship_depth[random_friend] -20
- Completely unpredictable — models real human spontaneity

---

**32. do_nothing / stare_at_ceiling**
- The zero action. Agent chooses to do absolutely nothing.
- All passive drains still apply (energy -0.5, stress +0.3, last_meal_hours_ago +1)
- No positive or negative reward
- But: if done when stress > 70 → stress actually drops -3 (sometimes doing nothing IS the answer)
- If done 3+ consecutive steps: motivation -5 per step (inertia builds)
- If done after burnout near-miss (stress was 95+): stress -8 (body forces rest)

---

**33. half_study / skim**
- Represents doing the bare minimum — reading notes passively, watching a video at 2x
- Energy -3, Academic +3, Happiness -1, Stress +1
- Half the cost of study, half the gain — but the compounding is different
- If done 4 consecutive times instead of 2 proper study sessions: same academic gain, LESS stress
- Models pacing — sometimes consistent low-effort beats sporadic high-effort

---

**34. micro_socialize (text a friend)**
- Energy 0, Happiness +5, Social +3, Loneliness_streak -12 hours, Money 0
- The minimum viable social action — just texting
- Doesn't require leaving the room
- Doesn't fully replace face-to-face socializing for social_bonds
- But: prevents loneliness_streak from getting dangerous without spending energy

---

**35. binge_eat**
- Energy +15, Happiness +10 (temporarily), Health -20, Gut_health -20, Stress -5
- Emotional eating under stress. Triggered often when stress > 75.
- The worst health action but a genuine human behavior
- If done when emotional_state == depressed: stress reduction is -15 (comfort eating actually works short-term)
- Next step after binge_eat: happiness -10 (regret), gut_health drops further -5

---

**36. nap_in_class**
- Can only be chosen during hours when class would normally occur
- Energy +8, Academic -5, Reputation -10, Stress -5
- You recover some energy but you miss the class content AND get caught
- If reputation < 20: professor calls you out → stress +10 on top of everything

---

**37. plagiarize**
- Academic +25 instantly, Stress -10 (short-term relief)
- 30% chance of getting caught each time used
- If caught: academic_score → 0, reputation → 0, stress +50, episode near-ending
- If not caught: lingering stress +3 per step for rest of episode (paranoia)
- Models moral risk-taking under extreme pressure

---

**38. withdraw_from_course**
- One-time action per episode (can only do once)
- Removes one assignment from assignment_queue permanently
- Stress -20, Academic_score -10 (course withdrawal penalty)
- Reputation -5
- Sometimes the right call — sacrificing one course to save the semester

---

**39. seek_peer_notes**
- Requires: friendship_depth > 40 with at least one person
- Energy -2, Academic +8, Social +5, Money 0
- Get notes from a friend for a missed class
- Less effective than attending (+8 vs +12) but repairs the damage of skip_class
- If friend's academic_score > 70: you get academic +12 (good notes from a smart friend)

---

**40. listen_to_music_while_studying**
- Not a standalone action — a MODIFIER applied to study
- If chosen: study becomes study_with_music
- study_with_music: energy -8 (less than study), academic +5 (less than study +8), happiness +5, stress -3
- Models focus trade-off: music helps some people, hurts others
- If focus_level > 6: music actually hurts — academic +3 only (distraction)
- If focus_level < 3: music helps — academic +7 (background noise fills the void)

---

## EDGE CASES — THE FULL LIST

---

### ACADEMIC EDGE CASES

**EC-A1: Skip class → personal project → exam**
Student skips a lecture and instead builds something real — a personal project, a side hustle, an experiment. Academic score doesn't rise from class, but creativity +15 and motivation +20. If exam is within 48 steps and academic_score < 50: huge risk. But if the project is completed (3 consecutive build actions): reputation +20 which reduces exam stress penalty. Real dilemma: short-term academic safety vs long-term reputation and motivation.

**EC-A2: Perfect attendance, zero learning**
Agent attends every class but never studies outside. Academic +12 per class step, but without additional studying or self-discipline, the gains don't compound well. Academic score plateaus around 60. Passes exams but barely. Models the student who shows up but never actually learns.

**EC-A3: Never attends, self-teaches everything**
Uses skip_class_and_self_study exclusively. Academic gain per step is lower (+6 vs +12) but creativity and self_discipline build. Reputation tanks (-5 per skip). If reputation drops below 20: cannot use attend_office_hours, group_study invitations stop, professor won't grant extensions. Can still pass if self-study is consistent, but reputation damage is permanent.

**EC-A4: Plagiarism spiral**
Agent plagiarizes once under pressure. Not caught (70% chance). Does it again. Not caught. Third time: caught. Academic → 0, reputation → 0. Episode becomes about survival and damage control. Models the real psychological spiral of academic dishonesty.

**EC-A5: Assignment submitted early**
Agent finishes and submits an assignment 48+ steps before the deadline. Reputation +10, stress -5 relief bonus. But: the agent spent energy and focus when they could have socialized or rested. Is early submission worth it? Only if stress was already high and reputation needed repair.

**EC-A6: Half-measure studying vs. full cramming**
Agent does half_study 6 times instead of study 3 times. Same academic total (+18 either way), but stress accumulation is lower (half_study stress +1 vs study stress +5). Over 72 steps, the pacing difference is enormous. The slow-and-steady agent beats the cramming agent on stress management even with identical academic scores.

**EC-A7: Group study with wrong people**
Three friends, all academic_score < 40. Group study together. Everyone contributes nothing useful — academic gain only +5 per step. But social_bonds +8 and friendship_depth all increase. The group study was socially valuable but academically wasteful. Good call? Depends on whether you need academics or social stability more urgently.

**EC-A8: Study group with one genius**
One friend with academic_score 85. Agent joins their study session. Agent gets academic +15 (learning from the best). But: that friend's friendship_depth must be > 60 for them to actually explain things. If friendship is shallow, they study in silence and you get +8.

---

### SOCIAL AND FRIENDSHIP EDGE CASES

**EC-S1: The friend who needs you when you need to study**
Friend A friendship_depth = 75 (deep bond). Friend A sends distress signal (random event). help_a_friend action available. Exam in 36 steps. Helping takes 2 steps, sets your studying back. But refusing: friendship_depth[A] -30, and if A was going to help you later (friend event), that help is now cancelled. Optimal: help for 1 step, not 2. Models real human trade-offs between loyalty and self-interest.

**EC-S2: Social butterfly with no depth**
Agent socializes constantly — social_bonds maxes at 100. But friendship_depth across all friends remains shallow (<30 each). Social_bonds gives rewards. But when friend events fire (crisis, study help, emergency loan), none of them help because no friendship is deep enough. High social capital, zero real support network.

**EC-S3: Lone wolf who calls family**
Zero social_bonds with peers. But calls family every day. Loneliness_streak never exceeds 24 hours (call_family resets it). Happiness stays moderate. Stress management is slightly worse (family can't help with roommate issues or exam anxiety the same way). Viable but suboptimal — models the student who stays close to home and never fully adapts to college social life.

**EC-S4: The toxic friendship**
Friend C has depth 60 but every interaction raises your stress +5 (toxic relationship flag — assigned at environment init for one random friend). Socializing with this person gives normal happiness but hidden stress cost. Agent must learn to identify and reduce contact with toxic friend — something no standard RL environment models.

**EC-S5: Friendship saved by crisis help**
Friend B has depth 15 (shallow). B is in trouble (random event). Agent helps anyway (help_a_friend). Depth jumps from 15 to 65 instantly. B now qualifies as a deep friend. Later, B helps agent with peer notes, emergency money loan, or emotional support. The entire trajectory of that relationship changed in one decision.

**EC-S6: Party the night before exam**
Agent socializes at hour_of_day 22 (10pm). Exam fires at step +8. Happiness +20, social +15. But: reward is -4 (exam within 24 steps). Sleep after party: sleep_quality -20 (was up late, probably drank, stimulated). Exam fires with sleep_debt higher, stress higher. Social gain isn't worth it. But the agent has to LEARN this — it feels like a good decision when you make it.

**EC-S7: Study group that becomes a friend group**
Three consecutive group_study actions with same friends. Academic gains happen. But friendship_depth increases across all three by 10 per session. After the third session: these people are now genuine friends (depth 50+). Future group studies are more effective, and friend events unlock. The study group became a support system. Models the organic formation of college friendships.

**EC-S8: Complete social withdrawal during finals**
Agent locks in: no socialize, no micro_socialize, no help_a_friend for 72 steps (3 days). Social_bonds decay -2/day. Loneliness_streak hits 72 hours → motivation drops to 20. Even with perfect studying, motivation penalty makes academic gains 50% less effective. Final academic score is lower than if agent had taken 2 socialize breaks. Isolation is academically counterproductive past a threshold.

**EC-S9: The group chat without meeting**
Agent uses micro_socialize repeatedly instead of real socializing. Loneliness_streak stays low. Social_bonds only grow +3 per action (vs +15 for real socializing). After 7 days of only micro_socializing: social_bonds = 71, but friendship_depth remains shallow on all friends. Technically not lonely, but no real depth. When friend events fire, help is minimal.

**EC-S10: Spontaneous connection**
pull_a_prank fires and randomly targets Friend C (the potentially toxic one). Prank goes well (80% chance in this case). Both laugh. friendship_depth[C] +30. Toxic flag removed for that friend (surprise — sometimes what looked toxic was just distance). Models how unexpected shared moments can repair or transform relationships.

---

### MONEY AND RESOURCE EDGE CASES

**EC-M1: Broke but creative**
Money hits 0. exercise, eat_healthy, socialize all locked. Agent is forced into: eat_junk, scroll_phone, watch_netflix, study, sleep. A miserable loop that destroys health and gut_health while academic score is the only thing the agent can work on. But: if agent works one part-time shift → +50 money → all options unlock again. The one work shift is worth it even though it costs energy and academic score.

**EC-M2: Money hoarding**
Agent works part-time 3 times, accumulates 250 money (capped). Never exercises, always eats healthy (money -20 per action). Money never becomes a problem but agent has spent 3 high-cost steps (energy -20 each, academic -5 each, stress +10 each) on earning money they don't fully need. Suboptimal. Money should be managed just enough to keep options open, not maximized.

**EC-M3: Emergency money from a friend**
Friend with depth > 70 can lend money during money crisis (random friend event). +30 money. No work step required. But: you owe them — next help_a_friend action costs 0 energy but is mandatory (social contract). If you refuse to help them back: friendship_depth -40.

**EC-M4: Cook saves everything**
Money is low (30 remaining). Agent discovers cook_at_home: health +15, gut_health +10, money -5 only (much cheaper than eat_healthy at -20). Cooking is strictly better per money unit. But it requires energy -5 and an extra step of setup. The agent who discovers cooking is economically dominant in the late game.

---

### HEALTH AND BODY EDGE CASES

**EC-H1: The junk food spiral into sickness**
eat_junk 3 consecutive days: health -10 per action = -30 total, then habit penalty fires (-5 more). Health now at 35. Below 40, gut_health is also low. Sleep only recovers 50% energy (sick). Study sessions are less effective. The student is sick, tired, and falling behind — all from food choices made days ago.

**EC-H2: Caffeine dependency**
drink_coffee every morning for 5 days. Caffeine level never fully clears before next coffee. Sleep quality -40 every night (can't sleep well with caffeine). Sleep debt accumulates. By day 5: sleep_debt at 20 hours, study gains at 50% due to sleep debt. The coffee that was supposed to help is now making everything worse.

**EC-H3: Exercise unlocks the cascade**
Agent exercises consistently (every 2 days). Health stays above 70. Sleep quality is high (physical tiredness = better sleep). Energy recovery from sleep is maximized. Stress stays manageable. Academic gains aren't directly boosted by exercise but everything that supports academic gains IS boosted. Exercise is the root action that stabilizes the entire system.

**EC-H4: Sick during exam**
Health dropped below 30 before step 72. Exam fires. Agent is sick. No specific exam penalty for sickness directly — but sleep was only 50% effective for days, creating sleep_debt, which then reduces exam academic_score multiplier. Sickness doesn't fail you directly; it fails you indirectly through every other system.

**EC-H5: Cold shower caffeine crash prevention**
Caffeine at 75. Agent is about to hit caffeine crash (next step caffeine drops below 30). Chooses cold_shower: caffeine -20, energy +15, stress -12. The crash is now a gentle landing instead of a collapse. Smart resource management of internal body chemistry.

**EC-H6: Recovery arc**
Agent hits burnout edge (stress 95) and emotional_state = burnt_edge. Chooses: do_nothing (stress -8 from forced rest) + journal (stress -10, motivation +10) + take_a_walk (stress -8, creativity +5) + sleep with journal bonus (sleep_quality +20). Three steps of what looks like "doing nothing" pulls the student back from the edge. Models genuine recovery.

---

### TIME AND SCHEDULING EDGE CASES

**EC-T1: The perfect morning routine**
Steps 0–3 of any day: take_a_walk (6am) → cook_at_home (7am) → journal (8am) → attend_class (9am). Four consecutive good choices before 10am. Focus_level builds, gut_health up, stress down, motivation up. The class at 9am gets academic +12 PLUS motivation multiplier (1.5x) = effectively +18. Morning routine is the highest-leverage thing in the game.

**EC-T2: The 3am study session**
Hour_of_day = 3. Stress = 60. Exam in 6 steps. Agent studies at 3am. Energy is low, sleep_debt is high, sleep_quality will suffer. study runs at degraded efficiency. But the agent panics and does it anyway. The academic gain is real but the cost is paid over the next 12 hours in crashed performance.

**EC-T3: Office hours timing**
Office hours only available 14:00–17:00. Agent doesn't track hour_of_day carefully. Tries attend_office_hours at 10am: action fails (-1 reward). Tries at 2pm: succeeds (+15 academic, best single-step academic gain in the game). Time-aware scheduling is a meta-skill the agent must learn.

**EC-T4: The deadline sandwich**
Two assignments due within 24 steps of each other. Agent can only fully complete one. Must choose: complete the harder one (difficulty 3, academic +15, but takes 3 study actions) or the easier one (difficulty 1, academic +5, takes 1 action) and partially complete the harder one. Missing the harder deadline: academic -20, stress +15. The triage decision is real.

**EC-T5: Weekend vs Weekday behavior**
day_of_week 5–6 (weekend): no classes fire. No office hours available. But: stress passive drain is lower on weekends (social norm — everyone relaxes). Optimal weekend use: deep study sessions (no class interruptions), social recovery, exercise, cooking. Agent that treats weekends like weekdays burns out faster. Agent that treats weekdays like weekends fails academically.

---

### MENTAL AND EMOTIONAL EDGE CASES

**EC-E1: Motivation collapse**
Motivation hits 0 after repeated failure. study, attend_class, exercise all locked. Only available: scroll_phone, watch_netflix, sleep, eat_junk, do_nothing, doomscroll. The agent is in a depressive episode — not burned out (stress isn't 100) but completely unmotivated. Only ways out: call_family, journal, therapy_session, or a random positive event. Models clinical depression-adjacent states.

**EC-E2: Euphoric overconfidence**
After passing first exam with score 80 → emotional_state = euphoric. Euphoric state: all actions cost 20% less energy (confidence boost). But: skip_class becomes more tempting (happiness gain looks higher). Agent skips 3 classes in euphoric state. Comes down. Academic score has dropped. Euphoria caused overconfidence. The good outcome set up the bad behavior.

**EC-E3: Journaling before sleep changes everything**
journal → sleep in consecutive steps. Journal gives stress -10 and sleep_quality +20. Sleep with high quality: energy +25 + 5 bonus = +30. Sleep_debt drops by 8. Morning energy starts at 80+ instead of 50. The entire next day is more productive. One small habit compounds into everything.

**EC-E4: The anxiety loop**
High stress → can't sleep well → sleep debt rises → study less effective → academic score stagnates → stress rises further. No single action breaks all of these simultaneously. The agent must identify the intervention point: meditate (stress -20) breaks the loop. But meditate costs a step, and the agent may keep choosing to study instead (optimizing the wrong metric).

**EC-E5: Emotional eating cascade**
Stress > 75 → emotional_state = anxious → binge_eat fires (agent or automatic) → health -20, gut_health -20 → next step happiness -10 (regret) → stress +5 (guilt) → emotional_state = depressed → doomscroll (automatic temptation) → motivation -10. Five steps of cascading harm from one moment of high stress. The cascade is real and modeled here.

**EC-E6: The comeback arc**
Episode is at step 100. Academic score is 35. Stress is 70. Money is 20. Motivation is 15. Most agents give up (high stress, low academic, low money = spiral). But: therapy_session (stress -30, motivation +25) → motivation unlocks actions → study with renewed motivation (1.5x academic) → healthy eating → exercise → social recovery. By step 144 (second exam): academic score 58. Passed. The comeback is possible and the grader should reward it.

---

### SYSTEMIC / COMPOUND EDGE CASES

**EC-SY1: The half-action optimizer**
Agent never takes "big" actions. Instead: micro_socialize (not full socialize), half_study (not full study), nap (not sleep), scroll_phone (not watch_netflix), take_a_walk (not exercise). Each action costs less, gains less. But the agent takes 2x more actions because each costs half the energy. Over 168 steps, the cumulative gains match a full-action agent — but stress is dramatically lower. This is the "pacing" strategy and it's genuinely superior for stress management.

**EC-SY2: The specialist**
Agent only maximizes academic. Every step: study or attend_class. Never socializes (social_bonds hit 0 at step 40 → all positive rewards halved). Never exercises (health declines → sleep efficiency drops). Never journals (stress climbs). Exam score is high on the first exam. But by step 144: sleep_debt is massive, stress near burnout, motivation low. Second exam score collapses. The specialist loses to the generalist in the long run.

**EC-SY3: The energy manager**
Agent treats energy as the primary constraint (which it is). Every action chosen based on energy cost first. Naps before big study sessions. Drinks coffee strategically. Never falls below 30 energy. This agent may not maximize any single stat but never hits constraints that lock actions. The energy-aware agent has more optionality than any other strategy.

**EC-SY4: Reputation as unlock condition**
Agent neglects reputation (stays around 25). Cannot use attend_office_hours (requires >30). Cannot receive professor extension (requires >80). Cannot lead group study (requires >60). Reputation is a hidden second-order resource that most agents discover too late. Once reputation is below 20, rebuilding requires 5+ consecutive positive actions just to unlock the basic options.

**EC-SY5: The build project payoff**
Steps 1–60: Agent studies normally, academic = 58. Steps 61–70: Stops studying. Builds personal project instead (3 build_personal_project actions). creativity maxes. motivation hits 90 (1.5x academic multiplier). Reputation +20 (project showcase). Steps 70–72: Returns to study with motivation multiplier. Academic jumps from 58 to 74 in just 2 steps. Passes exam with 74. The detour WAS the optimal path.

**EC-SY6: The trust fall**
At step 150 (18 steps from end), a deep friend (depth >75) offers: "let me explain the material to you — I'll tutor you for 2 steps." This is a friend event. Agent gets academic +20 over 2 steps (friend tutoring is the highest academic gain per step in the game). This only fires if: (1) you have a friendship deep enough, (2) you helped them at some point earlier. The friend investment pays off at the critical moment.

**EC-SY7: Nothing works, and that's real**
Rare scenario: all systems cascading negatively simultaneously. Sick (health < 30), broke (money = 0), lonely (social_bonds = 0), motivated (motivation = 0), sleep_debt = 20hrs, emotional_state = depressed. Almost no actions are effective. The agent is in genuine crisis. Only exits: call_family (free, always available, high emotional impact), do_nothing (passive stress drain when near burnout), therapy (if somehow money found). Models the reality that sometimes multiple systems fail simultaneously and there's no clean solution — only damage control.

---

## RANDOM EVENTS SYSTEM

Fire probabilistically at certain steps. Agent cannot control these.

| Event | Trigger Condition | Effect |
|---|---|---|
| Friend needs help | day 2, 4, or 6 | help_a_friend option appears for 3 steps |
| Assignment announced | day 1 and day 4 | new entry added to assignment_queue |
| Roommate conflict | random, once per episode | environmental_noise +4 for 24 steps |
| Professor cancelled class | random, 20% chance each class | attend_class gives 0 but energy saved |
| Free campus food | random, once per week | eat_healthy free (money 0) for 1 step |
| Campus counseling open | day 3 or 5 | therapy_session costs 0 for next 12 steps |
| Study group invitation | requires reputation > 40 | group_study available for 6 steps |
| Internship opportunity | requires academic > 75, reputation > 60 | bonus +30 to final grade score |
| Viral moment | after pull_a_prank, 20% chance | reputation +30, happiness +20 |
| Family calls you first | random if you haven't called in 3 days | happiness +15, stress -10 (no action needed) |
| Exam postponed | random, 10% chance | deadline extended by 24 steps |
| Power outage | random, once | scroll_phone, watch_netflix unavailable for 12 steps |
| Friend pays back loan | 10 steps after emergency money | money +30 returned |

---

## EMOTIONAL STATE SYSTEM

The current dominant emotion changes how actions behave.

| State | Trigger Condition | Effect on Actions |
|---|---|---|
| neutral | Default | All actions normal |
| anxious | stress > 65 | study gains -20%, procrastinate temptation higher |
| depressed | loneliness > 72hrs + happiness < 25 | motivation locked at current -20, all positive rewards ×0.7 |
| euphoric | exam score > 80 OR creativity > 90 | energy costs -20%, skip_class temptation higher |
| focused | focus_level > 7 | study +2 bonus, social actions cost -2 energy |
| burnt_edge | stress 90–99 | all rewards ×0.5, only rest actions effective |
| recovered | after therapy OR 3 consecutive journal+sleep | motivation +20, all stats get +5 one-time bonus |

---

## THE HIDDEN METRICS (not shown to agent, used by grader)

**Consistency score**
How consistently the agent maintained balance across all 7 days. High variance (great day → terrible day → great day) scores lower than steady moderate performance. Rewards sustainable habits over optimization spikes.

**Crisis response score**
How well the agent responded to random events. Did they help the friend? Did they handle the roommate conflict? Adds up to 10% of final grade.

**Self-awareness score**
Did the agent course-correct? If stress hit 80 and agent took meditate or journal in the next 3 steps: +5 to this metric. Models metacognitive awareness.

---

## GRADER — FULL VERSION

```python
def grade(self) -> float:
    # Primary: exam outcomes (most objective)
    if not self.exam_scores:
        return 0.0
    passed = sum(1 for s in self.exam_scores if s >= 50)
    avg_score = sum(self.exam_scores) / len(self.exam_scores)
    exam_component = (passed / len(self.exam_scores)) * 0.6 + (avg_score / 100) * 0.4

    # Secondary: survival and balance
    survived = 0.0 if self.burnout_occurred else 0.15
    balance_bonus = 0.0
    final_stats = [
        self.academic_score, self.health,
        self.happiness, self.social_bonds,
        (100 - self.stress)
    ]
    if all(s >= 50 for s in final_stats):
        balance_bonus = 0.10

    # Tertiary: special achievements
    achievement_bonus = 0.0
    if self.project_completed:
        achievement_bonus += 0.05
    if self.internship_unlocked:
        achievement_bonus += 0.10
    if self.helped_friend_in_crisis:
        achievement_bonus += 0.05

    raw = exam_component + survived + balance_bonus + achievement_bonus
    return float(max(0.0, min(1.0, raw)))
```

---

## SCORE INTERPRETATION

| Score | What It Means |
|---|---|
| 0.0 – 0.1 | Burned out before any exam. Complete collapse. |
| 0.1 – 0.2 | Survived but failed all exams. Barely functional. |
| 0.2 – 0.4 | Passed one exam. Struggling. High stress. No balance. |
| 0.4 – 0.6 | Passed two exams. Survivable week. Not thriving. |
| 0.6 – 0.7 | Passed all exams. Decent balance. Few crises handled. |
| 0.7 – 0.8 | Good week. Exams passed well. Social maintained. Healthy. |
| 0.8 – 0.9 | Excellent week. Balanced AND performed. Friend helped. |
| 0.9 – 1.0 | Optimal. Project completed. All exams 70+. No burnout. Internship. |

---

*End of expanded design document. Every edge case here is implementable and grounded in real human behavior. No fluff.*
