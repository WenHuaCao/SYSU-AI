import copy
import math
import random

import numpy as np


WORKCLASS = ["Private", "Self-emp-not-inc", "Self-emp-inc", "Federal-gov", "Local-gov", 
    "State-gov", "Without-pay", "Never-worked"]
EDUCATION = ["Bachelors", "Some-college", "11th", "HS-grad", "Prof-school", "Assoc-acdm", 
    "Assoc-voc", "9th", "7th-8th", "12th", "Masters", "1st-4th", "10th", "Doctorate", 
    "5th-6th", "Preschool"]
MARITAL_STATUS = ["Married-civ-spouse", "Divorced", "Never-married", "Separated", "Widowed", 
    "Married-spouse-absent", "Married-AF-spouse"]
OCCUPATION = ["Tech-support", "Craft-repair", "Other-service", "Sales", "Exec-managerial", 
    "Prof-specialty", "Handlers-cleaners", "Machine-op-inspct", "Adm-clerical", 
    "Farming-fishing", "Transport-moving", "Priv-house-serv", "Protective-serv", 
    "Armed-Forces"]
RELATIONSHIP = ["Wife", "Own-child", "Husband", "Not-in-family", "Other-relative", 
    "Unmarried"]
RACE = ["White", "Asian-Pac-Islander", "Amer-Indian-Eskimo", "Other", "Black"]
SEX = ["Female", "Male"]
NATIVE_COUNTRY = ["United-States", "Cambodia", "England", "Puerto-Rico", "Canada", 
    "Germany", "Outlying-US(Guam-USVI-etc)", "India", "Japan", "Greece", "South", 
    "China", "Cuba", "Iran", "Honduras", "Philippines", "Italy", "Poland", "Jamaica", 
    "Vietnam", "Mexico", "Portugal", "Ireland", "France", "Dominican-Republic", "Laos", 
    "Ecuador", "Taiwan", "Haiti", "Columbia", "Hungary", "Guatemala", "Nicaragua", 
    "Scotland", "Thailand", "Yugoslavia", "El-Salvador", "Trinadad&Tobago", "Peru", 
    "Hong", "Holand-Netherlands"]
LABEL = ["<=50K", ">50K"]

CONT_ATTR = [0, 2, 4, 10, 11, 12]
SEPE_ATTR = [1, 3, 5, 6, 7, 8, 9, 13]
SEPE_ATTR_LEN = [len(WORKCLASS), len(EDUCATION), len(MARITAL_STATUS), len(OCCUPATION), 
    len(RELATIONSHIP), len(RACE), len(SEX), len(NATIVE_COUNTRY)]
ATTR_NAME = ["age", "workclass", "fnlwgt", "education", "education_num", "marital_status", 
        "occupation", "relationship", "race", "sex", "capital_gain", "capital_loss", "hours_per_week", 
        "native_country"]

class Item(object):
    def __init__(self, age, workclass, fnlwgt, education, education_num, marital_status, 
        occupation, relationship, race, sex, capital_gain, capital_loss, hours_per_week, 
        native_country, label, weight=None, test=False):
        self.age = -1 if age == "?" else int(age)
        self.workclass = -1 if workclass == "?" else WORKCLASS.index(workclass)
        self.fnlwgt = -1 if fnlwgt == "?" else int(fnlwgt)
        self.education = -1 if education == "?" else EDUCATION.index(education)
        self.education_num = -1 if education_num == "?" else int(education_num)
        self.marital_status = -1 if marital_status == "?" else MARITAL_STATUS.index(marital_status)
        self.occupation = -1 if occupation == "?" else OCCUPATION.index(occupation)
        self.relationship = -1 if relationship == "?" else RELATIONSHIP.index(relationship)
        self.race = -1 if race == "?" else RACE.index(race)
        self.sex = -1 if sex == "?" else SEX.index(sex)
        self.capital_gain = -1 if capital_gain == "?" else int(capital_gain)
        self.capital_loss = -1 if capital_loss == "?" else int(capital_loss)
        self.hours_per_week = -1 if hours_per_week == "?" else int(hours_per_week)
        self.native_country = -1 if native_country == "?" else NATIVE_COUNTRY.index(native_country)
        
        self.label = LABEL.index(label) if not test else LABEL.index(label[:-1])# 最终结果标签
        self.weight = 1.0 if weight is None else weight # 处理缺失值用的权重
    
    def to_list(self):
        return [self.age, self.workclass, self.fnlwgt, self.education, self.education_num, 
            self.marital_status, self.occupation, self.relationship, self.race, self.sex, 
            self.capital_gain, self.capital_loss, self.hours_per_week, self.native_country]


class Dataset(object):
    def __init__(self, data, label, weight, attr_name):
        self.data = np.array(data, dtype=np.int_)
        self.label = np.array(label, dtype=np.int_)
        self.weight = np.array(weight)
        self.attr_name = attr_name.copy()
    
    def __len__(self):
        return self.data.shape[1]
    
    def split(self):
        entropy = self.cal_Entropy()
        if entropy == 0.0:
            return None, None, None, None

        print("Split dataset start. size: {}".format(len(self.data)))
        print("entropy {}.".format(entropy))
        max_IG = -np.inf
        max_attr = None
        max_value = None

        for attr in range(len(self)):
            # print("Calculate attribute {}.".format(attr))
            if ATTR_NAME.index(self.attr_name[attr]) not in CONT_ATTR:
                # 离散值
                cond_entropy = self.cal_CondEntropy(attr)
                # print("cond_entropy {}.".format(cond_entropy))
                if (entropy - cond_entropy) > max_IG:
                    max_IG = entropy - cond_entropy
                    max_attr = attr
                    max_value = list(range(SEPE_ATTR_LEN[SEPE_ATTR.index(ATTR_NAME.index(self.attr_name[attr]))]))
            else:
                # 连续值
                cond_entropy, binary = self.cal_CondEntropy(attr)
                # print("cond_entropy {}.".format(cond_entropy))
                if (entropy - cond_entropy) > max_IG:
                    max_IG = entropy - cond_entropy
                    max_attr = attr
                    max_value = binary
        
        # print("Choose maximum IG attr {}.".format(max_attr))
        empty_index = np.where(self.data[:,max_attr] == -1)[0]
        empty_data = self.data[empty_index]
        empty_label = self.label[empty_index]
        empty_weight = self.weight[empty_index]

        not_empty = len(self.data) - len(empty_index)
        
        if ATTR_NAME.index(self.attr_name[max_attr]) not in CONT_ATTR:
            # 离散值
            split_dataset = []
            split_type = "SEPE"
            split_value = max_value

            for i in range(SEPE_ATTR_LEN[SEPE_ATTR.index(ATTR_NAME.index(self.attr_name[max_attr]))]):
                index = np.where(self.data[:,max_attr] == i)[0]
                temp_data = self.data[index]
                temp_label = self.label[index]
                temp_weight = self.weight[index]

                if not_empty > 0:
                    # 缺失值赋予权重
                    temp_data = np.concatenate([temp_data, empty_data])
                    temp_label = np.concatenate([temp_label, empty_label])
                    temp_empty_weight = empty_weight * (len(index) / not_empty)
                    temp_weight = np.concatenate([temp_weight, temp_empty_weight])

                # 删去已被划分的属性
                temp_data = np.delete(temp_data, max_attr, axis=1)
                
                # 过滤权重为0的情况
                nonzero_weight_index = np.where(temp_weight > 0.0)[0]
                temp_data = temp_data[nonzero_weight_index]
                temp_label = temp_label[nonzero_weight_index]
                temp_weight = temp_weight[nonzero_weight_index]

                attr_name = self.attr_name.copy()
                del attr_name[max_attr]

                temp_dataset = Dataset(temp_data, temp_label, temp_weight, attr_name)
                split_dataset.append(temp_dataset)

            return split_dataset, split_type, max_attr, split_value
        else:
            # 连续值
            split_dataset = []
            split_type = "CONT"
            split_value = max_value

            not_empty_index = np.where(self.data[:,max_attr] != -1)[0]
            le_index = np.where(self.data[not_empty_index][:,max_attr] <= max_value)[0]
            gt_index = np.where(self.data[not_empty_index][:,max_attr] > max_value)[0]

            le_data = self.data[not_empty_index][le_index]
            gt_data = self.data[not_empty_index][gt_index]
            le_label = self.label[not_empty_index][le_index]
            gt_label = self.label[not_empty_index][gt_index]
            le_weight = self.weight[not_empty_index][le_index]
            gt_weight = self.weight[not_empty_index][gt_index]

            if not_empty > 0:
                le_data = np.concatenate([le_data, empty_data])
                gt_data = np.concatenate([gt_data, empty_data])
                le_label = np.concatenate([le_label, empty_label])
                gt_label = np.concatenate([gt_label, empty_label])
                le_weight = np.concatenate([le_weight, empty_weight * (len(le_data) / len(not_empty_index))])
                gt_weight = np.concatenate([gt_weight, empty_weight * (len(gt_data) / len(not_empty_index))])

            # 删去已被划分的属性
            le_data = np.delete(le_data, max_attr, axis=1)
            gt_data = np.delete(gt_data, max_attr, axis=1)

            # 过滤权重为0的情况
            le_nonzero_weight_index = np.where(le_weight > 0.0)[0]
            le_data = le_data[le_nonzero_weight_index]
            le_label = le_label[le_nonzero_weight_index]
            le_weight = le_weight[le_nonzero_weight_index]

            gt_nonzero_weight_index = np.where(gt_weight > 0.0)[0]
            gt_data = gt_data[gt_nonzero_weight_index]
            gt_label = gt_label[gt_nonzero_weight_index]
            gt_weight = gt_weight[gt_nonzero_weight_index]

            attr_name = self.attr_name.copy()
            del attr_name[max_attr]

            le_dataset = Dataset(le_data, le_label, le_weight, attr_name)
            split_dataset.append(le_dataset)
            gt_dataset = Dataset(gt_data, gt_label, gt_weight, attr_name)
            split_dataset.append(gt_dataset)

            return split_dataset, split_type, max_attr, split_value


    def cal_Entropy(self):
        res = 0.0
        for label in range(len(LABEL)):
            x = np.where(self.label == label)[0]
            if len(x) > 0:
                x = np.sum(self.weight[x])
                x = x / np.sum(self.weight)
                res -= x * math.log2(x)
        return res
    
    def cal_CondEntropy(self, index):
        if ATTR_NAME.index(self.attr_name[index]) not in CONT_ATTR:
            # 离散值
            res = 0.0
            # print("SEPE: total num {}.".format(str(SEPE_ATTR_LEN[SEPE_ATTR.index(ATTR_NAME.index(self.attr_name[index]))])))
            for i in range(SEPE_ATTR_LEN[SEPE_ATTR.index(ATTR_NAME.index(self.attr_name[index]))]):
                spec_index = np.where(self.data[:,index] == i)[0]
                spec_label = self.label[spec_index]
                spec_res = 0.0
                for label in range(len(LABEL)):
                    x = np.where(spec_label == label)[0]
                    if len(x) > 0:
                        x = np.sum(self.weight[spec_index][x])
                        x = x / np.sum(self.weight[spec_index])
                        spec_res -= x * math.log2(x)
                res += (len(spec_index) / len(self.data)) * spec_res
            # 缺失值不会计入熵，不需要处理，已经在计算中乘以权重
            return res
        else:
            # 连续值
            spec_index = np.where(self.data[:,index] != -1)[0]
            spec_attr = self.data[:,index][spec_index]
            spec_label = self.label[spec_index]
            sepc_weight = self.weight[spec_index]

            # 测试多个区间，自动排序从小到大
            uniq_attr = np.unique(spec_attr)
            # print("CONT: total num {}.".format(str(len(uniq_attr)-1)))
            if len(uniq_attr) == 1:
                return 0.0, uniq_attr[0]

            res = np.inf
            binary = None
            for i in range(0, len(uniq_attr)-1):
                mid = (uniq_attr[i] + uniq_attr[i+1]) / 2
                spec_res = 0.0
                le_index = np.where(spec_attr <= mid)[0]
                gt_index = np.where(spec_attr > mid)[0]

                le_label = spec_label[le_index]
                gt_label = spec_label[gt_index]

                le_res = 0.0
                gt_res = 0.0
                for label in range(len(LABEL)):
                    x1 = np.where(le_label == label)[0]
                    if len(x1) > 0:
                        x1 = np.sum(sepc_weight[le_index][x1])
                        x1 = x1 / np.sum(sepc_weight[le_index])
                        le_res -= x1 * math.log2(x1)

                    x2 = np.where(gt_label == label)[0]
                    if len(x2) > 0:
                        x2 = np.sum(sepc_weight[gt_index][x2])
                        x2 = x2 / np.sum(sepc_weight[gt_index])
                        gt_res -= x2 * math.log2(x2)

                spec_res += (len(le_index) / len(self.data)) * le_res
                spec_res += (len(gt_index) / len(self.data)) * gt_res

                if spec_res < res:
                    res = spec_res
                    binary = mid
            
            return res, binary


class DecisionTree(object):

    SPLIT_TYPE = ["CONT", "SEPE"] # 连续值，离散值

    def __init__(self, root):
        self.pos = 0
        self.tree = []
        self.is_traverse = []

        self.pos += 1
        self.tree.append(root)
        self.is_traverse.append(False)

        self.child = [] # 划分得到的子树编号
        self.split_type = [] # 划分类型连续CONT或离散SEPE
        self.split_attr = [] # 每一次划分的属性
        self.split_value = [] # 划分依据值，离散直接对应数组下标，连续对应二分点

        self.child.append([])
        self.split_type.append([])
        self.split_attr.append([])
        self.split_value.append([])
    
    def train(self):
        while True:
            traverse_index = None
            for i in range(len(self.is_traverse)):
                if not self.is_traverse[i]:
                    traverse_index = i
                    break
            if traverse_index is None:
                break
            print("Traverse tree {}.".format(traverse_index))
            
            self.is_traverse[traverse_index] = True

            # 叶节点，没有属性可以划分或者只剩下零/一个元素
            if len(self.tree[traverse_index].data) <= 1:
                continue
            elif len(self.tree[traverse_index]) == 0:
                continue

            split_dataset, split_type, split_attr, split_value = self.tree[traverse_index].split()
            if split_dataset is None:
                # 交叉熵为0，不必再分了，剪枝
                continue

            self.child[traverse_index] = list(range(self.pos, self.pos+len(split_dataset)))
            self.split_type[traverse_index] = split_type
            self.split_attr[traverse_index] = split_attr
            self.split_value[traverse_index] = split_value

            for dataset in split_dataset:
                self.tree.append(dataset)
                self.is_traverse.append(False)

                self.child.append([])
                self.split_type.append([])
                self.split_attr.append([])
                self.split_value.append([])

            self.pos += len(split_dataset)
    
    def test(self, item):
        pos = 0
        item_list = item.to_list()

        while True:
            child = self.child[pos]
            split_type = self.split_type[pos]
            split_attr = self.split_attr[pos]
            split_value = self.split_value[pos]

            # print(pos, child, split_type, split_attr, split_value, item_list[split_attr])

            if len(child) == 0:
                # 叶子节点且不为空节点，可以返回结果
                max_count = 0
                max_label = None
                for label in range(len(LABEL)):
                    count = np.sum(np.where(self.tree[pos].label == label))
                    if count > max_count:
                        max_count = count
                        max_label = label
                return max_label == item.label

            if split_type == "SEPE":
                # 离散值
                if item_list[split_attr] == -1:
                    # 缺失值，根据子节点的分布进行随机选取
                    probability = []
                    for c in child:
                        probability.append(len(self.tree[c].data) / len(self.tree[pos].data))
                        if len(probability) > 1:
                            probability[-1] += probability[-2]

                    random_choice = random.random()
                    for p in probability:
                        if random_choice < p:
                            random_index = probability.index(p)
                    
                    next_pos = child[random_index]
                else:
                    next_pos = child[item_list[split_attr]]

                del item_list[split_attr]
            else:
                # 连续值
                if item_list[split_attr] == -1:
                    # 缺失值，根据子节点的分布进行随机选取
                    p1 = len(self.tree[child[0]].data) / len(self.tree[pos].data)
                    p2 = len(self.tree[child[1]].data) / len(self.tree[pos].data)

                    random_choice = random.random()
                    if random_choice <= p1:
                        next_pos = child[0]
                    else:
                        next_pos = child[1]
                else:
                    if item_list[split_attr] <= split_value:
                        next_pos = child[0]
                    else:
                        next_pos = child[1]
                
                del item_list[split_attr]
            
            # 判定下一个位置是不是空节点，若是取当前节点的结果返回
            if len(self.tree[next_pos].data) == 0:
                # 空节点
                max_count = 0
                max_label = None
                for label in range(len(LABEL)):
                    count = np.sum(np.where(self.tree[pos].label == label))
                    if count > max_count:
                        max_count = count
                        max_label = label
                return max_label == item.label
            else:
                pos = next_pos


if __name__ == "__main__":
    train_data_path = "../adult.data"
    test_data_path = "../adult.test"

    train_data = []
    train_label = []
    train_weight = []

    line_cnt = 0
    with open(train_data_path, "r") as train_data_file:
        line = train_data_file.readline()
        while line.strip():
            line_cnt += 1
            # print("read line " + str(line_cnt))

            line_split = line.strip().split(',')
            args = tuple(list(map(lambda x: x.strip(), line_split)))
            item = Item(*args)

            train_data.append(item.to_list())
            train_label.append(item.label)
            train_weight.append(item.weight)

            line = train_data_file.readline()
    print("Read files done.")

    root = Dataset(train_data, train_label, train_weight, ATTR_NAME)
    print("Build root dataset done.")
    tree = DecisionTree(root)
    print("Create decision tree done.")
    tree.train()
    print("Train process done.")
    
    line_cnt = 0
    correct_prediction = 0
    with open(test_data_path, "r") as test_data_file:
        # 丢掉第一行
        line = test_data_file.readline()
        line = test_data_file.readline()
        while line.strip():
            line_cnt += 1
            print("test read {}".format(line_cnt))

            line_split = line.strip().split(',')
            args = tuple(list(map(lambda x: x.strip(), line_split)))
            item = Item(*args, test=True)
            if tree.test(item):
                correct_prediction += 1

            line = test_data_file.readline()

    print("Test Dataset Accuracy: {}%".format(correct_prediction / line_cnt * 100))