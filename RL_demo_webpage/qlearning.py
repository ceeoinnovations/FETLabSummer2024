def rl():
    script = """
import hub, color_sensor, color, motor, time
from hub import port, button
import urandom

### Agent class ###
class QLearningAgent:
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.qtable = self.initialize_qtable()
        self.actions = ["FORWARD", "BACKWARD"]
    
    def initialize_qtable(self):
        table = {}
        for key, val in enumerate(self.env.states):
            qvalue = [0] * 2
            table[val] = qvalue 
        return table

    def choose_action(self, state):
        k = urandom.uniform(0, 1)
        if self.epsilon > k:
            action = urandom.choice(self.actions)
            print(f"Action: Random action chosen: {action}")
        else:
            actions = self.qtable[state]
            max_val = max(actions)
            indices = [ind for ind, val in enumerate(actions) if val == max_val]
            action = self.actions[urandom.choice(indices)]
            print(f"Action: Best action chosen: {action}")
        self.last_state = state
        self.last_action = self.actions.index(action)
        return action

    def learn(self, reward, next_state):
        predict = self.qtable[self.last_state][self.last_action]
        target = reward + self.gamma * max(self.qtable[next_state])
        self.qtable[self.last_state][self.last_action] += self.alpha * (target - predict)
        print(f'Reward: {reward}, Q-table: {self.qtable}')

### Environment class ###
class Environment:
    def __init__(self):
        self.states = {
            -1:'ERR',
            0:"LEGO_BLACK",
            1:"LEGO_MAGENTA",
            3:"LEGO_BLUE",
            4:"LEGO_AZURE",
            6:"LEGO_GREEN",
            7:"LEGO_YELLOW",
            9:"LEGO_RED",
            10:"LEGO_WHITE",
        }
        self.goal_state = [6]
        self.end_state = [1, 6]
        self.reward_default = -1
        self.current_state = None
        self.action_space = ["FORWARD", "BACKWARD"]

    def reset(self):
        self.current_state = color_sensor.color(port.E)
        return self.current_state 

    def step(self, action):
        if action == "FORWARD":
            motor.run_for_degrees(port.A, 700, -1000)
            time.sleep(2)
        elif action == "BACKWARD":
            if(self.current_state != self.end_state[0]):
                motor.run_for_degrees(port.A, 700, 1000)
            time.sleep(2)
        self.current_state = color_sensor.color(port.E)
        if self.current_state in self.goal_state:
            reward = 10
            done = True
        else:
            reward = self.reward_default
            done = False
        print(f"Color: Current State: {self.states[self.current_state]}")
        return self.current_state, reward, done

EPSILON = 0.1 
env = Environment()
agent = QLearningAgent(env, epsilon=EPSILON)

rewards_history = []
timesteps = []

EPISODES = 10
TIMESTEPS = 15

for i in range(EPISODES):
    print(f"EPISODE {i}... Waiting to reset robot to START STATE ")
    while not button.pressed(button.LEFT):
        continue
    time.sleep(1)
    rew = 0
    ti = 0
    print(f"Episodqlearning.pye {i} Beginning...")
    state = env.reset()
    for j in range(TIMESTEPS):
        print(f"TIMESTEP {j}")
        action = agent.choose_action(state)
        new_state, reward, done = env.step(action)
        agent.learn(reward, new_state)
        rew += reward
        state = new_state
        ti += 1
        if(done):
            break
    rewards_history.append(rew)
    timesteps.append(ti)    
    print(f"Episode {i} Reward total {rew}")
    print("Rewards History...")
    print(rewards_history)
    print("Timesteps History...")
    print(timesteps)
"""

    return script
