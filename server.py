import os
import threading
import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from environment import HumanLifeSimulator

training_state = {
    "is_training": False,
    "is_complete": False,
    "current_episode": 0,
    "total_episodes": 0,
    "episode_grades": [],
    "episode_rewards": [],
    "best_grade": 0.0,
    "current_avg_grade": 0.0,
    "current_avg_reward": 0.0,
    "hyperparams": {},
    "error": None,
    "start_time": None,
    "elapsed_seconds": 0,
    "stop_flag": False
}

class TrainConfig(BaseModel):
    total_episodes: int = 500
    learning_rate: float = 0.0003
    gamma: float = 0.99
    n_steps: int = 168
    batch_size: int = 64
    n_epochs: int = 10
    ent_coef: float = 0.01
    clip_range: float = 0.2
    resume: bool = True
    device: str = "cuda"

class AgentRunConfig(BaseModel):
    agent_type: str

def run_training_background(config: TrainConfig):
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.callbacks import BaseCallback
        from gym_wrapper import HumanLifeGymEnv
        
        class DashboardCallback(BaseCallback):
            def __init__(self):
                super().__init__()
                self.current_reward = 0.0

            def _on_step(self) -> bool:
                if training_state["stop_flag"]:
                    return False
                self.current_reward += float(self.locals["rewards"][0])
                if self.locals["dones"]:
                    grade = self.training_env.env_method("get_grade")[0]
                    training_state["episode_grades"].append(grade)
                    training_state["episode_rewards"].append(self.current_reward)
                    self.current_reward = 0.0
                    training_state["current_episode"] += 1
                    training_state["best_grade"] = max(training_state["best_grade"], grade)
                    l10_g = training_state["episode_grades"][-10:]
                    l10_r = training_state["episode_rewards"][-10:]
                    training_state["current_avg_grade"] = sum(l10_g)/len(l10_g)
                    training_state["current_avg_reward"] = sum(l10_r)/len(l10_r)
                    training_state["elapsed_seconds"] = int(time.time() - training_state["start_time"])
                return True
                
        env = HumanLifeGymEnv()
        cb = DashboardCallback()
        
        if config.resume and os.path.exists("trained_agent.zip"):
            model = PPO.load("trained_agent", env=env, device=config.device, custom_objects={
                "learning_rate": config.learning_rate,
                "n_steps": config.n_steps,
                "batch_size": config.batch_size,
                "n_epochs": config.n_epochs,
                "gamma": config.gamma,
                "clip_range": config.clip_range,
                "ent_coef": config.ent_coef
            })
        else:
            model = PPO(
                policy="MlpPolicy", env=env, learning_rate=config.learning_rate,
                n_steps=config.n_steps, batch_size=config.batch_size, n_epochs=config.n_epochs,
                gamma=config.gamma, clip_range=config.clip_range, ent_coef=config.ent_coef,
                verbose=0, device=config.device
            )
            
        model.learn(total_timesteps=config.total_episodes * 168, callback=cb, reset_num_timesteps=not config.resume)
        model.save("trained_agent")
        training_state["is_complete"] = True
    except Exception as e:
        training_state["error"] = str(e)
    finally:
        training_state["is_training"] = False

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

try:
    import torch
    global_cuda_avail = torch.cuda.is_available()
    global_gpu_name = torch.cuda.get_device_name(0) if global_cuda_avail else "None"
except:
    global_cuda_avail = False
    global_gpu_name = "None"

@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")

@app.get("/system/info")
def system_info():
    info = {"cpu_load": 0.0, "ram_usage_pct": 0.0, "cuda_available": global_cuda_avail, "gpu_name": global_gpu_name}
    try:
        import os
        if hasattr(os, "getloadavg"):
            info["cpu_load"] = round(os.getloadavg()[0], 2)
    except: pass
        
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            total = int(lines[0].split()[1])
            free = int(lines[1].split()[1])
            buffers = int(lines[3].split()[1])
            cached = int(lines[4].split()[1])
            used = total - free - buffers - cached
            info["ram_usage_pct"] = round((used / total) * 100, 1)
    except: pass
    return info

@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    with open("dashboard.html", "r") as f:
        return f.read()

@app.post("/train/start")
def train_start(config: TrainConfig):
    if training_state["is_training"]:
        return {"status": "error", "message": "Already training"}
    
    training_state.update({
        "is_training": True, "is_complete": False, "current_episode": 0,
        "total_episodes": config.total_episodes, "episode_grades": [], "episode_rewards": [],
        "best_grade": 0.0, "current_avg_grade": 0.0, "current_avg_reward": 0.0,
        "hyperparams": config.model_dump(), "error": None,
        "start_time": time.time(), "elapsed_seconds": 0, "stop_flag": False
    })
    
    t = threading.Thread(target=run_training_background, args=(config,))
    t.start()
    return {"status": "started", "message": "Training started in background"}

@app.get("/train/status")
def train_status():
    st = training_state.copy()
    pct = (st["current_episode"] / max(1, st["total_episodes"])) * 100.0 if st["is_training"] or st["is_complete"] else 0.0
    est = 0
    if pct > 0 and pct < 100 and st["elapsed_seconds"] > 0:
        est = int((st["elapsed_seconds"] / pct) * (100 - pct))
        
    return {
        "is_training": st["is_training"],
        "is_complete": st["is_complete"],
        "current_episode": st["current_episode"],
        "total_episodes": st["total_episodes"],
        "progress_pct": pct,
        "best_grade": st["best_grade"],
        "current_avg_grade": st["current_avg_grade"],
        "current_avg_reward": st["current_avg_reward"],
        "episode_grades": st["episode_grades"],
        "episode_rewards": st["episode_rewards"],
        "elapsed_seconds": st["elapsed_seconds"],
        "estimated_remaining_seconds": est,
        "hyperparams": st["hyperparams"],
        "error": st["error"]
    }

@app.post("/train/stop")
def train_stop():
    if training_state["is_training"]:
        training_state["stop_flag"] = True
        return {"status": "stopping"}
    return {"status": "idle"}

@app.get("/train/history")
def train_history():
    grades = training_state["episode_grades"]
    roll = []
    for i in range(len(grades)):
        if i < 9:
            roll.append(None)
        else:
            roll.append(sum(grades[i-9:i+1])/10)
    return {
        "episodes": list(range(1, len(grades)+1)),
        "grades": grades,
        "rewards": training_state["episode_rewards"],
        "rolling_avg_10": roll
    }

@app.post("/agent/run")
def agent_run(req: AgentRunConfig):
    import random
    from visualize import greedy_action, nestify_obs
    from stable_baselines3 import PPO
    from gym_wrapper import HumanLifeGymEnv
    import os

    local_env = HumanLifeSimulator()
    flat_obs = local_env.reset()
    
    model = None
    if req.agent_type == "trained":
        if not os.path.exists("trained_agent.zip"):
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="No trained model found")
        model = PPO.load("trained_agent", device="cuda")
        gym_env = HumanLifeGymEnv()
        obs_array = gym_env._obs_to_array(flat_obs)

    steps = []
    total_reward = 0.0
    action_counts = {}
    
    for step_num in range(1, 169):
        if req.agent_type == "trained":
            action_idx, _ = model.predict(obs_array, deterministic=True)
            action = gym_env.action_list[int(action_idx)]
        elif req.agent_type == "greedy":
            action = greedy_action(nestify_obs(flat_obs, local_env))
        else:
            action = random.choice(local_env.VALID_ACTIONS)
            
        action_counts[action] = action_counts.get(action, 0) + 1
        
        result = local_env.step(action)
        if len(result) == 5:
            flat_obs, reward, terminated, truncated, _ = result
            done = terminated or truncated
        else:
            flat_obs, reward, done, _ = result
            
        if req.agent_type == "trained":
            obs_array = gym_env._obs_to_array(flat_obs)
            
        total_reward += reward
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        steps.append({
            "step": step_num,
            "day": days[flat_obs.get("day_of_week", 0)],
            "hour": flat_obs.get("hour_of_day", 0),
            "action": action,
            "reward": float(reward),
            "total_reward": float(total_reward),
            "stats": {
                "energy": flat_obs.get("energy"),
                "stress": flat_obs.get("stress"),
                "academic": flat_obs.get("academic_score"),
                "health": flat_obs.get("health"),
                "happiness": flat_obs.get("happiness"),
                "social_bonds": flat_obs.get("social_bonds"),
                "money": flat_obs.get("money"),
                "sleep_debt": flat_obs.get("sleep_debt")
            }
        })
        
        if done: break
        
    return {
        "agent_type": req.agent_type,
        "grade": local_env.grade(),
        "total_reward": total_reward,
        "steps": steps,
        "action_counts": action_counts,
        "exam_scores": local_env.exam_scores,
        "burnout_occurred": getattr(local_env, "burnout_occurred", False)
    }

@app.get("/agent/compare")
def agent_compare():
    import random
    from visualize import greedy_action, nestify_obs
    import os
    
    def run_ag(agent_type):
        local_env = HumanLifeSimulator()
        flat_obs = local_env.reset()
        reward_sum = 0.0
        
        if agent_type == "trained" and os.path.exists("trained_agent.zip"):
            from stable_baselines3 import PPO
            from gym_wrapper import HumanLifeGymEnv
            model = PPO.load("trained_agent", device="cuda")
            gym_env = HumanLifeGymEnv()
            obs_array = gym_env._obs_to_array(flat_obs)
            
            for _ in range(168):
                action_idx, _ = model.predict(obs_array, deterministic=True)
                action = gym_env.action_list[int(action_idx)]
                result = local_env.step(action)
                done = result[2] or result[3] if len(result) == 5 else result[2]
                flat_obs = result[0]
                reward_sum += result[1]
                obs_array = gym_env._obs_to_array(flat_obs)
                if done: break
                
        elif agent_type == "greedy":
            for _ in range(168):
                action = greedy_action(nestify_obs(flat_obs, local_env))
                result = local_env.step(action)
                done = result[2] or result[3] if len(result) == 5 else result[2]
                flat_obs = result[0]
                reward_sum += result[1]
                if done: break
                
        else: # random
            for _ in range(168):
                action = random.choice(local_env.VALID_ACTIONS)
                result = local_env.step(action)
                done = result[2] or result[3] if len(result) == 5 else result[2]
                reward_sum += result[1]
                if done: break
                
        return {"grade": local_env.grade(), "reward": reward_sum}
        
    t = run_ag("trained") if os.path.exists("trained_agent.zip") else {"grade": 0, "reward": 0}
    g = run_ag("greedy")
    r = run_ag("random")
    
    gap = t["grade"] - r["grade"]
    signal = f"Strong — gap of {gap:.2f} between trained and random" if gap > 0.25 else f"Weak — gap of {gap:.2f}"
    
    return {
        "trained": t,
        "greedy": g,
        "random": r,
        "learning_signal": signal
    }

@app.get("/environment/info")
def environment_info():
    e = HumanLifeSimulator()
    return {
        "name": "Human Life Simulator",
        "version": "1.0",
        "episode_length": 168,
        "action_count": len(e.VALID_ACTIONS),
        "actions": e.VALID_ACTIONS,
        "stat_count": 8,
        "stats": [
            {"name": "energy", "min": 0, "max": 100},
            {"name": "stress", "min": 0, "max": 100},
            {"name": "health", "min": 0, "max": 100},
            {"name": "happiness", "min": 0, "max": 100},
            {"name": "academic_score", "min": 0, "max": 100},
            {"name": "social_bonds", "min": 0, "max": 100},
            {"name": "money", "min": 0, "max": 200},
            {"name": "sleep_debt", "min": 0, "max": "unbounded"}
        ]
    }
