# watch_agent.py
# Run AFTER train.py has finished
# Run with: python watch_agent.py
# Shows the trained neural network making real decisions step by step

import time
from stable_baselines3 import PPO
from rich.console import Console
from rich.table import Table
from rich.rule import Rule
from rich.panel import Panel
from rich import box
from gym_wrapper import HumanLifeGymEnv

console = Console()

ACTION_EMOJI = {
    "attend_class":   "📚",
    "study":          "✏️ ",
    "skip_class":     "🚫",
    "procrastinate":  "📵",
    "sleep":          "💤",
    "nap":            "😴",
    "exercise":       "🏃",
    "eat_healthy":    "🥗",
    "eat_junk":       "🍔",
    "socialize":      "👥",
    "scroll_phone":   "📱",
    "watch_netflix":  "📺",
    "work_parttime":  "💼",
    "meditate":       "🧘",
    "build_personal_project": "💻",
    "drink_coffee": "☕",
    "journal": "📓",
}

def grade_label(g):
    if g < 0.20: return "💀 Burned Out"
    if g < 0.35: return "😓 Struggling"
    if g < 0.50: return "😐 Barely Passing"
    if g < 0.65: return "🙂 Average Student"
    if g < 0.80: return "😊 Good Student"
    if g < 0.90: return "🌟 Excellent Student"
    return "🏆 Outstanding"

if __name__ == "__main__":
    console.print(Panel(
        "[bold white]🤖 Watching Trained RL Agent Play[/bold white]\n"
        "[dim]The neural network is making every decision.[/dim]\n"
        "[dim]No if/else rules. Pure learned behavior.[/dim]",
        border_style="green",
        box=box.DOUBLE_EDGE
    ))
    time.sleep(1.0)

    env     = HumanLifeGymEnv()
    model   = PPO.load("trained_agent", device="cpu")
    obs, _  = env.reset()

    done         = False
    step         = 0
    total_reward = 0.0
    action_log   = []

    while not done:
        action_idx, _prob = model.predict(obs, deterministic=True)
        action_name        = env.action_list[int(action_idx)]
        obs, reward, terminated, truncated, info = env.step(int(action_idx))
        done          = terminated or truncated
        total_reward += reward
        step         += 1

        emoji      = ACTION_EMOJI.get(action_name, "❓")
        rew_color  = "green" if reward > 0 else "red" if reward < 0 else "dim"
        action_log.append((step, action_name, reward))

        console.print(
            f"[dim]{step:>3}[/dim] │ "
            f"{emoji} [bold]{action_name:<24}[/bold] │ "
            f"[{rew_color}]{reward:+.2f}[/{rew_color}] │ "
            f"Total: [yellow]{total_reward:+.1f}[/yellow]"
        )
        time.sleep(0.03)

    grade = env.get_grade()

    console.print(Rule())
    console.print(f"[bold green]Final Grade: {grade:.3f}[/bold green]  {grade_label(grade)}")
    console.print(f"[dim]Total Reward: {total_reward:+.2f}[/dim]")

    # Action frequency summary
    console.print(Rule("[dim]Action Breakdown[/dim]"))
    counts = {}
    for _, a, _ in action_log:
        counts[a] = counts.get(a, 0) + 1

    t = Table(box=box.SIMPLE, show_header=True)
    t.add_column("Action",    style="dim")
    t.add_column("Count",     justify="right", style="bold")
    t.add_column("% of week", justify="right")
    t.add_column("",          width=20)

    for action, count in sorted(counts.items(), key=lambda x: -x[1]):
        pct = (count / step) * 100
        bar = "█" * int(pct / 4)
        emoji = ACTION_EMOJI.get(action, "")
        t.add_row(
            f"{emoji} {action}",
            str(count),
            f"{pct:.1f}%",
            f"[cyan]{bar}[/cyan]"
        )
    console.print(t)
