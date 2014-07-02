#!/usr/bin/python


import wx
import os

class IOCListPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(IOCListPanel, self).__init__(*args, **kwargs)
        self.SetBackgroundColour("#ffffff")

class IOCEditorPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(IOCEditorPanel, self).__init__(*args, **kwargs)
        self.SetBackgroundColour("#ccffcc")

class IOCMetadataPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(IOCMetadataPanel, self).__init__(*args, **kwargs)
        self.SetBackgroundColour("#cccccc")

class PyIOCe(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(PyIOCe, self).__init__(*args, **kwargs) 
            
        self.InitUI()

    def InitUI(self):    

        #Menu Bar
        menubar = wx.MenuBar()
        
        fileMenu = wx.Menu()
        helpMenu = wx.Menu()
        
        fitem = fileMenu.Append(wx.ID_FILE, '&Open',)
        menubar.Append(fileMenu, '&File')
        
        hitem = helpMenu.Append(wx.ID_ABOUT,   "&About PyIOCe")
        menubar.Append(helpMenu, "&Help")

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        self.Bind(wx.EVT_MENU, self.OnAbout, hitem)
        
        self.SetMenuBar(menubar)


        #Toolbar
        toolbar = self.CreateToolBar()
        toolbar.AddSimpleTool(1, wx.Image('check.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'New', '')
        toolbar.AddSimpleTool(2, wx.Image('check.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Open', '')
        toolbar.AddSimpleTool(3, wx.Image('check.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save', '')
        toolbar.AddSimpleTool(4, wx.Image('check.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Exit', '')
        toolbar.Realize()
 
        self.Bind(wx.EVT_TOOL, self.OnQuit, id=1)
        self.Bind(wx.EVT_TOOL, self.OnQuit, id=2)
        self.Bind(wx.EVT_TOOL, self.OnQuit, id=3)
        self.Bind(wx.EVT_TOOL, self.OnQuit, id=4)
 
        #Split Panes
        vsplitter = wx.SplitterWindow(self)
        hsplitter = wx.SplitterWindow(vsplitter)
        ioclist = IOCListPanel(vsplitter)
        ioceditor = IOCEditorPanel(hsplitter)
        iocmetadata = IOCMetadataPanel(hsplitter)

        vsplitter.SplitVertically(ioclist, hsplitter)
        hsplitter.SplitHorizontally(iocmetadata, ioceditor)
        
        self.statusbar = self.CreateStatusBar()

        self.SetSize((800, 600))
        self.SetTitle('PyIOCe')
        self.Center()
        self.Show()
        
    def OnQuit(self, e):
        self.Close()

    def OnAbout(self, e):
        self.Close()

if __name__ == '__main__':
    app = wx.App()

    PyIOCe(None)
    
    app.MainLoop()
