import numpy as np

def _tanh(x, is_derivative=False):
    tan = np.tanh(x)
    if is_derivative:
        return 1 - np.square(tan)
    return tan

def _lin(x, is_derivative=False):
    if is_derivative:
        return np.ones_like(x)
    return x

def _relu(x, is_derivative=False):
    x = np.clip(x, -500, 500)
    res = np.maximum(x, 0)
    if is_derivative:
        res[res > 0] = 1
    return res

def _lrelu(x, is_derivative=False):
    x = np.clip(x, -500, 500)
    if is_derivative:
        res = np.maximum(x, 0.01)
        res[res > 0.01] = 1
        return res
    return np.maximum(x, 0.01*x)

def _sinus(x, is_derivative=False):
    if is_derivative:
        return np.cos(x)
    return np.sin(x)

def _sigmoid(x, is_derivative=False):
    x = np.clip(x, -500, 500)
    sig = 1 / (1 + np.exp(-x))
    if is_derivative:
        return np.multiply(sig, 1 - sig)
    return sig

class NNStructure(object):
    _norm_min = 0.0
    _norm_max = 0.0
    _scale = 0.0

    def __init__(self, layer_list, scale_min, scale_max, data_min, data_max,
                 learning_rate):
        self.activation_dict = {'linear': _lin, 'sigmoid': _sigmoid,
                                'tanh': _tanh, 'ReLU': _relu,
                                'LeakyReLU': _lrelu, 'sinus': _sinus}
        self._default_hidden_act = _tanh
        self._default_outer_act = _lin
        self._minimum = data_min
        self._maximum = data_max
        self._LEARNING_RATE = learning_rate
        self.restructure(layer_list, scale_min, scale_max)

    def restructure(self, layers, scale_min, scale_max):
        for val, _ in layers:
            if val is None or val <= 0:
                raise ValueError("invalid argument")
        self._calculate_scale(self._minimum, self._maximum, scale_min,
                              scale_max)
        self._no_of_layers = len(layers)
        self._weights = []
        self._activ_func = [
            self.activation_dict.get(layers[0][1], self._default_hidden_act)]
        for i, (layer_size, activ_func) in enumerate(layers[1:-1]):
            self._weights.append(np.random.uniform(
                -2.0, 2.0, (layers[i][0] + 1, layer_size + 1)))
            self._activ_func.append(self.activation_dict.get(
                activ_func, self._default_hidden_act))
        self._weights.append(np.random.uniform(
            -2.0, 2.0, (layers[-2][0] + 1, layers[-1][0])))
        self._activ_func.append(self.activation_dict.get(
            layers[-1][1], self._default_outer_act))

    def _calculate_scale(self, data_min, data_max, scale_min, scale_max):
        self._minimum = np.float(data_min)
        self._maximum = np.float(data_max)
        self._norm_min = np.float(scale_min)
        self._norm_max = np.float(scale_max)
        self._scale = ((self._norm_max - self._norm_min) /
                       (self._maximum - self._minimum))

    def set_learning_rate(self, rate):
        self._LEARNING_RATE = rate

    def get_learning_rate(self):
        return self._LEARNING_RATE

    def _normalize(self, data):
        data = np.asarray(data, dtype=np.float)
        return self._scale * (data - self._minimum) + self._norm_min

    def _denormalize(self, data):
        data = np.asarray(data, dtype=np.float)
        return (data - self._norm_min) / self._scale + self._minimum

    def _forward_pass(self, data_in):
        data_in = self._add_bias(data_in)
        n = self._no_of_layers
        layers = [None] * n
        layers[0] = np.asarray(data_in)
        for i in xrange(1, n):
            signal = np.dot(layers[i-1], self._weights[i-1])
            layers[i] = self._activ_func[i-1](signal)
        return layers

    def _back_propagate(self, data_out, layers):
        n = self._no_of_layers
        l_error = [None] * n
        l_delta = [None] * n
        l_error[n-1] = layers[n-1] - np.asarray(data_out)
        for i in xrange(n-1, 1, -1):
            l_delta[i] = l_error[i] * self._activ_func[i](layers[i], True)
            l_error[i-1] = l_delta[i].dot(self._weights[i-1].T)
        l_delta[1] = l_error[1] * self._activ_func[1](layers[1], True)
        return l_delta

    def _compute_gradient(self, layer, delta):
        return layer.T.dot(delta)

    def _update_weights(self, layers, l_delta):
        n = self._no_of_layers
        for i in xrange(n-2, -1, -1):
            self._weights[i] -= self._LEARNING_RATE * self._compute_gradient(
                layers[i], l_delta[i+1])

    def _add_bias(self, data):
        biased = np.ones([data.shape[0], data.shape[1] + 1])
        biased[:, :-1] = data
        return biased

    def train(self, data_in, data_out):
        data_in = self._normalize(data_in)
        data_out = self._normalize(data_out)
        layers = self._forward_pass(data_in)
        l_delta = self._back_propagate(data_out, layers)
        self._update_weights(layers, l_delta)

    def predict(self, data_in):
        data_in = self._normalize(data_in)
        layers = self._forward_pass(data_in)
        return self._denormalize(layers[-1])
