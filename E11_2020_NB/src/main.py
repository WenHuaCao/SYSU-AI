# Author: Lu Yanzuo
# Date: 2020-11-25
# Description: Naive Bayes classifier

import numpy as np
from scipy import stats

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
DISC_ATTR = [1, 3, 5, 6, 7, 8, 9, 13]
DISC_ATTR_LEN = [len(WORKCLASS), len(EDUCATION), len(MARITAL_STATUS), len(OCCUPATION), 
    len(RELATIONSHIP), len(RACE), len(SEX), len(NATIVE_COUNTRY)]
ATTR_NAME = ["age", "workclass", "fnlwgt", "education", "education_num", "marital_status", 
        "occupation", "relationship", "race", "sex", "capital_gain", "capital_loss", "hours_per_week", 
        "native_country"]


class Item(object):
    def __init__(self, age, workclass, fnlwgt, education, education_num, marital_status, 
        occupation, relationship, race, sex, capital_gain, capital_loss, hours_per_week, 
        native_country, label, test=False):
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
        
        self.label = LABEL.index(label) if not test else LABEL.index(label[:-1])
    
    def to_list(self):
        return [self.age, self.workclass, self.fnlwgt, self.education, self.education_num, 
            self.marital_status, self.occupation, self.relationship, self.race, self.sex, 
            self.capital_gain, self.capital_loss, self.hours_per_week, self.native_country]


def cal_normal_prob(x, mean, std):
    exp = np.exp(-(np.power(x-mean, 2))/(2*np.power(std, 2)))
    prob = (1 / (np.sqrt(2*np.pi)*std)) * exp
    return prob


class Dataset(object):
    def __init__(self, attr, label):
        self.attr = np.array(attr, dtype=np.int_)
        self.label = np.array(label, dtype=np.int_)

        self.label_prob = self.cal_label_prob()

        self.disc_prob = []
        for disc in DISC_ATTR:
            self.disc_prob.append(self.cal_attr_prob(disc))
        
        self.cont_mean = []
        self.cont_std = []
        for cont in CONT_ATTR:
            ret = self.cal_attr_prob(cont)
            self.cont_mean.append(ret[0])
            self.cont_std.append(ret[1])
        
        self.cond_disc_prob = {}
        for label in range(len(LABEL)):
            self.cond_disc_prob[label] = []
            for disc in DISC_ATTR:
                self.cond_disc_prob[label].append(self.cal_cond_attr_prob(disc, label))
        
        self.cond_cont_mean = {}
        self.cond_cont_std = {}
        for label in range(len(LABEL)):
            self.cond_cont_mean[label] = []
            self.cond_cont_std[label] = []
            for cont in CONT_ATTR:
                ret = self.cal_cond_attr_prob(cont, label)
                self.cond_cont_mean[label].append(ret[0])
                self.cond_cont_std[label].append(ret[1])

    def cal_label_prob(self):
        result = []
        total_num = len(self.label)
        for label in range(len(LABEL)):
            result.append(np.sum(self.label == label) / total_num)
        
        return result

    def cal_attr_prob(self, index):
        temp_attr = self.attr[:,index]
        temp_attr = temp_attr[temp_attr != -1]

        if index in DISC_ATTR:
            result = []
            total_num = len(temp_attr)
            for attr in range(DISC_ATTR_LEN[DISC_ATTR.index(index)]):
                result.append(np.sum(temp_attr == attr) / total_num)
            
            return result
        
        mean = np.mean(temp_attr)
        std = np.std(temp_attr)
        return mean, std

    def cal_cond_attr_prob(self, attr_index, label):
        temp_index = self.label == label
        temp_attr = self.attr[temp_index, attr_index]
        temp_attr = temp_attr[temp_attr != -1]

        if attr_index in DISC_ATTR:
            result = []
            total_num = len(temp_attr)
            for attr in range(DISC_ATTR_LEN[DISC_ATTR.index(attr_index)]):
                result.append(np.sum(temp_attr == attr) / total_num)
            
            return result
        
        mean = np.mean(temp_attr)
        std = np.std(temp_attr)
        return mean, std
    
    def test(self, item):
        item_list = item.to_list()

        for disc in DISC_ATTR:
            if item_list[disc] == -1:
                disc_prob = self.disc_prob[DISC_ATTR.index(disc)]
                item_list[disc] = np.random.choice(list(range(len(disc_prob))), p=disc_prob)
        
        for cont in CONT_ATTR:
            if item_list[cont] == -1:
                cont_mean = self.cont_mean[CONT_ATTR.index(cont)]
                cont_mean = self.cont_std[CONT_ATTR.index(cont)]
                item_list[cont] = np.random.normal(cont_mean, cont_mean)
        
        max_label = None
        max_label_prob = None
        for label in range(len(LABEL)):
            prob = self.label_prob[label]

            for disc in DISC_ATTR:
                prob *= self.cond_disc_prob[label][DISC_ATTR.index(disc)][item_list[disc]]
                prob /= self.disc_prob[DISC_ATTR.index(disc)][item_list[disc]]
            
            for cont in CONT_ATTR:
                prob *= cal_normal_prob(
                    item_list[cont], 
                    self.cond_cont_mean[label][CONT_ATTR.index(cont)],
                    self.cond_cont_std[label][CONT_ATTR.index(cont)]
                )
                prob *= cal_normal_prob(
                    item_list[cont], 
                    self.cont_mean[CONT_ATTR.index(cont)],
                    self.cont_std[CONT_ATTR.index(cont)]
                )
        
            if max_label_prob is None or prob > max_label_prob:
                max_label = label
                max_label_prob = prob
        
        return item.label == max_label



if __name__ == "__main__":
    train_data_path = "dataSet/adult.data"
    test_data_path = "dataSet/adult.test"

    train_attr = []
    train_label = []

    with open(train_data_path, "r") as train_data:
        line = train_data.readline()
        while line.strip():
            line_split = line.strip().split(',')
            args = tuple(list(map(lambda x: x.strip(), line_split)))
            item = Item(*args)

            train_attr.append(item.to_list())
            train_label.append(item.label)

            line = train_data.readline()
    print("Read train data done.")

    dataset = Dataset(train_attr, train_label)
    # print("dataset.label_prob:", dataset.label_prob)
    # print("dataset.disc_prob:", dataset.disc_prob)
    # print("dataset.cont_mean:", dataset.cont_mean)
    # print("dataset.cont_std:", dataset.cont_std)
    # print("dataset.cond_disc_prob:", dataset.cond_disc_prob)
    # print("dataset.cond_cont_mean:", dataset.cond_cont_mean)
    # print("dataset.cond_cont_std:", dataset.cond_cont_std)

    total_num = 0
    correct_prediction = 0
    with open(test_data_path, "r") as test_data:
        # 丢掉第一行
        line = test_data.readline()

        line = test_data.readline()
        while line.strip():
            total_num += 1

            line_split = line.strip().split(',')
            args = tuple(list(map(lambda x: x.strip(), line_split)))
            item = Item(*args, test=True)
            if dataset.test(item):
                correct_prediction += 1

            line = test_data.readline()

    print("Test Dataset Accuracy: {}%".format(correct_prediction / total_num * 100))