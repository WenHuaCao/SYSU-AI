from math import pow

class VariableElimination:
    @staticmethod
    def inference(factorList, queryVariables, orderedListOfHiddenVariables, evidenceList):
        for ev in evidenceList:
            #Your code here
            for i, factor in enumerate(factorList):
                if ev not in factor.varList:
                    continue
                factorList[i] = factor.restrict(ev, evidenceList[ev])
        for var in orderedListOfHiddenVariables:
            #Your code here
            index_list = []
            for i, factor in enumerate(factorList):
                if var in factor.varList:
                    index_list.append(i)
            new_factor_var = []
            for i in index_list:
                for factor_var in factorList[i].varList:
                    if factor_var not in new_factor_var and factor_var != var:
                        new_factor_var.append(factor_var)

            cal_factor = Node("tmp", factorList[index_list[0]].varList.copy())
            cal_factor.setCpt(factorList[index_list[0]].cpt.copy())
            for i in index_list[1:]:
                temp_factor = Node("tmp", factorList[i].varList.copy())
                temp_factor.setCpt(factorList[i].cpt.copy())
                cal_factor = cal_factor.multiply(temp_factor)
            
            new_factor = cal_factor.sumout(var)
            factorList.append(new_factor)
            factorList = [factor for i, factor in enumerate(factorList) if i not in index_list]

        print("RESULT:")
        res = factorList[0]
        for factor in factorList[1:]:
            res = res.multiply(factor)
        total = sum(res.cpt.values())
        res.cpt = {k: v/total for k, v in res.cpt.items()}
        res.printInf()

    @staticmethod
    def printFactors(factorList):
        for factor in factorList:
            factor.printInf()

class Util:
    @staticmethod
    def to_binary(num, len):
        return format(num, '0' + str(len) + 'b')
        
class Node:
    def __init__(self, name, var_list):
        self.name = name
        self.varList = var_list
        self.cpt = {}

    def setCpt(self, cpt):
        self.cpt = cpt

    def printInf(self):
        print("Name = " + self.name)
        print(" vars " + str(self.varList))
        for key in self.cpt:
            print("   key: " + key + " val : " + str(self.cpt[key]))
        print("")

    def multiply(self, factor):
        """function that multiplies with another factor"""
        #Your code here
        newList = self.varList.copy()
        not_same_index = []
        same_index = []
        for i, var in enumerate(factor.varList):
            if var not in newList:
                not_same_index.append(i)
                newList.append(var)
            else:
                same_index.append((newList.index(var), i))

        new_cpt = {}
        for cpt1 in self.cpt:
            for cpt2 in factor.cpt:
                valid_flag = True
                for si in same_index:
                    if cpt1[si[0]] != cpt2[si[1]]:
                        valid_flag = False
                        break
                if not valid_flag:
                    continue

                new_cpt_key = cpt1
                for nsi in not_same_index:
                    new_cpt_key = new_cpt_key + cpt2[nsi]
                if new_cpt_key in new_cpt:
                    new_cpt[new_cpt_key] += self.cpt[cpt1] * factor.cpt[cpt2]
                else:
                    new_cpt[new_cpt_key] = self.cpt[cpt1] * factor.cpt[cpt2]

        new_node = Node("f" + str(newList), newList)
        new_node.setCpt(new_cpt)
        return new_node

    def sumout(self, variable):
        """function that sums out a variable given a factor"""
        #Your code here
        var_index = self.varList.index(variable)
        new_var_list = self.varList.copy()
        new_var_list.remove(variable)

        new_cpt = {}
        for cpt1 in self.cpt:
            new_cpt_key = ""
            for i, ch in enumerate(cpt1):
                if i != var_index:
                    new_cpt_key = new_cpt_key + ch
            
            if new_cpt_key in new_cpt:
                new_cpt[new_cpt_key] += self.cpt[cpt1]
            else:
                new_cpt[new_cpt_key] = self.cpt[cpt1]

        new_node = Node("f" + str(new_var_list), new_var_list)
        new_node.setCpt(new_cpt)
        return new_node

    def restrict(self, variable, value):
        """function that restricts a variable to some value 
        in a given factor"""
        #Your code here
        # print(self.varList, self.cpt)
        var_index = self.varList.index(variable)
        new_var_list = self.varList.copy()
        new_var_list.remove(variable)

        new_cpt = {}
        for cpt1 in self.cpt:
            if cpt1[var_index] != str(value):
                continue
            
            new_cpt_key = ""
            for i, ch in enumerate(cpt1):
                if i != var_index:
                    new_cpt_key = new_cpt_key + ch
            
            new_cpt[new_cpt_key] = self.cpt[cpt1]

        # print(new_var_list, new_cpt)
        new_node = Node("f" + str(new_var_list), new_var_list)
        new_node.setCpt(new_cpt)
        return new_node

# create nodes for Bayes Net
B = Node("B", ["B"])
E = Node("E", ["E"])
A = Node("A", ["A", "B", "E"])
J = Node("J", ["J", "A"])
M = Node("M", ["M", "A"])

# Generate cpt for each node
B.setCpt({'0': 0.999, '1': 0.001})
E.setCpt({'0': 0.998, '1': 0.002})
A.setCpt({'111': 0.95, '011': 0.05, '110':0.94,'010':0.06,
'101':0.29,'001':0.71,'100':0.001,'000':0.999})
J.setCpt({'11': 0.9, '01': 0.1, '10': 0.05, '00': 0.95})
M.setCpt({'11': 0.7, '01': 0.3, '10': 0.01, '00': 0.99})

print("P(A) **********************")
VariableElimination.inference([B,E,A,J,M], ['A'], ['B', 'E', 'J','M'], {})

print("P(B | J~M) **********************")
VariableElimination.inference([B,E,A,J,M], ['B'], ['E','A'], {'J':1,'M':0})