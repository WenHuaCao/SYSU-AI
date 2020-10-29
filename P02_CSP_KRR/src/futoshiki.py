import time
import numpy as np

# 矩阵维度，矩阵，小于约束，可行域
N = 0
board = []
lessthan_constraints = []
current_domain = []

# 判断当前board是否全部放满
def is_allassigned():
    global N
    global board
    
    for row in range(N):
        for col in range(N):
            if board[row][col] == 0:
                return False

    return True

# 返回当前坐标涉及到的小于约束
def get_less_constraints(position):
    global lessthan_constraints

    # 目标结果
    constraints = []

    # 遍历所有小于约束
    for constraint in lessthan_constraints:
        if position == constraint[0] or position == constraint[1]:
            constraints.append(constraint)
    
    return constraints

# 根据小于约束从两个位置可行域中删除变量
def remove_variable_from_constraint(constraint):
    global current_domain

    less_position = constraint[0]
    position = constraint[1]

    # 保留被删除的变量用于回溯
    backup = []

    remove_list = []
    # 小于号左边位置的可行域
    for less_variable in current_domain[less_position[0]][less_position[1]]:
        remove_flag = True
        for variable in current_domain[position[0]][position[1]]:
            if variable > less_variable:
                remove_flag = False
                break
        if remove_flag:
            remove_list.append(less_variable)
    for remove_variable in remove_list:
        current_domain[less_position[0]][less_position[1]].remove(remove_variable)
        backup.append((less_position[0], less_position[1], remove_variable))
        if len(current_domain[less_position[0]][less_position[1]]) == 0:
            # DWO
            return backup, False
    
    remove_list.clear()
    # 小于号右边位置的可行域
    for variable in current_domain[position[0]][position[1]]:
        remove_flag = True
        for less_variable in current_domain[less_position[0]][less_position[1]]:
            if variable > less_variable:
                remove_flag = False
                break
        if remove_flag:
            remove_list.append(variable)
    for remove_variable in remove_list:
        current_domain[position[0]][position[1]].remove(remove_variable)
        backup.append((position[0], position[1], remove_variable))
        if len(current_domain[position[0]][position[1]]) == 0:
            # DWO
            return backup, False
    
    return backup, True

# 根据alldiff从一个位置的同行同列位置可行域中删除变量
def remove_variable_from_alldiff(position):
    global N
    global board
    global current_domain

    x = position[0]
    y = position[1]

    # 保留被删除的变量用于回溯
    backup = []

    # 同列
    for index in range(N):
        if index == x:
            continue
        if board[x][y] in current_domain[index][y]:
            current_domain[index][y].remove(board[x][y])
            backup.append((index, y, board[x][y]))
            if len(current_domain[index][y]) == 0:
                # DWO
                return backup, False
    
    # 同行
    for index in range(N):
        if index == y:
            continue
        if board[x][y] in current_domain[x][index]:
            current_domain[x][index].remove(board[x][y])
            backup.append((x, index, board[x][y]))
            if len(current_domain[x][index]) == 0:
                # DWO
                return backup, False
    
    return backup, True

# 初始化可行域
def init():
    global N
    global board
    global lessthan_constraints
    global current_domain

    # 每一格均初始化为全部数字
    for row in range(N):
        row_current_domain = []
        for col in range(N):
            row_current_domain.append(list(range(N + 1))[1:])
        current_domain.append(row_current_domain)

    # 处理已赋值的位置：设置可行域为单个元素，并去除同行同列位置可行域中的该元素
    for row in range(N):
        for col in range(N):
            if board[row][col] != 0:
                # 已赋值
                current_domain[row][col] = [board[row][col]]
                remove_variable_from_alldiff((row, col))
    
    # 处理小于约束
    for constraint in lessthan_constraints:
        remove_variable_from_constraint(constraint)

# 打印结果
def print_result():
    global N
    global board

    for row in range(N):
        print("\t\t\t", board[row])

# 挑选一个unassigned的位置
def pick_unassigned_variable():
    global N
    global board

    for row in range(N):
        for col in range(N):
            if board[row][col] == 0:
                return (row, col)
    
    return None

# 回溯
def BackTrace(backup):
    for x, y, digit in backup:
        current_domain[x][y].append(digit)

# FC记录信息
node_searched = 0
inference_total_time = 0.0

# FC recursive
def fc_recursive():
    global N
    global board
    global lessthan_constraints
    global current_domain
    global node_searched
    global inference_total_time

    # allassigned 直接return
    if is_allassigned():
        return True
    
    # 选出一个unassigned位置
    position = pick_unassigned_variable()
    variable_list = current_domain[position[0]][position[1]].copy()
    for variable in variable_list:
        # 遍历到一个节点
        inference_start_time = time.time()
        node_searched += 1
        board[position[0]][position[1]] = variable
        current_domain[position[0]][position[1]] = [variable]
        
        # 保存被删除的变量
        backup = []
        for temp_variable in variable_list:
            if temp_variable != variable:
                backup.append((position[0], position[1], temp_variable))

        # 处理约束
        ret = remove_variable_from_alldiff(position)
        backup.extend(ret[0])
        if not ret[1]:
            # DWO
            BackTrace(backup)
            board[position[0]][position[1]] = 0
            inference_total_time += time.time() - inference_start_time
            continue
        
        complete_flag = True
        constraints = get_less_constraints(position)
        for constraint in constraints:
            ret = remove_variable_from_constraint(constraint)
            backup.extend(ret[0])
            if not ret[1]:
                # DWO
                BackTrace(backup)
                board[position[0]][position[1]] = 0
                complete_flag = False
                break
        if not complete_flag:
            inference_total_time += time.time() - inference_start_time
            continue
        
        # 下一轮
        inference_total_time += time.time() - inference_start_time
        if fc_recursive():
            return True
        else:
            BackTrace(backup)
            board[position[0]][position[1]] = 0

    return False

# FC algorithm
def ForwardChecking():
    global node_searched
    global inference_total_time

    fc_start_time = time.time()
    fc_recursive()
    fc_end_time = time.time()

    print("ForwardChecking Algorithm Total Time: {} seconds".format(fc_end_time - fc_start_time))
    print("            Number of Nodes Searched: {}".format(node_searched))
    print("     Average Inference Time Per Node: {}".format(inference_total_time / node_searched))

# 生成GAC需要的约束序列
def generate_constraint_queue():
    global lessthan_constraints
    global N

    constraint_queue = []
    for constraint in lessthan_constraints:
        constraint_queue.append((constraint[0], constraint[1], "lt"))

    for row in range(N):
        constraint_queue.append((row, "row", "all-diff"))
    for col in range(N):
        constraint_queue.append((col, "col", "all-diff"))
    
    return constraint_queue

# 获取特定位置的所有未在队列内的有关约束
def generate_specific_constraint(position, constraint_queue):
    global N

    # 小于约束
    ret = get_less_constraints(position)
    for constraint in ret:
        if constraint not in constraint_queue:
            # print((constraint[0], constraint[1], "lt"))
            constraint_queue.append((constraint[0], constraint[1], "lt"))

    # 不等约束
    if (position[0], "row", "all-diff") not in constraint_queue:
        constraint_queue.append((position[0], "row", "all-diff"))
    if (position[1], "col", "all-diff") not in constraint_queue:
        constraint_queue.append((position[1], "col", "all-diff"))
    
    # exit()

# 检查all-diff约束是否满足
def check_alldiff(domain):
    global N

    selected_number = []
    for index in range(N):
        if len(domain[index]) == 1:
            # 已赋值
            if domain[index][0] not in selected_number:
                selected_number.append((domain[index][0], index))

    while True:
        break_flag = True
        for number, number_index in selected_number:
            # print(number, number_index)
            for index in range(N):
                if (number in domain[index]) and (index != number_index):
                    domain[index].remove(number)
                    break_flag = False
                    if len(domain[index]) == 0:
                        return False
                    elif len(domain[index]) == 1:
                        if domain[index][0] not in selected_number:
                            selected_number.append((domain[index][0], index))
        if break_flag:
            break
    
    if len(selected_number) == N:
        return True

    for index in range(N):
        if len(domain[index]) > 1:
            # pickup one unassigned
            for variable in domain[index]:
                temp_domain = []
                for element in domain:
                    temp_domain.append(element.copy())
                temp_domain[index] = [variable]
                if check_alldiff(temp_domain):
                    return True
            # all False
            return False

# GAC algorithm
def GeneralizedArcConsistency():
    global N
    global board
    global lessthan_constraints
    global current_domain
    global node_searched
    global inference_total_time

    # 约束队列
    constraint_queue = generate_constraint_queue()

    gac_start_time = time.time()

    # 运行直至队列为空
    while len(constraint_queue) != 0:
        # 循环一次算一个节点
        node_searched += 1
        inference_start_time = time.time()

        constraint = constraint_queue[0]
        constraint_queue.remove(constraint_queue[0])

        # print(constraint)
        # print(current_domain)

        if constraint[2] == 'lt':
            # 小于约束
            x1, y1 = constraint[0]
            x2, y2 = constraint[1]
            
            push_flag1 = False
            push_flag2 = False

            remove_list = []
            for less_variable in current_domain[x1][y1]:
                remove_flag = True
                for variable in current_domain[x2][y2]:
                    if less_variable < variable:
                        remove_flag = False
                        break
                if remove_flag:
                    push_flag1 = True
                    remove_list.append(less_variable)
            for less_variable in remove_list:
                current_domain[x1][y1].remove(less_variable)
            
            remove_list.clear()
            for variable in current_domain[x2][y2]:
                remove_flag = True
                for less_variable in current_domain[x1][y1]:
                    if less_variable < variable:
                        remove_flag = False
                        break
                if remove_flag:
                    push_flag2 = True
                    remove_list.append(variable)
            for variable in remove_list:
                current_domain[x2][y2].remove(variable)

            if push_flag1:
                generate_specific_constraint(constraint[0], constraint_queue)
            if push_flag2:
                generate_specific_constraint(constraint[1], constraint_queue)

        elif constraint[2] == 'all-diff':
            # 不等约束
            for index in range(N):
                domain = []
                if constraint[1] == 'row':
                    for index1 in range(N):
                        domain.append(current_domain[constraint[0]][index1].copy())
                elif constraint[1] == 'col':
                    for index1 in range(N):
                        domain.append(current_domain[index1][constraint[0]].copy())
                
                remove_list = []
                for variable in domain[index]:
                    temp_domain = []
                    for element in domain:
                        temp_domain.append(element.copy())
                    temp_domain[index] = [variable]
                    # print(temp_domain)
                    ret = check_alldiff(temp_domain)
                    # print(temp_domain, ret)
                    if not ret:
                        remove_list.append(variable)
                for variable in remove_list:
                    if constraint[1] == 'row':
                        current_domain[constraint[0]][index].remove(variable)
                        generate_specific_constraint((constraint[0], index), constraint_queue)
                    elif constraint[1] == 'col':
                        current_domain[index][constraint[0]].remove(variable)
                        generate_specific_constraint((index, constraint[0]), constraint_queue)
        
        inference_total_time += time.time() - inference_start_time

    gac_end_time = time.time()

    for row in range(N):
        for col in range(N):
            # print(current_domain[row][col])
            board[row][col] = current_domain[row][col][0]

    print("GeneralizedArcConsistency Algorithm Time Consuming: {} seconds".format(gac_end_time - gac_start_time))
    print("            Number of Nodes Searched: {}".format(node_searched))
    print("     Average Inference Time Per Node: {}".format(inference_total_time / node_searched))

if __name__ == '__main__':

    # 处理输入文件
    data_filedir = input("Please input source data file directory: ")
    data_filedir = "TestCase/data" + data_filedir + ".txt"

    with open(data_filedir, 'r') as data_file:
        for index, line in enumerate(data_file.readlines()):
            line = line.strip()
            if not line:
                continue
            # 第一行计算出矩阵维度
            if index == 0:
                N = len(line.split(' '))
                board = []
            
            line_split = line.split(' ')
            # 输入行要么是矩阵要么是小于约束
            if index < N:
                board.append([])
                for col in range(N):
                    board[index].append(int(line_split[col]))
            else:
                lessthan_constraints.append(((int(line_split[0]), int(line_split[1])), (int(line_split[2]), int(line_split[3]))))

    # 初始化可行域
    init()

    # 选择算法
    algorithm = input("Please input the algorithm to use: ")
    if algorithm == 'FC':
        ForwardChecking()
    elif algorithm == 'GAC':
        GeneralizedArcConsistency()
    
    print_result()