import gymnasium as gym
from gymnasium import spaces
import numpy as np
from environment import HumanLifeSimulator

class HumanLifeGymEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.env = HumanLifeSimulator()

        # ALL valid action strings from environment.py
        self.action_list = [
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

        # Discrete action space
        self.action_space = spaces.Discrete(len(self.action_list))

        # Observation space: 35 normalized dimensions
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(35,),
            dtype=np.float32
        )

    def _obs_to_array(self, obs_dict) -> np.ndarray:
        curr_step = obs_dict["current_step"]
        next_exam_step = min([e for e in [72, 144] if e >= curr_step] + [168])
        exam_in_days = (next_exam_step - curr_step) / 24.0
        
        assgn_due = 0.0
        if obs_dict.get("assignment_queue") and len(obs_dict["assignment_queue"]) > 0:
            if obs_dict["assignment_queue"][0]["due_step"] - curr_step <= 24:
                assgn_due = 1.0

        obs_array = np.array([
            obs_dict["energy"] / 100.0,
            obs_dict["happiness"] / 100.0,
            obs_dict["health"] / 100.0,
            obs_dict["academic_score"] / 100.0,
            obs_dict["stress"] / 100.0,
            obs_dict["social_bonds"] / 100.0,
            obs_dict["money"] / 200.0,
            min(obs_dict["sleep_debt"], 48.0) / 48.0,
            obs_dict["creativity"] / 100.0,
            obs_dict["motivation"] / 100.0,
            obs_dict["reputation"] / 100.0,
            obs_dict["focus_level"] / 10.0,
            min(obs_dict["loneliness_streak"], 168.0) / 168.0,
            obs_dict["caffeine_level"] / 100.0,
            obs_dict["gut_health"] / 100.0,
            obs_dict["sleep_quality"] / 100.0,
            obs_dict["self_discipline"] / 100.0,
            obs_dict["environmental_noise"] / 10.0,
            obs_dict["hour_of_day"] / 24.0,
            obs_dict["day_of_week"] / 7.0,
            obs_dict["last_meal_hours_ago"] / 12.0,
            obs_dict["current_step"] / 168.0,
            min(obs_dict["consecutive_junk_meals"], 10.0) / 10.0,
            float(obs_dict["project_completed"]),
            float(obs_dict["burnout_occurred"]),
            float(obs_dict["internship_unlocked"]),
            float(obs_dict["helped_friend_in_crisis"]),
            float(obs_dict["caffeine_crash_imminent"]),
            1.0 if obs_dict["toxic_friend"] is not None else 0.0,
            exam_in_days / 7.0,
            assgn_due,
            obs_dict["financial_stress"] / 100.0,
            obs_dict["physical_fitness"] / 100.0,
            float(obs_dict["scenario_active"]),
            obs_dict["scenario_domain_idx"] / 10.0
        ], dtype=np.float32)
        
        return np.clip(obs_array, 0.0, 1.0)

    def reset(self, seed=None, options=None):
        if seed is not None:
            np.random.seed(seed)
        obs_dict = self.env.reset()
        return self._obs_to_array(obs_dict), {}

    def step(self, action_idx: int):
        action_name = self.action_list[action_idx]
        result = self.env.step(action_name)

        if len(result) == 4:
            new_obs, reward, done, info = result
            terminated, truncated = done, False
        else:
            new_obs, reward, terminated, truncated, info = result

        obs_array = self._obs_to_array(new_obs)
        return obs_array, float(reward), terminated, truncated, info

    def get_grade(self) -> float:
        return self.env.grade()

    def get_stats(self) -> dict:
        return self.env.get_stats() if hasattr(self.env, 'get_stats') else {}
