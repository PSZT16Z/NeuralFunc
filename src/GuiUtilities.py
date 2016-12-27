import wx

class RmbMenu(wx.Menu):
    def __init__(self, parent, id_title_map):
        super(RmbMenu, self).__init__()
        self.parent = parent
        for i in range(len(id_title_map)):
            item = wx.MenuItem(self, id_title_map[i][0], id_title_map[i][1])
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, id_title_map[i][2], item)

def get_hidden_layers(frame, activation_dict):
    dlg = NNRestructureDialog(frame, activation_dict)
    if dlg.ShowModal() == wx.ID_OK:
        try:
            found_empty = False
            hidden_layers = []
            for x in range(len(dlg.texts)):
                num = dlg.texts[x].GetValue()
                fun = dlg.combos[x].GetValue()
                if (num.isnumeric() and fun in activation_dict.keys() and
                        not found_empty):
                    hidden_layers.append((int(num), fun))
                elif num == '' and fun == '':
                    found_empty = True
                else:
                    return False
            dlg.Destroy()
            return hidden_layers
        except Exception as e:
            print e
    return False

def get_normalization_range(frame):
    dlg = NormalizationDialog(frame)
    if dlg.ShowModal() == wx.ID_OK:
        try:
            dlg_min = dlg.min.GetValue()
            dlg_max = dlg.max.GetValue()
            if dlg_min.isnumeric() and dlg_max.isnumeric():
                return (float(dlg_min), float(dlg_max))
            dlg.Destroy()
        except Exception as e:
            print e

class NormalizationDialog(wx.Dialog):
    def __init__(self, parent):
        super(NormalizationDialog, self).__init__(
            parent, title='Set data normalization', size=(315, 300))
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add((0, 10))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((10, 0))
        label = wx.StaticText(
            self, label='Normalization range:', size=(180, 25))
        hbox.Add(label)
        vbox.Add(hbox)
        self.min = wx.TextCtrl(self, size=(30, 25))
        self.max = wx.TextCtrl(self, size=(30, 25))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5, 0))
        hbox.Add(wx.StaticText(self, label='<', size=(10, 25)))
        hbox.Add((5, 0))
        hbox.Add(self.min)
        hbox.Add((5, 0))
        hbox.Add(wx.StaticText(self, label=';', size=(10, 25)))
        hbox.Add((5, 0))
        hbox.Add(self.max)
        hbox.Add((5, 0))
        hbox.Add(wx.StaticText(self, label='>', size=(10, 25)))
        vbox.Add(hbox)
        vbox.Add((0, 10))
        btn_sizer = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        vbox.Add(btn_sizer, wx.EXPAND|wx.BOTTOM)
        self.SetSizer(vbox)
        self.Centre()
        self.SetInitialSize()
        self.Show(True)

class NNRestructureDialog(wx.Dialog):
    def __init__(self, parent, activation_dict):
        super(NNRestructureDialog, self).__init__(
            parent, title='Change network structure', size=(300, 300))
        self.ad = activation_dict
        wrapper = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add((0, 10))
        btn = wx.Button(self, label="Add layer")
        self.Bind(wx.EVT_BUTTON, self.on_click_cb, btn)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((10, 0))
        hbox.Add(btn)
        self.vbox.Add(hbox)
        self.vbox.Add((0, 10))
        self.texts = []
        self.combos = []
        for x in xrange(0, 2):
            self.add_row(self.vbox, self.ad)
        wrapper.Add(self.vbox)
        btn_sizer = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        wrapper.Add(btn_sizer, wx.EXPAND|wx.BOTTOM)
        self.SetSizer(wrapper)
        self.Centre()
        self.SetInitialSize()
        self.Show(True)

    def add_row(self, vbox, ad):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, label='Layer size:', size=(80, 25))
        text = wx.TextCtrl(self, size=(40, 25))
        self.texts.append(text)
        label2 = wx.StaticText(self, label='Function:', size=(80, 25))
        combo = wx.ComboBox(self, choices=ad.keys())
        self.combos.append(combo)
        sizer.Add((20, 0))
        sizer.Add(label, proportion=0, flag=wx.ALIGN_LEFT)
        sizer.Add((20, 0))
        sizer.Add(text, proportion=0, flag=wx.ALIGN_CENTRE)
        sizer.Add((20, 0))
        sizer.Add(label2, proportion=0, flag=wx.ALIGN_LEFT)
        sizer.Add((20, 0))
        sizer.Add(combo, proportion=0, flag=wx.ALIGN_CENTRE)
        vbox.Add(sizer, flag=wx.ALIGN_CENTRE)

    def on_click_cb(self, event):
        self.add_row(self.vbox, self.ad)
        self.Fit()

class PlotColorDialog(wx.Dialog):
    def __init__(self, parent, color_list, title_list):
        super(PlotColorDialog, self).__init__(
            parent, title='Change plot colours', size=(200, 200))
        self.colors = color_list
        self.titles = title_list
        self.ids = []
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add((0, 10))
        hboxs = [wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.HORIZONTAL),
                 wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.HORIZONTAL)]
        self.col_box = [None, None, None, None]
        spacer = 0
        for x in range(len(color_list)):
            text = wx.TextCtrl(panel, style=wx.TE_READONLY, size=(45, 25))
            text.SetValue(title_list[x])
            self.ids.append(wx.NewId())
            btn = wx.Button(panel, self.ids[-1], size=(60, 25),
                            label="Change")
            self.Bind(wx.EVT_BUTTON, self.on_click_cb, btn)
            self.col_box[x] = wx.Panel(panel, size=(25, 25))
            self.col_box[x].SetBackgroundColour(color_list[x])
            hboxs[x].Add((5, 0))
            hboxs[x].Add(text, proportion=0, flag=wx.ALIGN_LEFT)
            hboxs[x].Add((20, 0))
            hboxs[x].Add(self.col_box[x], proportion=0, flag=wx.ALIGN_CENTRE)
            hboxs[x].Add((20, 0))
            hboxs[x].Add(btn, proportion=0, flag=wx.ALIGN_RIGHT)
            hboxs[x].Add((5, 0))
            vbox.Add(hboxs[x], flag=wx.ALIGN_CENTRE)
            if x % 2 == 0:
                spacer = 10
            else:
                spacer = 30
            vbox.Add((0, spacer))
        panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)

    def refresh_colors(self):
        for x in range(len(self.colors)):
            self.col_box[x].SetBackgroundColour(self.colors[x])
        self.Refresh()

    def on_click_cb(self, event):
        dialog = wx.ColourDialog(None)
        dialog.GetColourData().SetChooseFull(False)
        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetColourData().GetColour().Get()
            idx = self.ids.index(event.GetId())
            self.colors[idx].Set(data[0], data[1], data[2])
            self.refresh_colors()
        dialog.Destroy()
