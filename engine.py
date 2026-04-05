"""
engine.py — Life Mechanics Engine for Human Life Simulator
Pure math functions. No game logic, no episode state — only stat calculations.
"""


class LifeEngine:
    # ── CONSTANTS ──────────────────────────────────────────────────────────
    MAX_ENERGY = 100
    MAX_HEALTH = 100
    MAX_HAPPINESS = 100
    MAX_ACADEMIC = 100
    MAX_SOCIAL = 100
    MAX_STRESS = 100
    MAX_MONEY = 200
    MAX_SLEEP_DEBT = 48  # hours

    # ── CLAMP HELPER ───────────────────────────────────────────────────────
    @staticmethod
    def _clamp(value, lo, hi):
        return max(lo, min(hi, value))

    # ── apply_action_effects ───────────────────────────────────────────────
    def apply_action_effects(self, stats: dict, action: str) -> dict:
        """
        Takes the current stats dict and an action string.
        Returns a NEW stats dict after applying action deltas and all modifiers.
        """
        s = {k: v for k, v in stats.items()}  # shallow copy

        if action == "attend_class":
            # Availability enforced by environment; engine applies raw deltas.
            s["energy"]      += -8
            s["happiness"]   += -3
            s["health"]      +=  0
            s["academic"]    += 12
            s["social_bonds"]+= 3
            s["money"]       +=  0
            s["stress"]      += -2
            s["sleep_debt"]  +=  0

        elif action == "study":
            energy_delta   = -10
            happiness_delta = -5
            stress_delta    =  5
            academic_gain   =  8.0  # float for modifier math

            # Modifiers — multiply all applicable together
            modifier = 1.0
            if s["sleep_debt"] > 10:
                modifier *= 0.5
            if s["energy"] < 20:
                modifier *= 0.4
            if s["stress"] > 70:
                modifier *= 0.6

            academic_gain *= modifier

            s["energy"]    += energy_delta
            s["happiness"] += happiness_delta
            s["academic"]  += academic_gain
            s["stress"]    += stress_delta

        elif action == "skip_class":
            s["energy"]      +=  5
            s["happiness"]   += 10
            s["health"]      +=  0
            s["academic"]    += -15
            s["social_bonds"]+=  0
            s["money"]       +=  0
            s["stress"]      +=  8
            s["sleep_debt"]  +=  0

        elif action == "procrastinate":
            s["energy"]      +=  2
            s["happiness"]   +=  3
            s["health"]      +=  0
            s["academic"]    +=  0
            s["social_bonds"]+=  0
            s["money"]       +=  0
            s["stress"]      += 15
            s["sleep_debt"]  +=  0

        elif action == "sleep":
            base_energy_gain = 25
            # Sick modifier: health < 30 → half energy recovery
            if s["health"] < 30:
                base_energy_gain = int(base_energy_gain * 0.5)

            # Day-sleep check is handled by the engine param hour if passed,
            # but environment passes the hour context separately.
            # Raw deltas (day/night distinction handled via context in env):
            s["energy"]      += base_energy_gain
            s["happiness"]   +=  5
            s["health"]      +=  3
            s["academic"]    +=  0
            s["social_bonds"]+=  0
            s["money"]       +=  0
            s["stress"]      += -15
            s["sleep_debt"]  +=  -8

        elif action == "sleep_day":
            # Internal alias used when environment detects daytime sleep
            base_energy_gain = 15
            if s["health"] < 30:
                base_energy_gain = int(base_energy_gain * 0.5)
            s["energy"]      += base_energy_gain
            s["happiness"]   +=  5
            s["health"]      +=  3
            s["stress"]      += -15
            s["sleep_debt"]  +=  -8

        elif action == "nap":
            s["energy"]      += 10
            s["happiness"]   +=  3
            s["health"]      +=  0
            s["academic"]    +=  0
            s["social_bonds"]+=  0
            s["money"]       +=  0
            s["stress"]      +=  -5
            s["sleep_debt"]  +=   0  # nap does NOT reduce sleep_debt

        elif action == "exercise":
            # Requires money >= 10; environment enforces and passes "idle" if not.
            s["energy"]      += -15
            s["happiness"]   +=  15
            s["health"]      +=  20
            s["academic"]    +=   0
            s["social_bonds"]+= 5
            s["money"]       += -10
            s["stress"]      += -10
            s["sleep_debt"]  +=   0

        elif action == "eat_healthy":
            # Requires money >= 20; environment falls back to eat_junk if not.
            s["energy"]      += 10
            s["happiness"]   +=  5
            s["health"]      += 10
            s["academic"]    +=  0
            s["social_bonds"]+=  0
            s["money"]       += -20
            s["stress"]      +=  -3
            s["sleep_debt"]  +=   0

        elif action == "eat_junk":
            if s["money"] >= 10:
                s["energy"]      +=  8
                s["happiness"]   +=  8
                s["health"]      += -10
                s["academic"]    +=   0
                s["social_bonds"]+=   0
                s["money"]       += -10
                s["stress"]      +=   0
                s["sleep_debt"]  +=   0
            else:
                # Starving — no money at all
                s["energy"]      +=  3
                s["happiness"]   +=  1
                s["health"]      +=  -5

        elif action == "socialize":
            if s["money"] >= 15:
                s["energy"]      +=  -5
                s["happiness"]   +=  20
                s["health"]      +=   0
                s["academic"]    +=   0
                s["social_bonds"]+= 15
                s["money"]       += -15
                s["stress"]      +=  -8
                s["sleep_debt"]  +=   0
            else:
                # Free hangout
                s["social_bonds"]+= 8
                s["happiness"]   += 10
                s["money"]       +=  0

        elif action == "scroll_phone":
            s["energy"]      +=  3
            s["happiness"]   +=  5
            s["health"]      +=  0
            s["academic"]    +=  0
            s["social_bonds"]+=  0  # social does NOT improve (fake connection)
            s["money"]       +=  0
            s["stress"]      +=  3
            s["sleep_debt"]  +=  0

        elif action == "watch_netflix":
            s["energy"]      +=  5
            s["happiness"]   += 12
            s["health"]      +=  0
            s["academic"]    +=  0
            s["social_bonds"]+=  0
            s["money"]       +=  0
            s["stress"]      +=  2
            s["sleep_debt"]  +=  0

        elif action == "work_parttime":
            s["energy"]      += -20
            s["happiness"]   +=  -5
            s["health"]      +=   0
            s["academic"]    +=  -5
            s["social_bonds"]+=  -5
            s["money"]       +=  50
            s["stress"]      +=  10
            s["sleep_debt"]  +=   0

        elif action == "meditate":
            s["energy"]      +=  5
            s["happiness"]   += 10
            s["health"]      +=  5
            s["academic"]    +=  0
            s["social_bonds"]+=  0
            s["money"]       +=  0
            s["stress"]      += -20
            s["sleep_debt"]  +=  0

        elif action == "idle":
            # Fallback: slight passive rest
            s["energy"]      +=  1
            s["stress"]      +=  2

        # ── CLAMP ALL STATS ────────────────────────────────────────────────
        s["energy"]       = self._clamp(s["energy"],       0,   self.MAX_ENERGY)
        s["health"]       = self._clamp(s["health"],       0,   self.MAX_HEALTH)
        s["happiness"]    = self._clamp(s["happiness"],    0,   self.MAX_HAPPINESS)
        s["academic"]     = self._clamp(s["academic"],     0,   self.MAX_ACADEMIC)
        s["social_bonds"] = self._clamp(s["social_bonds"], 0,   self.MAX_SOCIAL)
        s["money"]        = self._clamp(s["money"],        0,   self.MAX_MONEY)
        s["stress"]       = self._clamp(s["stress"],       0,   self.MAX_STRESS)
        s["sleep_debt"]   = self._clamp(s["sleep_debt"],   0,   self.MAX_SLEEP_DEBT)

        return s

    # ── apply_passive_decay ────────────────────────────────────────────────
    def apply_passive_decay(self, stats: dict, hour: int) -> dict:
        """
        Every timestep, passive effects happen regardless of action.
        Returns updated stats dict.
        """
        s = {k: v for k, v in stats.items()}

        # 1. Sleep debt passive stress multiplier
        if s["sleep_debt"] > 10:
            extra_stress = (s["sleep_debt"] - 10) * 0.5
            s["stress"] = min(100.0, s["stress"] + extra_stress)

        # 2. Social isolation decay
        if s["social_bonds"] < 20:
            s["happiness"] -= 2
        if s["social_bonds"] == 0:
            s["happiness"] -= 3  # additional penalty on top

        # 3. Stress-happiness drain
        if s["stress"] > 80:
            s["happiness"] -= 3

        # 4. Health passive drain (baseline aging/entropy)
        s["health"] -= 0.2

        # Clamp after passive effects
        s["energy"]       = self._clamp(s["energy"],       0,   self.MAX_ENERGY)
        s["health"]       = self._clamp(s["health"],       0,   self.MAX_HEALTH)
        s["happiness"]    = self._clamp(s["happiness"],    0,   self.MAX_HAPPINESS)
        s["social_bonds"] = self._clamp(s["social_bonds"], 0,   self.MAX_SOCIAL)
        s["stress"]       = self._clamp(s["stress"],       0,   self.MAX_STRESS)

        return s

    # ── calculate_study_effectiveness ─────────────────────────────────────
    def calculate_study_effectiveness(self, stats: dict) -> float:
        """
        Returns a multiplier (0.0–1.0) representing how effectively
        the person can study RIGHT NOW.
        """
        modifier = 1.0

        if stats["energy"] < 20:
            modifier *= 0.4
        if stats["sleep_debt"] > 16:
            modifier *= 0.5
        if stats["stress"] > 80:
            modifier *= 0.5
        if stats["happiness"] < 20:
            modifier *= 0.7

        # Floor at 0.1 — always some tiny gain
        return float(max(0.1, modifier))

    # ── calculate_reward ──────────────────────────────────────────────────
    def calculate_reward(
        self,
        stats_before: dict,
        stats_after: dict,
        action: str,
        context: dict
    ) -> float:
        """
        context keys: hour, day, exam_in_days, assignment_due,
                      junk_food_streak, exam_scores (list)
        Returns float reward.
        """
        hour             = context.get("hour", 12)
        exam_in_days     = context.get("exam_in_days", 7)
        assignment_due   = context.get("assignment_due", False)
        junk_food_streak = context.get("junk_food_streak", 0)

        base_reward = 0.0

        # ── POSITIVE REWARDS ──────────────────────────────────────────────
        if action == "attend_class":
            base_reward += 2.0

        if action == "study":
            energy_before = stats_before["energy"]
            if energy_before > 50:
                base_reward += 3.0
            elif energy_before <= 20:
                base_reward += 0.5
            else:  # 21–50
                base_reward += 1.5

        if action == "exercise":
            base_reward += 3.0

        if action == "eat_healthy":
            base_reward += 2.0

        if action == "meditate" and stats_before["stress"] > 60:
            base_reward += 4.0

        if action == "sleep" and (hour >= 22 or hour <= 7):
            # Night sleep bonus — each hour toward 7h target
            base_reward += 1.0  # Per-hour night sleep reward

        if action == "socialize" and exam_in_days > 2:
            base_reward += 2.0

        # ── NEGATIVE REWARDS ──────────────────────────────────────────────
        if action == "skip_class":
            base_reward -= 5.0

        if action == "procrastinate" and assignment_due:
            base_reward -= 6.0
        elif action == "procrastinate":
            base_reward -= 1.0

        if action == "watch_netflix" and exam_in_days <= 1:
            base_reward -= 3.0

        if action == "socialize" and exam_in_days <= 1:
            base_reward -= 4.0

        if junk_food_streak >= 3:
            base_reward -= 2.0

        # ── CATASTROPHIC EVENTS ───────────────────────────────────────────
        if stats_after["stress"] >= 100:
            base_reward -= 50.0

        if stats_after["energy"] == 0 and action != "sleep":
            base_reward -= 2.0

        # ── PROGRESS REWARDS ──────────────────────────────────────────────
        academic_gain = stats_after["academic"] - stats_before["academic"]
        if academic_gain > 0:
            base_reward += academic_gain * 0.3

        # Small time-step penalty to encourage efficiency
        base_reward -= 0.05

        return float(base_reward)
