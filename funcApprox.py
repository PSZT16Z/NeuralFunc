import wx
from neuron import Neuron
import numpy as np

class MyFrame(wx.Frame):
    
    panel = None
    isPointInputted = False

    def __init__(self):
        self.blueLines = []
        self.redLines=[]
        self.mouseX = 0
        self.mouseY = 0
        self.posX = 0
        self.posY1 = 0
        self.posY2 = 0
        
        self.frame = wx.Frame.__init__(self, None, title='NN function approx', size=(500,500))
        panel = wx.Panel(self, -1)
        
        self.button = wx.Button(panel, label="Change NN structure", pos=(250, 10))
        self.button.Bind(wx.EVT_BUTTON, self.onButton)
        wx.StaticText(panel, -1, "Pos:", pos=(10, 12))
        self.posRelease = wx.TextCtrl(panel, -1, "", pos=(40, 10))
        
        panel.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
        panel.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
        panel.Bind(wx.EVT_PAINT, self.onPaint)
        panel.Bind(wx.EVT_MOTION, self.onMove)
        self.neuronNet = None
        self.initNN()

    def initNN(self, synList = [1, 10, 10, 2], useOldData = False):
        oldTrainIn = None
        oldTrainOut = None
        if useOldData:
            oldTrainIn = self.neuronNet.trainingSet
            oldTrainOut = self.neuronNet.trainingVals
 
        self.neuronNet = Neuron(synList)
##        if useOldData:
##            self.neuronNet.trainingSet = oldTrainIn
##            self.neuronNet.trainingVals = oldTrainOut
##            self.neuronNet.train()
         
        if useOldData:
            for x in range(len(oldTrainIn)):
                self.neuronNet.addTrainingData(oldTrainIn[x], oldTrainOut[x])
                self.Refresh()

    def onButton(self, event):
        dlg = wx.TextEntryDialog(self.frame, 'Enter layer list for NN', 'NN structure edit')
        dlg.SetValue = '10, 10'
        if dlg.ShowModal() == wx.ID_OK:
            layerList = [int(k) for k in dlg.GetValue().split(',')]
            layerList = [1] + layerList + [2]
            print(layerList)
            dlg.Destroy()
##            dlg2 = wx.Dialog(self, title='Training new NN')
##            wx.StaticText(dlg2, -1, 'NN is being restructurized and trained.\nPlease wait.', pos=(10,12))
##            dlg2.Show()
            self.initNN(layerList, True)
##            dlg2.Destroy()
            self.Refresh()
        
    def onLeftClick(self, event):
        pos = event.GetPosition()
        self.posX = pos.x
        self.posY1 = pos.y
        self.isPointInputted = True

    def onRightClick(self, event):
        self.isPointInputted = False
        pos = event.GetPosition()
        self.posY2 = pos.y
        
        self.blueLines.append([self.posX, self.posY1, self.posX, self.posY1])
        self.redLines.append([self.posX, self.posY2, self.posX, self.posY2])
        
        newIn = [self.posX / 500.0]
        newOut = [self.posY1 / 500.0, self.posY2/500.0]
        self.neuronNet.addTrainingData(newIn, newOut)
        
        self.Refresh()

    def onPaint(self, event):
        dc = wx.PaintDC(event.GetEventObject())
        if self.isPointInputted is False:
            blueL = self.blueLines
            redL = self.redLines            
        else:
            blueL = self.blueLines + [[self.posX, self.posY1, self.posX, self.posY1]]
            redL = self.redLines + [[self.posX, self.mouseY, self.posX, self.mouseY]]

        dc.SetPen(wx.Pen('blue', 4))
        dc.DrawLineList(blueL)
        dc.SetPen(wx.Pen('red', 4))
        dc.DrawLineList(redL)

        if self.isPointInputted is False:
            self.drawPlot(dc)

    def drawPlot(self, dc):
        ptsB = []
        ptsR = []
        pen = []
        px = np.array( [ np.linspace(0, 1, num = 500) ])
        z = self.neuronNet.predict(px.T)
        z = z * 500.0
        for x, pz in enumerate(z):
            ptsB.append(wx.Point(x, pz[0]))
            ptsR.append(wx.Point(x, pz[1]))

        dc.SetPen(wx.Pen('blue', 1))
        dc.DrawLines(ptsB)
        dc.SetPen(wx.Pen('red', 1))
        dc.DrawLines(ptsR)

    def onMove(self, event):
        pos = event.GetPosition();
        self.mouseX = pos.x
        self.mouseY = pos.y
        self.posRelease.SetValue("%s, %s" % (self.mouseX, self.mouseY))
        if self.isPointInputted is True:
            self.Refresh()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show(True)
    np.random.seed(1)
    app.MainLoop()
