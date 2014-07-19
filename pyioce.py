#!/usr/bin/python


import wx
from wx.lib.mixins.listctrl import ColumnSorterMixin
from ioc import *
from lxml import etree as et
import wx.lib.scrolledpanel as sp

class PyIOCeHelpMenu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)
        self.help_about = self.Append(wx.ID_ABOUT,   "&About PyIOCe")

class PyIOCeFileMenu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)
        self.file_open = self.Append(wx.ID_FILE, '&Open')

class PyIOCeMenuBar(wx.MenuBar):
    def __init__(self):
        wx.MenuBar.__init__(self)
        
        self.file_menu = PyIOCeFileMenu()
        self.help_menu = PyIOCeHelpMenu()

        self.Append(self.file_menu, '&File')
        self.Append(self.help_menu, '&Help')

class IOCTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent, -1)

        self.root_item_id = None
    
    def is_descendent(self, dst_item_id, src_item_id):
        if dst_item_id == self.root_item_id:
            return False
        dst_item_parent_id = self.GetItemParent(dst_item_id)
        if dst_item_parent_id == src_item_id:
            return True
        else:
            return self.is_descendent(dst_item_parent_id, src_item_id)

    def build_tree(self, parent, parent_id):
        for child in parent:
            if child.tag.startswith("Indicator"):
                if child.tag == "Indicator":
                    label = child.get('operator')
                if child.tag == "IndicatorItem":
                    context = child.find('Context')
                    content = child.find('Content')
                    label = context.get('type') + ":" + context.get('search') + " " + child.get('condition') + " " + content.text
                child_id = self.AppendItem(parent_id, label, data=wx.TreeItemData(child))
                self.build_tree(child, child_id)

    def init_tree(self, criteria):        
        indicator = criteria.find('Indicator')

        self.clear_tree()
        self.root_item_id = self.AddRoot(indicator.get('operator'), data=wx.TreeItemData(indicator))

        self.build_tree(indicator, self.root_item_id)

        self.ExpandAll()

    def clear_tree(self):        
        if self.root_item_id != None:
            self.DeleteAllItems()
  

    def save_branch(self,node, depth = 0):
        item = {}
        item['label'] = self.GetItemText(node)
        item['data'] = self.GetItemPyData(node)
        item['was-expanded'] = self.IsExpanded(node)
        item['children'] = []
        
        children = self.GetChildrenCount(node, False)
        child, cookie = self.GetFirstChild(node)
        for i in xrange(children):
            item['children'].append(self.save_branch(child, depth + 1))
            child, cookie = self.GetNextChild(node, cookie)

        if depth == 0:
            return [item]
        else:
            return item


    def insert_branch(self, branch, dst_item_id, after_item_id=None, top_level=True):
        expanded_item_list = []
        for item in branch:
            if after_item_id:
                insert_item_id = self.InsertItem(dst_item_id, after_item_id, item['label'])
                if top_level:
                    dst_item_element = self.GetItemData(dst_item_id).GetData()
                    after_item_element = self.GetItemData(after_item_id).GetData()
                    item_element = item['data']
                    dst_item_element.insert(dst_item_element.index(after_item_element)+1,item_element)
            else:
                insert_item_id = self.AppendItem(dst_item_id, item['label'])
                if top_level:
                    dst_item_element = self.GetItemData(dst_item_id).GetData()
                    item_element = item['data']
                    dst_item_element.append(item_element)

            self.SetItemPyData(insert_item_id, item['data'])

            if item['was-expanded'] == True:
                expanded_item_list.append(insert_item_id)

            if 'children' in item:
                expanded_children_list = self.insert_branch(item['children'], insert_item_id, top_level=False)
                expanded_item_list = expanded_item_list + expanded_children_list
        if top_level:
            return (insert_item_id, expanded_item_list)
        else:
            return expanded_item_list

class IOCListCtrl(wx.ListCtrl, ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        ColumnSorterMixin.__init__(self, 3)

        self.itemDataMap = {}
        
    def GetListCtrl(self): #FIXME
        return self

    def update(self,ioc_list):

        self.DeleteAllItems()
        # self.index = 0 #FIXME

        for ioc_file in ioc_list.iocs:
            index = len(self.itemDataMap)
            
            ioc_name = ioc_list.iocs[ioc_file].get_name()
            ioc_uuid = ioc_list.iocs[ioc_file].get_uuid()
            ioc_modified = ioc_list.iocs[ioc_file].get_modified()
            ioc_version = ioc_list.iocs[ioc_file].version

            self.itemDataMap[index] = (ioc_name, ioc_uuid, ioc_modified, ioc_file)

            self.InsertStringItem(index, " " + ioc_name)
            self.SetStringItem(index, 1, " " + ioc_uuid)
            self.SetStringItem(index, 2, " " + ioc_version)
            self.SetStringItem(index, 3, ioc_modified)
            self.SetItemData(index, index)

            if et.tostring(ioc_list.iocs[ioc_file].working_xml) == et.tostring(ioc_list.iocs[ioc_file].orig_xml):
                self.SetItemTextColour(index, wx.BLACK)
            else:
                self.SetItemTextColour(index, wx.RED)

    def add(self, ioc_list, ioc_file):
        index = len(self.itemDataMap)

        ioc_name = ioc_list.iocs[ioc_file].get_name()
        ioc_uuid = ioc_list.iocs[ioc_file].get_uuid()
        ioc_modified = ioc_list.iocs[ioc_file].get_modified()
        ioc_version = ioc_list.iocs[ioc_file].version
       
        self.itemDataMap[index] = (ioc_name, ioc_uuid, ioc_modified, ioc_file)

        self.InsertStringItem(index, " " + ioc_name)
        self.SetStringItem(index, 1, " " + ioc_uuid)
        self.SetStringItem(index, 2, " " + ioc_version)
        self.SetStringItem(index, 3, ioc_modified)
        self.SetItemData(index, index)
        self.SetItemTextColour(index, wx.RED)

        return index

class IOCListPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.ioc_list_ctrl = IOCListCtrl(self)
        self.ioc_list_ctrl.InsertColumn(0, 'Name', width=140)
        self.ioc_list_ctrl.InsertColumn(1, 'UUID', width=130)
        self.ioc_list_ctrl.InsertColumn(2, 'Version', width=50)
        self.ioc_list_ctrl.InsertColumn(3, 'Modified', wx.LIST_FORMAT_RIGHT, 90)

        hbox.Add(self.ioc_list_ctrl, 1, flag = wx.EXPAND)
        self.SetSizer(hbox)

class IOCMetadataPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        self.SetBackgroundColour("#cccccc")
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        #UUID Label
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.ioc_uuid_view = wx.StaticText(self, label="")
        self.ioc_uuid_view.Font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        hbox1.Add(self.ioc_uuid_view)
        
        vbox.Add(hbox1, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)

        #Name/Created
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(2,4,10,5)

        ioc_name_label = wx.StaticText(self, label="Name:")
        ioc_created_label = wx.StaticText(self, label="Created:")
        ioc_author_label = wx.StaticText(self, label="Author:")
        ioc_modified_label = wx.StaticText(self, label="Modified:")
  
        self.ioc_created_view = wx.StaticText(self)
        self.ioc_modified_view = wx.StaticText(self)
  
        self.ioc_name_view = wx.TextCtrl(self)
        self.ioc_author_view = wx.TextCtrl(self)
  
        fgs.AddMany([(ioc_name_label), (self.ioc_name_view, 1, wx.EXPAND), (ioc_created_label,0,wx.LEFT,10), (self.ioc_created_view), (ioc_author_label), (self.ioc_author_view,1,wx.EXPAND), (ioc_modified_label,0,wx.LEFT,10), (self.ioc_modified_view)])
        fgs.AddGrowableCol(1)
        hbox2.Add(fgs, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.BOTTOM, border=10)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.ioc_desc_view = wx.TextCtrl(self, size = (0,75), style=wx.TE_MULTILINE)
        hbox3.Add(self.ioc_desc_view, proportion=1)
        vbox.Add(hbox3, flag=wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
       
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        self.ioc_links_view = wx.ListCtrl(self, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.ioc_links_view.InsertColumn(0, 'Key')
        self.ioc_links_view.InsertColumn(1, 'Value')
        self.ioc_links_view.InsertColumn(2, 'HREF', width=225)
        hbox4.Add(self.ioc_links_view, proportion=1, flag=wx.RIGHT|wx.EXPAND, border=5)
        

        hbox4_vbox = wx.BoxSizer(wx.VERTICAL)
        self.ioc_addlink_button = wx.Button(self, label='+', size=(25, 25))
        hbox4_vbox.Add(self.ioc_addlink_button)
        self.ioc_dellink_button = wx.Button(self, label='-', size=(25, 25))
        hbox4_vbox.Add(self.ioc_dellink_button)
        hbox4.Add(hbox4_vbox)       

        vbox.Add(hbox4, proportion=1, flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=10)

        self.SetSizer(vbox)

    def update(self, current_ioc):
        #FIXME
        if current_ioc != None:
            self.ioc_uuid_view.SetLabelText(current_ioc.get_uuid())
            self.ioc_created_view.SetLabelText(current_ioc.get_created())
            self.ioc_modified_view.SetLabelText(current_ioc.get_modified())

            self.ioc_author_view.SetLabelText(current_ioc.get_author())
            self.ioc_name_view.SetValue(current_ioc.get_name())
            self.ioc_desc_view.SetValue(current_ioc.get_desc()) #FIXME

             # self.ioc_links_view = wx.ListCtrl(ioc_metadata_panel, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        else:
            self.ioc_uuid_view.SetLabelText("")
            self.ioc_created_view.SetLabelText("")
            self.ioc_modified_view.SetLabelText("")

            self.ioc_author_view.SetValue("")
            self.ioc_name_view.SetValue("")
            self.ioc_desc_view.SetValue("") #FIXME
 

            # self.ioc_links_view = wx.ListCtrl(ioc_metadata_panel, style=wx.LC_REPORT|wx.BORDER_SUNKEN)

class IOCIndicatorPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent)
   
        accel_table = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL,  ord('c'), 4),
            (wx.ACCEL_NORMAL,  ord('n'), 5),
            (wx.ACCEL_NORMAL,  ord('a'), 6),
            (wx.ACCEL_NORMAL,  ord('o'), 7),
            (wx.ACCEL_NORMAL,  ord('i'), 8),
            (wx.ACCEL_NORMAL,  ord('d'), 9)
                              ])
        self.SetAcceleratorTable(accel_table)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.ioc_tree_ctrl = IOCTreeCtrl(self)
        self.ioc_tree_ctrl.SetBackgroundColour("#ccffcc")
        vbox.Add(self.ioc_tree_ctrl, proportion=1, flag=wx.EXPAND)
        self.SetSizer(vbox)

    def update(self, current_ioc):
        if current_ioc != None:
            self.ioc_tree_ctrl.init_tree(current_ioc.criteria)
        else:
            self.ioc_tree_ctrl.clear_tree()

class IOCXMLPage(sp.ScrolledPanel):
    def __init__(self, parent):
        sp.ScrolledPanel.__init__(self, parent, size=(800,800)) #FIXME

        self.SetBackgroundColour("#e8e8e8")
        self.SetupScrolling()
        self.AlwaysShowScrollbars(horz=True, vert=True)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.ioc_xml_view = wx.StaticText(self, label="No IOC Selected", style=wx.ALIGN_LEFT|wx.TE_MULTILINE)
        vbox.Add(self.ioc_xml_view, flag=wx.ALL, border=5)
        self.SetSizer(vbox)

    def update(self, current_ioc):
        if current_ioc != None:
            xml_view_string = et.tostring(current_ioc.working_xml, encoding="utf-8", xml_declaration=True, pretty_print = True)
            
        else:
            xml_view_string = "No IOC Selected"
        self.ioc_xml_view.SetLabel(xml_view_string)

class IOCNotebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self,parent)
        
        self.ioc_xml_page = IOCXMLPage(self)
        self.ioc_indicator_page = IOCIndicatorPage(self)

        self.AddPage(self.ioc_indicator_page, "IOC")
        self.AddPage(self.ioc_xml_page, "XML")
        
class PyIOCe(wx.Frame):

#
#   Initialize all views and variables
#
    def __init__(self, *args, **kwargs):
        super(PyIOCe, self).__init__(*args, **kwargs) 
            
        self.ioc_list = IOCList()
        self.current_ioc = None

        self.init_menubar()
        self.init_toolbar()
        self.init_statusbar()
        self.init_panes()

        self.SetSize((800, 600))
        self.SetTitle('PyIOCe')
        self.Center()
        self.Show()


    def init_menubar(self):
        menubar = PyIOCeMenuBar()
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.on_about, menubar.help_menu.help_about)
        self.Bind(wx.EVT_MENU, self.on_open, menubar.file_menu.file_open)  

    def init_toolbar(self):
        toolbar = self.CreateToolBar()

        self.toolbar_search = wx.TextCtrl(toolbar, size=(200,0))
        toolbar_search_label = wx.StaticText(toolbar, label="Search:")

        toolbar.AddSimpleTool(1, wx.Image('./images/new.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'New', '')
        toolbar.AddSimpleTool(10, wx.Image('./images/open.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Open Dir', '')
        toolbar.AddSimpleTool(2, wx.Image('./images/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save', '')
        toolbar.AddSimpleTool(3, wx.Image('./images/saveall.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save All', '')
        
        toolbar.AddSeparator()
        toolbar.AddSeparator()
        toolbar.AddStretchableSpace()
        toolbar.AddControl(toolbar_search_label)
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

    def init_panes(self):
        vsplitter = wx.SplitterWindow(self, size=(500,500), style = wx.SP_LIVE_UPDATE | wx.SP_3D)
        hsplitter = wx.SplitterWindow(vsplitter, style = wx.SP_LIVE_UPDATE | wx.SP_3D)

        self.ioc_list_panel = IOCListPanel(vsplitter)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_ioc_select)

        self.ioc_metadata_panel = IOCMetadataPanel(hsplitter)

        self.ioc_notebook_panel = IOCNotebook(hsplitter)

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_page_changing)

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self.on_end_drag)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activated)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_indicator_select)


        vsplitter.SplitVertically(self.ioc_list_panel, hsplitter)
        hsplitter.SplitHorizontally(self.ioc_metadata_panel, self.ioc_notebook_panel)

#
#  Update Displays
#

    def update_status_bar(self, status_text="No IOC Selected"):
        self.statusbar.SetStatusText(status_text)

    def select_dir(self):
        selected_dir = None

        select_dir_dialog = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)

        if select_dir_dialog.ShowModal() == wx.ID_OK:
            selected_dir = select_dir_dialog.GetPath()
            
        select_dir_dialog.Destroy()

        return selected_dir

    def on_quit(self, event):
        self.Close()

    def on_open(self, event):
        selected_dir = self.select_dir()
        if selected_dir is not None:
            self.ioc_list.open_ioc_path(selected_dir)
            self.ioc_list_panel.ioc_list_ctrl.update(self.ioc_list)
            self.ioc_list_panel.ioc_list_ctrl.Select(0, on=True)


    def on_about(self, event):
        self.Close()

    def on_ioc_select(self, event):
        # self.ioc_list_ctrl.index = e.m_itemIndex  #FIXME
        ioc_index = self.ioc_list_panel.ioc_list_ctrl.GetItemData(event.m_itemIndex)
        ioc_file = self.ioc_list_panel.ioc_list_ctrl.itemDataMap[ioc_index][3]
        self.current_ioc = self.ioc_list.iocs[ioc_file]
        self.ioc_metadata_panel.update(self.current_ioc)
        self.ioc_notebook_panel.ioc_indicator_page.update(self.current_ioc)
        self.ioc_notebook_panel.ioc_xml_page.update(self.current_ioc)
        self.update_status_bar(ioc_file)

    def on_new(self, event):
        if self.ioc_list.working_dir == None:
            selected_dir = self.select_dir()
            if selected_dir is not None:
                self.ioc_list.open_ioc_path(selected_dir)
                self.ioc_list_panel.ioc_list_ctrl.update(self.ioc_list)
            else:
                return

        ioc_file = self.ioc_list.add()
        self.current_ioc = self.ioc_list.iocs[ioc_file]
        new_ioc_index = self.ioc_list_panel.ioc_list_ctrl.add(self.ioc_list, ioc_file)
        self.ioc_list_panel.ioc_list_ctrl.Select(new_ioc_index, on=True)

        self.ioc_metadata_panel.update(self.current_ioc)
        self.ioc_notebook_panel.ioc_indicator_page.update(self.current_ioc)
        self.ioc_notebook_panel.ioc_xml_page.update(self.current_ioc)
        self.update_status_bar(ioc_file)

    def on_save(self, event):
        self.Close()

    def on_saveall(self, event):
        self.Close()

    def on_case(self, event):
        print "case"

    def on_not(self, event):
        print "not"

    def on_and(self, event):
        print "and"

    def on_or(self, event):
        print "or"

    def on_insert(self, event):
        print "insert"
        # print self.ioc_indicator_tree.selected_item

    def on_delete(self, event):
        print "delete"

    def on_page_changing(self, event):
        self.ioc_notebook_panel.ioc_indicator_page.update(self.current_ioc)
        self.ioc_notebook_panel.ioc_xml_page.update(self.current_ioc)

    def on_indicator_select(self, event):
        self.current_indicator_id = event.GetItem()

    def on_activated(self, event):
        ioc_tree_ctrl = self.ioc_notebook_panel.ioc_indicator_page.ioc_tree_ctrl
        item_id = event.GetItem()

        item_tag = ioc_tree_ctrl.GetItemData(item_id).GetData().tag
        if item_tag == "Indicator":
            if ioc_tree_ctrl.IsExpanded(item_id):
                ioc_tree_ctrl.Collapse(item_id)
            else:
                ioc_tree_ctrl.Expand(item_id)
        elif item_tag == "IndicatorItem":
            print "Open Dialog" #FIXME

    def on_begin_drag(self, event):
        ioc_tree_ctrl = self.ioc_notebook_panel.ioc_indicator_page.ioc_tree_ctrl
        item_id = event.GetItem()

        if item_id != ioc_tree_ctrl.GetRootItem():
            self.current_indicator_id = item_id
            event.Allow()

    def on_end_drag(self, event):
        ioc_tree_ctrl = self.ioc_notebook_panel.ioc_indicator_page.ioc_tree_ctrl
        src_item_id = self.current_indicator_id
        dst_item_id = event.GetItem()

        after_item_id = None
        self.current_indicator_id = None

        if not dst_item_id.IsOk():
            return

        # Prevent move to own descendent
        if ioc_tree_ctrl.is_descendent(dst_item_id, src_item_id):
            return
        # Prevent move to self
        if src_item_id == dst_item_id:
            return

        # If moving to IndicatorIndicator item find set positioning and set destination to parent
        if ioc_tree_ctrl.GetItemData(dst_item_id).GetData().tag == "IndicatorItem":
            after_item_id = dst_item_id
            dst_item_id = ioc_tree_ctrl.GetItemParent(dst_item_id)
    
    
        branch = ioc_tree_ctrl.save_branch(src_item_id)
        ioc_tree_ctrl.Delete(src_item_id)
        
        #Insert branch returning list of items that need to be expanded after move
        self.current_indicator_id, expanded_item_list = ioc_tree_ctrl.insert_branch(branch, dst_item_id, after_item_id)
        
        for expand_item_id in expanded_item_list:
            self.Expand(expand_item_id)

        ioc_tree_ctrl.SelectItem(self.current_indicator_id)
        self.ioc_list_panel.ioc_list_ctrl.update(self.ioc_list)


if __name__ == '__main__':
    app = wx.App()

    PyIOCe(None)

    app.MainLoop()
