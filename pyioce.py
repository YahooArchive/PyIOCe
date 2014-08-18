#!/usr/bin/python

# Copyright 2014 Yahoo! Inc.  
# Licensed under the Apache 2.0 license.  Developed for Yahoo! by Sean Gillespie. 
#
# Yahoo! licenses this file to you under the Apache License, Version
# 2.0 (the "License"); you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

import wx
from wx.lib.mixins.listctrl import ColumnSorterMixin
from ioc import *
from lxml import etree as et
import wx.lib.scrolledpanel as sp
import ioc_et
import copy
import json
import re

class TermDialog(wx.Dialog):
    def __init__(self, parent, current_term_values):
        wx.Dialog.__init__(self, parent, -1, title="Edit Term", style=wx.DEFAULT_DIALOG_STYLE)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        
        fgs = wx.FlexGridSizer(1,2,0,0)
  
        self.context_doc = current_term_values["context_doc"]
        self.content_type = current_term_values["content_type"]

        self.context_doc_box = wx.TextCtrl(self)
        self.context_doc_box.SetValue(self.context_doc)

        self.content_type_box = wx.TextCtrl(self)
        self.content_type_box.SetValue(self.content_type)

        fgs.AddMany([(self.context_doc_box, 0), (self.content_type_box,0, wx.EXPAND)])

        hbox1.Add(fgs, proportion = 1, flag = wx.EXPAND | wx.LEFT| wx.RIGHT | wx.TOP , border=10)
        vbox.Add(hbox1, flag=wx.EXPAND| wx.ALIGN_CENTER)

        self.Bind(wx.EVT_TEXT, self.on_context_doc_change, self.context_doc_box)
        self.Bind(wx.EVT_TEXT, self.on_content_type_change, self.content_type_box)

        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()

        vbox.Add(button_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT| wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)

    def on_context_doc_change(self, event):
        self.context_doc = self.context_doc_box.GetValue()

    def on_content_type_change(self, event):
        self.content_type = self.content_type_box.GetValue()


class KeyDialog(wx.Dialog):
    def __init__(self, parent, key_type):
        title = "Add " + key_type

        wx.Dialog.__init__(self, parent, -1, title=title, style=wx.DEFAULT_DIALOG_STYLE)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
  
        self.key = ""
        self.key_box = wx.TextCtrl(self)
        self.key_box.SetValue(self.key)

        hbox1.Add(self.key_box, proportion = 1, flag = wx.EXPAND | wx.LEFT| wx.RIGHT | wx.TOP , border=10)
        vbox.Add(hbox1, flag=wx.EXPAND| wx.ALIGN_CENTER)

        self.Bind(wx.EVT_TEXT, self.on_key_change, self.key_box)

        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()

        vbox.Add(button_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT| wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)

    def on_key_change(self, event):
        self.key = self.key_box.GetValue()


class ContextListCtrl(wx.ListCtrl, ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        ColumnSorterMixin.__init__(self, 3)

        context_types = parent.indicator_terms.keys()

        self.InsertColumn(0, 'Context Type', width=85)
        self.update(context_types)

    def GetListCtrl(self):
        return self

    def update(self, context_types):

        self.DeleteAllItems()
        self.itemDataMap = {}

        for context_type in sorted(context_types):
            index = len(self.itemDataMap)

            self.itemDataMap[index] = (context_type)

            self.InsertStringItem(index, " " + context_type)
            self.SetItemData(index, index)


class TermListCtrl(wx.ListCtrl, ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        ColumnSorterMixin.__init__(self, 3)

        index = parent.context_list_ctrl.GetItemData(parent.current_context_id)
        current_context_type = parent.context_list_ctrl.itemDataMap[index]

        current_terms = parent.indicator_terms[current_context_type]

        self.InsertColumn(0, 'Search Term', width=350)
        self.InsertColumn(1, 'Context Document', width=150)
        self.InsertColumn(2, 'Content Type', width=100)
        self.InsertColumn(3, 'Last Modified', width=180)

        self.update(current_terms)
      
    def GetListCtrl(self):
        return self

    def update(self, current_terms):
        self.DeleteAllItems()
        self.itemDataMap = {}

        for term in sorted(current_terms.keys()):
            index = len(self.itemDataMap)

            search_term = term
            context_doc = current_terms[term]["context_doc"]
            content_type = current_terms[term]["content_type"]
            last_modified = current_terms[term]["last_modified"]


            self.itemDataMap[index] = (search_term, context_doc, content_type, last_modified)

            self.InsertStringItem(index, " " + search_term)
            self.SetStringItem(index, 1, " " + context_doc)
            self.SetStringItem(index, 2, " " + content_type)
            self.SetStringItem(index, 3, " " + last_modified)
            self.SetItemData(index, index)


class TermsDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title="Indicator Terms", style=wx.DEFAULT_DIALOG_STYLE)

        self.indicator_terms = copy.deepcopy(parent.indicator_terms)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        
        fgs = wx.FlexGridSizer(1,2,0,0)
  
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.context_list_ctrl = ContextListCtrl(self)
        hbox2.Add(self.context_list_ctrl, proportion = 1, flag=wx.EXPAND | wx.RIGHT, border=5)


        hbox2_vbox = wx.BoxSizer(wx.VERTICAL)
        addcontext_button = wx.Button(self, label='+', size=(25, 25))
        hbox2_vbox.Add(addcontext_button)
        delcontext_button = wx.Button(self, label='-', size=(25, 25))
        hbox2_vbox.Add(delcontext_button)
        hbox2.Add(hbox2_vbox)

        self.context_list_ctrl.Select(0, on=True)
        self.current_context_id = 0

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.term_list_ctrl = TermListCtrl(self)
        hbox3.Add(self.term_list_ctrl, proportion = 1, flag=wx.EXPAND | wx.RIGHT, border=5)


        hbox3_vbox = wx.BoxSizer(wx.VERTICAL)
        addterm_button = wx.Button(self, label='+', size=(25, 25))
        hbox3_vbox.Add(addterm_button)
        delterm_button = wx.Button(self, label='-', size=(25, 25))
        hbox3_vbox.Add(delterm_button)
        hbox3.Add(hbox3_vbox)


        fgs.AddMany([(hbox2, 0), (hbox3,0, wx.EXPAND | wx.ALIGN_RIGHT)])

        hbox1.Add(fgs, proportion = 1, flag = wx.EXPAND | wx.LEFT| wx.RIGHT | wx.TOP , border=10)
        vbox.Add(hbox1, flag=wx.EXPAND| wx.ALIGN_CENTER)


        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)

        reset_button = wx.Button(self, wx.ID_NO, label="Restore Defaults")
        button_sizer.AddButton(reset_button)

        button_sizer.Realize()

        vbox.Add(button_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT| wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)

        self.Bind(wx.EVT_BUTTON, self.on_context_del, delcontext_button)
        self.Bind(wx.EVT_BUTTON, self.on_context_add, addcontext_button)
        self.Bind(wx.EVT_BUTTON, self.on_term_del, delterm_button)
        self.Bind(wx.EVT_BUTTON, self.on_term_add, addterm_button)
        self.Bind(wx.EVT_BUTTON, self.on_reset, reset_button)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_context_select, self.context_list_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_term_select, self.term_list_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_term_activated, self.term_list_ctrl)
    
    def on_reset(self, event):
        indicator_terms_file = open(BASE_DIR + 'indicator_terms.default','r')
        self.indicator_terms = json.loads(indicator_terms_file.read())
        indicator_terms_file.close()
        context_types = self.indicator_terms.keys()
        self.context_list_ctrl.update(context_types)
        try:
            self.context_list_ctrl.Select(0, on=True)
        except:
            self.term_list_ctrl.update({})

    def on_context_add(self, event):
        context_dialog = KeyDialog(self, "Context Type")
        context_dialog.CenterOnScreen()
    
        if context_dialog.ShowModal() == wx.ID_OK:
            new_context_type = context_dialog.key
            if new_context_type != "" and new_context_type not in self.indicator_terms.keys():
                self.indicator_terms[new_context_type] = {}
                context_types = self.indicator_terms.keys()
                self.context_list_ctrl.update(context_types)

        context_dialog.Destroy()

    def on_context_del(self, event):
        index = self.context_list_ctrl.GetItemData(self.current_context_id)
        current_context_type = self.context_list_ctrl.itemDataMap[index]
        self.context_list_ctrl.DeleteItem(self.current_context_id)
        self.context_list_ctrl.itemDataMap.pop(index)
        self.indicator_terms.pop(current_context_type, None)
        try:
            self.context_list_ctrl.Select(0, on=True)
        except:
            self.term_list_ctrl.update({})

    def on_term_add(self, event):
        index = self.context_list_ctrl.GetItemData(self.current_context_id)
        current_context_type = self.context_list_ctrl.itemDataMap[index]
        term_dialog = KeyDialog(self, "Search Term")
        term_dialog.CenterOnScreen()
    
        if term_dialog.ShowModal() == wx.ID_OK:
            new_term = term_dialog.key
            if new_term != "" and new_term not in self.indicator_terms[current_context_type].keys():
                new_term_values = {}
                new_term_values["context_doc"] = "default"
                new_term_values["content_type"] = "string"
                new_term_values["last_modified"] = ioc_et.get_current_date()

                self.indicator_terms[current_context_type][new_term] = new_term_values

                current_terms = self.indicator_terms[current_context_type]
                self.term_list_ctrl.update(current_terms)

        term_dialog.Destroy()

    def on_term_del(self, event):
        index = self.context_list_ctrl.GetItemData(self.current_context_id)
        current_context_type = self.context_list_ctrl.itemDataMap[index]
        index = self.term_list_ctrl.GetItemData(self.current_term_id)
        current_term = self.term_list_ctrl.itemDataMap[index][0]
        self.term_list_ctrl.DeleteItem(self.current_term_id)
        self.term_list_ctrl.itemDataMap.pop(index)
        self.indicator_terms[current_context_type].pop(current_term, None)

    def on_context_select(self, event):
        self.current_context_id = event.m_itemIndex
        index = self.context_list_ctrl.GetItemData(self.current_context_id)
        current_context_type = self.context_list_ctrl.itemDataMap[index]
        current_terms = self.indicator_terms[current_context_type]
        self.term_list_ctrl.update(current_terms)

    def on_term_select(self, event):
        self.current_term_id = event.m_itemIndex

    def on_term_activated(self, event):
        index = self.context_list_ctrl.GetItemData(self.current_context_id)
        current_context_type = self.context_list_ctrl.itemDataMap[index]

        index = self.term_list_ctrl.GetItemData(self.current_term_id)
        current_term = self.term_list_ctrl.itemDataMap[index][0]

        current_term_values = self.indicator_terms[current_context_type][current_term]

        term_dialog = TermDialog(self, current_term_values)
        term_dialog.CenterOnScreen()
    
        if term_dialog.ShowModal() == wx.ID_OK:
            context_doc = term_dialog.context_doc
            content_type = term_dialog.content_type
            last_modified = ioc_et.get_current_date()

            new_term_values = {}
            new_term_values["context_doc"] = context_doc
            new_term_values["content_type"] = content_type
            new_term_values["last_modified"] = last_modified

            self.indicator_terms[current_context_type][current_term] = new_term_values

            self.term_list_ctrl.itemDataMap[index] = (current_term, context_doc, content_type, last_modified)
            self.term_list_ctrl.SetStringItem(self.current_term_id, 1, " " + context_doc)
            self.term_list_ctrl.SetStringItem(self.current_term_id, 2, " " + content_type)

        term_dialog.Destroy()


class PreferencesDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title="Preferences", style=wx.DEFAULT_DIALOG_STYLE)

        self.default_version = parent.preferences["default_version"]
        self.default_context = parent.preferences["default_context"]
        self.default_author = parent.preferences["default_author"]

        version_list = ["1.0", "1.1"]
        context_type_list = parent.indicator_terms.keys()

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        
        fgs = wx.FlexGridSizer(3,2,0,10)
  
        version_label = wx.StaticText(self, label="Default Version")
        self.version_box = wx.ComboBox(self, choices = version_list, style=wx.CB_READONLY)
        self.version_box.SetValue(self.default_version)

        context_label = wx.StaticText(self, label="Default Context")
        self.context_box = wx.ComboBox(self, choices = context_type_list, style=wx.CB_READONLY)
        self.context_box.SetValue(self.default_context)

        author_label = wx.StaticText(self, label="Default Author")
        self.author_box = wx.TextCtrl(self, size=(200,-1))
        self.author_box.SetValue(self.default_author)

        fgs.AddMany([(version_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT), (self.version_box,0, wx.ALIGN_CENTER_VERTICAL |wx.ALIGN_RIGHT),(context_label, 0, wx.ALIGN_CENTER_VERTICAL |wx.ALIGN_LEFT), (self.context_box,0, wx.ALIGN_CENTER_VERTICAL |wx.ALIGN_RIGHT),(author_label, 0, wx.ALIGN_CENTER_VERTICAL |wx.ALIGN_LEFT), (self.author_box,0, wx.ALIGN_CENTER_VERTICAL |wx.ALIGN_RIGHT)])

        hbox1.Add(fgs, proportion = 1, flag = wx.EXPAND | wx.LEFT| wx.RIGHT | wx.TOP , border=10)
        vbox.Add(hbox1, flag=wx.EXPAND| wx.ALIGN_CENTER)
        
        self.Bind(wx.EVT_COMBOBOX, self.on_version_change, self.version_box)
        self.Bind(wx.EVT_COMBOBOX, self.on_context_change, self.context_box)
        self.Bind(wx.EVT_TEXT, self.on_author_change, self.author_box)

        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()

        vbox.Add(button_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT| wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)

    
    def on_version_change(self, event):
        self.default_version = self.version_box.GetValue()

    def on_context_change(self, event):
        self.default_context = self.context_box.GetValue()

    def on_author_change(self, event):    
        self.default_author = self.author_box.GetValue()


class ParamDialog(wx.Dialog):
    def __init__(self, parent, param):
        wx.Dialog.__init__(self, parent, -1, title="Edit Parameter", style=wx.DEFAULT_DIALOG_STYLE)

        self.param = param

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        
        name_label = wx.StaticText(self, label="Name")
        value_label = wx.StaticText(self, label="Value")

        fgs = wx.FlexGridSizer(2,2,0,5)
  
        param_name = self.param.get('name')
        param_value = self.param.find('value').text

        self.name_box = wx.TextCtrl(self)
        self.name_box.SetValue(param_name)

        self.value_box = wx.TextCtrl(self, size=(200,-1))
        self.value_box.SetValue(param_value)

        fgs.AddMany([(name_label, 0), (value_label,0, wx.EXPAND),(self.name_box, 0), (self.value_box,0, wx.EXPAND)])

        hbox1.Add(fgs, proportion = 1, flag = wx.EXPAND | wx.LEFT| wx.RIGHT | wx.TOP , border=10)
        vbox.Add(hbox1, flag=wx.EXPAND| wx.ALIGN_CENTER)

        self.Bind(wx.EVT_TEXT, self.on_name_change, self.name_box)
        self.Bind(wx.EVT_TEXT, self.on_value_change, self.value_box)

        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()

        vbox.Add(button_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT| wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)

    def on_name_change(self, event):
        self.param.set('name', self.name_box.GetValue())

    def on_value_change(self, event):
        self.param.find('value').text = self.value_box.GetValue()


class LinkDialog(wx.Dialog):
    def __init__(self, parent, link_data, version):
        wx.Dialog.__init__(self, parent, -1, title="Edit Link", style=wx.DEFAULT_DIALOG_STYLE)

        rel_list = ["link", "report", "related", "category", "capability", "dependency", "caveat", "family"]

        self.link_rel, self.link_value, self.link_href = link_data


        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        
        rel_label = wx.StaticText(self, label="Key")
        value_label = wx.StaticText(self, label="Value")


        self.rel_box = AutoComboBox(self, choices = rel_list)
        self.rel_box.SetValue(self.link_rel)

        self.value_box = wx.TextCtrl(self, size=(200,-1))
        self.value_box.SetValue(self.link_value)

        if version == "1.0":
            fgs = wx.FlexGridSizer(2,2,0,5)
            fgs.AddMany([(rel_label, 0, wx.ALIGN_CENTER_VERTICAL), (value_label,0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL),(self.rel_box, 0, wx.ALIGN_CENTER_VERTICAL), (self.value_box,0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)])
        else:
            fgs = wx.FlexGridSizer(2,3,0,5)
            href_label = wx.StaticText(self, label="Href")
            self.href_box = wx.TextCtrl(self, size=(200,-1))
            self.href_box.SetValue(self.link_href)

            fgs.AddMany([(rel_label, 0, wx.ALIGN_CENTER_VERTICAL), (value_label,0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL), (href_label, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL),(self.rel_box, 0, wx.ALIGN_CENTER_VERTICAL), (self.value_box,0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL), (self.href_box, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)])
            self.Bind(wx.EVT_TEXT, self.on_href_change, self.href_box)

        hbox1.Add(fgs, proportion = 1, flag = wx.EXPAND | wx.LEFT| wx.RIGHT | wx.TOP , border=10)
        vbox.Add(hbox1, flag=wx.EXPAND| wx.ALIGN_CENTER)

        
        self.Bind(wx.EVT_TEXT, self.on_rel_change, self.rel_box)
        self.Bind(wx.EVT_COMBOBOX, self.on_rel_change, self.rel_box)
        self.Bind(wx.EVT_TEXT, self.on_value_change, self.value_box)

        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()

        vbox.Add(button_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT| wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)

    def on_rel_change(self, event):
        self.link_rel = self.rel_box.GetValue()

    def on_value_change(self, event):
        self.link_value = self.value_box.GetValue()

    def on_href_change(self, event):
        self.link_href = self.href_box.GetValue()


class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title="About PyIOCe", style=wx.DEFAULT_DIALOG_STYLE)
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        title_text = "Python IOC Editor v" + VERSION
        title_text_box = wx.StaticText(self, label=title_text)
        vbox.Add(title_text_box, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        about_text = "Copyright 2014 Yahoo\nAuthored by Sean Gillespie\nLicensed under the Apache 2.0 license"
        
        about_text_box = wx.StaticText(self, label=about_text)
        vbox.Add(about_text_box, 0,  wx.ALIGN_CENTER | wx.BOTTOM| wx.LEFT | wx.RIGHT, 10)

        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)
        button_sizer.Realize()

        vbox.Add(button_sizer, 0, wx.ALIGN_CENTER| wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)


class HotkeyDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title="PyIOCe Hotkeys", style=wx.DEFAULT_DIALOG_STYLE)
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        title_text = "Python IOC Editor Hotkeys"
        title_text_box = wx.StaticText(self, label=title_text)
        vbox.Add(title_text_box, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        hotkey_text = "a - Insert AND\no - Insert OR\ni - Insert IndicatorItem\nd - Delete Item\nn - Toggle Negation\nc - Toggle Case Sensitivity (1.1+ only)"

        hotkey_text_box = wx.StaticText(self, label=hotkey_text)
        vbox.Add(hotkey_text_box, 0,  wx.ALIGN_CENTER | wx.BOTTOM| wx.LEFT | wx.RIGHT, 10)

        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)
        button_sizer.Realize()

        vbox.Add(button_sizer, 0, wx.ALIGN_CENTER| wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)


class ConvertDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title="Convert Indicator Terms", style=wx.DEFAULT_DIALOG_STYLE)
        
        context_type_list = parent.indicator_terms.keys()
        self.convert_context = parent.preferences["default_context"]

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(1,2,0,5)

        context_label = wx.StaticText(self, label="Convert to")
        self.context_box = wx.ComboBox(self, choices = context_type_list, style=wx.CB_READONLY)
        self.context_box.SetValue(self.convert_context)
        self.Bind(wx.EVT_COMBOBOX, self.on_context_change, self.context_box)

        fgs.AddMany([(context_label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL), (self.context_box,0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)])
        hbox1.Add(fgs, proportion = 1, flag = wx.EXPAND | wx.LEFT| wx.RIGHT | wx.TOP , border=10)
        vbox.Add(hbox1, flag=wx.EXPAND| wx.ALIGN_CENTER)

        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()

        vbox.Add(button_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT| wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)

    def on_context_change(self, event):
        self.convert_context = self.context_box.GetValue()


class AutoComboBox(wx.ComboBox):
    def __init__(self, parent, size=wx.DefaultSize, choices=[]):
        wx.ComboBox.__init__(self, parent, size=size, choices=choices)
        self.choices = choices
        self.Bind(wx.EVT_TEXT, self.on_change)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.autocomplete = False

    def on_key(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE or event.GetKeyCode() == wx.WXK_BACK:
            self.updatelist = True
            self.autocomplete = False
        else:
            self.updatelist = False
            self.autocomplete = True
        event.Skip()

    def on_change(self, event):
        current_text = event.GetString()
        if current_text != "":
            matches = []
            for choice in self.choices:
                if choice.lower().startswith(current_text.lower()):
                    matches.append(choice)

            if self.autocomplete:
                replace_text = current_text

                if len(matches) > 0:
                    replace_text = os.path.commonprefix(matches)

                if replace_text != current_text:
                    if len(current_text) > len(replace_text):
                        replace_text = current_text
                    self.autocomplete = False
                    self.SetItems(matches)
                    self.SetValue(replace_text)
                    self.SetInsertionPoint(len(current_text))
                    self.SetMark(len(current_text), len(replace_text))
            else:
                if self.updatelist:
                    self.updatelist = False
                    self.SetItems(matches)
                    self.SetValue(current_text)
                    self.SetInsertionPoint(len(current_text))

                self.autocomplete = True
        event.Skip()


class IndicatorDialog(wx.Dialog):
    def __init__(self, parent, element, current_ioc, indicator_terms):
        wx.Dialog.__init__(self, parent, -1, title="Edit Indicator", style=wx.DEFAULT_DIALOG_STYLE)
        
        self.current_ioc = current_ioc

        self.element = element
        self.indicator_terms = indicator_terms
        indicator_uuid = self.element.attrib['id']

        if self.element.tag == "Indicator":
            self.SetTitle("Indicator")

            vbox = wx.BoxSizer(wx.VERTICAL)
            hbox1 = wx.BoxSizer(wx.HORIZONTAL)
            gs = wx.GridSizer(1,2,0,0)
            self.or_toggle = wx.RadioButton( self, -1, "OR" )
            and_toggle = wx.RadioButton( self, -1, "AND" )

            if self.element.get('operator') == "OR":
                self.or_toggle.SetValue(1)
            else:
                and_toggle.SetValue(1)

            gs.AddMany([(self.or_toggle,0,wx.ALIGN_CENTER), (and_toggle,1,wx.ALIGN_CENTER)])
            hbox1.Add(gs, proportion=1, flag=wx.TOP, border=15)
            vbox.Add(hbox1, flag=wx.EXPAND| wx.ALIGN_CENTER)
            self.Bind(wx.EVT_RADIOBUTTON, self.on_operator_change)

        elif self.element.tag == "IndicatorItem":

            condition = self.element.attrib['condition']
            context_type = self.element.find('Context').attrib['type']
            search = self.element.find('Context').attrib['search']
            document = self.element.find('Context').attrib['document']
            content_type =  self.element.find('Content').attrib['type']
            content =  self.element.find('Content').text

            try:
                search_list = sorted(self.indicator_terms[context_type].keys())
            except:
                search_list = []

            context_type_list = list(set(indicator_terms.keys() + [context_type]))

            if self.current_ioc.version == "1.0":
                condition_list = ['is', 'isnot', 'contains', 'containsnot']
            elif self.current_ioc.version == "1.1":
                condition_list = ['is', 'contains', 'matches', 'starts-with', 'ends-with', 'greater-than', 'less-than']

            self.SetTitle("IndicatorItem")
            vbox = wx.BoxSizer(wx.VERTICAL)
            hbox1 = wx.BoxSizer(wx.HORIZONTAL)
            fgs = wx.FlexGridSizer(2,2,0,0)
            
            self.context_type_box = wx.ComboBox(self, choices = context_type_list, style=wx.CB_READONLY)
            self.context_type_box.SetValue(context_type)
            
            self.search_box = AutoComboBox(self, choices = search_list, size=(300,-1))
            self.search_box.SetValue(search)

            self.condition_box = AutoComboBox(self, choices = condition_list)
            self.condition_box.SetValue(condition)

            self.content_box = wx.TextCtrl(self, size=(300,-1))
            self.content_box.SetValue(content)

            fgs.AddMany([(self.context_type_box, 0, wx.ALIGN_CENTER_VERTICAL |wx.EXPAND), (self.search_box,1, wx.ALIGN_CENTER_VERTICAL), (self.condition_box, 0, wx.ALIGN_CENTER_VERTICAL), (self.content_box, 1, wx.ALIGN_CENTER_VERTICAL)])
            hbox1.Add(fgs, proportion = 1, flag = wx.EXPAND | wx.LEFT| wx.RIGHT | wx.TOP, border=15)
            vbox.Add(hbox1, flag=wx.EXPAND| wx.ALIGN_CENTER)

            if self.current_ioc.version != "1.0":
                hbox2 = wx.BoxSizer(wx.HORIZONTAL)
                gs = wx.GridSizer(1,2,0,0)
                negate_box = wx.CheckBox(self, -1, "Negate")
                preserve_case_box = wx.CheckBox(self, -1, "Preserve Case")
                gs.AddMany([(negate_box,0,wx.ALIGN_CENTER), (preserve_case_box,1,wx.ALIGN_CENTER)])
                hbox2.Add(gs, proportion = 1, flag = wx.EXPAND)
                vbox.Add(hbox2, flag=wx.EXPAND | wx.ALIGN_CENTER)

                if self.element.get('negate') == "true":
                    negate_box.SetValue(True)

                if self.element.get('preserve-case') == "true":
                    preserve_case_box.SetValue(True)

            self.Bind(wx.EVT_TEXT, self.on_context_type_change, self.context_type_box)
            self.Bind(wx.EVT_TEXT, self.on_search_change, self.search_box)
            self.Bind(wx.EVT_TEXT, self.on_condition_change, self.condition_box)
            self.Bind(wx.EVT_TEXT, self.on_content_change, self.content_box)
            self.Bind(wx.EVT_COMBOBOX, self.on_context_type_change, self.context_type_box)
            self.Bind(wx.EVT_COMBOBOX, self.on_search_change, self.search_box)
            self.Bind(wx.EVT_COMBOBOX, self.on_condition_change, self.condition_box)
            self.Bind(wx.EVT_COMBOBOX, self.on_content_change, self.content_box)


            if self.current_ioc.version != "1.0":
                self.Bind(wx.EVT_CHECKBOX, self.on_negate_change, negate_box)
                self.Bind(wx.EVT_CHECKBOX, self.on_preserve_case_change, preserve_case_box)

        #Insert Parameters list

        if self.current_ioc.version != "1.0":


            hbox3 = wx.BoxSizer(wx.HORIZONTAL)

            self.parameters_list_ctrl = ParameterListCtrl(self, indicator_uuid)
            hbox3.Add(self.parameters_list_ctrl, proportion = 1, flag=wx.EXPAND | wx.RIGHT , border=5)


            hbox3_vbox = wx.BoxSizer(wx.VERTICAL)
            self.indicator_addparam_button = wx.Button(self, label='+', size=(25, 25))
            hbox3_vbox.Add(self.indicator_addparam_button)
            self.indicator_delparam_button = wx.Button(self, label='-', size=(25, 25))
            hbox3_vbox.Add(self.indicator_delparam_button)
            hbox3.Add(hbox3_vbox)
            vbox.Add(hbox3, proportion = 1, flag=wx.EXPAND | wx.TOP| wx.LEFT | wx.RIGHT , border=15)

            self.Bind(wx.EVT_BUTTON, self.on_param_del, self.indicator_delparam_button)
            self.Bind(wx.EVT_BUTTON, self.on_param_add, self.indicator_addparam_button)

            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_param_activated, self.parameters_list_ctrl)


        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()

        vbox.Add(button_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT| wx.ALL, 5)

        self.SetSizer(vbox)
        vbox.Fit(self)
        

    def on_context_type_change(self, event):
        self.element.find('Context').set('type', self.context_type_box.GetValue())
        try:
            new_search_list = sorted(self.indicator_terms[self.context_type_box.GetValue()].keys())
        except:
            new_search_list = []
        self.search_box.SetItems(new_search_list)
        self.search_box.choices = new_search_list

    def on_search_change(self, event):
        self.element.find('Context').set('search', self.search_box.GetValue())
        context_type = self.context_type_box.GetValue()
        search = self.search_box.GetValue()
        try:
            if search in self.indicator_terms[context_type].keys():
                content_type = self.indicator_terms[context_type][search]['content_type']
                context_doc = self.indicator_terms[context_type][search]['context_doc']
                self.element.find('Content').set('type', content_type)
                self.element.find('Context').set('document', context_doc)
        except:
            pass

    def on_condition_change(self, event):
        self.element.set('condition', self.condition_box.GetValue())

    def on_content_change(self, event):
        self.element.find('Content').text = self.content_box.GetValue()

    def on_negate_change(self, event):
        if self.element.get('negate') == "true":
            self.element.set('negate', 'false')
        else:
            self.element.set('negate', 'true')

    def on_preserve_case_change(self, event):
        if self.element.get('preserve-case') == "true":
            self.element.set('preserve-case', 'false') 
        else:
            self.element.set('preserve-case', 'true')

    def on_operator_change(self, event):
        radio_selected = event.GetEventObject()
        if radio_selected == self.or_toggle:
            self.element.set('operator', "OR")
        else:
            self.element.set('operator', "AND")

    def on_param_add(self, event):
        self.parameters_list_ctrl.add_param()

    def on_param_del(self, event):
        param = self.parameters_list_ctrl.GetFirstSelected()
        if param >= 0:
            self.parameters_list_ctrl.del_param(param)

    def on_param_activated(self, event):
        param = self.parameters_list_ctrl.GetFirstSelected()
        self.parameters_list_ctrl.edit_param(param)
    

class PyIOCeFileMenu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)
        self.Append(wx.ID_NEW, '&New')
        self.Append(wx.ID_OPEN, '&Open')
        self.Append(wx.ID_SAVE, '&Save')
        self.Append(wx.ID_SAVEAS, 'Save &All')
        self.Append(wx.ID_PREFERENCES, '&Preferences')


class PyIOCeEditMenu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)
        self.Append(wx.ID_CUT, '&Cut')
        self.Append(wx.ID_COPY, '&Copy')
        self.Append(wx.ID_PASTE, '&Paste')
        self.Append(wx.ID_REVERT, '&Revert')
        self.Append(wx.ID_REPLACE, 'Con&vert')
        self.Append(wx.ID_DUPLICATE, 'C&lone')


class PyIOCeHelpMenu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)
        self.Append(wx.ID_ABOUT, "&About PyIOCe")
        self.Append(wx.ID_HELP, "&Hotkey List")


class PyIOCeHelpMenu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)
        self.Append(wx.ID_ABOUT, "&About PyIOCe")
        self.Append(wx.ID_HELP, "&Hotkey List")


class PyIOCeTermsMenu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)
        self.Append(wx.ID_PROPERTIES, "&Indicator Terms")
        self.Append(wx.ID_CONVERT, "&Term Conversion Map")


class PyIOCeMenuBar(wx.MenuBar):
    def __init__(self):
        wx.MenuBar.__init__(self)
        
        self.Append(PyIOCeFileMenu(), '&File')
        self.Append(PyIOCeEditMenu(), '&Edit')
        self.Append(PyIOCeHelpMenu(), '&Help')
        self.Append(PyIOCeTermsMenu(), '&Terms')


class IOCTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent, -1)

        self.root_item_id = None
        self.current_indicator_id = None
        self.preferences = None
        self.current_ioc = None
        self.indicator_terms = None

        size = (16, 16)
        self.imageList = wx.ImageList(*size)
        self.imageList.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, size))
        self.imageList.Add(wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_OTHER, size))
        self.SetImageList(self.imageList)

        accel_table = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL,  ord('c'), wx.ID_FILE1),
            (wx.ACCEL_NORMAL,  ord('n'), wx.ID_FILE2),
            (wx.ACCEL_NORMAL,  ord('a'), wx.ID_FILE3),
            (wx.ACCEL_NORMAL,  ord('o'), wx.ID_FILE4),
            (wx.ACCEL_NORMAL,  ord('i'), wx.ID_FILE5),
            (wx.ACCEL_NORMAL,  ord('d'), wx.ID_FILE6)
            ])
        self.SetAcceleratorTable(accel_table)

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_indicator_begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self.on_indicator_end_drag)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_indicator_select)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_indicator_activated)

        self.Bind(wx.EVT_TOOL, self.on_case, id=wx.ID_FILE1)
        self.Bind(wx.EVT_TOOL, self.on_not, id=wx.ID_FILE2)
        self.Bind(wx.EVT_TOOL, self.on_and, id=wx.ID_FILE3)
        self.Bind(wx.EVT_TOOL, self.on_or, id=wx.ID_FILE4)
        self.Bind(wx.EVT_TOOL, self.on_insert, id=wx.ID_FILE5)
        self.Bind(wx.EVT_TOOL, self.on_delete, id=wx.ID_FILE6)

  
    def set_config(self, preferences, indicator_terms):
        self.preferences = preferences
        self.indicator_terms = indicator_terms

    def is_descendent(self, dst_item_id, src_item_id):
        if dst_item_id == self.root_item_id:
            return False
        dst_item_parent_id = self.GetItemParent(dst_item_id)
        if dst_item_parent_id == src_item_id:
            return True
        else:
            return self.is_descendent(dst_item_parent_id, src_item_id)

    def build_tree(self, parent, parent_id, param_list):
        for child in parent:
            if child.tag.startswith("Indicator"):
                (label, color) = generate_label(child)
                child_id = self.AppendItem(parent_id, label, data=wx.TreeItemData(child))
                self.SetItemTextColour(child_id, color)
                if child.get('id') in param_list:
                    self.SetItemImage(child_id, 0, wx.TreeItemIcon_Normal)
                self.build_tree(child, child_id, param_list)

    def init_tree(self, criteria, parameters):        
        indicator = criteria.find('Indicator')

        self.clear_tree()
        self.root_item_id = self.AddRoot(indicator.get('operator'), data=wx.TreeItemData(indicator))

        param_list = []

        if parameters != None:
            for param in parameters.findall('param'):
                param_list.append(param.get('ref-id'))

        self.build_tree(indicator, self.root_item_id, param_list)

        self.ExpandAll()

    def clear_tree(self):        
        if self.root_item_id != None:
            self.DeleteAllItems()

    def save_branch(self,node, depth = 0):
        item = {}
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
            label, color = generate_label(item['data'])
            if after_item_id:
                insert_item_id = self.InsertItem(dst_item_id, after_item_id, label)
                if top_level:
                    dst_item_element = self.GetItemData(dst_item_id).GetData()
                    after_item_element = self.GetItemData(after_item_id).GetData()
                    item_element = item['data']
                    dst_item_element.insert(dst_item_element.index(after_item_element)+1,item_element)
            else:
                insert_item_id = self.AppendItem(dst_item_id, label)
                if top_level:
                    dst_item_element = self.GetItemData(dst_item_id).GetData()
                    item_element = item['data']
                    dst_item_element.append(item_element)

            self.SetItemTextColour(insert_item_id, color)
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

    def update_item(self, indicator_id, indicator_element, parameters):
        param_list = []
        if parameters != None:
            for param in parameters.findall('param'):
                param_list.append(param.get('ref-id'))

        (label, color) = generate_label(indicator_element)
        self.SetItemText(indicator_id, label)
        self.SetItemTextColour(indicator_id, color)
        self.SetItemData(indicator_id, wx.TreeItemData(indicator_element))
        if indicator_element.get('id') in param_list:
            self.SetItemImage(indicator_id, 0, wx.TreeItemIcon_Normal)

    def update(self, current_ioc):
        if current_ioc != None:
            self.current_ioc = current_ioc
            self.init_tree(current_ioc.criteria, current_ioc.parameters)
            self.current_indicator_id = self.root_item_id
            self.SetBackgroundColour("#ccffcc") #FIXME - Valdiation 
        else:
            self.clear_tree()
            self.current_indicator_id = None
            self.root_item_id = None

    def on_indicator_select(self, event):
        self.current_indicator_id = event.GetItem()

    def on_indicator_activated(self, event):
        if self.current_indicator_id != self.root_item_id:
            current_indicator_element = self.GetItemData(self.current_indicator_id).GetData()
            new_indicator_element = copy.deepcopy(current_indicator_element)

            indicator_dialog = IndicatorDialog(self, element=new_indicator_element, current_ioc=self.current_ioc, indicator_terms = self.indicator_terms)
            indicator_dialog.CenterOnScreen()
        
            if indicator_dialog.ShowModal() == wx.ID_OK:
                parent_element = current_indicator_element.getparent()
                parent_element.insert(parent_element.index(current_indicator_element),new_indicator_element)
                parent_element.remove(current_indicator_element)
                current_indicator_element = new_indicator_element
                self.update_item(self.current_indicator_id, current_indicator_element, self.current_ioc.parameters)

            indicator_dialog.Destroy()

            self.SetFocus()
            event.Skip()

    def on_indicator_begin_drag(self, event):
        if self.current_indicator_id != self.root_item_id:
            event.Allow()

    def on_indicator_end_drag(self, event):
        src_item_id = self.current_indicator_id
        dst_item_id = event.GetItem()

        after_item_id = None
        self.current_indicator_id = None

        if not dst_item_id.IsOk():
            return

        # Prevent move to own descendent
        if self.is_descendent(dst_item_id, src_item_id):
            return
        # Prevent move to self
        if src_item_id == dst_item_id:
            return

        # If moving to IndicatorIndicator item find set positioning and set destination to parent
        if self.GetItemData(dst_item_id).GetData().tag == "IndicatorItem":
            after_item_id = dst_item_id
            dst_item_id = self.GetItemParent(dst_item_id)
    
    
        branch = self.save_branch(src_item_id)
        self.Delete(src_item_id)
        
        #Insert branch returning list of items that need to be expanded after move
        self.current_indicator_id, expanded_item_list = self.insert_branch(branch, dst_item_id, after_item_id)
        
        for expand_item_id in expanded_item_list:
            self.Expand(expand_item_id)

        self.SelectItem(self.current_indicator_id)
        event.Skip()

    def on_case(self, event):
        current_indicator_element = self.GetItemData(self.current_indicator_id).GetData()
        if current_indicator_element.tag == "IndicatorItem":
            if self.current_ioc.version != "1.0":
                if current_indicator_element.get('preserve-case') == "true":
                    current_indicator_element.set('preserve-case', 'false')
                else:
                    current_indicator_element.set('preserve-case', 'true') 

                (label, color) = generate_label(current_indicator_element)
                self.SetItemTextColour(self.current_indicator_id, color)

    def on_not(self, event):
        current_indicator_element = self.GetItemData(self.current_indicator_id).GetData()
        if current_indicator_element.tag == "IndicatorItem":
            if self.current_ioc.version == "1.0":
                if current_indicator_element.get('condition') == "is":
                    current_indicator_element.set('condition', 'isnot')
                elif current_indicator_element.get('condition') == "isnot":
                    current_indicator_element.set('condition', 'is')
                elif current_indicator_element.get('condition') == "contains":
                    current_indicator_element.set('condition', 'containsnot')
                elif current_indicator_element.get('condition') == "containsnot":
                    current_indicator_element.set('condition', 'contains')
            else:
                if current_indicator_element.get('negate') == "true":
                    current_indicator_element.set('negate', 'false')
                else:
                    current_indicator_element.set('negate', 'true')

            (label, color) = generate_label(current_indicator_element)
            self.SetItemText(self.current_indicator_id, label)
            self.SetItemTextColour(self.current_indicator_id, color)

    def on_and(self, event):
        new_indicator_element = ioc_et.make_Indicator_node("AND")
        current_indicator_element = self.GetItemData(self.current_indicator_id).GetData()

        if current_indicator_element.tag == "Indicator":
            current_indicator_element.append(new_indicator_element)
            self.AppendItem(self.current_indicator_id, new_indicator_element.get('operator'), data=wx.TreeItemData(new_indicator_element))
        elif current_indicator_element.tag == "IndicatorItem":
            current_indicator_element.getparent().append(new_indicator_element)
            self.AppendItem(self.GetItemParent(self.current_indicator_id), new_indicator_element.get('operator'), data=wx.TreeItemData(new_indicator_element))
        self.Expand(self.current_indicator_id)

    def on_or(self, event):
        new_indicator_element = ioc_et.make_Indicator_node("OR")
        current_indicator_element = self.GetItemData(self.current_indicator_id).GetData()
 
        if current_indicator_element.tag == "Indicator":
            current_indicator_element.append(new_indicator_element)
            self.AppendItem(self.current_indicator_id, new_indicator_element.get('operator'), data=wx.TreeItemData(new_indicator_element))
        elif current_indicator_element.tag == "IndicatorItem":
            current_indicator_element.getparent().append(new_indicator_element)
            self.AppendItem(self.GetItemParent(self.current_indicator_id), new_indicator_element.get('operator'), data=wx.TreeItemData(new_indicator_element))
        self.Expand(self.current_indicator_id)

    def on_insert(self, event):
        new_indicatoritem_element = ioc_et.make_IndicatorItem_node(context_type = self.preferences["default_context"])
        current_indicator_element = self.GetItemData(self.current_indicator_id).GetData()
        
        (label, color) = generate_label(new_indicatoritem_element)

        if current_indicator_element.tag == "Indicator":
            current_indicator_element.append(new_indicatoritem_element)
            new_indicatoritem_id = self.AppendItem(self.current_indicator_id, label, data=wx.TreeItemData(new_indicatoritem_element))
        elif current_indicator_element.tag == "IndicatorItem":
            current_indicator_element.getparent().append(new_indicatoritem_element)
            new_indicatoritem_id = self.AppendItem(self.GetItemParent(self.current_indicator_id), label, data=wx.TreeItemData(new_indicatoritem_element))
        self.SetItemTextColour(new_indicatoritem_id, color)
        self.Expand(self.current_indicator_id)
        self.SetFocus()

    def on_delete(self, event):
        if self.current_indicator_id != self.root_item_id:
            current_indicator_element = self.GetItemData(self.current_indicator_id).GetData()

            parent_element = current_indicator_element.getparent()

            parent_id = self.GetItemParent(self.current_indicator_id)

            child_element = current_indicator_element
            child_id = self.current_indicator_id
            
            self.current_indicator_id = parent_id
            current_indicator_element = parent_element
            
            self.Delete(child_id)

            parent_element.remove(child_element)

    def convert_terms(self, convert_context):
        if self.current_indicator_id != None:                
            self.SetFocus() #FIXME
        


class IOCListCtrl(wx.ListCtrl, ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        ColumnSorterMixin.__init__(self, 3)

        self.itemDataMap = {}
        
    def GetListCtrl(self):
        return self

    def update(self,ioc_list, search_filter=None):

        self.DeleteAllItems()
        self.itemDataMap = {}

        for ioc_file in ioc_list.iocs:
            index = len(self.itemDataMap)
            
            ioc_name = ioc_list.iocs[ioc_file].get_name()
            ioc_uuid = ioc_list.iocs[ioc_file].get_uuid()
            ioc_modified = ioc_list.iocs[ioc_file].get_modified()
            ioc_version = ioc_list.iocs[ioc_file].version

            if search_filter != None:
                if search_filter.lower() not in ioc_name.lower() and search_filter.lower() not in ioc_uuid.lower():
                    continue


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
    
    def refresh(self,ioc_list):
        items = self.GetItemCount()
        for item_id in range(items):
            index = self.GetItemData(item_id)
            ioc_file = self.itemDataMap[index][3]

            ioc_name = ioc_list.iocs[ioc_file].get_name()
            ioc_uuid = ioc_list.iocs[ioc_file].get_uuid()
            ioc_modified = ioc_list.iocs[ioc_file].get_modified()
            self.itemDataMap[index] = (ioc_name, ioc_uuid, ioc_modified, ioc_file)
            self.SetStringItem(item_id, 0, " " + ioc_name)

            if et.tostring(ioc_list.iocs[ioc_file].working_xml) == et.tostring(ioc_list.iocs[ioc_file].orig_xml):
                self.SetItemTextColour(item_id, wx.BLACK)
            else:
                self.SetItemTextColour(item_id, wx.RED)

    def add_ioc(self, ioc_list, ioc_file):
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

        return index


class LinkListCtrl(wx.ListCtrl, ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        ColumnSorterMixin.__init__(self, 3)

        self.InsertColumn(0, 'Key')
        self.InsertColumn(1, 'Value', width=150)
        self.InsertColumn(2, 'HREF', width=250)

        self.itemDataMap = {}
        
    def GetListCtrl(self):
        return self

    def update(self,links):

        self.DeleteAllItems()
        self.itemDataMap = {}

        if links != None:
            for link in links.findall('link'):
                index = len(self.itemDataMap)
                
                link_rel = link.get('rel')
                link_value = link.text

                link_href = link.get('href')

                if link_href == None:
                    link_href = ""            

                if link_rel == None:
                    link_rel = ""

                self.itemDataMap[index] = (link_rel, link_value, link_href)

                self.InsertStringItem(index, " " + link_rel)
                self.SetStringItem(index, 1, " " + link_value)
                self.SetStringItem(index, 2, " " + link_href)
                self.SetItemData(index, index)

    def add_link(self):
        index = len(self.itemDataMap)

        link_rel = "*NEW*"
        link_value = ""
        link_href = ""
       
        self.itemDataMap[index] = (link_rel, link_value, link_href)

        self.InsertStringItem(index, " " + link_rel)
        self.SetStringItem(index, 1, " " + link_value)
        self.SetStringItem(index, 2, " " + link_href)
        self.SetItemData(index, index)

    def del_link(self, link):
        self.itemDataMap.pop(self.GetItemData(link))
        self.DeleteItem(link)

    def reload(self, links):
        for link in links.findall('link'):
            links.remove(link)

        for index in range(0,self.GetItemCount()):
            (link_rel, link_value, link_href) = self.itemDataMap[self.GetItemData(index)]

            if link_href == "":
                link_href = None
            links.append(ioc_et.make_link_node(link_rel, link_value, link_href))
        self.update(links)

    def edit_link(self, link, version):

        index = self.GetItemData(link)

        link_data = self.itemDataMap[index]

        link_dialog = LinkDialog(self, link_data=link_data, version=version)
        link_dialog.CenterOnScreen()
    
        if link_dialog.ShowModal() == wx.ID_OK:
            self.itemDataMap[index] = (link_dialog.link_rel, link_dialog.link_value, link_dialog.link_href)

        link_dialog.Destroy()


class ParameterListCtrl(wx.ListCtrl, ColumnSorterMixin):
    def __init__(self, parent, indicator_id):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        ColumnSorterMixin.__init__(self, 3)

        self.itemDataMap = {}
        self.indicator_id = indicator_id
        self.parameters = parent.current_ioc.parameters

        self.InsertColumn(0, 'Name')
        self.InsertColumn(1, 'Value', width = 300)

        parameters = self.parameters.findall("param[@ref-id='"+ self.indicator_id +"']")
        if parameters != None:
            for param in parameters:
                index = len(self.itemDataMap)
                
                param_name = param.get('name')
                param_id = param.get('id')
                param_value = param.find('value').text

                self.itemDataMap[index] = (param_id, param_name, param_value)

                self.InsertStringItem(index, " " + param_name)
                self.SetStringItem(index, 1, " " + param_value)
                self.SetItemData(index, index)
        
    def GetListCtrl(self):
        return self

    def add_param(self):
        index = len(self.itemDataMap)
    
        param_name = "*NEW*"
        param_value = ""
        param_ref = self.indicator_id
        
        new_param = ioc_et.make_param_node(id=param_ref, content=param_value, name=param_name)
        
        self.itemDataMap[index] = (new_param.get('id'), param_name, param_value)

        self.InsertStringItem(index, " " + param_name)
        self.SetStringItem(index, 1, " " + param_value)
        self.SetItemData(index, index)
        self.parameters.append(new_param)

    def del_param(self, param):
        index = self.GetItemData(param)
        param_id = self.itemDataMap[index][0]
        self.itemDataMap.pop(self.GetItemData(param))
        self.DeleteItem(param)

        element = self.parameters.find("param[@id='"+ param_id +"']")
        self.parameters.remove(element)

    def edit_param(self, param):
        index = self.GetItemData(param)
        param_id, param_name, param_value = self.itemDataMap[index]

        element = self.parameters.find("param[@id='"+ param_id +"']")

        new_param_element = copy.deepcopy(element)

        param_dailog = ParamDialog(self, param=new_param_element)
        param_dailog.CenterOnScreen()
    
        if param_dailog.ShowModal() == wx.ID_OK:
            parent_element = element.getparent()
            parent_element.insert(parent_element.index(element),new_param_element)
            parent_element.remove(element)
            param_name = new_param_element.get('name')
            param_value = new_param_element.find('value').text

            self.SetStringItem(param, 0, " " + param_name)
            self.SetStringItem(param, 1, " " + param_value)
            self.itemDataMap[index] = (param_id, param_name, param_value)

        param_dailog.Destroy()


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

        self.current_ioc = None

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

        self.ioc_created_view.SetLabel("0001-01-01T00:00:00")
        self.ioc_modified_view.SetLabel("0001-01-01T00:00:00")
  
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

        self.links_list_ctrl = LinkListCtrl(self)
        hbox4.Add(self.links_list_ctrl, proportion=1, flag=wx.RIGHT|wx.EXPAND, border=5)
        

        hbox4_vbox = wx.BoxSizer(wx.VERTICAL)
        self.ioc_addlink_button = wx.Button(self, label='+', size=(25, 25))
        hbox4_vbox.Add(self.ioc_addlink_button)
        self.ioc_dellink_button = wx.Button(self, label='-', size=(25, 25))
        hbox4_vbox.Add(self.ioc_dellink_button)
        hbox4.Add(hbox4_vbox)       

        vbox.Add(hbox4, proportion=1, flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=10)


        self.Bind(wx.EVT_TEXT, self.on_author_input, self.ioc_author_view)
        self.Bind(wx.EVT_TEXT, self.on_name_input, self.ioc_name_view)
        self.Bind(wx.EVT_TEXT, self.on_desc_input, self.ioc_desc_view)
        self.Bind(wx.EVT_BUTTON, self.on_link_del, self.ioc_dellink_button)
        self.Bind(wx.EVT_BUTTON, self.on_link_add, self.ioc_addlink_button)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_link_activated, self.links_list_ctrl)

        self.SetSizer(vbox)

    def update(self, current_ioc):
        self.current_ioc = current_ioc

        if self.current_ioc != None:
            self.ioc_uuid_view.SetLabelText(current_ioc.get_uuid())
            self.ioc_created_view.SetLabelText(current_ioc.get_created())
            self.ioc_modified_view.SetLabelText(current_ioc.get_modified())
            self.ioc_author_view.ChangeValue(current_ioc.get_author())
            self.ioc_name_view.ChangeValue(current_ioc.get_name())
            self.ioc_desc_view.ChangeValue(current_ioc.get_desc())
            self.links_list_ctrl.update(current_ioc.links)
        else:
            self.ioc_uuid_view.SetLabelText("")
            self.ioc_created_view.SetLabelText("")
            self.ioc_modified_view.SetLabelText("")
            self.ioc_author_view.ChangeValue("")
            self.ioc_name_view.ChangeValue("")
            self.ioc_desc_view.ChangeValue("")
            self.links_list_ctrl.update(None)


    def on_author_input(self, event):
        if self.current_ioc != None:
            author = self.ioc_author_view.GetValue()
            self.current_ioc.set_author(author)
            event.Skip()

    def on_name_input(self, event):
        if self.current_ioc != None:
            name = self.ioc_name_view.GetValue()
            self.current_ioc.set_name(name)
            event.Skip()

    def on_desc_input(self, event):
        if self.current_ioc != None:
            desc = self.ioc_desc_view.GetValue()
            self.current_ioc.set_desc(desc)
            event.Skip()

    def on_link_add(self, event):
        if self.current_ioc != None:
            self.links_list_ctrl.add_link()
            self.links_list_ctrl.reload(self.current_ioc.links)
            event.Skip()

    def on_link_del(self, event):
        if self.current_ioc != None:
            link = self.links_list_ctrl.GetFirstSelected()
            if link >= 0:
                self.links_list_ctrl.del_link(link)
                self.links_list_ctrl.reload(self.current_ioc.links)
            event.Skip()

    def on_link_activated(self, event):
        if self.current_ioc != None:
            link = self.links_list_ctrl.GetFirstSelected()
            self.links_list_ctrl.edit_link(link, self.current_ioc.version)
            self.links_list_ctrl.reload(self.current_ioc.links)
            event.Skip()


class IOCIndicatorPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.ioc_tree_ctrl = IOCTreeCtrl(self)
        vbox.Add(self.ioc_tree_ctrl, proportion=1, flag=wx.EXPAND)
        self.SetSizer(vbox)


class IOCXMLPage(sp.ScrolledPanel):
    def __init__(self, parent):
        sp.ScrolledPanel.__init__(self, parent)

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
        self.ioc_xml_view.SetLabel(xml_view_string.decode('utf-8'))
        self.SetupScrolling()


class IOCNotebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self,parent)
        
        self.ioc_xml_page = IOCXMLPage(self)
        self.ioc_indicator_page = IOCIndicatorPage(self)

        self.AddPage(self.ioc_indicator_page, "IOC")
        self.AddPage(self.ioc_xml_page, "XML")

        
class PyIOCe(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(PyIOCe, self).__init__(*args, **kwargs) 
        
        self.ioc_list = IOCList()
        self.current_ioc = None
        self.current_ioc_file = None

        self.preferences = {}

        try:
            preferences_file = open(BASE_DIR + 'preferences.json','r')
            self.preferences = json.loads(preferences_file.read())
            preferences_file.close()
        except:
            self.preferences["default_version"] = "1.1"
            self.preferences["default_context"] = "mir"
            self.preferences["default_author"] = "PyIOCe"



        try:
            indicator_terms_file = open(BASE_DIR + 'indicator_terms.json','r')
            self.indicator_terms = json.loads(indicator_terms_file.read())
            indicator_terms_file.close()
        except:
            indicator_terms_file = open(BASE_DIR + 'indicator_terms.default','r')
            self.indicator_terms = json.loads(indicator_terms_file.read())
            indicator_terms_file.close()

        self.init_menubar()
        self.init_toolbar()
        self.init_statusbar()
        self.init_panes()
        self.init_bindings()

        self.SetSize((800, 600))
        self.SetTitle('PyIOCe')
        self.Center()
        self.Show()

    def init_menubar(self):
        menubar = PyIOCeMenuBar()
        self.SetMenuBar(menubar)

    def init_toolbar(self):
        toolbar = self.CreateToolBar()

        self.toolbar_search = wx.TextCtrl(toolbar, size=(200,-1))
        toolbar_search_label = wx.StaticText(toolbar, label="Search:")

        toolbar.AddSimpleTool(wx.ID_NEW, wx.Image(BASE_DIR + 'images/new.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'New', '')
        toolbar.AddSimpleTool(wx.ID_OPEN, wx.Image(BASE_DIR + 'images/open.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Open Dir', '')
        toolbar.AddSimpleTool(wx.ID_SAVE, wx.Image(BASE_DIR + 'images/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save', '')
        toolbar.AddSimpleTool(wx.ID_SAVEAS, wx.Image(BASE_DIR + 'images/saveall.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save All', '')
        toolbar.AddStretchableSpace()
        toolbar.AddControl(toolbar_search_label)
        toolbar.AddControl(self.toolbar_search,'Search')
        toolbar.AddStretchableSpace()
        toolbar.AddSimpleTool(wx.ID_FILE1, wx.Image(BASE_DIR + 'images/case.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Case', '')
        toolbar.AddSimpleTool(wx.ID_FILE2, wx.Image(BASE_DIR + 'images/lnot.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Not', '')
        toolbar.AddSimpleTool(wx.ID_FILE3, wx.Image(BASE_DIR + 'images/land.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'And', '')
        toolbar.AddSimpleTool(wx.ID_FILE4, wx.Image(BASE_DIR + 'images/lor.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Or', '')
        toolbar.AddSimpleTool(wx.ID_FILE5, wx.Image(BASE_DIR + 'images/insert.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Insert Item', '')
        toolbar.AddSimpleTool(wx.ID_FILE6, wx.Image(BASE_DIR + 'images/delete.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Delete Item', '')

        toolbar.Realize()

    def init_statusbar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("No IOC Selected")

    def init_panes(self):
        vsplitter = wx.SplitterWindow(self, size=(500,550), style = wx.SP_LIVE_UPDATE | wx.SP_3D)
        hsplitter = wx.SplitterWindow(vsplitter, style = wx.SP_LIVE_UPDATE | wx.SP_3D)

        self.ioc_list_panel = IOCListPanel(vsplitter)

        self.ioc_metadata_panel = IOCMetadataPanel(hsplitter)

        self.ioc_notebook = IOCNotebook(hsplitter)
        self.ioc_notebook.ioc_indicator_page.ioc_tree_ctrl.set_config(self.preferences, self.indicator_terms)

        vsplitter.SplitVertically(self.ioc_list_panel, hsplitter)
        hsplitter.SplitHorizontally(self.ioc_metadata_panel, self.ioc_notebook)

    def init_bindings(self):
        self.Bind(wx.EVT_MENU, self.on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_new, id=wx.ID_NEW) 
        self.Bind(wx.EVT_MENU, self.on_save, id=wx.ID_SAVE) 
        self.Bind(wx.EVT_MENU, self.on_saveall, id=wx.ID_SAVEAS) 
        self.Bind(wx.EVT_MENU, self.on_cut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.on_copy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.on_paste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.on_revert, id=wx.ID_REVERT)
        self.Bind(wx.EVT_MENU, self.on_convert, id=wx.ID_REPLACE)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_help, id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self.on_clone, id=wx.ID_DUPLICATE)
        self.Bind(wx.EVT_MENU, self.on_preferences, id=wx.ID_PREFERENCES)
        self.Bind(wx.EVT_MENU, self.on_terms, id=wx.ID_PROPERTIES)
        self.Bind(wx.EVT_MENU, self.on_map, id=wx.ID_CONVERT)

        accel_table = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('n'), wx.ID_NEW),
            (wx.ACCEL_CTRL, ord('o'), wx.ID_OPEN),
            (wx.ACCEL_CTRL, ord('s'), wx.ID_SAVE),
            (wx.ACCEL_CTRL, ord('a'), wx.ID_SAVEAS),
            (wx.ACCEL_CTRL, ord('c'), wx.ID_COPY),
            (wx.ACCEL_CTRL, ord('p'), wx.ID_PASTE),
            (wx.ACCEL_CTRL, ord('x'), wx.ID_CUT),
            (wx.ACCEL_CTRL, ord('r'), wx.ID_REVERT),
            (wx.ACCEL_CTRL, ord('v'), wx.ID_REPLACE),
            (wx.ACCEL_CTRL, ord('l'), wx.ID_DUPLICATE)
            ])

        self.SetAcceleratorTable(accel_table)

        self.Bind(wx.EVT_TOOL, self.on_new, id=wx.ID_NEW)
        self.Bind(wx.EVT_TOOL, self.on_save, id=wx.ID_SAVE)
        self.Bind(wx.EVT_TOOL, self.on_saveall, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_TOOL, self.on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_TOOL, self.ioc_notebook.ioc_indicator_page.ioc_tree_ctrl.on_case, id=wx.ID_FILE1)
        self.Bind(wx.EVT_TOOL, self.ioc_notebook.ioc_indicator_page.ioc_tree_ctrl.on_not, id=wx.ID_FILE2)
        self.Bind(wx.EVT_TOOL, self.ioc_notebook.ioc_indicator_page.ioc_tree_ctrl.on_and, id=wx.ID_FILE3)
        self.Bind(wx.EVT_TOOL, self.ioc_notebook.ioc_indicator_page.ioc_tree_ctrl.on_or, id=wx.ID_FILE4)
        self.Bind(wx.EVT_TOOL, self.ioc_notebook.ioc_indicator_page.ioc_tree_ctrl.on_insert, id=wx.ID_FILE5)
        self.Bind(wx.EVT_TOOL, self.ioc_notebook.ioc_indicator_page.ioc_tree_ctrl.on_delete, id=wx.ID_FILE6)

        self.Bind(wx.EVT_TEXT, self.on_search_input, self.toolbar_search)

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.update, self.ioc_notebook)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_esc)


        self.Bind(wx.EVT_TEXT, self.update, self.ioc_metadata_panel.ioc_author_view)
        self.Bind(wx.EVT_TEXT, self.update, self.ioc_metadata_panel.ioc_name_view)
        self.Bind(wx.EVT_TEXT, self.update, self.ioc_metadata_panel.ioc_desc_view)
        self.Bind(wx.EVT_BUTTON, self.update, self.ioc_metadata_panel.ioc_dellink_button)
        self.Bind(wx.EVT_BUTTON, self.update, self.ioc_metadata_panel.ioc_addlink_button)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.update, self.ioc_metadata_panel.links_list_ctrl)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_ioc_select, self.ioc_list_panel.ioc_list_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_ioc_activated, self.ioc_list_panel.ioc_list_ctrl)

    def update(self, event=None):
        self.ioc_metadata_panel.update(self.current_ioc)
        self.ioc_notebook.ioc_indicator_page.ioc_tree_ctrl.update(self.current_ioc)
        self.ioc_notebook.ioc_xml_page.update(self.current_ioc)
        self.ioc_list_panel.ioc_list_ctrl.refresh(self.ioc_list)
        if self.current_ioc_file != None:
            self.statusbar.SetStatusText(self.current_ioc_file)
        else:
            self.statusbar.SetStatusText("No IOC Selected")

        self.ioc_metadata_panel.Layout()

    def select_dir(self):
        select_dir_dialog = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)

        if select_dir_dialog.ShowModal() == wx.ID_OK:
            selected_dir = select_dir_dialog.GetPath()
        else:
            selected_dir = None
            
        select_dir_dialog.Destroy()

        return selected_dir

    def on_esc(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.ioc_list_panel.ioc_list_ctrl.SetFocus()
        event.Skip()

    def on_search_input(self, event):
        self.ioc_list_panel.ioc_list_ctrl.update(self.ioc_list, self.toolbar_search.GetValue())
        if self.ioc_list_panel.ioc_list_ctrl.GetItemCount() > 0:
            self.ioc_list_panel.ioc_list_ctrl.Select(0, on=True)
        else:
            self.current_ioc = None
            self.current_ioc_file = None
            self.update()

    def on_preferences(self, event):
        preferences_dialog = PreferencesDialog(self)
        preferences_dialog.CenterOnScreen()

        if preferences_dialog.ShowModal() == wx.ID_OK:
            self.preferences["default_version"] = preferences_dialog.default_version
            self.preferences["default_context"] = preferences_dialog.default_context
            self.preferences["default_author"] = preferences_dialog.default_author
        
            preferences_file = open(BASE_DIR + 'preferences.json','w')
            preferences_file.write(json.dumps(self.preferences))
            preferences_file.close()

        preferences_dialog.Destroy()

    def on_terms(self, event):
        terms_dialog = TermsDialog(self)
        terms_dialog.CenterOnScreen()

        if terms_dialog.ShowModal() == wx.ID_OK:
            self.indicator_terms = terms_dialog.indicator_terms
            indicator_terms_file = open(BASE_DIR + 'indicator_terms.json','w')
            indicator_terms_file.write(json.dumps(self.indicator_terms))
            indicator_terms_file.close()

        terms_dialog.Destroy()
        
    def on_map(self, event):
        pass

    def on_about(self, event):
        about_dialog = AboutDialog(self)
        about_dialog.CenterOnScreen()

        about_dialog.ShowModal()

        about_dialog.Destroy()

    def on_help(self, event):
        hotkey_dialog = HotkeyDialog(self)
        hotkey_dialog.CenterOnScreen()

        hotkey_dialog.ShowModal()

        hotkey_dialog.Destroy()

    def on_quit(self, event):
        self.Close()

    def on_open(self, event):
        selected_dir = self.select_dir()
        if selected_dir is not None:
            self.ioc_list.open_ioc_path(selected_dir)
            self.ioc_list_panel.ioc_list_ctrl.update(self.ioc_list)
            if len(self.ioc_list.iocs) > 0:
                self.ioc_list_panel.ioc_list_ctrl.Select(0, on=True)
            else:
                self.current_ioc = None
                self.current_ioc_file = None
                self.update()

            self.ioc_list_panel.ioc_list_ctrl.SetFocus()            
    
    def on_clone(self, event):
        if self.current_ioc != None:
            self.current_ioc_file = self.ioc_list.clone_ioc(self.current_ioc)
            self.current_ioc = self.ioc_list.iocs[self.current_ioc_file]
            new_ioc_index = self.ioc_list_panel.ioc_list_ctrl.add_ioc(self.ioc_list, self.current_ioc_file)
            self.ioc_list_panel.ioc_list_ctrl.Select(new_ioc_index, on=True)
            self.ioc_list_panel.ioc_list_ctrl.SetFocus()

    def on_new(self, event):
        if self.ioc_list.working_dir == None:
            selected_dir = self.select_dir()
            if selected_dir is not None:
                self.ioc_list.open_ioc_path(selected_dir)
                self.ioc_list_panel.ioc_list_ctrl.update(self.ioc_list)
            else:
                return

        self.current_ioc_file = self.ioc_list.add_ioc(author = self.preferences["default_author"], version = self.preferences["default_version"])
        self.current_ioc = self.ioc_list.iocs[self.current_ioc_file]
        new_ioc_index = self.ioc_list_panel.ioc_list_ctrl.add_ioc(self.ioc_list, self.current_ioc_file)
        self.ioc_list_panel.ioc_list_ctrl.Select(new_ioc_index, on=True)
        self.ioc_list_panel.ioc_list_ctrl.SetFocus()

    def on_save(self, event):
        if self.current_ioc != None:
            self.ioc_list.save_iocs(self.current_ioc_file)
            self.update()

    def on_saveall(self, event):
        if self.current_ioc != None:
            self.ioc_list.save_iocs()
            self.update()
    
    def on_ioc_select(self, event):
        ioc_index = self.ioc_list_panel.ioc_list_ctrl.GetItemData(event.m_itemIndex)
        self.current_ioc_file = self.ioc_list_panel.ioc_list_ctrl.itemDataMap[ioc_index][3]
        self.current_ioc = self.ioc_list.iocs[self.current_ioc_file]
        self.update()

    def on_ioc_activated(self,event):
        self.ioc_notebook.ioc_indicator_page.ioc_tree_ctrl.SetFocus()

    def on_cut(self,event):
        pass

    def on_copy(self,event):
        pass

    def on_paste(self,event):
        pass

    def on_revert(self, event):
        if self.current_ioc != None and self.current_ioc.orig_xml.tag != "New":
            #Reset all the IOC references using original xml
            self.ioc_list.iocs[self.current_ioc_file] = IOC(self.current_ioc.orig_xml)
            self.current_ioc = self.ioc_list.iocs[self.current_ioc_file]
            self.update()

    def on_convert(self, event):
        if self.current_ioc != None:
            convert_dialog = ConvertDialog(self)
            convert_dialog.CenterOnScreen()
        
            if convert_dialog.ShowModal() == wx.ID_OK:
                convert_context = convert_dialog.convert_context
                self.ioc_notebook.ioc_indicator_page.ioc_tree_ctrl.convert_terms(convert_context)
            
            convert_dialog.Destroy()

if __name__ == '__main__':
    BASE_DIR = "./"
    VERSION = "0.9"
    app = wx.App()

    PyIOCe(None)

    app.MainLoop()
