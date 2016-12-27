import threading
import time
import wx
from NeuralNetwork import NeuralNetwork
import GuiUtilities

class MyFrame(wx.Frame):
    posx1 = None
    posy1 = None
    posy2 = None
    panel = None
    is_painting = False
    is_deleting = False
    is_running = True
    CIRCLE_RADIUS = 4
    points1 = []
    points2 = []
    colors = [wx.Colour(0, 0, 153), wx.Colour(102, 178, 255),
              wx.Colour(0, 153, 0), wx.Colour(102, 255, 102)]
    titles = ['Pnt1', 'Plot1', 'Pnt2', 'Plot2']
    menu_cb_title = []

    def __init__(self):
        self.frame = wx.Frame.__init__(
            self, None, title='Aproksymacja funkcji dwuwartosciowej',
            size=(500, 500))
        self.panel = wx.Panel(self, -1)
        menu_titles = ["Plot colours", "Learning rate", "NN structure",
                       "Reset", "Quit"]
        menu_cb = [self.color_select_cb, self.set_learning_rate_cb,
                   self.restructure_cb, self.reset_cb, self.close_cb]
        for i in range(len(menu_titles)):
            idx = wx.NewId()
            self.menu_cb_title.append([idx, menu_titles[i], menu_cb[i]])
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_click)
        self.panel.Bind(wx.EVT_MIDDLE_DOWN, self.on_mid_down)
        self.panel.Bind(wx.EVT_MIDDLE_UP, self.on_mid_up)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_MOTION, self.on_move)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.approximation = []
        self.lock = threading.Lock()
        norm_limit = self.GetSize().GetWidth()
        self.default_layer_list = [(1, 'tanh'), (10, 'tanh'), (10, 'tanh'),
                                   (2, 'linear')]
        self.neural_network = NeuralNetwork(self.default_layer_list, -1.0, 1.0,
                                            0, norm_limit, 0.5)
        self.neural_network.start_online_training()
        self.predict_thread = threading.Thread(None, self.update_approximation)
        self.predict_thread.daemon = True
        self.predict_thread.start()

    def update_approximation(self):
        while self.is_running:
            time.sleep(0.1)
            self.lock.acquire()
            self.approximation = self.neural_network.predict(
                list([x] for x in range(self.GetSize().GetWidth())))
            self.lock.release()
            wx.CallAfter(self.Refresh)

    def on_left_click(self, event):
        pos = event.GetPosition()
        self.posx1 = pos.x
        self.posy1 = pos.y
        self.is_painting = True

    def on_mid_down(self, event):
        self.is_deleting = True

    def on_mid_up(self, event):
        pos = event.GetPosition()
        idx = -1
        for i, (x, y, _, _) in enumerate(self.points1):
            x_dif = abs(x - pos.x)
            y1_dif = abs(y - pos.y)
            y2_dif = abs(self.points2[i][1] - pos.y)
            if x_dif <= 10 and (y1_dif <= 10 or y2_dif <= 10):
                idx = i
                break
        if idx > -1:
            self.neural_network.remove_datapoints([self.points1[idx][0]],
                                                  [self.points1[idx][1],
                                                   self.points2[idx][1]])
            del self.points1[idx]
            del self.points2[idx]
        self.is_deleting = False

    def on_right_click(self, event):
        if self.is_painting is True:
            self.is_painting = False
            pos = event.GetPosition()
            self.posy2 = pos.y
            self.points1.append([self.posx1, self.posy1,
                                 self.CIRCLE_RADIUS, self.CIRCLE_RADIUS])
            self.points2.append([self.posx1, self.posy2,
                                 self.CIRCLE_RADIUS, self.CIRCLE_RADIUS])
            self.neural_network.append_datapoints([[self.posx1]],
                                                  [[self.posy1, self.posy2]])
            self.posx1 = self.posy1 = self.posy2 = None
            self.Refresh()
        else:
            menu = GuiUtilities.RmbMenu(self, self.menu_cb_title)
            self.PopupMenu(menu, event.GetPosition())
            menu.Destroy()

    def on_paint(self, event):
        dc = wx.PaintDC(event.GetEventObject())
        drawn_points1 = list(self.points1)
        drawn_points2 = list(self.points2)
        if self.is_painting:
            dc.SetPen(wx.Pen('black', 1, wx.PENSTYLE_DOT))
            dc.DrawLine(self.posx1, 0, self.posx1, self.GetSize().GetHeight())
            if self.posy1 is not None:
                drawn_points1.append([self.posx1, self.posy1,
                                      self.CIRCLE_RADIUS, self.CIRCLE_RADIUS])
            if self.posx1 is not None and self.posy2 is not None:
                drawn_points2.append([self.posx1, self.posy2,
                                      self.CIRCLE_RADIUS, self.CIRCLE_RADIUS])
        elif self.is_deleting:
            dc.SetPen(wx.Pen('black', 1))
            dc.SetBrush(wx.Brush('black', wx.CROSSDIAG_HATCH))
            dc.DrawCircle(self.posx1, self.posy1, 10)
            dc.SetBrush(wx.Brush('black', wx.TRANSPARENT))
        dc.SetPen(wx.Pen(self.colors[0], 1))
        dc.DrawEllipseList(drawn_points1)
        dc.SetPen(wx.Pen(self.colors[2], 1))
        dc.DrawEllipseList(drawn_points2)

        self.lock.acquire()
        points = list(self.approximation)
        self.lock.release()

        drawn_line1 = []
        drawn_line2 = []
        for i, val in enumerate(points):
            drawn_line1.append(wx.Point(i, val[0]))
            drawn_line2.append(wx.Point(i, val[1]))
        dc.SetPen(wx.Pen(self.colors[1], 1))
        dc.DrawLines(drawn_line1)
        dc.SetPen(wx.Pen(self.colors[3], 1))
        dc.DrawLines(drawn_line2)

    def on_move(self, event):
        pos = event.GetPosition()
        if self.is_painting is True:
            self.posy2 = pos.y
            self.Refresh()
        else:
            self.posy1 = pos.y
            self.posx1 = pos.x

    def on_close(self, event):
        self.is_running = False
        self.predict_thread.join()
        self.Destroy()

    def color_select_cb(self, event):
        dialog = GuiUtilities.PlotColorDialog(self.frame, self.colors,
                                              self.titles)
        if dialog.ShowModal() == wx.ID_OK:
            pass
        dialog.Destroy()

    def close_cb(self, event):
        self.Close()

    def reset_cb(self, event):
        self.lock.acquire()
        self.neural_network.restructure(self.default_layer_list, -1.0, 1.0)
        self.neural_network.update_dataset([], [])
        del self.points1[:]
        del self.points2[:]
        self.lock.release()

    def set_learning_rate_cb(self, event):
        dlg = wx.TextEntryDialog(
            self.frame, 'Enter new learning rate',
            'Change network\'s learning rate',
            str(self.neural_network.get_learning_rate()))
        if dlg.ShowModal() == wx.ID_OK:
            try:
                rate = float(dlg.GetValue())
                dlg.Destroy()
                self.neural_network.set_learning_rate(rate)
            except Exception as e:
                print e

    def restructure_cb(self, event):
        hidden_layers = GuiUtilities.get_hidden_layers(
            self.frame, self.neural_network.get_activation_dict())
        ranges = GuiUtilities.get_normalization_range(self.frame)
        norm_min = 0
        norm_max = 1
        if ranges:
            norm_min = ranges[0]
            norm_max = ranges[1]
        if hidden_layers:
            first_layer_act = hidden_layers[0][1]
            layer_list = [(1, first_layer_act)] + hidden_layers + [(2, None)]
            self.neural_network.restructure(layer_list, norm_min, norm_max)

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()
