# train.py
# Run with: python train.py
# Requires: pip install stable-baselines3 rich

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from rich.console import Console
from rich.table import Table
from rich.rule import Rule
from rich import box
from gym_wrapper import HumanLifeGymEnv
import numpy as np

console = Console()

# ── Progress Callback ──────────────────────────────────────────
class TrainingCallback(BaseCallback):

    def __init__(self):
        super().__init__()
        self.episode_grades   = []
        self.episode_rewards  = []
        self.current_reward   = 0.0
        self.ep_count         = 0

    def _on_step(self) -> bool:
        self.current_reward += float(self.locals["rewards"][0])

        if self.locals["dones"]:
            grade = self.training_env.env_method("get_grade")[0]
            self.episode_grades.append(grade)
            self.episode_rewards.append(self.current_reward)
            self.current_reward = 0.0
            self.ep_count += 1

            if self.ep_count % 10 == 0:
                last10_grades  = self.episode_grades[-10:]
                last10_rewards = self.episode_rewards[-10:]
                avg_grade      = sum(last10_grades)  / len(last10_grades)
                avg_reward     = sum(last10_rewards) / len(last10_rewards)
                best_grade     = max(last10_grades)

                label = (
                    "💀 Still Random"  if avg_grade < 0.20 else
                    "😓 Struggling"    if avg_grade < 0.35 else
                    "📈 Learning..."   if avg_grade < 0.50 else
                    "🙂 Getting There" if avg_grade < 0.65 else
                    "😊 Good Student"  if avg_grade < 0.80 else
                    "🌟 Excellent"
                )

                # Notice `float` wrapping to work with numpy arrays returned in locals
                console.print(
                    f"[dim]Ep[/dim] [bold]{self.ep_count:>4}[/bold] │ "
                    f"Avg Grade: [bold cyan]{float(avg_grade):.3f}[/bold cyan] │ "
                    f"Best: [green]{float(best_grade):.3f}[/green] │ "
                    f"Avg Reward: [yellow]{float(avg_reward):+.1f}[/yellow] │ "
                    f"{label}"
                )
        return True


# ── MAIN TRAINING ──────────────────────────────────────────────
if __name__ == "__main__":
    console.print(Rule("[bold green]🚀 Human Life Simulator — RL Training[/bold green]"))
    console.print("[dim]Algorithm: PPO (Proximal Policy Optimization)[/dim]")
    console.print("[dim]The agent starts knowing nothing and learns from rewards.[/dim]")
    console.print("[dim]Watch the grade improve over 2500 episodes.\n[/dim]")
    console.print("[bold]Episode │ Avg Grade │ Best │ Avg Reward │ Status[/bold]")
    console.print(Rule(style="dim"))

    env      = HumanLifeGymEnv()
    callback = TrainingCallback()

    model = PPO(
        policy          = "MlpPolicy",
        env             = env,
        verbose         = 0,
        learning_rate   = 1e-4,
        n_steps         = 336,    # 2 full weeks
        batch_size      = 168,    # Properly factorized
        n_epochs        = 15,
        gamma           = 0.995,
        clip_range      = 0.15,
        ent_coef        = 0.005,
        policy_kwargs   = dict(net_arch=dict(pi=[256, 256], vf=[256, 256])), # Deeper NN
        device          = "cuda"
    )

    model.learn(
        total_timesteps = 2500 * 168, # 2500 Episodes
        callback        = callback,
        progress_bar    = False
    )

    model.save("trained_agent")

    console.print(Rule("[bold green]✅ Training Complete[/bold green]"))
    console.print("[bold green]Model saved → trained_agent.zip[/bold green]\n")

    # ── Final evaluation ──────────────────────────────────────
    console.print("[bold]Running 10 test episodes with trained agent...[/bold]")
    grades = []
    for i in range(10):
        obs, _ = env.reset()
        done   = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(int(action))
            done = terminated or truncated
        g = env.get_grade()
        grades.append(g)

        label = (
            "💀 Failed"  if g < 0.35 else
            "😐 Average" if g < 0.60 else
            "😊 Good"    if g < 0.80 else
            "🌟 Excellent"
        )
        console.print(f"  Test {i+1:>2}: grade = [bold cyan]{g:.3f}[/bold cyan]  {label}")

    avg = sum(grades) / len(grades)
    console.print(f"\n[bold green]Average trained grade: {avg:.3f}[/bold green]")
    console.print(
        f"[dim]Improvement over random baseline (~0.12): "
        f"+{avg - 0.12:.3f}[/dim]"
    )
