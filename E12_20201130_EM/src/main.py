import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from scipy.stats import multivariate_normal
from tqdm import tqdm

LABEL2ID = {
    "Iris-setosa": 0,
    "Iris-versicolor": 1,
    "Iris-virginica": 2
}

def load_data(path):
    attr, label = [], []
    with open(path, "r") as data:
        for line in data:
            if not line.strip(): continue
            line_split = line.strip().split(',')
            attr.append(list(map(lambda x: float(x), line_split[:-1])))
            label.append(LABEL2ID[line_split[-1]])
    attr = np.array(attr)
    label = np.array(label)
    return attr, label

def GMM_EM(X, K, iters):
    N, D = X.shape

    alpha = np.ones((K, 1)) / K
    gamma = np.zeros((N, K))
    mu = np.random.random((K, D))
    cov = np.stack([np.eye(D) for i in range(K)])

    for i in tqdm(range(iters)):
        # E step
        p = np.zeros((N, K))
        for k in range(K):
            p[:, k] = alpha[k] * multivariate_normal(mean=mu[k], cov=cov[k]).pdf(X)
        sum_p = np.sum(p, axis=1)
        gamma = p / sum_p[:, np.newaxis]

        # M step
        sum_gamma = np.sum(gamma, axis=0)
        alpha = sum_gamma / N
        for k in range(K):
            gamma_X = X * gamma[:, k][:, np.newaxis]
            mu[k] = np.sum(gamma_X, axis=0) / sum_gamma[k]

            X_mu = X - mu[k]
            gamma_X_mu = gamma[:, k][:, np.newaxis] * X_mu
            cov[k] = np.matmul(gamma_X_mu.T, X_mu) / sum_gamma[k]
    
    return alpha, gamma, mu, cov

if __name__ == "__main__":
    K = 3
    iters = 10000

    attr, label = load_data("iris.data")
    alpha, gamma, mu, cov = GMM_EM(attr, K, iters)

    max_gamma = np.argmax(gamma, axis=1)

    pca = PCA(n_components=2)
    coord = pca.fit_transform(attr)

    class_0 = coord[label == 0]
    class_1 = coord[label == 1]
    class_2 = coord[label == 2]

    plt.scatter(class_0[:, 0], class_0[:, 1], c="red")
    plt.scatter(class_1[:, 0], class_1[:, 1], c="green")
    plt.scatter(class_2[:, 0], class_2[:, 1], c="blue")
    plt.legend(["Iris-setosa", "Iris-versicolor", "Iris-virginica"])
    plt.savefig("origin.jpg")

    class_0 = coord[max_gamma == 0]
    class_1 = coord[max_gamma == 1]
    class_2 = coord[max_gamma == 2]

    plt.scatter(class_0[:, 0], class_0[:, 1], c="red")
    plt.scatter(class_1[:, 0], class_1[:, 1], c="green")
    plt.scatter(class_2[:, 0], class_2[:, 1], c="blue")
    plt.legend(["class_0", "class_1", "class_2"])
    plt.savefig("result.jpg")