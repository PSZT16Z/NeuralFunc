import numpy as np
import time
import random
import threading


class NeuralNetwork(threading.Thread):
    def __init__(self, layers, minimum, maximum):
        threading.Thread.__init__(self)
        self.daemon = True
        self.ONLINE_TRAINING = False
        self.minimum = minimum
        self.maximum = maximum
        np.random.seed(1)
        self.lock = threading.Lock()
        self.restructure(layers)
        self.dataset = []

    def sigmoid(self, x):
        return 1/(1+np.exp(-x))

    def sigmoid_deriv(self, x):
        return x*(1-x)
    
    def normalize(self, data):
        return (data - self.minimum) / (self.maximum - self.minimum)

    def denormalize(self, data):
        return (data * (self.maximum - self.minimum)) + self.minimum

    def forward_pass(self, dataset):
        n = self.no_of_layers
        layers = [None] * n
        layers[0] = np.asarray([dataset.T[0]]).T
        for i in xrange(1, n):
            layers[i] = self.sigmoid(np.dot(layers[i-1], self.weights[i-1]))
        return layers

    def compute_error(self, dataset, layers):
        n = self.no_of_layers
        l_error = [None] * n
        l_delta = [None] * n
        l_error[n-1] = dataset[:,1:3] - layers[n-1]
        for i in xrange(n-1, 1, -1):
            l_delta[i] = l_error[i] *self.sigmoid_deriv(layers[i])
            l_error[i-1] = l_delta[i].dot(self.weights[i-1].T)
        l_delta[1] = l_error[1] * self.sigmoid_deriv(layers[1])
        return l_delta
    
    def back_propagate(self, layers, l_delta):
        n = self.no_of_layers
        for i in xrange(n-2, -1, -1):
            self.weights[i] += layers[i].T.dot(l_delta[i+1])

    def train(self, dataset):
        self.lock.acquire()
        print dataset
        if dataset:
            n = self.no_of_layers
            dataset = self.normalize(np.asarray(dataset, dtype=float))
            layers = self.forward_pass(dataset)
            l_delta = self.compute_error(dataset, layers)
            self.back_propagate(layers, l_delta)
        self.lock.release()

    def train_online(self):
        if self.dataset:
            datapoint = [self.dataset[random.randint(0, len(self.dataset) - 1)]]
            self.train(datapoint)

    def run(self):
        while True:
            if self.ONLINE_TRAINING:
                self.train_online()
            else:
                self.train(self.dataset)
            time.sleep(0.0001)

    def start_online_training(self):
        self.ONLINE_TRAINING = True
        self.start()

    def predict(self, dataset):
        dataset = self.normalize(np.asarray(dataset, dtype=float))
        result = []
        layers = [None] * self.no_of_layers
        self.lock.acquire()
        for val in dataset:
            layers[0] = np.asarray(float(val))
            for i in xrange(1, self.no_of_layers):
                layers[i] = self.sigmoid(np.dot(layers[i-1], self.weights[i-1]))
            result.append(layers[self.no_of_layers-1][0])
        self.lock.release()
        return self.denormalize(np.asarray(result)).tolist()

    def update_dataset(self, dataset):
        #TODO validate dataset against layers structure (# of in and out values)
        self.lock.acquire()
        self.dataset = list(dataset)
        self.lock.release()

    def append_dataset(self, data):
        self.lock.acquire()
        self.dataset.append(data)
        self.lock.release()

    def restructure(self, layerList):
        self.lock.acquire()
        for val in layerList:
            if val is None or val <= 0:
                self.lock.release()
                return
        self.no_of_layers = len(layerList)
        self.weights = [
            (2 * np.random.random((layerList[i], val)) - 1)
            for i, val in enumerate(layerList[1:])]
        self.lock.release()
