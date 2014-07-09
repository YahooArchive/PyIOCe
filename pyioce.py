#!/usr/bin/python


import wx
import os
from wx.lib.mixins.listctrl import ColumnSorterMixin
import sys
import uuid

class IOC():
    def __init__(self, dummyname, dummyuuid, dummymodified):
        self.dummyname = dummyname
        self.dummyuuid = dummyuuid
        self.dummymodified = dummymodified

        self.orig_xml = None
        self.mod_xml = None

    def get_uuid(self):
        # uuid = ""
        # if self.mod_xml == None:
        #     uuid = "Orig XML"
        # else:
        #     uuid = "Mod XML"
        # return uuid
        return self.dummyuuid

    def get_name(self):
        return self.dummyname

    def get_modified(self):
        return self.dummymodified

    def get_metadata(field):
        pass

    def get_keys(self):
        pass

    def get_indicator(self):
        pass

class IOCList():
    def __init__(self):
        self.iocs = {
         'af1dfc8b-bdd9-40f7-92a6-f8e2c7391db3': IOC('IOC1','af1dfc8b-bdd9-40f7-92a6-f8e2c7391db3','12 Jun 12'),
        '3c95f06b-a3d8-4021-a05a-207ec67afb12': IOC('IOC2','3c95f06b-a3d8-4021-a05a-207ec67afb12','12 Jun 12'),
        'bdbbd16d-b674-4cea-bc2a-0a1ec70a5bb8': IOC('IOC3','bdbbd16d-b674-4cea-bc2a-0a1ec70a5bb8','12 Jun 12')
        }        

    def add_ioc(self,ioc):
        pass
        #add IOC to list

    def open_iocs(self,dir):
        pass
        #open dir of IOCs

class IOCListCtrl(wx.ListCtrl, ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ColumnSorterMixin.__init__(self, 3)
        
    def GetListCtrl(self):
        return self

class PyIOCe(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(PyIOCe, self).__init__(*args, **kwargs) 
            
        self.init_data()
        self.init_ui()
 

    def init_file_menu(self, menubar):
        file_menu = wx.Menu()

        file_open = file_menu.Append(wx.ID_FILE, '&Open',)
        menubar.Append(file_menu, '&File')
        self.Bind(wx.EVT_MENU, self.on_open, file_open)
      
    def init_help_menu(self, menubar):
        help_menu = wx.Menu()
        
        help_about = help_menu.Append(wx.ID_ABOUT,   "&About PyIOCe")
        menubar.Append(help_menu, "&Help")
        self.Bind(wx.EVT_MENU, self.on_about, help_about)

    def init_menubar(self):
        menubar = wx.MenuBar()
      
        self.init_file_menu(menubar)
        self.init_help_menu(menubar)  
        
        self.SetMenuBar(menubar)

    def init_toolbar(self):
        toolbar = self.CreateToolBar()

        self.toolbar_search = wx.TextCtrl(toolbar, size=(200,0))

        toolbar.AddSimpleTool(1, wx.Image('new.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'New', '')
        toolbar.AddSimpleTool(2, wx.Image('save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save', '')
        toolbar.AddSimpleTool(3, wx.Image('saveall.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save All', '')
        toolbar.AddSeparator()
        toolbar.AddSeparator()
        toolbar.AddSeparator()
        toolbar.AddStretchableSpace()
        toolbar.AddControl(self.toolbar_search,'Search')
        toolbar.AddStretchableSpace()
        toolbar.AddSimpleTool(4, wx.Image('case.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Case', '')
        toolbar.AddSimpleTool(5, wx.Image('lnot.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Not', '')
        toolbar.AddSimpleTool(6, wx.Image('land.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'And', '')
        toolbar.AddSimpleTool(7, wx.Image('lor.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Or', '')
        toolbar.AddSimpleTool(8, wx.Image('add.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Add Item', '')
        toolbar.AddSimpleTool(9, wx.Image('remove.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Remove Item', '')


        toolbar.Realize()
        toolbar.Fit()
 
        self.Bind(wx.EVT_TOOL, self.on_new, id=1)
        self.Bind(wx.EVT_TOOL, self.on_save, id=2)
        self.Bind(wx.EVT_TOOL, self.on_saveall, id=3)
        self.Bind(wx.EVT_TOOL, self.on_case, id=4)
        self.Bind(wx.EVT_TOOL, self.on_not, id=5)
        self.Bind(wx.EVT_TOOL, self.on_and, id=6)
        self.Bind(wx.EVT_TOOL, self.on_or, id=7)
        self.Bind(wx.EVT_TOOL, self.on_add, id=8)
        self.Bind(wx.EVT_TOOL, self.on_remove, id=9)

    def init_statusbar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("No IOC")

    def init_ioc_list_ctrl(self, ioc_list_panel):
        self.ioc_list_ctrl = IOCListCtrl(ioc_list_panel)
        self.ioc_list_ctrl.InsertColumn(0, 'Name', width=140)
        self.ioc_list_ctrl.InsertColumn(1, 'UUID', width=130)
        self.ioc_list_ctrl.InsertColumn(2, 'Modified', wx.LIST_FORMAT_RIGHT, 90)

        self.ioc_list_ctrl.itemDataMap = {}
        self.ioc_list_ctrl.index = 0

        for ioc in self.ioc_list.iocs:
            index = len(self.ioc_list_ctrl.itemDataMap)
            
            ioc_name = self.ioc_list.iocs[ioc].get_name()
            ioc_uuid = self.ioc_list.iocs[ioc].get_uuid()
            ioc_modified = self.ioc_list.iocs[ioc].get_modified()

            self.ioc_list_ctrl.itemDataMap[index] = (ioc_name, ioc_uuid, ioc_modified)

            self.ioc_list_ctrl.InsertStringItem(index, ioc_name)
            self.ioc_list_ctrl.SetStringItem(index, 1, ioc_uuid)
            self.ioc_list_ctrl.SetStringItem(index, 2, ioc_modified)
            self.ioc_list_ctrl.SetItemData(index, index)

    def init_ioc_list_panel(self, vsplitter):

        ioc_list_panel = wx.Panel(vsplitter)
        ioc_list_panel.SetBackgroundColour("#ffffff")

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.init_ioc_list_ctrl(ioc_list_panel)
        hbox.Add(self.ioc_list_ctrl, 1, wx.EXPAND)
        ioc_list_panel.SetSizer(hbox)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)

        return ioc_list_panel

    def init_ioc_metadata_panel(self, hsplitter):
        ioc_metadata_panel = wx.Panel(hsplitter)
        ioc_metadata_panel.SetBackgroundColour("#cccccc")
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        #UUID Label
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.ioc_uuid_view = wx.StaticText(ioc_metadata_panel, label="uuid")
        self.ioc_uuid_view.Font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        hbox1.Add(self.ioc_uuid_view)
        
        vbox.Add(hbox1, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)

        #Name/Created
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(2,4,10,5)

        ioc_name_label = wx.StaticText(ioc_metadata_panel, label="Name:")
        ioc_created_label = wx.StaticText(ioc_metadata_panel, label="Created:")
        ioc_author_label = wx.StaticText(ioc_metadata_panel, label="Author:")
        ioc_modified_label = wx.StaticText(ioc_metadata_panel, label="Modified:")
  
        self.ioc_created_view = wx.StaticText(ioc_metadata_panel, label="XXXTXX:XX:XX")
        self.ioc_modified_view = wx.StaticText(ioc_metadata_panel, label="XX-XX-XXX:XX:XX")
  
        self.ioc_name_view = wx.TextCtrl(ioc_metadata_panel)
        self.ioc_author_view = wx.TextCtrl(ioc_metadata_panel)
  
        fgs.AddMany([(ioc_name_label), (self.ioc_name_view, 1, wx.EXPAND), (ioc_created_label,0,wx.LEFT,10), (self.ioc_created_view), (ioc_author_label), (self.ioc_author_view,1,wx.EXPAND), (ioc_modified_label,0,wx.LEFT,10), (self.ioc_modified_view)])
        fgs.AddGrowableCol(1)
        hbox2.Add(fgs, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.BOTTOM, border=10)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.ioc_desc_view = wx.TextCtrl(ioc_metadata_panel, size = (0,75), style=wx.TE_MULTILINE)
        hbox3.Add(self.ioc_desc_view, proportion=1)
        vbox.Add(hbox3, flag=wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
       
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        self.ioc_links_view = wx.ListCtrl(ioc_metadata_panel, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.ioc_links_view.InsertColumn(0, 'Key')
        self.ioc_links_view.InsertColumn(1, 'Value')
        self.ioc_links_view.InsertColumn(2, 'HREF', width=225)
        hbox4.Add(self.ioc_links_view, proportion=1, flag=wx.RIGHT|wx.EXPAND, border=5)
        

        hbox4_vbox = wx.BoxSizer(wx.VERTICAL)
        self.ioc_addlink_button = wx.Button(ioc_metadata_panel, label='+', size=(25, 25))
        hbox4_vbox.Add(self.ioc_addlink_button)
        self.ioc_dellink_button = wx.Button(ioc_metadata_panel, label='-', size=(25, 25))
        hbox4_vbox.Add(self.ioc_dellink_button)
        hbox4.Add(hbox4_vbox)       

        vbox.Add(hbox4, proportion=1, flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=10)

        ioc_metadata_panel.SetSizer(vbox)
        return ioc_metadata_panel

    def init_ioc_indicator_panel(self, hsplitter):
        ioc_indicator_panel = wx.Panel(hsplitter)
        ioc_indicator_panel.SetBackgroundColour("#ccffcc")
        vbox = wx.BoxSizer(wx.VERTICAL)
        st1 = wx.StaticText(ioc_indicator_panel, label="ioc indicator", style=wx.ALIGN_CENTRE)
        vbox.Add(st1, flag=wx.ALL, border=5)
        ioc_indicator_panel.SetSizer(vbox)
        return ioc_indicator_panel

    def init_panes(self):
        vsplitter = wx.SplitterWindow(self, size=(500,500))
        hsplitter = wx.SplitterWindow(vsplitter)

        ioc_list_panel = self.init_ioc_list_panel(vsplitter)
        ioc_metadata_panel = self.init_ioc_metadata_panel(hsplitter)
        ioc_indicator_panel = self.init_ioc_indicator_panel(hsplitter)

        vsplitter.SplitVertically(ioc_list_panel, hsplitter)
        hsplitter.SplitHorizontally(ioc_metadata_panel, ioc_indicator_panel)
    
    def init_ui(self):    
        self.init_menubar()
        self.init_toolbar()
        self.init_statusbar()
        self.init_panes()

        self.SetSize((800, 600))
        self.SetTitle('PyIOCe')
        self.Center()
        self.Show()
        
    def init_data(self):
        self.ioc_list = IOCList()
        self.current_ioc = "Empty IOC Object"
        self.metadata_panel_short_desc = ""
        self.metadata_panel_author = ""
        self.metadata_panel_created = ""
        self.metadata_panel_modified = ""
        self.metadata_panel_description = ""
        self.metadata_panel_keys = ""
        self.editor_panel_indicator_xml = ""

    def on_quit(self, e):
        self.Close()

    def on_open(self, e):
        self.Close()

    def on_about(self, e):
        self.Close()

    def on_select(self, e):
        self.ioc_list_ctrl.index = e.m_itemIndex
        ioc_index = self.ioc_list_ctrl.GetItemData(e.m_itemIndex)
        uuid = self.ioc_list_ctrl.itemDataMap[ioc_index][1]
        self.current_ioc = self.ioc_list.iocs[uuid]

    def on_new(self, e):
        self.Close()

    def on_save(self, e):
        self.Close()

    def on_saveall(self, e):
        self.Close()

    def on_case(self, e):
        self.Close()

    def on_not(self, e):
        self.Close()

    def on_and(self, e):
        self.Close()

    def on_or(self, e):
        self.Close()

    def on_add(self, e):
        self.Close()

    def on_remove(self, e):
        self.Close()

if __name__ == '__main__':
    app = wx.App()

    PyIOCe(None)
    
    app.MainLoop()
