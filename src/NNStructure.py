import numpy as np
import random

class NNStructure():
    def __init__(self, layerList, scaleMin, scaleMax, dataMin, dataMax, learningRate):
        self.activationDict = {'linear': self.lin, 'sigmoid': self.sigmoid, 'tanh':self.tanh, 'ReLU':self.relu, 'LeakyReLU':self.lrelu, 'sinus':self.sinus}
        self.defaultHiddenAct = self.tanh
        self.defaultOuterAct = self.lin
        self.minimum = dataMin
        self.maximum = dataMax
        self.learningRate = learningRate
        self.restructure(layerList, scaleMin, scaleMax)

    def restructure(self, layers, scaleMin, scaleMax):
        for val, func in layers:
            if val is None or val <= 0:
                raise ValueError("invalid argument")
        self.calculateScale(self.minimum, self.maximum, scaleMin, scaleMax)
        self.no_of_layers = len(layers)
        self.weights = []
        self.activFunc = [self.activationDict.get(layers[0][1], self.defaultHiddenAct)]
        for i, (layerSize, activFun) in enumerate(layers[1:-1]):
            self.weights.append(np.random.uniform(-2.0, 2.0, (layers[i][0] + 1, layerSize + 1)))
            self.activFunc.append(self.activationDict.get(activFun, self.defaultHiddenAct))            
        self.weights.append(np.random.uniform(-2.0, 2.0, (layers[-2][0] + 1, layers[-1][0])))
        self.activFunc.append(self.activationDict.get(layers[-1][1], self.defaultOuterAct))

    def calculateScale(self, dataMin, dataMax, scaleMin, scaleMax):
        self.minimum = np.float(dataMin)
        self.maximum = np.float(dataMax)
        self.normMin = np.float(scaleMin)
        self.normMax = np.float(scaleMax)
        self.scale = (self.normMax - self.normMin) / (self.maximum - self.minimum)

    def setLearningRate(self, rate):
        self.learningRate = rate

    def getLearningRate(self):
        return self.learningRate

    def tanh(self, x, isDerivative = False):
        tan = np.tanh(x)
        if isDerivative:
            return 1 - np.square(tan)
        return tan

    def lin(self, x, isDerivative = False):
        if isDerivative:
            return np.ones_like(x)
        return x

    def relu(self, x, isDerivative = False):
        x = np.clip(x, -500, 500)
        res = np.maximum(x, 0)
        if isDerivative:
            res[res > 0] = 1
        return res

    def lrelu(self, x, isDerivative = False):
        x = np.clip(x, -500, 500)
        if isDerivative:
            res = np.maximum(x, 0.01)
            res[res > 0.01] = 1            
            return res
        return np.maximum(x, 0.01*x)

    def sinus(self, x, isDerivative = False):
        if isDerivative:
            return np.cos(x)
        return np.sin(x)

    def sigmoid(self, x, isDerivative = False):
        x = np.clip(x, -500, 500)
        sig = 1 / (1 + np.exp(-x))
        if isDerivative:
            return np.multiply(sig, 1 - sig)
        return sig
    
    def normalize(self, data):
        data = np.asarray(data, dtype = np.float)
        return self.scale * (data - self.minimum) + self.normMin

    def denormalize(self, data):
        data = np.asarray(data, dtype = np.float)
        return (data - self.normMin) / self.scale + self.minimum

    def forward_pass(self, dataIn):
        dataIn = self.addBias(dataIn)
        n = self.no_of_layers
        layers = [None] * n
        layers[0] = np.asarray(dataIn)
        for i in xrange(1, n):
            signal = np.dot(layers[i-1], self.weights[i-1])
            layers[i] = self.activFunc[i-1](signal)
        return layers

    def back_propagate(self, dataOut, layers):
        n = self.no_of_layers
        l_error = [None] * n
        l_delta = [None] * n
        l_error[n-1] = layers[n-1] - np.asarray(dataOut)
        for i in xrange(n-1, 1, -1):
            l_delta[i] = l_error[i] * self.activFunc[i](layers[i], True)
            l_error[i-1] = l_delta[i].dot(self.weights[i-1].T)
        l_delta[1] = l_error[1] * self.activFunc[1](layers[1], True)
        return l_delta

    def compute_gradient(self, layer, delta):
        return layer.T.dot(delta)
    
    def update_weights(self, layers, l_delta):
        n = self.no_of_layers
        for i in xrange(n-2, -1, -1):
            self.weights[i] -= self.learningRate * self.compute_gradient(
                    layers[i], l_delta[i+1])

    def addBias(self, data):
        biased = np.ones([ data.shape[0], data.shape[1] + 1 ])
        biased[:, :-1] = data
        return biased

    def train(self, dataIn, dataOut):
        n = self.no_of_layers
        dataIn = self.normalize(dataIn)
        dataOut = self.normalize(dataOut)
        layers = self.forward_pass(dataIn)
        l_delta = self.back_propagate(dataOut, layers)
        self.update_weights(layers, l_delta)

    def predict(self, dataIn):
        dataIn = self.normalize(dataIn)
        layers = self.forward_pass(dataIn)
        return self.denormalize(layers[-1])
