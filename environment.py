import numpy as np
from scenarios import ScenarioEngine

class HumanLifeSimulator:
    def __init__(self):
        self.VALID_ACTIONS = [
            "attend_class", "study", "skip_class", "procrastinate", "sleep",
            "nap", "exercise", "eat_healthy", "eat_junk", "socialize",
            "scroll_phone", "watch_netflix", "work_parttime", "meditate",
            "build_personal_project", "group_study", "drink_coffee", "journal",
            "take_a_walk", "attend_office_hours", "help_a_friend",
            "skip_class_and_self_study", "cold_shower", "cook_at_home",
            "meal_prep", "call_family", "therapy_session", "doomscroll",
            "all_nighter", "seek_peer_notes", "study_with_music", "pull_a_prank",
            "do_nothing", "half_study", "micro_socialize", "binge_eat",
            "nap_in_class", "plagiarize", "withdraw_from_course",
            "help_a_friend_in_crisis",
            "apply_for_internship", "part_time_study_break", "visit_campus_clinic",
            "attend_club_meeting", "buy_groceries", "stress_eat_late_night",
            "all_day_grind", "sleep_schedule_reset", "visit_library",
            "ask_professor_for_help", "self_care_day", "pull_all_nighter_group",
            "online_course", "freelance_work", "decline_social_invite"
        ]
        self.scenario_engine = ScenarioEngine()
        self.reset()

    def reset(self) -> dict:
        self.rng = np.random.default_rng(seed=42)

        # Core Stats
        self.energy = 80.0
        self.happiness = 60.0
        self.health = 70.0
        self.academic_score = 50.0
        self.stress = 20.0
        self.social_bonds = 50.0
        self.money = 100.0
        self.sleep_debt = 0.0

        # New Variables
        self.creativity = 50.0
        self.motivation = 60.0
        self.reputation = 50.0
        self.focus_level = 5
        self.loneliness_streak = 0
        self.caffeine_level = 0.0
        self.gut_health = 70.0
        self.sleep_quality = 70.0
        self.self_discipline = 50.0
        self.environmental_noise = 3

        # Tracking Variables
        self.hour_of_day = 8
        self.day_of_week = 0
        self.last_meal_hours_ago = 0
        self.current_step = 0
        self.exam_scores = []
        self.consecutive_junk_meals = 0
        self.emotional_state = "neutral"
        self.assignment_queue = []
        
        self.friendship_depth = {
            "friend_a": 40.0,
            "friend_b": 20.0,
            "friend_c": 10.0
        }
        toxic_choices = ["friend_a", "friend_b", "friend_c"]
        self.toxic_friend = self.rng.choice(toxic_choices)
        
        self.project_build_count = 0
        self.project_completed = False
        self.burnout_occurred = False
        self.internship_unlocked = False
        self.helped_friend_in_crisis = False
        self.caffeine_crash_imminent = False
        
        self.cook_at_home_count = 0
        self.meal_prep_active_steps = 0
        self.withdrawn_from_course = False
        self.plagiarism_paranoia = False
        self.office_hours_this_week = 0
        self.counseling_free_steps = 0
        self.study_group_invite_steps = 0
        self.power_outage_steps = 0
        self.roommate_conflict_steps = 0
        self.roommate_conflict_noise_applied = False
        self.friend_needs_help_steps = 0
        self.emergency_loan_debt = False
        self.friend_loan_repayment_step = -1
        self.deadline_extension = 0
        self.consecutive_journal_sleep = 0
        self.journal_done_last_step = False
        self.skip_class_self_study_count = 0
        self.cold_shower_streak = 0
        self.do_nothing_streak = 0
        self.doomscroll_streak = 0
        self.binge_ate_last_step = False
        self.free_food_available = False
        self.last_call_family_step = 0
        self.professor_cancelled = False
        self.friend_tutoring_active = 0
        
        # New Redesign Stats
        self.financial_stress = 0.0
        self.physical_fitness = 50.0
        
        self.scenario_active = False
        self.scenario_domain_idx = 0
        self.scenario_engine = ScenarioEngine()
        
        return self._get_obs()

    def _get_obs(self) -> dict:
        return {
            "energy": self.energy,
            "happiness": self.happiness,
            "health": self.health,
            "academic_score": self.academic_score,
            "stress": self.stress,
            "social_bonds": self.social_bonds,
            "money": self.money,
            "sleep_debt": self.sleep_debt,
            "creativity": self.creativity,
            "motivation": self.motivation,
            "reputation": self.reputation,
            "focus_level": self.focus_level,
            "loneliness_streak": self.loneliness_streak,
            "caffeine_level": self.caffeine_level,
            "gut_health": self.gut_health,
            "sleep_quality": self.sleep_quality,
            "self_discipline": self.self_discipline,
            "environmental_noise": self.environmental_noise,
            "hour_of_day": self.hour_of_day,
            "day_of_week": self.day_of_week,
            "last_meal_hours_ago": self.last_meal_hours_ago,
            "current_step": self.current_step,
            "exam_scores": list(self.exam_scores),
            "consecutive_junk_meals": self.consecutive_junk_meals,
            "emotional_state": self.emotional_state,
            "assignment_queue": list(self.assignment_queue),
            "friendship_depth": dict(self.friendship_depth),
            "project_build_count": self.project_build_count,
            "project_completed": self.project_completed,
            "burnout_occurred": self.burnout_occurred,
            "internship_unlocked": self.internship_unlocked,
            "helped_friend_in_crisis": self.helped_friend_in_crisis,
            "caffeine_crash_imminent": self.caffeine_crash_imminent,
            "toxic_friend": self.toxic_friend,
            "financial_stress": self.financial_stress,
            "physical_fitness": self.physical_fitness,
            "scenario_active": self.scenario_active,
            "scenario_domain_idx": self.scenario_domain_idx
        }

    def _clamp(self):
        self.physical_fitness = max(0.0, min(100.0, self.physical_fitness))
        self.financial_stress = max(0.0, min(100.0, self.financial_stress))
        self.energy = max(0.0, min(100.0, self.energy))
        self.happiness = max(0.0, min(100.0, self.happiness))
        self.health = max(0.0, min(100.0, self.health))
        self.academic_score = max(0.0, min(100.0, self.academic_score))
        self.stress = max(0.0, min(100.0, self.stress))
        self.social_bonds = max(0.0, min(100.0, self.social_bonds))
        self.money = max(0.0, min(200.0, self.money))
        self.sleep_debt = max(0.0, self.sleep_debt)
        self.creativity = max(0.0, min(100.0, self.creativity))
        self.motivation = max(0.0, min(100.0, self.motivation))
        self.reputation = max(0.0, min(100.0, self.reputation))
        self.focus_level = max(0, min(10, self.focus_level))
        self.caffeine_level = max(0.0, min(100.0, self.caffeine_level))
        self.gut_health = max(0.0, min(100.0, self.gut_health))
        self.sleep_quality = max(0.0, min(100.0, self.sleep_quality))
        self.self_discipline = max(0.0, min(100.0, self.self_discipline))
        self.environmental_noise = max(0, min(10, self.environmental_noise))
        self.last_meal_hours_ago = max(0, min(12, self.last_meal_hours_ago))

    def step(self, action: str) -> tuple:
        reward = 0.0
        done = False
        info = {
            "action_taken": action,
            "constraints_triggered": [],
            "events_fired": [],
            "reward_breakdown": {},
            "warnings": []
        }

        # 1. Update emotional state FIRST (so it applies to this step)
        self._update_emotional_state()
        info["emotional_state"] = self.emotional_state

        # Pre-action caffeine level for crash check
        prev_caffeine = self.caffeine_level

        # Validation & Locks
        if action not in self.VALID_ACTIONS:
            info["warnings"].append("Unknown action string.")
            action = "skip"
            reward -= 0.5
            
        locked = False
        if self.money <= 0 and action in ["exercise", "eat_healthy", "socialize"]:
            locked = True
        
        if self.motivation <= 0:
            allowed_when_unmotivated = ["scroll_phone", "watch_netflix", "sleep",
                "eat_junk", "do_nothing", "doomscroll", "call_family", "journal", "nap", "eat_healthy", "binge_eat"]
            if action not in allowed_when_unmotivated:
                locked = True
            
        if self.power_outage_steps > 0 and action in ["scroll_phone", "watch_netflix"]:
            locked = True
            
        if action == "meal_prep" and self.cook_at_home_count < 5:
            locked = True
            
        if action == "build_personal_project" and not (self.creativity > 85 or self.motivation > 80):
            locked = True

        if action == "group_study":
            if not any(v > 40 for v in self.friendship_depth.values()):
                locked = True

        if action == "help_a_friend":
            if not any(v > 30 for v in self.friendship_depth.values()) or self.energy <= 30:
                locked = True

        if action == "seek_peer_notes":
            if not any(v > 40 for v in self.friendship_depth.values()):
                locked = True
            
        if action == "attend_office_hours":
            if not (14 <= self.hour_of_day <= 17):
                locked = True
            if self.office_hours_this_week >= 2:
                locked = True
            if self.reputation < 30:
                locked = True

        if action == "nap_in_class":
            if not (9 <= self.hour_of_day <= 17 and self.day_of_week <= 4):
                locked = True

        if action == "therapy_session":
            if not (self.stress > 60 or self.emotional_state == "depressed") and self.counseling_free_steps <= 0:
                locked = True

        if action == "withdraw_from_course" and self.withdrawn_from_course:
            locked = True

        if self.energy <= 0:
            info["constraints_triggered"].append("energy <= 0 (forced sleep)")
            action = "sleep"
            locked = False # Forced action

        if locked:
            info["constraints_triggered"].append(f"Locked action attempted: {action}")
            reward -= 1.0
            action = "skip"

        # Special Action Replacements
        if action in ["watch_netflix", "scroll_phone", "doomscroll", "socialize", "micro_socialize"]:
            self.focus_level = 0

        # Modifiers based on state and overrides
        action_cost_multiplier = 0.8 if self.emotional_state == "euphoric" else 1.0
        
        is_meal = False
        is_social = False
        
        if self.meal_prep_active_steps > 0 and action not in ["eat_healthy", "eat_junk", "cook_at_home", "binge_eat"]:
            self.meal_prep_active_steps -= 1
            if self.meal_prep_active_steps > 0:
                pass # Already acting as eat_healthy in background logic? Spec says "benefits without spending an action"
                self.energy += 10
                self.health += 10
                self.gut_health += 8 # approximated
                is_meal = True

        # Process Action
        if action == "attend_class":
            if self.professor_cancelled:
                self.professor_cancelled = False
                info["events_fired"].append("Professor cancelled class — energy saved")
            else:
                gain = 12
                if self.motivation < 30: gain *= 0.5
                if self.gut_health < 15: gain *= 0.5
                self.academic_score += gain
                self.energy -= 8
                self.stress -= 2
                self.social_bonds += 3
                self.creativity -= 2
            reward += 2.0
            
        elif action == "study":
            gain = 8
            if self.environmental_noise > 8:
                gain = 0
            elif self.focus_level == 10:
                gain *= 2
            elif self.focus_level > 7:
                gain += 2
                
            if self.motivation > 70: gain *= 1.5
            if self.sleep_debt > 10: gain *= 0.7
            if self.gut_health < 15: gain *= 0.5
            if self.emotional_state == "anxious": gain *= 0.8
            
            if self.journal_done_last_step and self.stress > 70:
                gain += 5 # Insight bonus from journaling previous step
                
            self.academic_score += gain
            self.energy -= 10 * action_cost_multiplier
            self.happiness -= 5
            self.stress += 5
            self.focus_level += 1
            self.creativity -= 1
            
            if self.energy > 50: reward += 3.0
            elif self.energy < 20: reward += 0.5
            else: reward += 1.5
            
        elif action == "study_with_music":
            gain = 5
            if self.focus_level > 6: gain = 3
            elif self.focus_level < 3: gain = 7
            
            if self.sleep_debt > 10: gain *= 0.7
            if self.gut_health < 15: gain *= 0.5
            
            self.academic_score += gain
            self.energy -= 8 * action_cost_multiplier
            self.happiness += 5
            self.stress -= 3
            self.focus_level += 1
            
            if self.energy > 50: reward += 3.0
            elif self.energy < 20: reward += 0.5
            else: reward += 1.5

        elif action == "skip_class":
            self.energy += 5
            self.happiness += 10
            self.academic_score -= 15
            self.stress += 8
            self.reputation -= 5
            reward -= 5.0

        elif action == "procrastinate":
            stress_gain = 5 if self.self_discipline > 75 else 15
            self.stress += stress_gain
            self.energy += 2
            
            deadline_soon = False
            for a in self.assignment_queue:
                if not a["submitted"] and a["due_step"] - self.current_step <= 24:
                    deadline_soon = True
                    break
            
            if deadline_soon:
                reward -= 6.0
            else:
                reward -= 1.0
                
            if self.self_discipline > 90:
                reward -= 1.0

        elif action == "sleep":
            recovery = 25
            if self.health < 30: recovery *= 0.5
            if self.sleep_quality > 70: recovery += 5
            
            prev_debt = self.sleep_debt
            self.energy += recovery
            self.stress -= 15
            self.sleep_debt = max(0.0, self.sleep_debt - 8)
            
            if self.sleep_quality < 30:
                self.sleep_debt += 2
                
            if self.journal_done_last_step:
                self.consecutive_journal_sleep += 1
            else:
                self.consecutive_journal_sleep = 0
                
            debt_reduced = prev_debt - self.sleep_debt
            if debt_reduced >= 6: reward += 4.0
            elif prev_debt == 0: reward += 1.0

        elif action == "nap":
            self.energy += 10
            self.stress -= 5
            # Doesn't reduce sleep debt

        elif action == "exercise":
            self.health += 20
            self.happiness += 15
            self.stress -= 10
            self.energy -= 15 * action_cost_multiplier
            self.money -= 10
            self.motivation += 5
            reward += 3.0

        elif action == "eat_healthy":
            self.energy += 10
            self.health += 10
            self.happiness += 5
            self.stress -= 3
            self.money -= 20
            self.gut_health += 8
            is_meal = True
            reward += 2.0

        elif action == "eat_junk":
            self.energy += 8
            self.health -= 10
            self.happiness += 8
            self.money -= 10
            self.gut_health -= 5
            is_meal = True
            self.consecutive_junk_meals += 1

        elif action == "socialize":
            self.social_bonds += 15
            self.happiness += 20
            self.stress -= 8
            self.energy -= 5 * action_cost_multiplier
            self.money -= 15
            if self.reputation > 70:
                self.social_bonds += 5
            is_social = True
            
            exam_soon = any(e - self.current_step <= 24 for e in [72, 144] if e > self.current_step)
            if exam_soon:
                reward -= 4.0
            elif self.stress < 60:
                reward += 2.0

        elif action == "scroll_phone":
            self.happiness += 5
            self.stress += 3
            self.energy += 3
            reward -= 0.3

        elif action == "watch_netflix":
            if self.creativity < 20:
                hp = 0
            else:
                hp = 12
            self.happiness += hp
            self.stress += 2
            self.energy += 5
            reward -= 0.2

        elif action == "work_parttime":
            self.money += 50
            self.energy -= 20 * action_cost_multiplier
            self.academic_score -= 5
            self.social_bonds -= 5
            self.stress += 10
            reward += 1.0

        elif action == "meditate":
            self.stress -= 20
            self.happiness += 10
            self.health += 5
            self.energy += 5
            reward += 2.0

        elif action == "build_personal_project":
            self.energy -= 12 * action_cost_multiplier
            self.happiness += 18
            self.academic_score += 3
            self.creativity += 15
            self.stress -= 5
            self.focus_level += 2
            self.project_build_count += 1
            if self.project_build_count >= 3:
                self.project_completed = True
                self.reputation += 20
                self.motivation += 30
                reward += 15.0
                self.project_build_count = 0
            reward += 2.5

        elif action == "group_study":
            gain = 10
            if self.environmental_noise > 5:
                gain = 3
            self.academic_score += gain
            self.energy -= 8 * action_cost_multiplier
            self.happiness += 8
            self.social_bonds += 8
            self.stress -= 3
            is_social = True
            
            for k in self.friendship_depth:
                self.friendship_depth[k] += 1
            reward += 2.0

        elif action == "drink_coffee":
            pre_caff = self.caffeine_level
            self.energy += 20
            self.caffeine_level += 30
            self.stress += 5
            if pre_caff < 50: reward += 0.5
            elif pre_caff > 70: reward -= 1.0

        elif action == "journal":
            self.energy -= 2 * action_cost_multiplier
            self.happiness += 8
            self.stress -= 10
            self.creativity += 8
            self.motivation += 10
            self.self_discipline += 3
            reward += 1.5

        elif action == "take_a_walk":
            self.energy -= 5 * action_cost_multiplier
            self.happiness += 10
            self.health += 5
            self.creativity += 5
            self.focus_level += 1
            stress_drop = 16 if self.environmental_noise > 7 else 8
            self.stress -= stress_drop
            if 6 <= self.hour_of_day <= 8:
                self.sleep_quality += 10
            reward += 1.0

        elif action == "attend_office_hours":
            self.energy -= 5 * action_cost_multiplier
            self.academic_score += 15
            self.stress -= 5
            self.reputation += 8
            self.office_hours_this_week += 1
            reward += 3.5

        elif action == "help_a_friend":
            self.energy -= 10 * action_cost_multiplier
            self.happiness += 15
            self.social_bonds += 20
            self.stress -= 5
            # Pick highest friend to help
            best_friend = max(self.friendship_depth, key=self.friendship_depth.get)
            self.friendship_depth[best_friend] += 25
            is_social = True
            
            exam_soon = any(e - self.current_step <= 24 for e in [72, 144] if e > self.current_step)
            if exam_soon:
                reward -= 1.0
            else:
                reward += 2.0

        elif action == "skip_class_and_self_study":
            self.energy -= 5 * action_cost_multiplier
            self.academic_score += 6
            self.creativity += 5
            self.happiness += 5
            self.reputation -= 5
            self.stress += 3
            self.skip_class_self_study_count += 1
            if self.skip_class_self_study_count >= 3:
                self.self_discipline += 5
                self.reputation -= 15
            reward -= 1.0

        elif action == "cold_shower":
            self.energy += 15
            self.stress -= 12
            self.health += 3
            self.caffeine_level -= 20
            self.happiness -= 2
            self.cold_shower_streak += 1
            if self.cold_shower_streak >= 3:
                self.health += 5
            reward += 1.0

        elif action == "cook_at_home":
            self.energy -= 5 * action_cost_multiplier
            self.health += 15
            self.gut_health += 10
            self.money -= 5
            self.happiness += 10
            self.creativity += 3
            self.cook_at_home_count += 1
            if any(v > 50 for v in self.friendship_depth.values()):
                if self.rng.random() < 0.3:
                    self.social_bonds += 10
                    is_social = True
            is_meal = True
            reward += 2.5

        elif action == "meal_prep":
            self.energy -= 15 * action_cost_multiplier
            self.money -= 15
            self.meal_prep_active_steps = 3
            self.self_discipline += 5
            self.cook_at_home_count += 1

        elif action == "call_family":
            self.energy += 5
            self.happiness += 20
            if self.stress > 80:
                self.stress -= 25
            else:
                self.stress -= 15
            self.loneliness_streak = 0
            self.last_call_family_step = self.current_step
            reward += 2.0

        elif action == "therapy_session":
            if self.counseling_free_steps <= 0:
                self.money -= 30
            self.stress -= 30
            self.happiness += 20
            self.motivation += 25
            self.emotional_state = "neutral"
            reward += 3.0

        elif action == "doomscroll":
            self.energy += 2
            self.happiness -= 5 # +3 then -8
            self.stress += 8
            self.self_discipline -= 5
            self.motivation -= 10
            self.focus_level = 0
            self.doomscroll_streak += 1
            if self.doomscroll_streak >= 3:
                self.emotional_state = "depressed"
            reward -= 1.5

        elif action == "all_nighter":
            if self.health < 40:
                self.academic_score += 7
                self.energy = 0
                info["warnings"].append("all_nighter failed due to low health")
            else:
                self.academic_score += 20
                self.energy -= 40
            
            self.stress += 25
            self.sleep_debt += 8
            self.health -= 5
            self.sleep_quality -= 40
            
            exam_soon = any(e - self.current_step <= 1 for e in [72, 144] if e > self.current_step)
            if exam_soon:
                reward += 2.0
            else:
                reward -= 3.0

        elif action == "seek_peer_notes":
            self.energy -= 2 * action_cost_multiplier
            self.academic_score += 8 # Ignoring genius friend edge case for simplicity
            self.social_bonds += 5
            is_social = True

        elif action == "pull_a_prank":
            self.happiness += 25
            self.social_bonds += 10
            self.stress -= 10
            
            r = self.rng.random()
            if r < 0.2:
                self.reputation += 30
                self.happiness += 20
                info["events_fired"].append("Viral moment! reputation +30, happiness +20")
            elif r < 0.35:
                # Annoy
                self.friendship_depth[self.rng.choice(list(self.friendship_depth.keys()))] -= 20
                self.reputation -= 15
            else:
                self.reputation += 15
                
            reward += float(self.rng.uniform(-2, 3))

        elif action == "do_nothing":
            self.do_nothing_streak += 1
            if self.stress > 95:
                self.stress -= 8
            elif self.stress > 70:
                self.stress -= 3
                reward += 0.5
            else:
                reward -= 0.2
            if self.do_nothing_streak >= 3:
                self.motivation -= 5

        elif action == "half_study":
            self.energy -= 3 * action_cost_multiplier
            self.academic_score += 3
            self.happiness -= 1
            self.stress += 1
            reward += 1.0

        elif action == "micro_socialize":
            self.happiness += 5
            self.social_bonds += 3
            self.loneliness_streak = max(0, self.loneliness_streak - 12)
            reward += 0.5

        elif action == "binge_eat":
            self.energy += 15
            self.happiness += 0 # +10 then -10
            self.health -= 20
            self.gut_health -= 25
            
            if self.emotional_state == "depressed":
                self.stress -= 15
            else:
                self.stress -= 5
                
            is_meal = True
            reward -= 2.0

        elif action == "nap_in_class":
            self.energy += 8
            self.academic_score -= 5
            self.reputation -= 10
            self.stress -= 5
            if self.reputation < 20:
                self.stress += 10
            reward -= 2.0

        elif action == "plagiarize":
            self.academic_score += 25
            self.stress -= 10
            if self.rng.random() < 0.3:
                self.academic_score = 0
                self.reputation = 0
                self.stress += 50
                reward -= 30.0
            else:
                self.plagiarism_paranoia = True
                
        elif action == "withdraw_from_course":
            self.withdrawn_from_course = True
            self.stress -= 20
            self.academic_score -= 10
            self.reputation -= 5
            if self.assignment_queue:
                self.assignment_queue.pop(0)
            reward -= 2.0

        elif action == "help_a_friend_in_crisis":
            self.helped_friend_in_crisis = True
            self.friendship_depth[self.rng.choice(list(self.friendship_depth.keys()))] += 25
            reward += 2.0

        elif action == "apply_for_internship":
            if self.academic_score > 75 and self.reputation > 70:
                self.internship_unlocked = True
                self.happiness += 20
                reward += 10.0
            else:
                self.stress += 15
                self.happiness -= 10
                reward -= 5.0
                
        elif action == "part_time_study_break":
            self.energy += 5
            self.stress -= 5
            self.academic_score += 1
            reward += 0.5
            
        elif action == "visit_campus_clinic":
            self.health += 30
            self.energy -= 10
            self.money -= 10
            self.stress -= 10
            reward += 2.0

        elif action == "attend_club_meeting":
            self.social_bonds += 10
            self.reputation += 5
            self.creativity += 5
            self.energy -= 10
            is_social = True
            reward += 1.5

        elif action == "buy_groceries":
            self.money -= 40
            self.health += 5
            self.financial_stress += 10
            self.energy -= 10
            reward += 1.0

        elif action == "stress_eat_late_night":
            self.happiness += 10
            self.stress -= 5
            self.physical_fitness -= 5
            self.health -= 5
            self.energy -= 5
            is_meal = True
            reward -= 1.0

        elif action == "all_day_grind":
            self.academic_score += 25
            self.energy = 0
            self.stress += 30
            self.social_bonds -= 10
            reward += 3.0

        elif action == "sleep_schedule_reset":
            self.sleep_debt = 0
            self.energy += 50
            self.academic_score -= 10
            self.social_bonds -= 5
            reward += 1.5

        elif action == "visit_library":
            self.academic_score += 12
            self.focus_level = min(10, self.focus_level + 3)
            self.energy -= 10
            reward += 2.0

        elif action == "ask_professor_for_help":
            if self.reputation > 40:
                self.academic_score += 15
                self.stress -= 10
                reward += 3.0
            else:
                self.stress += 10
                reward -= 1.0

        elif action == "self_care_day":
            self.stress -= 40
            self.happiness += 20
            self.health += 10
            self.energy += 20
            self.academic_score -= 15
            reward += 2.0

        elif action == "pull_all_nighter_group":
            self.academic_score += 15
            self.social_bonds += 15
            self.energy = 0
            self.stress += 20
            self.sleep_debt += 8
            is_social = True
            reward += 2.0

        elif action == "online_course":
            self.academic_score += 5
            self.creativity += 10
            self.energy -= 10
            reward += 1.5

        elif action == "freelance_work":
            self.money += 80
            self.energy -= 25
            self.stress += 15
            self.financial_stress = max(0, self.financial_stress - 20)
            reward += 2.0

        elif action == "decline_social_invite":
            self.self_discipline += 5
            self.loneliness_streak += 12
            self.stress -= 5
            reward += 1.0

        # Streak resets for non-matching actions
        if action != "do_nothing": self.do_nothing_streak = 0
        if action != "cold_shower": self.cold_shower_streak = 0
        if action != "doomscroll": self.doomscroll_streak = 0
        if action not in ["take_a_walk"]: self.consecutive_walk_count = 0
        elif action == "take_a_walk": self.consecutive_walk_count += 1

        # Binge eat post-step regret (fires the step AFTER binge_eat)
        if self.binge_ate_last_step:
            self.happiness -= 10
            self.gut_health -= 5
            info["constraints_triggered"].append("Post-binge regret: happiness -10, gut_health -5")
        self.binge_ate_last_step = (action == "binge_eat")

        # Journal flag persists to NEXT step for journal→sleep combo
        self.journal_done_last_step = (action == "journal")

        # Loneliness & Meals Tracking
        if is_social or action in ["call_family", "micro_socialize"]:
            self.loneliness_streak = 0
            if is_social and action != "micro_socialize":
                # Increase random friends depth slightly
                for k in self.friendship_depth:
                    if self.rng.random() < 0.5:
                        self.friendship_depth[k] += 2
        else:
            self.loneliness_streak += 1

        if is_meal:
            self.last_meal_hours_ago = 0
            if action != "eat_junk":
                self.consecutive_junk_meals = 0
        else:
            self.last_meal_hours_ago = min(12, self.last_meal_hours_ago + 1)
            
        if self.consecutive_junk_meals >= 72: # hours
            reward -= 2.0
            self.health -= 5
            self.consecutive_junk_meals = 0

        # PASSIVE DRAINS
        self.energy -= 0.5
        stress_passive = 0.3
        if self.sleep_debt > 10:
            stress_passive *= 1.2
        self.stress += stress_passive
        self.caffeine_level = max(0.0, self.caffeine_level - 10)
        
        if 22 <= self.hour_of_day or self.hour_of_day <= 6:
            if action not in ["sleep", "nap"]:
                self.sleep_debt += 0.5
                
        for k in self.friendship_depth:
            self.friendship_depth[k] -= 0.1
            
        self.motivation -= 0.2
        self.creativity -= 0.1
        
        if self.plagiarism_paranoia:
            self.stress += 3
            
        if self.caffeine_level > 80:
            self.stress += 5
        if self.caffeine_level > 90:
            self.health -= 1
            
        if prev_caffeine > 70 and self.caffeine_level < 30:
            self.energy -= 20
            self.caffeine_crash_imminent = True
        else:
            self.caffeine_crash_imminent = False
            
        if self.loneliness_streak > 24:
            self.happiness -= 1
        if self.loneliness_streak > 48:
            self.health -= 0.5
        if self.loneliness_streak > 72:
            self.motivation = 20
            
        if self.gut_health < 30:
            self.happiness -= 2

        # Environmental noise caps focus
        if self.environmental_noise > 6:
            self.focus_level = min(self.focus_level, 4)

        # Reward Multipliers
        if self.social_bonds <= 0 and reward > 0:
            reward *= 0.5
        if self.emotional_state == "depressed" and reward > 0:
            reward *= 0.7
        if self.stress >= 90 and self.stress <= 99:
            reward *= 0.5

        # Random Events Check
        self._check_random_events()

        # Toxic friend interaction
        if is_social:
            friend_interacted = self.rng.choice(list(self.friendship_depth.keys()))
            if friend_interacted == self.toxic_friend:
                self.stress += 5
                info["constraints_triggered"].append("Toxic friend interaction: hidden stress +5")

        # SCENARIO PROCESSING
        scenario_res = self.scenario_engine.step(self._get_obs(), action)
        if scenario_res.get("deltas"):
            for k, v in scenario_res["deltas"].items():
                if hasattr(self, k):
                    setattr(self, k, getattr(self, k) + v)
                    
        if scenario_res.get("message"):
            info["events_fired"].append(scenario_res["message"])
            
        new_scen = self.scenario_engine.try_trigger(self._get_obs(), self.current_step)
        if new_scen:
            info["events_fired"].append(f"SCENARIO STARTED: {new_scen.title} - {new_scen.description}")
            domains = ["Education", "Friendship", "Family", "Romance", "Identity", "Career", "Moral", "Mental_Health", "Money", "Societal"]
            self.scenario_active = True
            self.scenario_domain_idx = domains.index(new_scen.domain) if new_scen.domain in domains else 0
        elif self.scenario_engine.active_scenario is None:
            self.scenario_active = False

        # Advance Time
        self.hour_of_day += 1
        self.current_step += 1
        if self.hour_of_day >= 24:
            self.hour_of_day = 0
            self.day_of_week = (self.day_of_week + 1) % 7
            if self.day_of_week == 0:
                self.office_hours_this_week = 0

        # Exam Triggers
        if self.current_step == 72 or self.current_step == 144:
            score = self.academic_score
            if self.stress > 80: score *= 0.7
            if self.sleep_debt > 15: score *= 0.6
            if self.motivation < 20: score *= 0.5
            
            self.exam_scores.append(score)
            info["events_fired"].append(f"Exam taken: {score:.2f}")
            if score >= 70:
                reward += 15.0

        # Clamping
        self._clamp()

        # Burnout & Done Condition
        if self.stress >= 100:
            done = True
            reward -= 50.0
            self.burnout_occurred = True
            info["constraints_triggered"].append("Burnout reached.")
            
        if self.current_step >= 168:
            done = True
            if not self.burnout_occurred:
                reward += 10.0
            
            passed = sum(1 for s in self.exam_scores if s >= 50)
            if passed == len(self.exam_scores) and len(self.exam_scores) > 0:
                reward += 30.0
                
            final_stats = [self.energy, self.happiness, self.health, self.academic_score, self.social_bonds, 100-self.stress]
            if all(s > 50 for s in final_stats):
                reward += 20.0

        if self.internship_unlocked and done:
            reward += 20.0

        info["reward_breakdown"]["total"] = reward
        return self._get_obs(), float(reward), done, info

    def _update_emotional_state(self):
        if self.stress >= 90:
            self.emotional_state = "burnt_edge"
        elif self.loneliness_streak > 72 and self.happiness < 25:
            self.emotional_state = "depressed"
        elif (len(self.exam_scores) > 0 and self.exam_scores[-1] > 80) or self.creativity > 90:
            self.emotional_state = "euphoric"
        elif self.focus_level > 7:
            self.emotional_state = "focused"
        elif self.stress > 65:
            self.emotional_state = "anxious"
        elif self.consecutive_journal_sleep >= 3:
            self.emotional_state = "recovered"
            self.motivation += 20
            self.energy += 5
            self.health += 5
            self.happiness += 5
            self.stress = max(0, self.stress - 5)
            self.social_bonds += 5
            self.consecutive_journal_sleep = 0
        else:
            self.emotional_state = "neutral"

    def _check_random_events(self):
        if self.counseling_free_steps > 0: self.counseling_free_steps -= 1
        if self.study_group_invite_steps > 0: self.study_group_invite_steps -= 1
        if self.power_outage_steps > 0: self.power_outage_steps -= 1
        if self.friend_tutoring_active > 0:
            self.academic_score += 10
            self.friend_tutoring_active -= 1
        if self.roommate_conflict_steps > 0:
            if not self.roommate_conflict_noise_applied:
                self.environmental_noise = min(10, self.environmental_noise + 4)
                self.roommate_conflict_noise_applied = True
            self.roommate_conflict_steps -= 1
            if self.roommate_conflict_steps == 0:
                self.environmental_noise = max(0, self.environmental_noise - 4)
                self.roommate_conflict_noise_applied = False
            
        if self.friend_loan_repayment_step == self.current_step:
            self.money += 30
            
        r = self.rng.random()
        
        # Roommate conflict (day 2 or 4, 40%)
        if self.day_of_week in [2, 4] and self.hour_of_day == 12 and r < 0.4 and self.roommate_conflict_steps == 0:
            self.roommate_conflict_steps = 24
            
        # Free campus food (once per week)
        if self.hour_of_day == 12 and r < 0.1 and not self.free_food_available:
            self.free_food_available = True

        # Professor cancelled class (20% each class step)
        if 9 <= self.hour_of_day <= 17 and self.day_of_week <= 4 and self.rng.random() < 0.2:
            self.professor_cancelled = True
            
        # Counseling (day 3 or 5)
        if self.day_of_week in [3, 5] and self.hour_of_day == 10 and r < 0.5:
            self.counseling_free_steps = 12
            
        # Study group invite
        if self.reputation > 40 and r < 0.05:
            self.study_group_invite_steps = 6
            
        # Internship offer
        if not self.internship_unlocked and self.academic_score > 75 and self.reputation > 60 and r < 0.02:
            self.internship_unlocked = True

        # Friend needs help event (day 2, 4, 6)
        if self.day_of_week in [2, 4, 6] and self.hour_of_day == 14 and self.friend_needs_help_steps == 0:
            self.friend_needs_help_steps = 3

        # Friend tutoring (steps 140-155, friend depth > 75)
        if 140 <= self.current_step <= 155 and any(v > 75 for v in self.friendship_depth.values()) and self.friend_tutoring_active == 0:
            if self.rng.random() < 0.3:
                self.friend_tutoring_active = 2

        # Emergency money (friend depth > 70, money <= 0)
        if self.money <= 0 and any(v > 70 for v in self.friendship_depth.values()) and not self.emergency_loan_debt:
            self.money += 30
            self.emergency_loan_debt = True
            self.friend_loan_repayment_step = self.current_step + 10

        # Family calls you (if no call_family in 3 days = 72 steps)
        if self.current_step - self.last_call_family_step >= 72:
            self.happiness += 15
            self.stress -= 10
            self.last_call_family_step = self.current_step
            
        # Exam postponed (10% at step 60 or 132)
        if self.current_step in [60, 132] and r < 0.1:
            self.deadline_extension += 24
            
        # Power outage (once)
        if self.power_outage_steps == 0 and r < 0.01:
            self.power_outage_steps = 12

        # Assignment due
        if self.hour_of_day == 9 and self.day_of_week in [1, 4]:
            self.assignment_queue.append({
                "name": f"Assignment {len(self.assignment_queue)+1}",
                "due_step": self.current_step + 72 + self.deadline_extension,
                "difficulty": self.rng.integers(1, 4),
                "submitted": False
            })

    def grade(self) -> float:
        if not self.exam_scores:
            return 0.01
            
        passed = sum(1 for s in self.exam_scores if s >= 50)
        avg_score = sum(self.exam_scores) / len(self.exam_scores)
        exam_component = (passed / max(1, len(self.exam_scores))) * 0.6 + (avg_score / 100.0) * 0.4
        
        survived = 0.0 if self.burnout_occurred else 0.10
        
        balance_bonus = 0.0
        final_stats = [
            self.academic_score, self.health,
            self.happiness, self.social_bonds,
            (100.0 - self.stress)
        ]
        if all(s >= 50 for s in final_stats):
            balance_bonus = 0.08
            
        achievement_bonus = 0.0
        if self.project_completed:
            achievement_bonus += 0.04
        if self.internship_unlocked:
            achievement_bonus += 0.08
        if self.helped_friend_in_crisis:
            achievement_bonus += 0.04
            
        raw = exam_component + survived + balance_bonus + achievement_bonus
        return float(max(0.01, min(0.99, raw)))
