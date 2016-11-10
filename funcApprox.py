import wx
import time
import numpy as np
import threading
from neuron import Neuron

refreshStep = 4000
el = 4

class NeuronPopupMenu(wx.Menu):
    def __init__(self, parent, idTitleMap, cbList):
        assert(len(idTitleMap) == len(cbList))
        super(NeuronPopupMenu, self).__init__()
        self.parent = parent
        for cbNo,(id,title) in enumerate(idTitleMap.items()):
            item = wx.MenuItem(self, id, title)
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, cbList[cbNo], item)

class PlotColorDialog(wx.Dialog):
    def __init__(self, parent, colorList, titleList):
        super(PlotColorDialog, self).__init__(parent, title = 'Change plot colours', size = (200,200))
        self.colors = colorList
        self.titles = titleList
        self.ids = []
        panel = wx.Panel(self) 
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add((0,10))
        hboxs = [ wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.HORIZONTAL) ]
        self.colBox = [None, None, None, None]
        spacer = 0
        for x in range(len(colorList)):
            text = wx.TextCtrl(panel,style = wx.TE_READONLY, size=(40,25))
            text.SetValue(titleList[x])
            self.ids.append(wx.NewId())
            btn = wx.Button(panel, self.ids[-1], size=(50,25),label = "Change")

            self.Bind(wx.EVT_BUTTON, self.OnClickCbDud, btn)
            self.colBox[x] = wx.Panel(panel, size=(25,25))
            self.colBox[x].SetBackgroundColour(colorList[x])
            hboxs[x].Add(text, proportion = 0, flag = wx.ALIGN_LEFT)
            hboxs[x].Add((20,0))
            hboxs[x].Add(self.colBox[x], proportion = 0, flag = wx.ALIGN_CENTRE)
            hboxs[x].Add((40,0))
            hboxs[x].Add(btn, proportion = 0, flag = wx.ALIGN_RIGHT)
 
            vbox.Add(hboxs[x], flag = wx.ALIGN_CENTRE)
            if x % 2 == 0:
                spacer = 10
            else:
                spacer = 30
            vbox.Add((0, spacer))
                
        panel.SetSizer(vbox) 
        self.Centre() 
        self.Show(True)

    def refreshColours(self):
        for x in range(len(self.colors)):
            self.colBox[x].SetBackgroundColour(self.colors[x])
        self.Refresh()
        
    def OnClickCbDud(self, event):
        dialog = wx.ColourDialog(None)
        dialog.GetColourData().SetChooseFull(False)
        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetColourData().GetColour().Get()
            idx = self.ids.index(event.GetId())
            self.colors[idx].Set(data[0],data[1],data[2])
            self.refreshColours()
        dialog.Destroy()
        

class MyFrame(wx.Frame):
    
    def __init__(self):
        self.colors = [
            wx.Colour(0,0,153),
            wx.Colour(102,178,255),
            wx.Colour(0,153,0),
            wx.Colour(102,255,102) ]
        self.titles = ['Pnt1', 'Plot1', 'Pnt2', 'Plot2']
        menu_titles = [ "Plot colours",
                "NN structure",
                "Reset",
                "Quit" ]
        self.menuIdTitle = {}
        for title in menu_titles:
            self.menuIdTitle[wx.NewId()] = title
        self.isPointInputted = False
        self.isThreadRunning = True;
        self.trainIn = []
        self.trainOut = []

        self.blueLines = []
        self.redLines=[]
        self.mouseX = 0
        self.mouseY = 0
        self.posX = 0
        self.posY1 = 0
        self.posY2 = 0
        self.solver = None
        self.th = None
        
        self.frame = wx.Frame.__init__(self, None, title='NN function approx', size=(500,500))
        self.Bind(wx.EVT_CLOSE, self.onCloseCb)
        self.panel = wx.Panel(self, -1)
        self.initPanel()
        self.initNN()
        self.restartNetThread(True)

    def initPanel(self):
        wx.StaticText(self.panel, -1, "Pos:", pos=(10, 12))
        self.posRelease = wx.TextCtrl(self.panel, -1, "", pos=(40, 10))
        
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
        self.panel.Bind(wx.EVT_PAINT, self.onPaint)
        self.panel.Bind(wx.EVT_MOTION, self.onMove)

    def onCloseCb(self, event):
        self.restartNetThread()
        self.Destroy()

    def initNN(self, synList = [1, 10, 10, 2]):
        self.solver = Neuron(0, self.GetSize().GetHeight(), self.trainIn, self.trainOut, synList)

    def restartNetThread(self, runIt = False):
        if self.th is not None and self.th.isAlive():
            self.isThreadRunning = False
            self.th.join()
        self.th = threading.Thread(None, self.trainLoop)
        self.th.daemon = True
        self.isThreadRunning = True
        if runIt:
            self.th.start()
        
    def trainLoop(self):
        while self.isThreadRunning:
            for _ in xrange(refreshStep):
                self.solver.train()
            self.Refresh()

    def drawPlot(self, dc):
        if len(self.trainIn) > 0:
            ptsB = []
            ptsR = []
            px = np.array([range(500)])
            z = self.solver.predict(px.T)
            for x, pz in enumerate(z):
                ptsB.append(wx.Point(x, pz[0]))
                ptsR.append(wx.Point(x, pz[1]))

            dc.SetPen(wx.Pen(self.colors[1], 1))
            dc.DrawLines(ptsB)
            dc.SetPen(wx.Pen(self.colors[3], 1))
            dc.DrawLines(ptsR)

    def onButton(self, event):
        dlg = wx.TextEntryDialog(self.frame, 'Enter layer list for NN', 'NN structure edit')
        dlg.SetValue = '10, 10'
        if dlg.ShowModal() == wx.ID_OK:
            try:
                layerList = [int(k) for k in dlg.GetValue().split(',')]
                layerList = [1] + layerList + [2]
                print(layerList)
                dlg.Destroy()
                self.restartNetThread()
                self.initNN(layerList)
                self.th.start()
            except Exception as e:
                print(e)
        
    def onLeftClick(self, event):
        pos = event.GetPosition()
        self.posX = pos.x
        self.posY1 = pos.y
        self.isPointInputted = True

    def onRightClick(self, event):
        if self.isPointInputted:
            self.isPointInputted = False
            self.posY2 = event.GetPosition().y
            
            self.blueLines.append([self.posX, self.posY1, el, el])
            self.redLines.append([self.posX, self.posY2, el, el])

            self.trainIn.append(self.posX)
            self.trainOut.append([self.posY1, self.posY2])
        else:
            menu = NeuronPopupMenu(self, self.menuIdTitle, [self.ColorSelCb, self.onButton, self.onReset, self.CloseCb])
            self.PopupMenu(menu, event.GetPosition())
            menu.Destroy()

    def CloseCb(self, event):
        self.Close()

    def onReset(self, event):
        self.restartNetThread()
        del self.blueLines[:]
        del self.redLines[:]
        del self.trainIn[:]
        del self.trainOut[:]
        self.initNN()
        self.th.start()

    def ColorSelCb(self, event):
        dialog = PlotColorDialog(self.frame, self.colors, self.titles)
        if dialog.ShowModal() == wx.ID_OK:
            pass
        dialog.Destroy()
        
    def onPaint(self, event):
        dc = wx.PaintDC(event.GetEventObject())
        if self.isPointInputted is False:
            blueL = self.blueLines
            redL = self.redLines            
        else:
            blueL = self.blueLines + [[self.posX, self.posY1, el, el]]
            redL = self.redLines + [[self.posX, self.mouseY, el, el]]

        dc.SetPen(wx.Pen(self.colors[0], 1))
        dc.DrawEllipseList(blueL)
        dc.SetPen(wx.Pen(self.colors[2], 1))
        dc.DrawEllipseList(redL)

        if self.isPointInputted is False:
            self.drawPlot(dc)

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
    app.MainLoop()
