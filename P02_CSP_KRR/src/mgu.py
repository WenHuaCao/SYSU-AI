import re
import queue

# 解析输入语句
def parser(clause):
    parser_result = []
    for item in re.findall(r'¬*[a-zA-Z]+\([a-zA-Z,\s]*\)', clause):
        parser_result.append(item)
    return parser_result

# parser赋值
def assign(uparser, uresult):
    assignment = []
    for index in range(len(uresult)):
        pos = uresult[index].find('=')
        variable = uresult[index][:pos]
        constant = uresult[index][pos+1:]
        assignment.append((variable, constant))
    # print(assignment)
    for index in range(len(uparser)):
        items = re.findall(r'[¬a-zA-Z]+', uparser[index])
        # print(items)
        for i, item in enumerate(items):
            if i == 0:
                continue
            for variable, constant in assignment:
                if item == variable:
                    items[i] = constant
                    break
        uparser[index] = items[0] + '(' + items[1]
        for item in items[2:]:
            uparser[index] += ", " + item
        uparser[index] += ')'
        # print(uparser[index])

#  合一
def unifier(parser1, parser2):
    unifier_parser = []
    for index1, item1 in enumerate(parser1):
        for index2, item2 in enumerate(parser2):
            # print(item1, item2)
            not_flag1 = int('¬' in item1)
            not_flag2 = int('¬' in item2)            
            if not_flag1 + not_flag2 != 1:
                continue
            # print(not_flag1, not_flag2)
            items1 = re.findall(r'[¬a-zA-Z]+', item1)
            items2 = re.findall(r'[¬a-zA-Z]+', item2)
            # print(items1, items2)
            predicate1 = items1[0][1:] if not_flag1 else items1[0]
            predicate2 = items2[0][1:] if not_flag2 else items2[0]
            # print(predicate1, predicate2)
            if predicate1 != predicate2:
                continue
            if len(items1) != len(items2):
                print("Error: Same predicate with different argument!")
                exit()
            
            check_flag = True
            unifier_result = []
            for argument_index in range(1, len(items1)):
                argument1 = items1[argument_index]
                argument2 = items2[argument_index]
                # print(argument1, argument2)
                # 单字母均认为是变量
                variable_flag1 = 1 if len(argument1) == 1 else 0
                variable_flag2 = 1 if len(argument2) == 1 else 0
                # print(variable_flag1, variable_flag2)
                if variable_flag1 + variable_flag2 == 2:
                    check_flag = False
                    break
                if variable_flag1 + variable_flag2 == 0:
                    if argument1 != argument2:
                        check_flag = False
                        break
                    continue

                if variable_flag1:
                    unifier_result.append(argument1 + "=" + argument2)
                else:
                    unifier_result.append(argument2 + "=" + argument1)
                # print(unifier_result)

            if check_flag:
                for i in range(len(parser1)):
                    if i != index1 and parser1[i] not in unifier_parser:
                        unifier_parser.append(parser1[i])
                for j in range(len(parser2)):
                    if j != index2 and parser2[j] not in unifier_parser:
                        unifier_parser.append(parser2[j])
                assign(unifier_parser, unifier_result)
                unifier_parser = list(set(unifier_parser))
                unifier_pick = (chr(97+index1), chr(97+index2))
                return True, unifier_parser, unifier_result, unifier_pick
                
    return False, None, None, None

# 深搜
def dfs(clauses, results, records):
    # print(clauses)
    if clauses[-1] == "()":
        return clauses, results, records, True

    for i in range(len(clauses) - 1, -1, -1):
        for j in range(i - 1, -1, -1):
            if (i, j) in records:
                continue
            parser1 = parser(clauses[i])
            parser2 = parser(clauses[j])
            ret = unifier(parser1, parser2)

            if ret[0]:
                copy_clauses = clauses.copy()
                copy_results = results.copy()
                copy_records = records.copy()

                result = "R[" + str(i + 1)
                if len(parser1) != 1:
                    result += ret[3][0]
                result += "," + str(j + 1)
                if len(parser2) != 1:
                    result += ret[3][1]
                result += "]"
                if len(ret[2]) >= 1:
                    result += "(" + ret[2][0]
                for k in range(1, len(ret[2])):
                    result += "," + ret[2][k]
                if len(ret[2]) >= 1:
                    result += ")"

                clause = ret[1]
                # print(result, clause)
                if len(clause) > 1:
                    join_clause = "(" + ','.join(clause) + ")"
                elif len(clause) == 1:
                    join_clause = clause[0]
                elif len(clause) == 0:
                    join_clause = "()"

                if join_clause in copy_clauses:
                    continue
                
                copy_clauses.append(join_clause)
                copy_results.append(result)
                copy_records.append((i, j))
                # print(copy_clauses, copy_results, copy_records)

                dfs_ret = dfs(copy_clauses, copy_results, copy_records)
                # print(dfs_ret)
                if dfs_ret[3]:
                    return dfs_ret

    return clauses, results, records, False

def heuristic_function(clause):
    return len(parser(clause))

class Node(object):
    def __init__(self, clauses, results, records):
        self.clauses = clauses.copy()
        self.results = results.copy()
        self.records = records.copy()
        self.value = len(self.records) + heuristic_function(clauses[-1])
    def __lt__(self, other):
        return self.value < other.value

def astar(clauses, results, records):
    pq = queue.PriorityQueue()
    pq.put(Node(clauses, results, records))
    while not pq.empty():
        node = pq.get()
        if node.clauses[-1] == "()":
            return node.clauses, node.results, node.records, True
        for i in range(len(node.clauses)):
            for j in range(i+1, len(node.clauses)):
                if (i, j) in records:
                    continue

                parser1 = parser(node.clauses[i])
                parser2 = parser(node.clauses[j])
                ret = unifier(parser1, parser2)

                if ret[0]:
                    copy_clauses = node.clauses.copy()
                    copy_results = node.results.copy()
                    copy_records = node.records.copy()

                    result = "R[" + str(i + 1)
                    if len(parser1) != 1:
                        result += ret[3][0]
                    result += "," + str(j + 1)
                    if len(parser2) != 1:
                        result += ret[3][1]
                    result += "]"
                    if len(ret[2]) >= 1:
                        result += "(" + ret[2][0]
                    for k in range(1, len(ret[2])):
                        result += "," + ret[2][k]
                    if len(ret[2]) >= 1:
                        result += ")"

                    clause = ret[1]
                    if len(clause) > 1:
                        join_clause = "(" + ','.join(clause) + ")"
                    elif len(clause) == 1:
                        join_clause = clause[0]
                    elif len(clause) == 0:
                        join_clause = "()"
                    
                    if join_clause in copy_clauses:
                        continue

                    copy_clauses.append(join_clause)
                    copy_results.append(result)
                    copy_records.append((i, j))

                    pq.put(Node(copy_clauses, copy_results, copy_records))

    return clauses, results, records, False



if __name__ == "__main__":

    clauses = []
    results = []
    records = []

    clause_num = int(input("Please input the number of clauses: "))
    for i in range(clause_num):
        results.append("")
        clauses.append(input())

    # clauses = ["GradStudent(sue)", "(¬GradStudent(x), Student(x))", "(¬Student(x), HardWorker(x))", "¬HardWorker(sue)"]
    # results = ["", "", "", ""]

    ret = astar(clauses, results, records)
    # ret = dfs(clauses, results, records)
    count = 1
    # print(clauses, results, records)
    for result, clause in zip(ret[1], ret[0]):
        print(str(count) + '.' + result + clause)
        count += 1