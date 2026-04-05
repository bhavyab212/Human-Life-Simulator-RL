from typing import List, Dict, Any
import random

class LifeScenario:
    def __init__(self, id: str, domain: str, title: str, description: str, context: str, character: str, internal_thoughts: str, conflict: str, outcomes: Dict[str, Dict[str, int]], life_insight: str):
        self.id = id
        self.domain = domain
        self.title = title
        self.description = description
        self.context = context
        self.character = character
        self.internal_thoughts = internal_thoughts
        self.conflict = conflict
        self.outcomes = outcomes
        self.life_insight = life_insight

def _mix(variants: List[str], rng: random.Random) -> str:
    return rng.choice(variants)

# ── DOMAINS AND OUTCOME DEFINITIONS ──
# Possible Outcomes must match agent's action abilities or broadly define what the user chooses to "focus on"
# In the env, we will restrict the agent's actions during an active scenario.
# e.g., if scenario has ["face_it", "avoid"], agent must pick one. To hook this up to agent's standard actions:
# We map scenario outcomes to standard actions. 
# Or we just use standard actions as the resolution vectors. 
# For example, in a "Heartbreak" scenario:
# - "socialize" -> Talk it out (+ happiness, - time)
# - "do_nothing" -> Wallow (- happiness, + stress)
# - "study" -> Distract with work (+ academic, - social)

def generate_scenario(seed: int, env_state: dict) -> LifeScenario:
    rng = random.Random(seed)
    domains = [
        "Education", "Friendship", "Family", "Romance", "Identity",
        "Career", "Moral", "Mental_Health", "Money", "Societal"
    ]
    domain = rng.choice(domains)

    # ── GENERATIVE TEMPLATES ──
    templates = {
        "Education": {
            "titles": ["The Harsh Curve", "Unfair Grading", "The Plagiarism Accusation", "Group Project Disaster", "The Genius Freshman"],
            "contexts": [
                "You find yourself staring at an exam grade that doesn't reflect your actual effort.",
                "Your group project members have completely abandoned the work due tomorrow.",
                "The professor makes a highly controversial remark during a lecture, targeting your demographic."
            ],
            "conflicts": [
                "Do you confront authority and risk your grade, or stay silent and swallow your pride?",
                "Do you do all the work to save the grade, or let the project fail to teach them a lesson?"
            ],
            "insights": [
                "Sometimes 'fairness' is a subjective illusion. Resilience is objective.",
                "Academic success is rarely a solo endeavor, even when you feel alone.",
                "Grades measure compliance, not intelligence."
            ]
        },
        "Friendship": {
            "titles": ["The Betrayal", "Drifting Apart", "The Intervention", "Viral Embarrassment", "Borrowed Money"],
            "contexts": [
                "Your oldest friend has started dating someone who actively disrespects you.",
                "You accidentally see a group chat where your 'friends' are mocking your recent failure.",
                "A friend comes to you at 3 AM having a severe mental health crisis."
            ],
            "conflicts": [
                "Stand up for yourself and lose the friend group, or laugh it off and lose your self-respect?",
                "Sacrifice your most important exam tomorrow to stay with them, or call a hotline and distance yourself?"
            ],
            "insights": [
                "Not all history is worth bringing into the future.",
                "Boundaries are the only way to sustain long-term empathy.",
                "People grow at different speeds. It is okay to outgrow people you love."
            ]
        },
        "Family": {
            "titles": ["Financial Ruin", "The Ultimatum", "Cultural Expectations", "The Golden Sibling", "Fading Health"],
            "contexts": [
                "Your parents call to tell you they can no longer afford to help with tuition.",
                "Your family demands you switch your major to something more 'prestigious' or face being cut off.",
                "A strict cultural norm dictates you must return home immediately to care for an ailing relative."
            ],
            "conflicts": [
                "Do you honor your parents' sacrifices at the cost of your own dreams?",
                "Do you take on massive debt to stay independent, or move back home and delay your life?"
            ],
            "insights": [
                "Love and obligation are often intertwined in families, but they are not the same thing.",
                "You cannot pour from an empty cup. Saving yourself first is sometimes the highest duty.",
                "Generational trauma ends with the one willing to be the villain in the family story."
            ]
        },
        "Romance": {
            "titles": ["The Cheater", "Unrequited Love", "The 'Right Person, Wrong Time'", "Jealousy Spiral", "The Distance"],
            "contexts": [
                "The person you are deeply in love with tells you they are moving to another continent tomorrow.",
                "You discover a text message on your partner's phone that shatters your trust.",
                "Someone you considered a platonic soulmate suddenly confesses deep romantic feelings for you."
            ],
            "conflicts": [
                "Do you hold on to the fantasy and try long-distance, or end it cleanly now to avoid delayed pain?",
                "Forgive the indiscretion for the sake of the history, or walk away and face intense loneliness?"
            ],
            "insights": [
                "Closure is something you give yourself, not something you extract from another.",
                "Love is never wasted, it just changes forms and teaches you what you actually need.",
                "You cannot negotiate desire."
            ]
        },
        "Mental_Health": {
            "titles": ["The Abyss", "Impostor Syndrome", "The Panic Attack", "Numbness", "The Sleep Paralysis"],
            "contexts": [
                "You wake up and the world feels entirely gray. Getting out of bed feels like moving mountains.",
                "You are sitting in a room of overachievers and suddenly feel utterly unqualified to be there.",
                "Your heart starts racing in the middle of a crowded lecture hall for no apparent reason."
            ],
            "conflicts": [
                "Do you mask the pain and push through, risking a total breakdown, or withdraw and fall behind?",
                "Do you admit your weakness and seek therapy, costing money you barely have, or tough it out alone?"
            ],
            "insights": [
                "Healing is not linear. Sometimes surviving the day is enough.",
                "The brain is an organ like any other; it gets sick, and it needs medicine or rest.",
                "You are not your darkest thoughts. You are the observer of them."
            ]
        },
        "Moral": {
            "titles": ["The Lost Wallet", "The Exam Leak", "Lying for a Friend", "The Whistleblower", "Borrowed Idea"],
            "contexts": [
                "You find a wallet containing $500 cash and an ID belonging to someone wealthy who was rude to you yesterday.",
                "Someone sends you the exact answer key to tomorrow's final exam. The curve will be ruined.",
                "Your friend asks you to provide a false alibi for them, and it involves a serious offense."
            ],
            "conflicts": [
                "Do you take the money to pay your rent, or return it and struggle?",
                "Report the leak and become the most hated person in the cohort, or use it and compromise your integrity?"
            ],
            "insights": [
                "Integrity is what you do when no one is watching, but also what you do when everyone is.",
                "Sometimes the 'right' choice comes with the heaviest penalty.",
                "True morality often requires sacrificing harmony."
            ]
        },
        # These 4 fallbacks will use a generic pool to ensure we don't crash if RNG picks them
        "Identity": {"titles":["Who Am I?"], "contexts":["You look in the mirror and don't recognize yourself anymore."], "conflicts":["Cling to the past or embrace the unknown?"], "insights":["Identity is fluid."]},
        "Career": {"titles":["Rejected"], "contexts":["The internship you desperately needed rejects you."], "conflicts":["Give up or try a harder path?"], "insights":["Rejection is redirection."]},
        "Money": {"titles":["Broke"], "contexts":["Your bank account hits zero."], "conflicts":["Beg for money or starve?"], "insights":["Money is a lever for freedom."]},
        "Societal": {"titles":["Expectations"], "contexts":["Society expects you to behave a certain way."], "conflicts":["Conform or rebel?"], "insights":["Conformity is comfortable but restrictive."]}
    }
    
    t = templates.get(domain, templates["Moral"]) 

    title = _mix(t["titles"], rng)
    context = _mix(t["contexts"], rng)
    conflict = _mix(t["conflicts"], rng)
    insight = _mix(t["insights"], rng)

    characters = ["A trusted confidant", "An antagonistic peer", "An authoritative figure", "A silent observer", "Your own reflection"]
    character = _mix(characters, rng)
    
    thoughts = [
        "Why does this always happen to me?", 
        "I need to stay calm and analyze the situation.", 
        "I don't care anymore, let everything burn.", 
        "If I make the wrong choice, my life is ruined."
    ]
    thought = _mix(thoughts, rng)

    desc = f"{context} {conflict} {thought}"
    
    # We map resolution options directly to standard core actions so the agent can naturally select them
    # and the environment computes the reward based on standard logic PLUS scenario deltas.
    # We will pick 3 random actions that the agent can take to resolve it.
    possible_actions = [
        "socialize", "study", "sleep", "journal", "exercise", 
        "do_nothing", "call_family", "pull_a_prank", "meditate", "doomscroll"
    ]
    acts = rng.sample(possible_actions, 3)
    
    outcomes = {}
    for act in acts:
        # Generate some randomized stat deltas based on domain and action
        mult = 1
        if act in ["do_nothing", "doomscroll", "eat_junk"]: mult = -1
        
        outcomes[act] = {
            "happiness": rng.randint(5, 20) * mult,
            "stress": rng.randint(-15, 15),
            "academic_score": rng.randint(-10, 10),
            "social_bonds": rng.randint(-10, 10),
            "reputation": rng.randint(-5, 5)
        }

    return LifeScenario(
        id=f"{domain.lower()}_{seed}",
        domain=domain,
        title=title,
        description=desc,
        context=context,
        character=character,
        internal_thoughts=thought,
        conflict=conflict,
        outcomes=outcomes,
        life_insight=insight
    )

class ScenarioEngine:
    def __init__(self):
        self.active_scenario = None
        self.scenario_steps_left = 0
        self.history = []
        
    def step(self, env_state: dict, action_taken: str) -> dict:
        """Returns stat deltas if the scenario resolves this step."""
        deltas = {}
        msg = ""

        if self.active_scenario is not None:
            if action_taken in self.active_scenario.outcomes:
                # The agent took a valid resolution action
                deltas = self.active_scenario.outcomes[action_taken]
                msg = f"Scenario Resolved! Insight: {self.active_scenario.life_insight}"
                self.history.append(self.active_scenario.id)
                self.active_scenario = None
                self.scenario_steps_left = 0
            else:
                self.scenario_steps_left -= 1
                if self.scenario_steps_left <= 0:
                    msg = "Scenario failed (timeout). " + self.active_scenario.life_insight
                    # Apply a negative consequence for ignoring life
                    deltas = {"stress": 15, "happiness": -10}
                    self.active_scenario = None

        return {"deltas": deltas, "message": msg}

    def try_trigger(self, env_state: dict, step: int) -> LifeScenario:
        # Random chance to fire if not active
        if self.active_scenario is None:
            # e.g., 2% chance per step to hit a life scenario
            if random.random() < 0.02:
                seed = int(step * random.randint(1, 1000))
                self.active_scenario = generate_scenario(seed, env_state)
                self.scenario_steps_left = 3  # The agent has 3 steps to react using one of the mapped actions
                return self.active_scenario
        return None
