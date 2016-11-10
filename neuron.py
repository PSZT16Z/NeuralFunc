import numpy as np
import random

def sigmoid(x, deriv=False):
    if(deriv==True):
        return x*(1-x);
    return 1/(1+np.exp(-x));

class SynapseTree(object):
    def __init__(self, synapseList):
        self.nodes = []
        for idx in range(len(synapseList) - 1):
            inNo = synapseList[idx];
            outNo = synapseList[idx + 1];
            print('[{}] Add synapse({}, {})'.format(idx, inNo, outNo))
            self.nodes.append(SynapseNode(inNo, outNo));
            if (idx != 0):
                self.nodes[idx].prevNode = self.nodes[idx - 1]
                self.nodes[idx - 1].nextNode = self.nodes[idx]

    def update(self, trainIn, trainOut):
        self.nodes[0].update(trainIn, trainOut)

    def predict(self, x):
        return self.nodes[0].predict(x)
    

class SynapseNode(object):
    def __init__(self, inNo, outNo):
        self.syn = 2 * np.random.random((inNo, outNo)) - 1;
        self.result = None;
        self.error = None;
        self.delta = None;
        self.nextNode = None;
        self.prevNode = None;
    
    def update(self, trainIn, trainOut):
        # Calculate result for current node
        if (self.prevNode != None):
            self.calc(self.prevNode.result);
        else:
            self.calc(trainIn);

        # Proceed with calculation until the last node
        if (self.nextNode != None):
            self.nextNode.update(trainIn, trainOut);

        # Continue from the last node till first one
        # Calculate error for current node   
        if (self.nextNode != None):
            self.error = self.nextNode.delta.dot(self.nextNode.syn.T);
        else:
            self.error = trainOut - self.result;

        # Calculate delta for current node
        self.delta = self.error * sigmoid(self.result, True);

        # Alter synapses from the first node till the last one
        if (self.prevNode == None):
            self.res(trainIn);

    def calc(self, x):
        self.result = sigmoid(np.dot(x, self.syn));

    def res(self, trainIn):
        if (self.prevNode == None):
            self.syn += trainIn.T.dot(self.delta);
        else:
            self.syn += self.prevNode.result.T.dot(self.delta);
            
        if (self.nextNode):
            self.nextNode.res(trainIn);
            
    def predict(self, x):
        res = sigmoid(np.dot(x, self.syn))
        if (self.nextNode != None):
            return self.nextNode.predict(res);
        else:
            return res;


class Neuron(object):         
    def __init__(self, minVal, maxVal, trainIn, trainOut, layerList = [1, 10, 10, 2]):
        self.trainIn = trainIn;
        self.trainOut = trainOut;
        self.min = minVal;
        self.max = maxVal;
        self.minmax = float(maxVal - minVal)
        assert(len(layerList) > 2);
        np.random.seed(1)
        self.synapseTree = SynapseTree(layerList)

    def normalize(self, data):
        return (data - self.min) / self.minmax

    def denormalize(self, data):
        return (data * self.minmax) + self.min

    def train(self):
        trainlen = len(self.trainIn)
        if (trainlen > 0):
            idx = random.randint(0, trainlen - 1)
            x = self.normalize(np.array([[self.trainIn[idx]]]))
            y = self.normalize(np.array([self.trainOut[idx]]))
            self.synapseTree.update(x, y)

    def predict(self, x):
        return self.denormalize(self.synapseTree.predict(self.normalize(x)))
