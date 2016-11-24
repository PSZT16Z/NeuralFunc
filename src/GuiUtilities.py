import wx

class RmbMenu(wx.Menu):
    def __init__(self, parent, idTitleMap, cbList):
        assert(len(idTitleMap) == len(cbList))
        super(RmbMenu, self).__init__()
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
