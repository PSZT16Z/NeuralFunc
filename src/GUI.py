import wx
import threading
import time
from NeuralNetwork import NeuralNetwork
import GuiUtilities

class MyFrame(wx.Frame):
    posx1 = None
    posy1 = None
    posy2 = None
    panel = None
    isPainting = False
    isDeleting = False
    isRunning = True
    circleRadius = 4
    points1 = []
    points2 = []
    colors = [
        wx.Colour(  0,   0, 153),
        wx.Colour(102, 178, 255),
        wx.Colour(  0, 153,   0),
        wx.Colour(102, 255, 102) ]
    titles = ['Pnt1', 'Plot1', 'Pnt2', 'Plot2']
    
    menuIdTitle = {}

    def __init__(self):
        self.frame = wx.Frame.__init__(self, None, 
                title='Aproksymacja funkcji dwuwartosciowej',
                size=(500,500))
        self.panel = wx.Panel(self, -1)
        menuTitles = [ "Plot colours",
                       "NN structure",
                       "Reset",
                       "Quit" ]
        for title in menuTitles:
            self.menuIdTitle[wx.NewId()] = title
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
        self.panel.Bind(wx.EVT_MIDDLE_DOWN, self.onMidDown)
        self.panel.Bind(wx.EVT_MIDDLE_UP, self.onMidUp)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
        self.panel.Bind(wx.EVT_PAINT, self.onPaint)
        self.panel.Bind(wx.EVT_MOTION, self.onMove)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.approximation = []
        self.lock = threading.Lock()
        self.nn = NeuralNetwork([1,10,10,2], 0, self.GetSize().GetWidth(), 15)
        self.nn.start_online_training()
        self.predict_thread = threading.Thread(None, self.update_approximation)
        self.predict_thread.daemon = True
        self.predict_thread.start()

    def update_approximation(self):
        while self.isRunning:
            time.sleep(0.1)
            self.lock.acquire()
            self.approximation = self.nn.predict(
                    list([x] for x in range(self.GetSize().GetWidth())))
            self.lock.release()
            wx.CallAfter(self.Refresh)

    def onLeftClick(self, event):
        pos = event.GetPosition()
        self.posx1 = pos.x
        self.posy1 = pos.y
        self.isPainting = True

    def onMidDown(self, event):
        self.isDeleting = True

    def onMidUp(self, event):
        pos = event.GetPosition();
        idx = -1
        for i, (x, y, _, _) in enumerate(self.points1):
            xDif = abs(x - pos.x)
            y1Dif = abs(y - pos.y)
            y2Dif = abs(self.points2[i][1] - pos.y)
            if xDif <= 10 and (y1Dif <= 10 or y2Dif <= 10):
                idx = i
                break

        if idx > -1:
            self.nn.remove_datapoints([ self.points1[idx][0] ] ,
                                      [ self.points1[idx][1],
                                        self.points2[idx][1] ])
            del self.points1[idx]
            del self.points2[idx]
        self.isDeleting = False

    def onRightClick(self, event):
        if self.isPainting is True:
            self.isPainting = False
            pos = event.GetPosition()
            self.posy2 = pos.y
            self.points1.append([self.posx1, self.posy1, self.circleRadius, self.circleRadius])
            self.points2.append([self.posx1, self.posy2, self.circleRadius, self.circleRadius])
            self.nn.append_datapoints([[self.posx1]], [[self.posy1, self.posy2]])
            self.posx1 = self.posy1 = self.posy2 = None
            self.Refresh()
        else:
            menu = GuiUtilities.RmbMenu(self, self.menuIdTitle, [self.colorSelectCb, self.restructureCb, self.resetCb, self.closeCb])
            self.PopupMenu(menu, event.GetPosition())
            menu.Destroy()

    def onPaint(self, event):
        dc = wx.PaintDC(event.GetEventObject())
        drawnPoints1 = list(self.points1)
        drawnPoints2 = list(self.points2)

        if self.isPainting:
            dc.SetPen(wx.Pen('black', 1, wx.PENSTYLE_DOT))
            dc.DrawLine(self.posx1, 0, self.posx1, self.GetSize().GetHeight())
            
            if self.posy1 is not None:
                drawnPoints1.append([self.posx1, self.posy1, self.circleRadius, self.circleRadius])
            if self.posx1 is not None and self.posy2 is not None:
                drawnPoints2.append([self.posx1, self.posy2, self.circleRadius, self.circleRadius])
        elif self.isDeleting:
            dc.SetPen(wx.Pen('black', 1))
            dc.SetBrush(wx.Brush('black', wx.CROSSDIAG_HATCH))
            dc.DrawCircle(self.posx1, self.posy1, 10)
            dc.SetBrush(wx.Brush('black', wx.TRANSPARENT))
            
        dc.SetPen(wx.Pen(self.colors[0], 1))
        dc.DrawEllipseList(drawnPoints1)
        dc.SetPen(wx.Pen(self.colors[2], 1))
        dc.DrawEllipseList(drawnPoints2)

        self.lock.acquire()
        points = list(self.approximation)
        self.lock.release()

        drawnLine1 = []
        drawnLine2 = []
        for i, val in enumerate(points):
            drawnLine1.append(wx.Point(i, val[0]))
            drawnLine2.append(wx.Point(i, val[1]))
        dc.SetPen(wx.Pen(self.colors[1], 1))
        dc.DrawLines(drawnLine1)
        dc.SetPen(wx.Pen(self.colors[3], 1))
        dc.DrawLines(drawnLine2)

    def onMove(self, event):
        pos = event.GetPosition()
        if self.isPainting is True:
            self.posy2 = pos.y
            self.Refresh()
        else:
            self.posy1 = pos.y
            self.posx1 = pos.x

    def onClose(self, event):
        self.isRunning = False
        self.predict_thread.join()
        self.Destroy()

    def colorSelectCb(self, event):
        dialog = GuiUtilities.PlotColorDialog(self.frame, self.colors, self.titles)
        if dialog.ShowModal() == wx.ID_OK:
            pass
        dialog.Destroy()

    def closeCb(self, event):
        self.Close()

    def resetCb(self, event):
        self.lock.acquire()
        self.nn.restructure([1,10,10,2])
        self.nn.update_dataset([], [])
        del self.points1[:]
        del self.points2[:]
        self.lock.release()

    def restructureCb(self, event):
        dlg = wx.TextEntryDialog(self.frame, 'Enter layer list for NN', 'NN structure edit')
        dlg.SetValue = '10, 10'
        if dlg.ShowModal() == wx.ID_OK:
            try:
                layerList = [int(k) for k in dlg.GetValue().split(',')]
                layerList = [1] + layerList + [2]
                dlg.Destroy()
                self.nn.restructure(layerList)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()
