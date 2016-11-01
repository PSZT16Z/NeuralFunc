import numpy as np
import pprint

#sigmoid
def nonlin(x, deriv=False):
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
            self.nodes.append(SynapseNode(inNo, outNo, idx));
            if (idx != 0):
                self.nodes[idx].prevNode = self.nodes[idx - 1]
                self.nodes[idx - 1].nextNode = self.nodes[idx]

    def update(self, trainIn, trainOut):
        self.nodes[0].update(trainIn, trainOut)

    def predict(self, x):
        return self.nodes[0].predict(x)
    

class SynapseNode(object):
    def __init__(self, inNo, outNo, idx):
        self.syn = 2 * np.random.random((inNo, outNo)) - 1;
        self.id = idx
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
            self.calc(np.array(trainIn));

        # Proceed with calculation until the last node
        if (self.nextNode != None):
            self.nextNode.update(trainIn, trainOut)
        # Continue from the last node till first one

        # Calculate error for current node   
        if (self.nextNode != None):
            self.error = self.nextNode.delta.dot(self.nextNode.syn.T)
        else:
            self.error = np.array(trainOut) - self.result

        # Calculate delta for current node
        self.delta = self.error * nonlin(self.result, True)

        # Alter synapses from the first node till the last one
        if (self.prevNode == None):
            self.res(trainIn)

    def calc(self, x):
        self.result = nonlin(np.dot(x, self.syn));

    def res(self, trainIn):
        if (self.prevNode == None):
            self.syn += np.array(trainIn).T.dot(self.delta)
        else:
            self.syn += self.prevNode.result.T.dot(self.delta)
            
        if (self.nextNode):
            self.nextNode.res(trainIn)
            
    def predict(self, x):
        res = nonlin(np.dot(x, self.syn))
        if (self.nextNode != None):
            return self.nextNode.predict(res);
        else:
            return res;


class Neuron(object):         
    trainIntensity = 10000;

    def __init__(self, layerList = [1, 10, 10, 2]):
        self.trainingSet = [];
        self.trainingVals = [];
        assert(len(layerList) > 2);
        np.random.seed(1)
        print(layerList)
        self.synapseTree = SynapseTree(layerList)
 
    def addTrainingData(self, inList, outList):
        self.trainingSet.append(inList);
        self.trainingVals.append(outList);
        self.train();

    def train(self):
        for x in xrange(self.trainIntensity):
            self.synapseTree.update(self.trainingSet, self.trainingVals)

    def predict(self, x):
        return self.synapseTree.predict(x)
