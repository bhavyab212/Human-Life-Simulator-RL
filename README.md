# Human Life Simulator — OpenEnv Hackathon Submission

## 1. Overview
Current reinforcement learning systems optimize for engagement—maximizing clicks, watch time, and continuous interactions. However, real human wellbeing involves managing a complex Pareto curve of energy, stress, academic success, and social bonds. 

**Human Life Simulator** asks: what does a good human week actually look like as an RL objective? This environment provides a 168-step (1 week) college simulator where an agent must handle burnout, deadlines, sleep debt, and social isolation. This environment directly contributes to **AI Alignment** research by forcing an agent to learn how to balance competing, sometimes contradictory human needs over long time horizons.

---

## 2. Environment Design

### 2.1 State Space (30+ Variables)

| Category | Variable | Range | Description |
|---|---|---|---|
| **Core** | `energy` | 0–100 | Drops per action and passively. Hits 0 = forced sleep. |
| **Core** | `happiness` | 0–100 | Influenced by stress, socializing, and health. |
| **Core** | `health` | 0–100 | Physical health. Low health halves sleep recovery. |
| **Core** | `academic_score`| 0–100 | Tracked to determine exam scores. |
| **Core** | `stress` | 0–100 | Hits 100 = Burnout (Episode ends). |
| **Core** | `social_bonds` | 0–100 | Hits 0 = all positive rewards halved. |
| **Core** | `money` | 0–200 | Needed for meals, gym, and socializing. |
| **Core** | `sleep_debt` | 0+ | >10 cuts study gains and increases stress. |
| **New** | `creativity` | 0–100 | High unlocks side projects. |
| **New** | `motivation` | 0–100 | <0 locks major actions. |
| **New** | `reputation` | 0–100 | Unlocks study groups and office hours. |
| **New** | `focus_level` | 0–10 | Compounding flow state for studying. |
| **New** | `loneliness_streak`| 0+ (hrs)| Cascading penalty if left untreated. |
| **New** | `caffeine_level` | 0–100 | >70 dropping to <30 = caffeine crash. |
| **New** | `gut_health` | 0–100 | Low health drops happiness. |
| **New** | `sleep_quality` | 0–100 | Influences how much energy sleep restores. |
| **New** | `self_discipline`| 0–100 | Prevents procrastinate cascades. |
| **New** | `environmental_noise`| 0-10 | Blocks deep focus studying. |

### 2.2 Action Space (40 Actions)

**Academic & Work**: `attend_class`, `study`, `skip_class`, `procrastinate`, `work_parttime`, `build_personal_project`, `group_study`, `attend_office_hours`, `skip_class_and_self_study`, `all_nighter`, `seek_peer_notes`, `study_with_music`, `half_study`, `nap_in_class`, `plagiarize`, `withdraw_from_course`.

**Health & Rest**: `sleep`, `nap`, `exercise`, `eat_healthy`, `eat_junk`, `drink_coffee`, `take_a_walk`, `cold_shower`, `cook_at_home`, `meal_prep`, `therapy_session`, `do_nothing`, `binge_eat`.

**Social & Emotional**: `socialize`, `scroll_phone`, `watch_netflix`, `meditate`, `journal`, `help_a_friend`, `call_family`, `doomscroll`, `pull_a_prank`, `micro_socialize`, `help_a_friend_in_crisis`.

### 2.3 Hard Constraints & Mechanics
- **Burnout**: `stress >= 100` stops the episode instantly (`reward = -50`).
- **Sleep Debt Penalty**: `sleep_debt > 10` drops study efficiency to 70% and increases stress passively.
- **Loneliness Cascade**: >24h without social drops happiness. >48h drops health. >72h locks motivation to 20.
- **Caffeine Crash**: Dropping from 70+ caffeine to <30 crashes energy by 20.
- **Exam Multipliers**: Exams at steps 72 and 144 apply multiplicative penalties for stress, sleep debt, and motivation.

---

## 3. Reward Function

Rewards reflect the delicate balance needed in life.
- `study`: +1.5 (+3.0 if high energy, +0.5 if exhausted).
- `skip_class`: -5.0.
- `meditate` or `eat_healthy` or `socialize`: +2.0.
- `procrastinate`: -6.0 if deadline soon, -1.0 otherwise.
- `all_nighter`: +2.0 if exam tomorrow, -3.0 if not.
- `plagiarize`: +0.0 if not caught, -30.0 if caught.
- **Milestones**: Pass all exams (+30.0), Week without burnout (+10.0), Balanced stats (+20.0).

---

## 4. Grader Design

The final performance uses the `env.grade()` function:
```python
exam_component = (passed / total) * 0.6 + (avg / 100) * 0.4
survived = 0.10 if not burnout else 0.0
balance_bonus = 0.08 if all major stats >= 50
achievements = project (0.04) + internship (0.08) + helped friend (0.04)
# Clamped between 0.01 and 0.99
```
**Why this matters**: True RL success here isn't just about passing tests. It requires surviving the week, graduating with a healthy body/mind, and being an active participant in society (achievements). 
- `Score < 0.3`: Burned out or failed.
- `Score ~ 0.5`: Passed, but stressed and miserable.
- `Score > 0.8`: Outstanding human life balance.

---

## 5. Key Dilemmas the Agent Must Solve

1. **Studying vs. Socializing**: You need to study, but skipping social events causes the `loneliness_streak` cascade.
2. **Caffeine vs. Sleep**: Coffee gives instant energy but destroys `sleep_quality` and triggers caffeine crashes.
3. **Cooking vs. Fast Food**: Junk food is cheap and fast, but destroys `gut_health` over time, quietly dragging happiness down.

---

## 6. Real World Relevance

This environment acts as a proxy for solving **Value Alignment**. Rather than training models to click links or score points, AI researchers can deploy algorithms like PPO or SAC on this environment to see how well standard RL handles human-level trade-offs like prioritizing mental health against impending deadlines.

---

## 7. How to Run

### Local Start
```bash
pip install -r requirements.txt
python test.py
uvicorn server:app --port 7860
```

### Docker
```bash
docker build -t human_life_sim .
docker run -p 7860:7860 human_life_sim
```

---

## 8. Architecture

- **`environment.py`**: A robust OOP container for state management and step logic.
- **`server.py`**: Exposes the environment to distributed workers (and AI evaluation benches) through a RESTful FastAPI.
- **`test.py`**: Benchmarks episodic agent behaviors and edge case testing.
