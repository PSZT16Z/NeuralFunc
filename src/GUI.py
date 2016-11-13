import wx
from NeuralNetwork import NeuralNetwork

class MyFrame(wx.Frame):
    posx1 = None
    posy1 = None
    posy2 = None
    panel = None
    isPainting = False
    points = [] 
    def __init__(self):
        wx.Frame.__init__(self, None, title='Aproksymacja funkcji dwuwartosciowej')
        panel = wx.Panel(self, -1)
        panel.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
        panel.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
        panel.Bind(wx.EVT_PAINT, self.on_paint)
        panel.Bind(wx.EVT_MOTION, self.on_move)
        self.approximation = []
        self.nn = NeuralNetwork([1,10,10,2], 0, self.GetSize().GetWidth())
        #self.update_approximation()

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

    def update_approximation(self):
        self.approximation = self.nn.predict(list(range(self.GetSize().GetWidth())))
        self.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(event.GetEventObject())
        dc.SetPen(wx.Pen('blue', 1, wx.PENSTYLE_DOT))
        if self.posx1 is not None:
            dc.DrawLine(self.posx1, 0, self.posx1, self.GetSize().GetHeight())
        if self.posx1 is not None and self.posy1 is not None:
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
        for i, val in enumerate(self.approximation):
            dc.SetPen(wx.Pen('blue'))
            dc.DrawPoint(i, val[0])
            dc.SetPen(wx.Pen('red'))
            dc.DrawPoint(i, val[1])

    def on_move(self, event):
        if self.isPainting is True:
            pos = event.GetPosition()
            self.posy2 = pos.y
            self.Refresh()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()
