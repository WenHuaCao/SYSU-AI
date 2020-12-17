import numpy as np

# State-Action R Table
R = np.array([
    [np.nan, np.nan, np.nan, np.nan, 0, np.nan],
    [np.nan, np.nan, np.nan, 0, np.nan, 100],
    [np.nan, np.nan, np.nan, 0, np.nan, np.nan],
    [np.nan, 0, 0, np.nan, 0, np.nan],
    [0, np.nan, np.nan, 0, np.nan, 100],
    [np.nan, 0, np.nan, np.nan, 0, 100]
])

# State-Action Q Table
Q = np.zeros((6, 6))

def getValidAction(position):
    action_list = []
    R_position = R[position]
    for index in range(len(R_position)):
        if not np.isnan(R_position[index]):
            action_list.append(index)
    return np.array(action_list)

def getNextActionWithRandomChoice(position, returnMax=False):
    valid_action = getValidAction(position)
    if len(valid_action) == 0:
        return -1
    random_float = np.random.rand()
    if not returnMax:
        # randomly choose action from valid_action
        return valid_action[np.random.randint(0, len(valid_action))]
    else:
        # choose a* action form Q
        return valid_action[np.argmax(Q[position][valid_action])]

def QLearning(maxIteration=500, alpha=0.5, gamma=0.9):
    for iterIndex in range(maxIteration):
        state = np.random.randint(0, 6)
        while state != 5:
            nextState = getNextActionWithRandomChoice(state)
            nextAction = getNextActionWithRandomChoice(nextState, returnMax=True)
            Q[state][nextState] += alpha * (R[state][nextState] + gamma * Q[nextState][nextAction] - Q[state][nextState])
            state = nextState

if __name__ == '__main__':
    QLearning()

    print("State-Action Q Table:")
    print(Q)

    for i in range(5):
        print("highest value for state {}: ".format(i))
        print("\t", np.where(Q[i] == Q[i][np.argmax(Q[i])])[0])