#!/usr/bin/python


import wx
from wx.lib.mixins.listctrl import ColumnSorterMixin
from ioc import *
from lxml import etree as et
import wx.lib.scrolledpanel as sp

class IOCListCtrl(wx.ListCtrl, ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ColumnSorterMixin.__init__(self, 3)
        
    def GetListCtrl(self):
        return self

class PyIOCe(wx.Frame):

#
#   Initialize all views and variables
#
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

        toolbar.AddSimpleTool(1, wx.Image('./images/new.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'New', '')
        toolbar.AddSimpleTool(10, wx.Image('./images/open.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Open Dir', '')
        toolbar.AddSimpleTool(2, wx.Image('./images/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save', '')
        toolbar.AddSimpleTool(3, wx.Image('./images/saveall.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save All', '')
        
        toolbar.AddSeparator()
        toolbar.AddSeparator()
        toolbar.AddStretchableSpace()
        toolbar.AddControl(self.toolbar_search,'Search')
        toolbar.AddStretchableSpace()
        toolbar.AddSimpleTool(4, wx.Image('./images/case.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Case', '')
        toolbar.AddSimpleTool(5, wx.Image('./images/lnot.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Not', '')
        toolbar.AddSimpleTool(6, wx.Image('./images/land.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'And', '')
        toolbar.AddSimpleTool(7, wx.Image('./images/lor.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Or', '')
        toolbar.AddSimpleTool(8, wx.Image('./images/insert.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Add Item', '')
        toolbar.AddSimpleTool(9, wx.Image('./images/delete.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Remove Item', '')


        toolbar.Realize()
 
        self.Bind(wx.EVT_TOOL, self.on_new, id=1)
        self.Bind(wx.EVT_TOOL, self.on_save, id=2)
        self.Bind(wx.EVT_TOOL, self.on_saveall, id=3)
        self.Bind(wx.EVT_TOOL, self.on_case, id=4)
        self.Bind(wx.EVT_TOOL, self.on_not, id=5)
        self.Bind(wx.EVT_TOOL, self.on_and, id=6)
        self.Bind(wx.EVT_TOOL, self.on_or, id=7)
        self.Bind(wx.EVT_TOOL, self.on_insert, id=8)
        self.Bind(wx.EVT_TOOL, self.on_delete, id=9)
        self.Bind(wx.EVT_TOOL, self.on_open, id=10)


    def init_statusbar(self):
        self.statusbar = self.CreateStatusBar()
        self.update_status_bar()

    def init_ioc_list_panel(self, vsplitter):
        ioc_list_panel = wx.Panel(vsplitter)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.ioc_list_ctrl = IOCListCtrl(ioc_list_panel)
        self.ioc_list_ctrl.InsertColumn(0, 'Name', width=140)
        self.ioc_list_ctrl.InsertColumn(1, 'UUID', width=130)
        self.ioc_list_ctrl.InsertColumn(2, 'Modified', wx.LIST_FORMAT_RIGHT, 90)

        hbox.Add(self.ioc_list_ctrl, 1, flag = wx.EXPAND)
        ioc_list_panel.SetSizer(hbox)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)

        return ioc_list_panel

    def init_ioc_metadata_panel(self, hsplitter):
        ioc_metadata_panel = wx.Panel(hsplitter)
        ioc_metadata_panel.SetBackgroundColour("#cccccc")
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        #UUID Label
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.ioc_uuid_view = wx.StaticText(ioc_metadata_panel, label="")
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
  
        self.ioc_created_view = wx.StaticText(ioc_metadata_panel, label="")
        self.ioc_modified_view = wx.StaticText(ioc_metadata_panel, label="")
  
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

    def init_ioc_indicator_page(self, ioc_notebook):
        ioc_indicator_panel = wx.Panel(ioc_notebook)
        ioc_indicator_panel.SetBackgroundColour("#ccffcc")

        accel_table = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL,  ord('c'), 4),
            (wx.ACCEL_NORMAL,  ord('n'), 5),
            (wx.ACCEL_NORMAL,  ord('a'), 6),
            (wx.ACCEL_NORMAL,  ord('o'), 7),
            (wx.ACCEL_NORMAL,  ord('i'), 8),
            (wx.ACCEL_NORMAL,  ord('d'), 9)
                              ])
        ioc_indicator_panel.SetAcceleratorTable(accel_table)






        return ioc_indicator_panel

    def init_ioc_xml_page(self, ioc_notebook):
        ioc_xml_panel = sp.ScrolledPanel(ioc_notebook, size=(800, 800))
        ioc_xml_panel.SetBackgroundColour("#e8e8e8")
        ioc_xml_panel.SetupScrolling()
        ioc_xml_panel.AlwaysShowScrollbars(horz=True, vert=True)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.ioc_xml_view = wx.StaticText(ioc_xml_panel, label="No IOC Selected", style=wx.ALIGN_LEFT|wx.TE_MULTILINE)
        vbox.Add(self.ioc_xml_view, flag=wx.ALL, border=5)
        ioc_xml_panel.SetSizer(vbox)

        return ioc_xml_panel

    def init_ioc_notebook(self, hsplitter):
        ioc_notebook = wx.Notebook(hsplitter)
        ioc_notebook.AddPage(self.init_ioc_indicator_page(ioc_notebook), "IOC")
        ioc_notebook.AddPage(self.init_ioc_xml_page(ioc_notebook), "XML")
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_page_changing)

        return ioc_notebook

    def init_panes(self):
        vsplitter = wx.SplitterWindow(self, size=(500,500), style = wx.SP_LIVE_UPDATE | wx.SP_3D)
        hsplitter = wx.SplitterWindow(vsplitter, style = wx.SP_LIVE_UPDATE |wx.SP_3D)

        ioc_list_panel = self.init_ioc_list_panel(vsplitter)
        ioc_metadata_panel = self.init_ioc_metadata_panel(hsplitter)
        ioc_notebook = self.init_ioc_notebook(hsplitter)

        vsplitter.SplitVertically(ioc_list_panel, hsplitter)
        hsplitter.SplitHorizontally(ioc_metadata_panel, ioc_notebook)
    
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
        self.current_ioc = None
        self.metadata_panel_short_desc = ""
        self.metadata_panel_author = ""
        self.metadata_panel_created = ""
        self.metadata_panel_modified = ""
        self.metadata_panel_description = ""
        self.metadata_panel_keys = ""
        self.editor_panel_indicator_xml = ""

#
#  Update Displays
#

    def update_ioc_list_panel(self):

        self.ioc_list_ctrl.DeleteAllItems()
        self.ioc_list_ctrl.itemDataMap = {}
        # self.ioc_list_ctrl.index = 0 #FIXME

        for ioc in self.ioc_list.iocs:
            index = len(self.ioc_list_ctrl.itemDataMap)
            
            ioc_name = self.ioc_list.iocs[ioc].get_name()
            ioc_uuid = self.ioc_list.iocs[ioc].get_uuid()
            ioc_modified = self.ioc_list.iocs[ioc].get_modified()

            self.ioc_list_ctrl.itemDataMap[index] = (ioc_name, ioc_uuid, ioc_modified, ioc)

            self.ioc_list_ctrl.InsertStringItem(index, " "+ioc_name)
            self.ioc_list_ctrl.SetStringItem(index, 1, " "+ioc_uuid)
            self.ioc_list_ctrl.SetStringItem(index, 2, ioc_modified)
            self.ioc_list_ctrl.SetItemData(index, index)

    def update_ioc_indicator_page(self):
        pass
    
    def update_ioc_xml_page(self):
        if self.current_ioc == None:
            xml_view_string = "No IOC Selected"
        else:
            xml_view_string = et.tostring(self.current_ioc.working_xml)
        self.ioc_xml_view.SetLabel(xml_view_string)

    def update_ioc_metadata_panel(self):
        #FIXME
        self.ioc_author_view.SetLabel("FIXME")
        self.ioc_name_view.SetLabel("FIXME")
        self.ioc_desc_view.SetLabel("FIXME")

        self.ioc_uuid_view.SetLabel(self.current_ioc.get_uuid())
        self.ioc_created_view.SetLabel(self.current_ioc.get_created())
        self.ioc_modified_view.SetLabel(self.current_ioc.get_modified())
        self.ioc_author_view.SetLabel(self.current_ioc.get_author())
        self.ioc_name_view.SetLabel(self.current_ioc.get_name())
        self.ioc_desc_view.SetLabel(self.current_ioc.get_desc())

        # self.ioc_links_view = wx.ListCtrl(ioc_metadata_panel, style=wx.LC_REPORT|wx.BORDER_SUNKEN)

    def update_status_bar(self, status_text="No IOC Selected"):
        self.statusbar.SetStatusText(status_text)

    def select_dir(self):
        selected_dir = None

        select_dir_dialog = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)

        if select_dir_dialog.ShowModal() == wx.ID_OK:
            selected_dir = select_dir_dialog.GetPath()
            
        select_dir_dialog.Destroy()

        return selected_dir

    def on_quit(self, e):
        self.Close()

    def on_open(self, e):
        selected_dir = self.select_dir()
        if selected_dir is not None:
            self.ioc_list.open_ioc_path(selected_dir)
            self.current_ioc = None
            self.update_ioc_list_panel()
            self.update_ioc_metadata_panel()
            self.update_ioc_indicator_page()
            self.update_ioc_xml_page()
            self.update_status_bar(ioc_file)

    def on_about(self, e):
        self.Close()

    def on_select(self, e):
        # self.ioc_list_ctrl.index = e.m_itemIndex  #FIXME
        ioc_index = self.ioc_list_ctrl.GetItemData(e.m_itemIndex)
        ioc_file = self.ioc_list_ctrl.itemDataMap[ioc_index][3]
        self.current_ioc = self.ioc_list.iocs[ioc_file]
        self.update_ioc_metadata_panel()
        self.update_ioc_indicator_page()
        self.update_ioc_xml_page()
        self.update_status_bar(ioc_file)

    def on_new(self, e):
        self.Close()

    def on_save(self, e):
        self.Close()

    def on_saveall(self, e):
        self.Close()

    def on_case(self, e):
        print "case"

    def on_not(self, e):
        print "not"

    def on_and(self, e):
        print "and"

    def on_or(self, e):
        print "or"

    def on_insert(self, e):
        print "insert"

    def on_delete(self, e):
        print "delete"

    def on_page_changing(self, e):
        self.update_ioc_indicator_page()
        self.update_ioc_xml_page()

if __name__ == '__main__':
    app = wx.App()

    PyIOCe(None)

    app.MainLoop()
