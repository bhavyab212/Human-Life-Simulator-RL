
# visualize.py
# Drop this file into your project folder.
# Run with: python visualize.py
# Requires: pip install rich

import time
import random
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich import box
from rich.rule import Rule

# ─────────────────────────────────────────
# IMPORT YOUR ENVIRONMENT
# ─────────────────────────────────────────
try:
    from environment import HumanLifeSimulator
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

console = Console()

# ─────────────────────────────────────────
# GREEDY AGENT (same logic as test.py)
# ─────────────────────────────────────────
def greedy_action(obs):
    stats   = obs["stats"]
    ctx     = obs["context"]
    time_   = obs["time"]
    avail   = obs["available_actions"]
    hour    = time_["hour"]
    day     = time_["day"]

    energy    = stats["energy"]
    stress    = stats["stress"]
    happiness = stats["happiness"]
    health    = stats["health"]
    social    = stats["social_bonds"]
    money     = stats["money"]
    academic  = stats["academic"]
    exam_days = ctx.get("exam_in_days", 7)
    assgn_due = ctx.get("assignment_due_today", False)

    # Priority rules
    if stress >= 80 and "meditate" in avail:
        return "meditate"
    if energy <= 15 and "sleep" in avail:
        return "sleep"
    if hour >= 22 or hour <= 6:
        return "sleep" if "sleep" in avail else "nap"
    if exam_days <= 1 and 8 <= hour <= 22:
        return "study" if "study" in avail else "attend_class"
    if assgn_due and "study" in avail:
        return "study"
    if "attend_class" in avail and 9 <= hour <= 17 and day <= 4:
        return "attend_class"
    if social <= 25 and money >= 15 and "socialize" in avail:
        return "socialize"
    if money <= 20 and "work_parttime" in avail:
        return "work_parttime"
    if health <= 40 and money >= 10 and "exercise" in avail:
        return "exercise"
    if stress >= 60 and "meditate" in avail:
        return "meditate"
    if energy <= 30 and "nap" in avail:
        return "nap"
    return "study" if "study" in avail else random.choice(avail)

# ─────────────────────────────────────────
# STAT BAR RENDERER
# ─────────────────────────────────────────
def make_bar(value, max_val, width=20, color="green"):
    filled = int((value / max_val) * width)
    bar    = "█" * filled + "░" * (width - filled)
    return f"[{color}]{bar}[/{color}] [bold]{int(value):>3}[/bold]"

def stat_color(name, value):
    if name == "stress":
        if value >= 80: return "red"
        if value >= 50: return "yellow"
        return "green"
    if name == "energy":
        if value <= 20: return "red"
        if value <= 40: return "yellow"
        return "cyan"
    if name == "health":
        if value <= 30: return "red"
        if value <= 50: return "yellow"
        return "green"
    if name == "happiness":
        if value <= 20: return "red"
        if value <= 40: return "yellow"
        return "magenta"
    if name == "academic":
        if value <= 40: return "red"
        if value <= 60: return "yellow"
        return "blue"
    if name == "social_bonds":
        if value <= 20: return "red"
        if value <= 40: return "yellow"
        return "cyan"
    if name == "money":
        if value <= 20: return "red"
        if value <= 50: return "yellow"
        return "green"
    if name == "sleep_debt":
        if value >= 16: return "red"
        if value >= 10: return "yellow"
        return "green"
    return "white"

# ─────────────────────────────────────────
# ACTION EMOJI MAP
# ─────────────────────────────────────────
ACTION_EMOJI = {
    "attend_class":   "📚 attend_class",
    "study":          "✏️  study",
    "skip_class":     "🚫 skip_class",
    "procrastinate":  "📵 procrastinate",
    "sleep":          "💤 sleep",
    "nap":            "😴 nap",
    "exercise":       "🏃 exercise",
    "eat_healthy":    "🥗 eat_healthy",
    "eat_junk":       "🍔 eat_junk",
    "socialize":      "👥 socialize",
    "scroll_phone":   "📱 scroll_phone",
    "watch_netflix":  "📺 watch_netflix",
    "work_parttime":  "💼 work_parttime",
    "meditate":       "🧘 meditate",
}

def fmt_action(a):
    return ACTION_EMOJI.get(a, f"❓ {a}")

def reward_color(r):
    if r >= 3:   return f"[bold green]+{r:.2f}[/bold green]"
    if r >= 0:   return f"[green]+{r:.2f}[/green]"
    if r >= -3:  return f"[yellow]{r:.2f}[/yellow]"
    return       f"[bold red]{r:.2f}[/bold red]"

# ─────────────────────────────────────────
# RENDER FULL FRAME
# ─────────────────────────────────────────
def render_frame(obs, action, reward, step, total_reward, log, exam_scores, done=False):
    stats  = obs["stats"]
    ctx    = obs["context"]
    time_  = obs["time"]

    day_name = time_["day_name"]
    hour     = time_["hour"]
    day      = time_["day"]

    # ── Header ──
    exam_warn = ""
    if ctx.get("exam_in_days", 7) <= 1:
        exam_warn = " [bold red blink]⚠ EXAM TOMORROW![/bold red blink]"
    if ctx.get("assignment_due_today"):
        exam_warn += " [yellow]📋 ASSIGNMENT DUE![/yellow]"

    header = Panel(
        f"[bold white]🎓 Human Life Simulator[/bold white]  —  "
        f"[cyan]{day_name} {hour:02d}:00[/cyan]  "
        f"│  Step [bold]{step}[/bold]/168  "
        f"│  Total Reward: [bold yellow]{total_reward:+.1f}[/bold yellow]"
        + exam_warn,
        style="bold blue",
        box=box.DOUBLE_EDGE
    )

    # ── Stats panel ──
    stats_table = Table(box=box.SIMPLE, show_header=False, padding=(0,1))
    stats_table.add_column("Icon", width=3)
    stats_table.add_column("Stat", width=12)
    stats_table.add_column("Bar", width=30)

    STAT_DISPLAY = [
        ("⚡", "Energy",     "energy",      100, stat_color("energy",     stats["energy"])),
        ("😰", "Stress",     "stress",       100, stat_color("stress",     stats["stress"])),
        ("📚", "Academic",   "academic",     100, stat_color("academic",   stats["academic"])),
        ("💪", "Health",     "health",       100, stat_color("health",     stats["health"])),
        ("😊", "Happiness",  "happiness",    100, stat_color("happiness",  stats["happiness"])),
        ("👥", "Social",     "social_bonds", 100, stat_color("social_bonds",stats["social_bonds"])),
        ("💰", "Money",      "money",        200, stat_color("money",      stats["money"])),
        ("😴", "Sleep Debt", "sleep_debt",    48, stat_color("sleep_debt", stats["sleep_debt"])),
    ]

    for icon, label, key, max_v, color in STAT_DISPLAY:
        val = stats[key]
        stats_table.add_row(
            icon,
            f"[dim]{label}[/dim]",
            make_bar(val, max_v, width=18, color=color)
        )

    stats_panel = Panel(stats_table, title="[bold]📊 Stats[/bold]", border_style="cyan")

    # ── Context panel ──
    ctx_table = Table(box=box.SIMPLE, show_header=False, padding=(0,1))
    ctx_table.add_column("Key",   style="dim",   width=18)
    ctx_table.add_column("Value", style="bold",  width=14)

    eff = ctx.get("study_effectiveness", 1.0)
    eff_color = "green" if eff >= 0.8 else "yellow" if eff >= 0.5 else "red"
    exam_days_left = ctx.get("exam_in_days", "?")
    burnout_risk = "[bold red]YES ⚠[/bold red]" if ctx.get("burnout_risk") else "[green]No[/green]"
    debt_warn = "[red]YES ⚠[/red]" if ctx.get("sleep_debt_warning") else "[green]No[/green]"
    last_meal = ctx.get("last_meal_hours_ago", 0)
    meal_color = "red" if last_meal >= 8 else "yellow" if last_meal >= 5 else "green"

    ctx_table.add_row("🎯 Study Effectiveness",  f"[{eff_color}]{eff:.0%}[/{eff_color}]")
    ctx_table.add_row("📅 Exam In",              f"{exam_days_left} days")
    ctx_table.add_row("🔥 Burnout Risk",          burnout_risk)
    ctx_table.add_row("😴 Sleep Debt Warning",    debt_warn)
    ctx_table.add_row(f"🍽️ Last Meal",            f"[{meal_color}]{last_meal}h ago[/{meal_color}]")
    if exam_scores:
        scores_str = ", ".join([f"{s}" for s in exam_scores])
        ctx_table.add_row("📝 Exam Scores",       f"[bold]{scores_str}[/bold]")

    ctx_panel = Panel(ctx_table, title="[bold]🔍 Context[/bold]", border_style="yellow")

    # ── Action log ──
    log_table = Table(box=box.SIMPLE, show_header=True, padding=(0,1))
    log_table.add_column("Step", style="dim",   width=5)
    log_table.add_column("Time", style="cyan",  width=8)
    log_table.add_column("Action",              width=24)
    log_table.add_column("Reward",              width=8)

    for entry in log[-12:]:  # last 12 actions
        log_table.add_row(
            str(entry["step"]),
            entry["time"],
            fmt_action(entry["action"]),
            reward_color(entry["reward"])
        )

    log_panel = Panel(log_table, title="[bold]📋 Action Log (last 12)[/bold]", border_style="green")

    return header, stats_panel, ctx_panel, log_panel

# ─────────────────────────────────────────
# DAILY SUMMARY
# ─────────────────────────────────────────
def print_daily_summary(day_name, stats, day_actions, day_reward, exam_scores):
    console.print(Rule(f"[bold yellow]📅 End of {day_name} — Daily Summary[/bold yellow]"))

    t = Table(box=box.ROUNDED, show_header=True)
    t.add_column("Stat",   style="dim")
    t.add_column("Value",  justify="right", style="bold")
    t.add_column("Status", justify="center")

    def status(name, val):
        if name == "stress":
            if val >= 80: return "[red]⚠ HIGH[/red]"
            if val >= 50: return "[yellow]~ MED[/yellow]"
            return "[green]✓ OK[/green]"
        if name in ["energy","health","happiness","academic","social_bonds"]:
            if val >= 70: return "[green]✓ GOOD[/green]"
            if val >= 40: return "[yellow]~ OK[/yellow]"
            return "[red]⚠ LOW[/red]"
        if name == "money":
            if val >= 50: return "[green]✓ OK[/green]"
            if val >= 20: return "[yellow]~ LOW[/yellow]"
            return "[red]⚠ BROKE[/red]"
        return ""

    rows = [
        ("⚡ Energy",     "energy"),
        ("😰 Stress",     "stress"),
        ("📚 Academic",   "academic"),
        ("💪 Health",     "health"),
        ("😊 Happiness",  "happiness"),
        ("👥 Social",     "social_bonds"),
        ("💰 Money",      "money"),
        ("😴 Sleep Debt", "sleep_debt"),
    ]
    for label, key in rows:
        val = stats[key]
        t.add_row(label, str(round(val, 1)), status(key, val))

    console.print(t)

    # Action frequency
    action_counts = {}
    for a in day_actions:
        action_counts[a] = action_counts.get(a, 0) + 1

    freq_text = "  ".join(
        [f"{fmt_action(a)} ×{c}" for a, c in sorted(action_counts.items(), key=lambda x: -x[1])[:5]]
    )
    console.print(f"[dim]Top actions today:[/dim] {freq_text}")
    console.print(f"[dim]Day reward total:[/dim] [bold yellow]{day_reward:+.2f}[/bold yellow]")

    if exam_scores:
        for i, score in enumerate(exam_scores):
            result = "[green]✅ PASSED[/green]" if score >= 50 else "[red]❌ FAILED[/red]"
            console.print(f"[bold]Exam {i+1} Score:[/bold] {score}/100  {result}")

    console.print()

# ─────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────
def print_final_summary(obs, exam_scores, total_reward, grade, action_history):
    console.print(Rule("[bold magenta]🏆 EPISODE COMPLETE — FINAL REPORT[/bold magenta]"))
    stats = obs["stats"]

    grade_label = (
        "💀 Burned Out / Failed"        if grade < 0.2 else
        "😓 Barely Surviving"           if grade < 0.35 else
        "😐 Struggling"                  if grade < 0.5 else
        "🙂 Average Student"             if grade < 0.65 else
        "😊 Good Student"                if grade < 0.8 else
        "🌟 Excellent Student"           if grade < 0.9 else
        "🏆 Optimal Week — Outstanding"
    )

    grade_color = (
        "red"     if grade < 0.35 else
        "yellow"  if grade < 0.5  else
        "cyan"    if grade < 0.65 else
        "green"   if grade < 0.8  else
        "bold green"
    )

    console.print(Panel(
        f"[{grade_color}]Grade: {grade:.3f}[/{grade_color}]\n"
        f"{grade_label}\n\n"
        f"Total Reward: [bold yellow]{total_reward:+.2f}[/bold yellow]\n"
        f"Exams: {exam_scores}",
        title="[bold]📊 Final Grade[/bold]",
        border_style=grade_color if grade_color != "bold green" else "green"
    ))

    # Action breakdown for the whole week
    action_counts = {}
    for a in action_history:
        action_counts[a] = action_counts.get(a, 0) + 1

    t = Table(title="📋 Full Week Action Breakdown", box=box.ROUNDED)
    t.add_column("Action", style="dim")
    t.add_column("Count", justify="right", style="bold")
    t.add_column("Hours", justify="right")
    t.add_column("% of Week", justify="right")

    total_steps = len(action_history)
    for action, count in sorted(action_counts.items(), key=lambda x: -x[1]):
        pct = (count / total_steps) * 100
        bar = "█" * int(pct / 5)
        t.add_row(
            fmt_action(action),
            str(count),
            f"{count}h",
            f"{pct:.1f}% {bar}"
        )

    console.print(t)

    # Final stats
    console.print(Rule("[dim]Final Stats[/dim]"))
    for label, key, max_v in [
        ("⚡ Energy",     "energy",      100),
        ("😰 Stress",     "stress",      100),
        ("📚 Academic",   "academic",    100),
        ("💪 Health",     "health",      100),
        ("😊 Happiness",  "happiness",   100),
        ("👥 Social",     "social_bonds",100),
    ]:
        val   = stats[key]
        color = stat_color(key.lower().split()[1] if " " in key else key, val)
        bar   = make_bar(val, max_v, width=30, color=color)
        console.print(f"  {label:<16} {bar}")

def nestify_obs(flat_obs, env):
    curr_step = flat_obs["current_step"]
    next_exam_step = min([e for e in [72, 144] if e >= curr_step] + [168])
    return {
        "stats": {
            "energy": flat_obs["energy"],
            "stress": flat_obs["stress"],
            "happiness": flat_obs["happiness"],
            "health": flat_obs["health"],
            "academic": flat_obs["academic_score"],
            "social_bonds": flat_obs["social_bonds"],
            "money": flat_obs["money"],
            "sleep_debt": flat_obs["sleep_debt"]
        },
        "time": {
            "hour": flat_obs["hour_of_day"],
            "day": flat_obs["day_of_week"],
            "day_name": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][flat_obs["day_of_week"]]
        },
        "context": {
            "exam_in_days": (next_exam_step - curr_step) / 24.0,
            "assignment_due_today": len(flat_obs.get("assignment_queue", [])) > 0 and (flat_obs["assignment_queue"][0]["due_step"] - curr_step <= 24),
            "burnout_risk": flat_obs["stress"] >= 80,
            "sleep_debt_warning": flat_obs["sleep_debt"] > 10,
            "last_meal_hours_ago": flat_obs.get("last_meal_hours_ago", 0),
            "study_effectiveness": 0.7 if flat_obs["sleep_debt"] > 10 else 1.0,
        },
        "available_actions": env.VALID_ACTIONS
    }

# ─────────────────────────────────────────
# MAIN RUN FUNCTION
# ─────────────────────────────────────────
def run_visualization(agent="greedy", delay=0.05):
    """
    agent: "greedy" or "random"
    delay: seconds between steps (0 = instant, 0.1 = slow)
    """
    if not ENV_LOADED:
        console.print("[bold red]ERROR: Could not import HumanLifeSimulator from environment.py[/bold red]")
        console.print("[dim]Make sure visualize.py is in the same folder as environment.py[/dim]")
        return

    env = HumanLifeSimulator()
    flat_obs = env.reset()
    obs = nestify_obs(flat_obs, env)

    log            = []
    action_history = []
    total_reward   = 0.0
    last_day       = 0
    day_actions    = []
    day_reward     = 0.0

    console.clear()
    console.print(Panel(
        "[bold white]Welcome to the Human Life Simulator[/bold white]\n"
        f"[dim]Agent: {agent.upper()} | Speed: {'Fast' if delay < 0.05 else 'Normal'}[/dim]\n"
        "[dim]Watch the AI agent live through an entire college week...[/dim]",
        border_style="magenta",
        box=box.DOUBLE_EDGE
    ))
    time.sleep(1.0)

    for step in range(168):
        # Pick action
        if agent == "greedy":
            action = greedy_action(obs)
        else:
            action = random.choice(obs["available_actions"])

        # Take step
        flat_new_obs, reward, done, info = env.step(action)
        new_obs = nestify_obs(flat_new_obs, env)
        total_reward  += reward
        action_history.append(action)
        day_actions.append(action)
        day_reward += reward

        # Build log entry
        time_str = f"{new_obs['time']['day_name']} {new_obs['time']['hour']:02d}:00"
        log.append({"step": step+1, "time": time_str, "action": action, "reward": reward})

        # Get exam scores
        exam_scores = info.get("exam_scores", [])

        # Render
        header, stats_panel, ctx_panel, log_panel = render_frame(
            new_obs, action, reward, step+1, total_reward, log, exam_scores, done
        )

        console.clear()
        console.print(header)
        console.print(Columns([stats_panel, ctx_panel], equal=False))
        console.print(log_panel)

        # Day change
        current_day = new_obs["time"]["day"]
        if current_day != last_day:
            day_name = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][min(last_day,6)]
            time.sleep(0.3)
            print_daily_summary(day_name, new_obs["stats"], day_actions, day_reward, exam_scores)
            day_actions = []
            day_reward  = 0.0
            last_day    = current_day
            time.sleep(0.5)

        # Special events
        if info.get("event") == "burnout":
            console.print(Panel(
                "[bold red]💥 BURNOUT! The student completely collapsed.[/bold red]\n"
                "[dim]Stress hit 100. Episode ended early.[/dim]",
                border_style="red"
            ))
            break

        if done:
            break

        obs = new_obs
        time.sleep(delay)

    # Final grade
    grade = env.grade()
    console.clear()
    print_final_summary(new_obs, exam_scores, total_reward, grade, action_history)

# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────
if __name__ == "__main__":
    import sys

    agent = "greedy"
    delay = 0.04   # seconds between steps — change to 0 for instant, 0.2 for slow

    if len(sys.argv) > 1:
        agent = sys.argv[1]           # python visualize.py random
    if len(sys.argv) > 2:
        delay = float(sys.argv[2])    # python visualize.py greedy 0.1

    console.print(f"[dim]Starting with agent=[bold]{agent}[/bold], delay={delay}s...[/dim]")
    time.sleep(0.5)
    run_visualization(agent=agent, delay=delay)
