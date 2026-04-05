from fastapi import FastAPI
from pydantic import BaseModel
from environment import HumanLifeSimulator

app = FastAPI(
    title="HumanLifeSimulator API",
    description="Extended OpenEnv Hackathon Environment"
)

env = HumanLifeSimulator()

class ActionRequest(BaseModel):
    action: str

@app.post("/reset")
def reset():
    obs = env.reset()
    return {"observation": obs}

@app.post("/step")
def step(req: ActionRequest):
    obs, reward, done, info = env.step(req.action)
    
    # Ensure numpy types are converted for JSON serialization if necessary,
    # though standard python types are used in env.
    return {
        "observation": obs,
        "reward": float(reward),
        "done": bool(done),
        "info": info
    }

@app.get("/grade")
def grade():
    g = env.grade()
    return {"grade": g}

@app.get("/actions")
def actions():
    return {"actions": env.VALID_ACTIONS}

@app.get("/state")
def state():
    return env._get_obs()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/docs_info")
def docs_info():
    return {
        "description": "HumanLifeSimulator — A 168-step RL environment simulating a college week with 40 distinct actions, real-world constraints (burnout, sleep debt, loneliness cascade), and an exam-based grader.",
        "version": "2.0",
        "action_space": len(env.VALID_ACTIONS),
        "episode_length": 168
    }

@app.get("/visualize")
def visualize():
    from collections import Counter
    # Initialize a clean environment for visualization
    local_env = HumanLifeSimulator()
    obs = local_env.reset()
    
    total_reward = 0.0
    action_counts = Counter()
    done = False
    
    while not done:
        # Extract stats for greedy logic
        energy    = obs["energy"]
        stress    = obs["stress"]
        happiness = obs["happiness"]
        health    = obs["health"]
        social    = obs["social_bonds"]
        money     = obs["money"]
        hour      = obs["hour_of_day"]
        day       = obs["day_of_week"]
        
        curr_step = obs["current_step"]
        next_exam_step = min([e for e in [72, 144] if e >= curr_step] + [999])
        exam_days = (next_exam_step - curr_step) / 24.0
        assgn_due = len(obs["assignment_queue"]) > 0 and obs["assignment_queue"][0]["due_step"] - curr_step <= 24

        def can(action):
            return action in local_env.VALID_ACTIONS

        # Greedy Action Logic
        if stress >= 80 and can("meditate"):       action = "meditate"
        elif energy <= 15 and can("sleep"):          action = "sleep"
        elif hour >= 22 or hour <= 6:
            action = "sleep" if can("sleep") else "nap"
        elif exam_days <= 1 and 8 <= hour <= 22:
            action = "study" if can("study") else "attend_class"
        elif assgn_due and can("study"):             action = "study"
        elif can("attend_class") and 9 <= hour <= 17 and day <= 4:
            action = "attend_class"
        elif social <= 25 and money >= 15 and can("socialize"): action = "socialize"
        elif money <= 20 and can("work_parttime"):              action = "work_parttime"
        elif health <= 40 and money >= 10 and can("exercise"):  action = "exercise"
        elif stress >= 60 and can("meditate"):                  action = "meditate"
        elif energy <= 30 and can("nap"):                       action = "nap"
        else:
            action = "study" if can("study") else local_env.VALID_ACTIONS[0]
            
        result = local_env.step(action)
        if len(result) == 5:
            obs, reward, terminated, truncated, _ = result
            done = terminated or truncated
        else:
            obs, reward, done, _ = result
            
        total_reward += reward
        action_counts[action] += 1
        
    grade_score = local_env.grade()
    if grade_score <= 0.2: label = "Burned Out"
    elif grade_score <= 0.4: label = "Struggling"
    elif grade_score <= 0.6: label = "Average"
    elif grade_score <= 0.8: label = "Good Student"
    else: label = "Excellent"
    
    return {
        "grade": round(grade_score, 4),
        "grade_label": label,
        "exam_scores": local_env.exam_scores,
        "total_reward": round(total_reward, 2),
        "action_counts": dict(action_counts),
        "final_stats": {
            "energy": obs["energy"],
            "stress": obs["stress"],
            "health": obs["health"],
            "happiness": obs["happiness"],
            "academic_score": obs["academic_score"],
            "social_bonds": obs["social_bonds"],
            "money": obs["money"],
            "sleep_debt": obs["sleep_debt"]
        },
        "burnout_occurred": local_env.burnout_occurred
    }

@app.get("/baseline")
def run_baseline():
    """
    Runs one random episode and one greedy episode.
    Returns both grades for comparison.
    Used by judges to verify the environment has a real learning signal.
    """
    import random
    from visualize import greedy_action, nestify_obs

    # Random agent
    env = HumanLifeSimulator()
    obs = env.reset()
    for _ in range(168):
        action = random.choice(env.VALID_ACTIONS)
        result = env.step(action)
        done = result[2] or result[3] if len(result) == 5 else result[2]
        if done:
            break
    random_grade = env.grade()

    # Greedy agent (using greedy logic from visualize.py)
    env2 = HumanLifeSimulator()
    flat_obs = env2.reset()
    for _ in range(168):
        obs2 = nestify_obs(flat_obs, env2)
        action = greedy_action(obs2)
        result = env2.step(action)
        done = result[2] or result[3] if len(result) == 5 else result[2]
        flat_obs = result[0]
        if done:
            break
    greedy_grade = env2.grade()

    gap = greedy_grade - random_grade
    return {
        "random_agent_grade":  round(random_grade, 3),
        "greedy_agent_grade":  round(greedy_grade, 3),
        "grade_gap":           round(gap, 3),
        "verdict": (
            "✅ Strong learning signal — gap > 0.25"
            if gap > 0.25
            else "⚠️ Weak signal — gap < 0.25, check reward function"
        )
    }

