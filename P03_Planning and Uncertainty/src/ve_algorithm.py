from math import pow
import time

maximum_width = None

def select(orderedListOfHiddenVariables, factorList):
    min_var = None
    min_cnt = None
    for var in orderedListOfHiddenVariables:
        cnt = 0
        for factor in factorList:
            if var in factor.varList:
                cnt += 1
        
        if min_cnt is None or cnt < min_cnt:
            min_var = var
            min_cnt = cnt
    
    return min_var

class VariableElimination:
    @staticmethod
    def inference(factorList, queryVariables, orderedListOfHiddenVariables, evidenceList):
        global maximum_width

        for ev in evidenceList:
            #Your code here
            for i, factor in enumerate(factorList):
                if ev not in factor.varList:
                    continue
                factorList[i] = factor.restrict(ev, evidenceList[ev])
    
        # for var in orderedListOfHiddenVariables:
        while len(orderedListOfHiddenVariables) > 0:
            var = select(orderedListOfHiddenVariables, factorList)
            orderedListOfHiddenVariables.remove(var)
            # print(var)
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

            if len(new_factor.varList) > maximum_width:
                maximum_width = len(new_factor.varList)

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

        new_node = Node("f" + str(new_var_list), new_var_list)
        new_node.setCpt(new_cpt)
        return new_node

# create nodes for Bayes Net
PatientAge = Node("PatientAge", ["PatientAge"])
CTScanResult = Node("CTScanResult", ["CTScanResult"])
MRIScanResult = Node("MRIScanResult", ["MRIScanResult"])
Anticoagulants = Node("Anticoagulants", ["Anticoagulants"])
StrokeType = Node("StrokeType", ["StrokeType", "CTScanResult", "MRIScanResult"])
Mortality = Node("Mortality", ["Mortality", "StrokeType", "Anticoagulants"])
Disability = Node("Disability", ["Disability", "StrokeType", "PatientAge"])

# Generate cpt for each node
PatientAge.setCpt({'0': 0.1, '1': 0.3, '2': 0.6})
CTScanResult.setCpt({'0': 0.7, '1': 0.3})
MRIScanResult.setCpt({'0': 0.7, '1': 0.3})
Anticoagulants.setCpt({'0': 0.5, '1': 0.5})
StrokeType.setCpt({'000': 0.8, '001': 0.5, '010': 0.5, '011': 0.0, 
    '100': 0.0, '101': 0.4, '110': 0.4, '111': 0.9, 
    '200': 0.2, '201': 0.1, '210': 0.1, '211': 0.1})
Mortality.setCpt({'000': 0.28, '010': 0.99, '020': 0.1, 
    '001': 0.56, '011': 0.58, '021': 0.05,
    '100': 0.72, '110': 0.01, '120': 0.9,
    '101': 0.44, '111': 0.42, '121': 0.95})
Disability.setCpt({'000': 0.8, '010': 0.7, '020': 0.9, 
    '001': 0.6, '011': 0.5, '021': 0.4, 
    '002': 0.3, '012': 0.2, '022': 0.1,
    '100': 0.1, '110': 0.2, '120': 0.05, 
    '101': 0.3, '111': 0.4, '121': 0.3, 
    '102': 0.4, '112': 0.2, '122': 0.1,
    '200': 0.1, '210': 0.1, '220': 0.05, 
    '201': 0.1, '211': 0.1, '221': 0.3, 
    '202': 0.3, '212': 0.6, '222': 0.8,})

print("P(Mortality='True' ∧ CTScanResult='Ischemic Stroke' | PatientAge='31-65')")
VariableElimination.inference([PatientAge, CTScanResult, MRIScanResult, Anticoagulants, \
    StrokeType, Mortality, Disability], ["Mortality", "CTScanResult"], \
    ["MRIScanResult", "Anticoagulants", "StrokeType", "Disability"], {"PatientAge": 1})

print("P(Disability='Moderate' ∧ CTScanResult='Hemmorraghic Stroke' | PatientAge='65+' ∧ MRIScanResult='Hemmorraghic Stroke')")
VariableElimination.inference([PatientAge, CTScanResult, MRIScanResult, Anticoagulants, \
    StrokeType, Mortality, Disability], ["Disability", "CTScanResult"], \
    ["Anticoagulants", "StrokeType", "Mortality"], {"PatientAge": 2, "MRIScanResult": 1})

print("P(StrokeType='Hemmorraghic Stroke' | PatientAge='65+' ∧ CTScanResult='Hemmorraghic Stroke' ∧ MRIScanResult='Ischemic Stroke')")
VariableElimination.inference([PatientAge, CTScanResult, MRIScanResult, Anticoagulants, \
    StrokeType, Mortality, Disability], ["StrokeType"], \
    ["Anticoagulants", "Mortality", "Disability"], \
    {"PatientAge": 2, "CTScanResult": 1, "MRIScanResult": 0})

print("P(Anticoagulants='Used' | PatientAge='31-65')")
VariableElimination.inference([PatientAge, CTScanResult, MRIScanResult, Anticoagulants, \
    StrokeType, Mortality, Disability], ["Anticoagulants"], \
    ["CTScanResult", "MRIScanResult", "StrokeType", "Mortality", "Disability"], \
    {"PatientAge": 1})

print("P(Disability='Negligible')")
VariableElimination.inference([PatientAge, CTScanResult, MRIScanResult, Anticoagulants, \
    StrokeType, Mortality, Disability], ["Disability"], \
    ["PatientAge", "CTScanResult", "MRIScanResult", "Anticoagulants", "StrokeType", "Mortality"], \
    {})

# start = time.time()
# for i in range(100):
#     print("P(Anticoagulants='Used' | PatientAge='31-65')")
#     maximum_width = 3
#     VariableElimination.inference([PatientAge, CTScanResult, MRIScanResult, Anticoagulants, \
#         StrokeType, Mortality, Disability], ["Disability"], \
#         ["PatientAge",  "MRIScanResult","StrokeType","Anticoagulants",  "CTScanResult", "Mortality"], \
#         {})
#     print(maximum_width)
# end = time.time()

# print("total time: {}".format(end - start))