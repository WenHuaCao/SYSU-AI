import time
from math import sqrt

from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

def load_data(path):
    attr, label = [], []
    with open(path, "r") as f:
        for line in f:
            if not line.strip(): break
            line_split = line.strip().split()
            for i in range(len(line_split)):
                if line_split[i] == "?": line_split[i] = "-1"
            
            if int(line_split[22]) == -1: continue
            label_onehot = np.zeros(3)
            label_onehot[int(line_split[22])-1] = 1
            label.append(label_onehot)

            line_split = [float(x) for x in line_split]
            attr.append([])
            attr[-1].extend(line_split[0:2])
            attr[-1].extend(line_split[3:22])
            attr[-1].append(line_split[23])
            attr[-1].append(line_split[27])

    attr = np.array(attr, dtype=np.float64)
    for i in range(attr.shape[1]):
        nonzero = np.where(attr[:,i] != -1)
        data = attr[:,i][nonzero[0]]
        mean_value = np.mean(data)
        zero = np.where(attr[:,i] == -1)
        for j in zero[0]:
            attr[j][i] = mean_value

    mean = np.mean(attr, axis=0).reshape(1,-1)
    var = np.var(attr, axis=0).reshape(1,-1)
    attr = (attr - mean) / var

    label = np.stack(label)
    return attr, label

class SoftmaxRegression(object):
    def __init__(self, lr):
        self.lr = lr
        self.w1 = np.random.uniform(low=-1.0, high=1.0, size=(13, 23)) * sqrt(13/(13+23))
        self.b1 = np.zeros((13, 1))
        self.w2 = np.random.uniform(low=-1.0, high=1.0, size=(3, 13)) * sqrt(13/(3+13))
        self.b2 = np.zeros((3, 1))

        self.z1 = np.zeros((13,1))
        self.y_hat = np.zeros((3,1))
        self.loss = np.zeros(1)
    
    def forward(self, x):
        assert x.shape == (1,23)
        z1 = np.matmul(self.w1, x.T) + self.b1
        sigmoid_z1 = 1 / (1 + np.exp(-z1))
        self.z1 = sigmoid_z1

        assert z1.shape == (13,1)
        z2 = np.matmul(self.w2, self.z1) + self.b2

        assert z2.shape == (3,1)
        exp_z = np.exp(z2)
        sum_exp_z = np.sum(exp_z)
        self.y_hat = exp_z / sum_exp_z
        assert self.y_hat.shape == (3,1)
        # print(self.y_hat)
        return np.argmax(self.y_hat)
    
    def backward(self, x, y):
        assert y.shape == (1,3)

        gt = np.where(y == 1)[0][0]
        self.loss = -np.log(self.y_hat[gt])[0]

        y_hat_y = self.y_hat - y.T
        y_hat_y_z1 = np.matmul(y_hat_y, self.z1.T)
        w2_y_hat_y = np.matmul(self.w2.T, y_hat_y)
        sigmoid_w2_y_hat_y = w2_y_hat_y * (1 - w2_y_hat_y)
        w2_y_hat_y_x = np.matmul(sigmoid_w2_y_hat_y, x)
        
        assert y_hat_y.shape == (3,1)
        assert y_hat_y_z1.shape == (3,13)
        assert w2_y_hat_y.shape == (13,1)
        assert w2_y_hat_y_x.shape == (13,23)
        self.w2 -= self.lr * y_hat_y_z1
        self.b2 -= self.lr * y_hat_y
        self.w1 -= self.lr * w2_y_hat_y_x
        self.b1 -= self.lr * sigmoid_w2_y_hat_y

def test(model:SoftmaxRegression, attr, label):
    correct = 0
    for i in range(len(attr)):
        predict = model.forward(attr[i].reshape(1,-1))
        if label[i][predict] == 1: 
            correct += 1
            # print(predict)
    return correct / len(attr)

if __name__ == "__main__":
    EPOCH = 2000
    LR = 1e-6

    np.random.seed(int(time.time()))
    train_attr, train_label = load_data("horse-colic.data")
    test_attr, test_label = load_data("horse-colic.test")

    model = SoftmaxRegression(lr=LR)

    loss_list = []
    accu_list = []
    for i in range(EPOCH):
        loss_sum = 0.0
        for j in range(len(train_attr)):
            model.forward(train_attr[j].reshape(1,-1))
            model.backward(train_attr[j].reshape(1,-1), train_label[j].reshape(1,-1))
            loss_sum += model.loss
        
        accuracy = test(model, test_attr, test_label)
        loss_list.append(loss_sum / len(train_attr))
        accu_list.append(accuracy)
        print("EPOCH {}/{} - accuracy:{:.3f} loss:{:.13f}".format(i+1, EPOCH, accuracy, loss_sum / len(train_attr)))
    
    plt.plot(range(EPOCH), accu_list, color="red")
    plt.plot(range(EPOCH), loss_list, color="blue")
    plt.xlabel("epoch")
    plt.ylabel("accuracy/loss")
    plt.legend(["accuracy", "loss"])
    plt.savefig("result.jpg")