import numpy as np
import time
import random
import threading
from NNStructure import NNStructure

class NeuralNetwork(threading.Thread):
    def __init__(self, layers, minimum, maximum, learningRate):
        threading.Thread.__init__(self)
        self.daemon = True
        self.ONLINE_TRAINING = False
        self.lock = threading.Lock()
        self.minimum = np.float(minimum)
        self.maximum = np.float(maximum)
        self.dataIn = []
        self.dataOut = []
        self.lock.acquire()
        self.nns = NNStructure(layers, self.minimum, self.maximum, learningRate)
        self.lock.release()

    def restructure(self, layers):
        self.lock.acquire()
        self.nns.restructure(layers)
        self.lock.release()

    def setLearningRate(self, rate):
        self.lock.acquire()
        self.nns.setLearningRate(rate)
        self.lock.release()

    def run(self):
        while True:
            if self.dataIn and self.dataOut:
                self.lock.acquire()
                if self.ONLINE_TRAINING:
                    idx = random.randint(0, len(self.dataIn) - 1)
                    self.nns.train([self.dataIn[idx] ], [self.dataOut[idx] ])
                else:
                    self.nns.train(self.dataIn, self.dataOut)
                self.lock.release()
                time.sleep(0.00001)

    def start_online_training(self):
        self.ONLINE_TRAINING = True
        self.start()

    def predict(self, dataIn):
        self.lock.acquire()
        result = self.nns.predict(dataIn)
        self.lock.release()
        return result

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

