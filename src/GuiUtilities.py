import wx

class RmbMenu(wx.Menu):
    def __init__(self, parent, idTitleMap):
        super(RmbMenu, self).__init__()
        self.parent = parent
        for i in range(len(idTitleMap)):
            item = wx.MenuItem(self, idTitleMap[i][0], idTitleMap[i][1])
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, idTitleMap[i][2], item)

def getHiddenLayers(frame, activationDict):
        dlg = NNRestructureDialog(frame, activationDict)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                foundEmpty = False
                hiddenLayers = []
                for x in range(len(dlg.texts)):
                    num = dlg.texts[x].GetValue()
                    fun = dlg.combos[x].GetValue()
                    if num.isnumeric() and fun in activationDict.keys() and not foundEmpty:
                        hiddenLayers.append((int(num), fun))
                    elif num == '' and fun == '':
                        foundEmpty = True
                    else:
                        return False
                dlg.Destroy()
                return hiddenLayers
            except Exception as e:
                print(e)
        return False


class NNRestructureDialog(wx.Dialog):
    def __init__(self, parent, activationDict):
        super(NNRestructureDialog, self).__init__(parent, title = 'Change network structure', size = (300, 300))
        self.ad = activationDict
        wrapper = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add((0, 10))
        btn = wx.Button(self, label="Add layer")
        self.Bind(wx.EVT_BUTTON, self.onClickCb, btn)
        self.vbox.Add(btn)
        self.vbox.Add((0, 10))
        self.texts = []
        self.combos = []
        for x in xrange(0,2):
            self.addRow(self.vbox, self.ad)
        wrapper.Add(self.vbox)
        btnSizer = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        wrapper.Add(btnSizer, wx.EXPAND|wx.BOTTOM)
        self.SetSizer(wrapper)
        self.Centre()
        self.SetInitialSize()
        self.Show(True)

    def addRow(self, vbox, ad):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, label='Layer size:', size = (80, 25))
        text = wx.TextCtrl(self, size = (40, 35))
        self.texts.append(text)
        label2 = wx.StaticText(self, label='Function:', size = (80, 25))
        combo = wx.ComboBox(self, choices = ad.keys())
        self.combos.append(combo)

        sizer.Add((20, 0))
        sizer.Add(label, proportion = 0, flag = wx.ALIGN_LEFT)
        sizer.Add((20, 0))
        sizer.Add(text, proportion = 0, flag = wx.ALIGN_CENTRE)
        sizer.Add((20, 0))
        sizer.Add(label2, proportion = 0, flag = wx.ALIGN_LEFT)
        sizer.Add((20, 0))
        sizer.Add(combo, proportion = 0, flag = wx.ALIGN_CENTRE)
        vbox.Add(sizer, flag = wx.ALIGN_CENTRE)

    def onClickCb(self, event):
        self.addRow(self.vbox, self.ad)
        self.Fit()

class PlotColorDialog(wx.Dialog):
    def __init__(self, parent, colorList, titleList):
        super(PlotColorDialog, self).__init__(parent, title = 'Change plot colours', size = (200,200))
        self.colors = colorList
        self.titles = titleList
        self.ids = []
        panel = wx.Panel(self) 
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add((0, 10))
        hboxs = [ wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.HORIZONTAL) ]
        self.colBox = [None, None, None, None]
        spacer = 0
        for x in range(len(colorList)):
            text = wx.TextCtrl(panel, style = wx.TE_READONLY, size = (40, 25))
            text.SetValue(titleList[x])
            self.ids.append(wx.NewId())
            btn = wx.Button(panel, self.ids[-1], size = (50, 25), label = "Change")

            self.Bind(wx.EVT_BUTTON, self.onClickCb, btn)
            self.colBox[x] = wx.Panel(panel, size=(25, 25))
            self.colBox[x].SetBackgroundColour(colorList[x])
            hboxs[x].Add(text, proportion = 0, flag = wx.ALIGN_LEFT)
            hboxs[x].Add((20, 0))
            hboxs[x].Add(self.colBox[x], proportion = 0, flag = wx.ALIGN_CENTRE)
            hboxs[x].Add((40, 0))
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

    def onClickCb(self, event):
        dialog = wx.ColourDialog(None)
        dialog.GetColourData().SetChooseFull(False)
        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetColourData().GetColour().Get()
            idx = self.ids.index(event.GetId())
            self.colors[idx].Set(data[0], data[1], data[2])
            self.refreshColours()
        dialog.Destroy()
