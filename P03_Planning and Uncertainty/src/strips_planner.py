# Author: Lu Yanzuo
# Date: 2020-11-22
# Description: a STRIPS planner by using A* search and heuristic function 
#   implemented personally


from itertools import product

import re
import time
import queue


# parse parameters line
def parameters_parser(s):
    pattern = re.compile(r"\?(\w+) - (\w+)")
    return re.findall(pattern, s)[0]


# parse predicate/objects 
def general_parser(s):
    pattern = re.compile(r"(\w+)")
    return tuple(re.findall(pattern, s))


# readin and parse domain file
def domain_parser(filename):
    name = []
    parameters = []
    prec = []
    adds = []
    dels = []

    with open(filename, "r") as domain_file:
        lines = domain_file.readlines()
        pos = 0

        while True:
            if pos == len(lines):
                break

            if "action" not in lines[pos]:
                pos += 1
                continue
            
            line = lines[pos].strip() # action
            name_index = line.find("action") + 7
            name.append(line[name_index:])

            pos += 1 # parameters
            line = lines[pos].strip()
            para_pattern = re.compile(r"(?:\?\w+ - \w+)")
            para_list = re.findall(para_pattern, line)
            temp_parameters = []
            for para in para_list:
                temp_parameters.append(parameters_parser(para))
            parameters.append(temp_parameters)
            
            pos += 1 # precondition
            line = lines[pos].strip()
            prec_pattern = re.compile(r"\((?!not \()(?:\w+)(?: \?\w+)+\)(?!\))")
            prec_list = re.findall(prec_pattern, line)
            temp_prec = []
            for prec_item in prec_list:
                temp_prec.append(general_parser(prec_item))
            prec.append(temp_prec)

            pos += 1 # effect
            line = lines[pos].strip()
            adds_pattern = re.compile(r"\((?!not \()(?:\w+)(?: \?\w+)+\)(?!\))")
            dels_pattern = re.compile(r"\((?:not )\((?:\w+)(?: \?\w+)+\)(?:\))")
            adds_list = re.findall(adds_pattern, line)
            dels_list = re.findall(dels_pattern, line)
            temp_adds = []
            temp_dels = []
            for _adds in adds_list:
                temp_adds.append(general_parser(_adds))
            for _dels in dels_list:
                temp_dels.append(general_parser(_dels)[1:])
            adds.append(temp_adds)
            dels.append(temp_dels)

            pos += 1
    
    return name, parameters, prec, adds, dels


# readin and parse problem file
def problem_parser(filename):
    objects = []
    init = []
    goal = []

    with open(filename, "r") as problem_file:
        lines = problem_file.readlines()
        pos = 0

        while True:
            if pos == len(lines):
                break

            line = lines[pos].strip()

            if "objects" in line:
                pos += 1
                line = lines[pos].strip()
                while line != ")":
                    if line:
                        objects.append(general_parser(line))
                    pos += 1
                    line = lines[pos].strip()
            elif "init" in line:
                pos += 1
                line = lines[pos].strip()
                while line != ")":
                    if line:
                        init.append(general_parser(line))
                    pos += 1
                    line = lines[pos].strip()
            elif "goal" in line:
                goal_pattern = re.compile(r"\((?!not \()(?:\w+)(?: \w+)+\)(?!\))")
                goal_list = re.findall(goal_pattern, line)
                for goal_item in goal_list:
                    goal.append(general_parser(goal_item))
            
            pos += 1

    return objects, init, goal


# replace predicate variable with real paras 
def replace(prec, para_variable, paras):
    # start_time = time.time()
    result = [prec[0]]
    for prec_item in prec[1:]:
        index = para_variable.index(prec_item)
        result.append(paras[index])
    # end_time = time.time()
    return tuple([*result])


# store_input = []
# store_output = []
# check whether action is valid for current state 
def check_action(cur_state, parameters, prec, objects):
    # start_time = time.time()
    # # print("check action cur_state:", cur_state)

    # if (cur_state, parameters, prec) in store_input:
    #     return store_output[store_input.index((cur_state, parameters, prec))]

    objects_name = []
    objects_item = []
    for _object in objects:
        objects_name.append(_object[-1])
        objects_item.append([*_object[:-1]])

    para_index = []
    para_variable = []
    for para in parameters:
        para_index.append(objects_name.index(para[1]))
        para_variable.append(para[0])
    
    para_item = []
    for i in para_index:
        para_item.append(objects_item[i])
    
    result = []
    for paras in product(*para_item):
        if len(set(paras)) < len(paras):
            continue
        valid_flag = True
        for prec_item in prec:
            replace_pred = replace(prec_item, para_variable, paras)
            if replace_pred not in cur_state:
                valid_flag = False
                break
        if valid_flag:
            result.append(paras)

    # store_input.append((cur_state, parameters, prec))
    # store_output.append(None if len(result) == 0 else result)

    # end_time = time.time()
    # # print("Check Action function takes time {}s".format(end_time - start_time))
    return None if len(result) == 0 else result


# get valid action index and paras for specific state
store_input = []
store_output = []
def get_valid_action(state):
    global name
    global parameters
    global prec
    global objects

    if state in store_input:
        return store_output[store_input.index(state)]

    valid_action_index = []
    valid_action_paras = []
    for action_index in range(len(name)):
        res = check_action(state, parameters[action_index], \
            prec[action_index], objects)
        if res is not None:
            valid_action_index.append(action_index)
            valid_action_paras.append(res)
    
    store_input.append(state)
    store_output.append((valid_action_index, valid_action_paras))
    return valid_action_index, valid_action_paras


# CountAction recursive function
def CountAction(goal, state_layer, cur_layer, action, objects):
    # start_time = time.time()
    # print("cur_layer:", cur_layer)

    if cur_layer == 0:
        return 0

    # print("cur state layer:", state_layer[cur_layer])
    # print("pre state layer:", state_layer[cur_layer-1])

    name = action["name"]
    parameters = action["parameters"]
    prec = action["prec"]
    adds = action["adds"]

    goal_p = []
    goal_n = []

    for goal_item in goal:
        if goal_item in state_layer[cur_layer-1]:
            goal_p.append(goal_item)
        else:
            goal_n.append(goal_item)
    
    # print("goal_p:", goal_p)
    # print("goal_n:", goal_n)
    
    objects_name = []
    objects_item = []
    for _object in objects:
        objects_name.append(_object[-1])
        objects_item.append([*_object[:-1]])

    # valid_action_index = []
    # valid_action_paras = []
    # for action_index in range(len(name)):
    #     res = check_action(state_layer[cur_layer-1], parameters[action_index], \
    #         prec[action_index], objects)
    #     if res is not None:
    #         valid_action_index.append(action_index)
    #         valid_action_paras.append(res)

    valid_action_index, valid_action_paras = get_valid_action(state_layer[cur_layer-1])
    
    # print("valid_action_index:", valid_action_index)
    # print("valid_action_paras:", valid_action_paras)
    
    action_index_set = []
    action_paras_set = []
    adds_list = []
    for i in range(len(valid_action_index)):
        para_variable = []
        for para in parameters[valid_action_index[i]]:
            para_variable.append(para[0])

        for paras in valid_action_paras[i]:
            temp_adds_list = []
            for pred in adds[valid_action_index[i]]:
                replace_pred = replace(pred, para_variable, paras)
                temp_adds_list.append(replace_pred)

            for temp_adds in temp_adds_list:
                if temp_adds not in adds_list and temp_adds in goal_n:
                    action_index_set.append(valid_action_index[i])
                    action_paras_set.append(paras)
                    adds_list.extend(temp_adds_list)
                    break

            if set(goal_n) <= set(adds_list):
                break
    
    # print("action_index_set:", action_index_set)
    # print("action_paras_set:", action_paras_set)
    # # print("adds_list:", adds_list)

    next_goal = goal_p.copy()
    for i in range(len(action_index_set)):
        para_index = []
        para_variable = []
        for para in parameters[action_index_set[i]]:
            para_index.append(objects_name.index(para[1]))
            para_variable.append(para[0])

        for prec_item in prec[action_index_set[i]]:
            replace_pred = replace(prec_item, para_variable, action_paras_set[i])
            if replace_pred not in next_goal:
                next_goal.append(replace_pred)
    
    # print("next_goal:", next_goal)

    # end_time = time.time()
    # # print("Count Action function takes time {}s".format(end_time - start_time))
    return CountAction(next_goal, state_layer, cur_layer-1, action, objects) + len(action_index_set)


# compute heuristic function values for current state
def heuristic(cur_state, action, goal, objects):
    start_time = time.time()

    state_layer = []
    state_layer.append(cur_state)

    name = action["name"]
    parameters = action["parameters"]
    prec = action["prec"]
    adds = action["adds"]

    while True:
        # print("the latest state layer:", state_layer[-1])

        goal_flag = True
        for goal_item in goal:
            if goal_item not in state_layer[-1]:
                goal_flag = False
                break
        if goal_flag:
            # print("get goal state layer.")
            break

        # valid_action_index = []
        # valid_action_paras = []
        # for action_index in range(len(name)):
        #     res = check_action(state_layer[-1], parameters[action_index], \
        #         prec[action_index], objects)
        #     if res is not None:
        #         valid_action_index.append(action_index)
        #         valid_action_paras.append(res)
        
        valid_action_index, valid_action_paras = get_valid_action(state_layer[-1])
        
        # print("valid action index and paras:", valid_action_index, valid_action_paras)
        # print("\n")
        
        next_state = state_layer[-1].copy()

        for i in range(len(valid_action_index)):
            para_variable = []
            for para in parameters[valid_action_index[i]]:
                para_variable.append(para[0])

            for valid_paras in valid_action_paras[i]:
                for pred in adds[valid_action_index[i]]:
                    replace_pred = replace(pred, para_variable, valid_paras)
                    if replace_pred not in next_state:
                        next_state.append(replace_pred)
        
        state_layer.append(next_state)

    heuristic_value = CountAction(goal, state_layer, len(state_layer)-1, action, objects)
    
    end_time = time.time()
    # print("Heuristic function takes time {}s".format(end_time - start_time))
    return heuristic_value


class Node(object):
    def __init__(self, state, gx, action_index, action_paras):
        self.state = state
        self.gx = gx
        self.hx = heuristic(state, action, goal, objects)
        self.fx = self.gx + self.hx
        self.action_index = action_index.copy()
        self.action_paras = action_paras.copy()
    
    def __lt__(self, other):
        return self.fx < other.fx
    
    def is_goal(self):
        return set(goal) <= set(self.state)


if __name__ == "__main__":
    test_num = int(input("Please input the number of test file(0-4): "))

    parser_start = time.time()

    domain_filename = "pddl/test{}/test{}_domain.txt".format(str(test_num), str(test_num))
    problem_filename = "pddl/test{}/test{}_problem.txt".format(str(test_num), str(test_num))

    name, parameters, prec, adds, dels = domain_parser(domain_filename)
    objects, init, goal = problem_parser(problem_filename)
    action = {
        "name": name,
        "parameters": parameters,
        "prec": prec,
        "adds": adds,
        "dels": dels
    }
    
    history = []
    q = queue.PriorityQueue()

    history.append(init)
    init_node = Node(init, 0, [], [])
    q.put(init_node)

    parser_end = time.time()

    while not q.empty():
        head_node = q.get()
        if head_node.is_goal():
            print("\n" + "*****"*4 + " Action List " + "*****"*4)
            for i in range(len(head_node.action_index)):
                print(action["name"][head_node.action_index[i]], head_node.action_paras[i])
            print("*****"*4 + "**** end ****" + "*****"*4)
            break

        # print("head_node.state:", head_node.state)
        
        # valid_action_index = []
        # valid_action_paras = []
        # for action_index in range(len(name)):
        #     res = check_action(head_node.state, parameters[action_index], \
        #         prec[action_index], objects)
        #     if res is not None:
        #         valid_action_index.append(action_index)
        #         valid_action_paras.append(res)
        
        valid_action_index, valid_action_paras = get_valid_action(head_node.state)
        
        for i in range(len(valid_action_index)):
            para_variable = []
            for para in parameters[valid_action_index[i]]:
                para_variable.append(para[0])

            for valid_paras in valid_action_paras[i]:
                new_state = head_node.state.copy()

                for pred in dels[valid_action_index[i]]:
                    replace_pred = replace(pred, para_variable, valid_paras)
                    if replace_pred in new_state:
                        new_state.remove(replace_pred)

                for pred in adds[valid_action_index[i]]:
                    replace_pred = replace(pred, para_variable, valid_paras)
                    if replace_pred not in new_state:
                        new_state.append(replace_pred)
            
                if new_state not in history:
                    history.append(new_state)
                    # print("new_state:", new_state)

                    new_index = head_node.action_index.copy()
                    new_paras = head_node.action_paras.copy()

                    new_index.append(valid_action_index[i])
                    new_paras.append(valid_paras)
                    # print("new_index:", new_index)
                    # print("new_paras:", new_paras)

                    new_node = Node(new_state, head_node.gx+1, new_index, new_paras)
                    q.put(new_node)
    
    astar_end = time.time()
    print("Parser time cost:{}".format(parser_end - parser_start))
    print("Astar search time cost:{}\n".format(astar_end - parser_end))