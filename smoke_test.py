from server import TrainConfig, run_training_background, training_state
import time
import threading

def check():
    cfg = TrainConfig(n_envs=1, total_episodes=5, device="cpu")
    t = threading.Thread(target=run_training_background, args=(cfg,))
    t.start()
    
    for _ in range(15):
        time.sleep(1)
        print(f"Episode: {training_state['current_episode']}, Rewards: {training_state['current_avg_reward']}")
        if training_state['current_episode'] >= 4:
            break
            
    training_state['stop_flag'] = True
    t.join()
    print("Smoke test finished!")

if __name__ == "__main__":
    check()
