import time
import random
import threading
from NNStructure import NNStructure

class NeuralNetwork(threading.Thread):
    def __init__(self, layers, scale_min, scale_max, data_min, data_max,
                 learning_rate):
        threading.Thread.__init__(self)
        self.daemon = True
        self._ONLINE_TRAINING = False
        self._lock = threading.Lock()
        self._data_in = []
        self._data_out = []
        self._lock.acquire()
        self._nns = NNStructure(layers, scale_min, scale_max, data_min,
                                data_max, learning_rate)
        self._lock.release()

    def restructure(self, layers, scale_min, scale_max):
        self._lock.acquire()
        self._nns.restructure(layers, scale_min, scale_max)
        self._lock.release()

    def set_learning_rate(self, rate):
        self._lock.acquire()
        self._nns.set_learning_rate(rate)
        self._lock.release()

    def get_learning_rate(self):
        return self._nns.get_learning_rate()

    def get_activation_dict(self):
        return self._nns.activation_dict

    def run(self):
        while True:
            if self._data_in and self._data_out:
                self._lock.acquire()
                if self._data_in and self._data_out:
                    if self._ONLINE_TRAINING:
                        idx = random.randint(0, len(self._data_in) - 1)
                        self._nns.train([self._data_in[idx]],
                                        [self._data_out[idx]])
                    else:
                        self._nns.train(self._data_in, self._data_out)
                self._lock.release()
                time.sleep(0.00001)

    def start_online_training(self):
        self._ONLINE_TRAINING = True
        self.start()

    def start_bulk_training(self):
        self._ONLINE_TRAINING = False
        self.start()

    def predict(self, data_in):
        self._lock.acquire()
        result = self._nns.predict(data_in)
        self._lock.release()
        return result

    def update_dataset(self, data_in, data_out):
        self._lock.acquire()
        self._data_in = data_in
        self._data_out = data_out
        self._lock.release()

    def append_datapoints(self, data_in, data_out):
        self._lock.acquire()
        self._data_in.extend(data_in)
        self._data_out.extend(data_out)
        self._lock.release()

    def remove_datapoints(self, point_in, point_out):
        self._lock.acquire()
        if point_in in self._data_in:
            del self._data_in[self._data_in.index(point_in)]
        if point_out in self._data_out:
            del self._data_out[self._data_out.index(point_out)]
        self._lock.release()

