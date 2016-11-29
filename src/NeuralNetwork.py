import numpy as np
import time
import random
import threading


class NeuralNetwork(threading.Thread):
    def __init__(self, layers, minimum, maximum):
        threading.Thread.__init__(self)
        self.daemon = True
        self.ONLINE_TRAINING = False
        self.LEARNING_RATE = 10
        self.minimum = np.float(minimum)
        self.maximum = np.float(maximum)
        np.random.seed(1)
        self.lock = threading.Lock()
        self.restructure(layers)
        self.dataIn = []
        self.dataOut = []

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

    def sigmoid(self, x):
        return 1/(1+np.exp(-x))

    def sigmoid_deriv(self, x):
        return x*(1-x)
    
    def normalize(self, data):
        data = np.asarray(data, dtype = np.float)
        return (data - self.minimum) / (self.maximum - self.minimum)

    def denormalize(self, data):
        data = np.asarray(data, dtype = np.float)
        return (data * (self.maximum - self.minimum)) + self.minimum

    def forward_pass(self, dataIn):
        n = self.no_of_layers
        layers = [None] * n
        layers[0] = np.asarray(dataIn)
        for i in xrange(1, n):
            layers[i] = self.sigmoid(np.dot(layers[i-1], self.weights[i-1]))
        return layers

    def compute_error(self, dataOut, layers):
        n = self.no_of_layers
        l_error = [None] * n
        l_delta = [None] * n
        l_error[n-1] = layers[n-1] - np.asarray(dataOut)
        for i in xrange(n-1, 1, -1):
            l_delta[i] = l_error[i] *self.sigmoid_deriv(layers[i])
            l_error[i-1] = l_delta[i].dot(self.weights[i-1].T)
        l_delta[1] = l_error[1] * self.sigmoid_deriv(layers[1])
        return l_delta
    
    def back_propagate(self, layers, l_delta):
        n = self.no_of_layers
        for i in xrange(n-2, -1, -1):
            self.weights[i] -= self.LEARNING_RATE * layers[i].T.dot(l_delta[i+1])

    def train(self, dataIn, dataOut):
        self.lock.acquire()
        if dataIn and dataOut:
            n = self.no_of_layers
            dataIn = self.normalize(dataIn)
            dataOut = self.normalize(dataOut)
            layers = self.forward_pass(dataIn)
            l_delta = self.compute_error(dataOut, layers)
            self.back_propagate(layers, l_delta)
        self.lock.release()

    def train_online(self):
        if self.dataIn and self.dataOut:
            idx = random.randint(0, len(self.dataIn) - 1)
            self.train([self.dataIn[idx] ], [self.dataOut[idx] ])

    def run(self):
        while True:
            if self.ONLINE_TRAINING:
                self.train_online()
            else:
                self.train(self.dataIn, self.dataOut)
            time.sleep(0.00001)

    def start_online_training(self):
        self.ONLINE_TRAINING = True
        self.start()

    def predict(self, dataIn):
        dataIn = self.normalize(dataIn)
        self.lock.acquire()
        layers = self.forward_pass(dataIn)
        self.lock.release()
        return self.denormalize(layers[self.no_of_layers-1])

    def update_dataset(self, dataIn, dataOut):
        #TODO validate dataset against layers structure (# of in and out values)
        self.lock.acquire()
        self.dataIn = dataIn
        self.dataOut = dataOut
        self.lock.release()

    def append_datapoints(self, dataIn, dataOut):
        self.lock.acquire()
        self.dataIn.extend(dataIn)
        self.dataOut.extend(dataOut)
        self.lock.release()

    def remove_datapoints(self, pointIn, pointOut):
        self.lock.acquire()
        if pointIn in self.dataIn:
            del self.dataIn[self.dataIn.index(pointIn)]
        if pointOut in self.dataOut:
            del self.dataOut[self.dataOut.index(pointOut)]
        self.lock.release()
