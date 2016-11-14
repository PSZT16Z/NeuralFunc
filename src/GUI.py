import wx
import threading
import time
from NeuralNetwork import NeuralNetwork

class MyFrame(wx.Frame):
    posx1 = None
    posy1 = None
    posy2 = None
    panel = None
    isPainting = False
    points = [] 
    def __init__(self):
        wx.Frame.__init__(self, None, title='Aproksymacja funkcji dwuwartosciowej',
                size=(500,500))
        self.panel = wx.Panel(self, -1)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_MOTION, self.on_move)
        self.approximation = []
        self.lock = threading.Lock()
        self.nn = NeuralNetwork([1,10,10,2], 0, self.GetSize().GetWidth())
        self.nn.start_online_training()
        self.predict_thread = threading.Thread(None, self.update_approximation)
        self.predict_thread.daemon = True
        self.predict_thread.start()

    def update_approximation(self):
        while True:
            time.sleep(0.1)
            self.lock.acquire()
            self.approximation = self.nn.predict(list(range(self.GetSize().GetWidth())))
            self.lock.release()
            wx.CallAfter(self.Refresh)

    def onLeftClick(self, event):
        pos = event.GetPosition()
        self.posx1 = pos.x
        self.posy1 = pos.y
        self.isPainting = True

    def onRightClick(self, event):
        if self.isPainting is True:
            self.isPainting = False
            pos = event.GetPosition()
            self.posy2 = pos.y
            self.points.append([self.posx1, self.posy1, self.posy2])
            self.nn.update_dataset(self.points)
            self.posx1 = self.posy1 = self.posy2 = None
            self.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(event.GetEventObject())
        dc.SetPen(wx.Pen('blue', 1, wx.PENSTYLE_DOT))
        if self.isPainting:
            dc.DrawLine(self.posx1, 0, self.posx1, self.GetSize().GetHeight())
        if self.posy1 is not None:
            dc.SetPen(wx.Pen('blue'))
            dc.DrawCircle(self.posx1, self.posy1, 2)
        if self.posx1 is not None and self.posy2 is not None:
            dc.SetPen(wx.Pen('red'))
            dc.DrawCircle(self.posx1, self.posy2, 2)
        for val in self.points:
            dc.SetPen(wx.Pen('blue'))
            dc.DrawCircle(val[0], val[1], 2)
            dc.SetPen(wx.Pen('red'))
            dc.DrawCircle(val[0], val[2], 2)
        self.lock.acquire()
        points = list(self.approximation)
        self.lock.release()
        for i, val in enumerate(points):
            dc.SetPen(wx.Pen('blue'))
            dc.DrawPoint(i, val[0])
            dc.SetPen(wx.Pen('red'))
            dc.DrawPoint(i, val[1])

    def on_move(self, event):
        pos = event.GetPosition()
        if self.isPainting is True:
            self.posy2 = pos.y
        else:
            self.posy1 = pos.y
            self.posx1 = pos.x
        self.Refresh()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()
