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
