import os
from lxml import etree as et
import copy
import ioc_et
import wx

def strip_namespace(ioc_xml):
    if ioc_xml.tag.startswith('{'):
        ns_length = ioc_xml.tag.find('}')
        namespace = ioc_xml.tag[0:ns_length+1]
    for element in ioc_xml.getiterator():
        if element.tag.startswith(namespace):
            element.tag = element.tag[len(namespace):]  
    return ioc_xml

def generate_label(element):
    if element.tag == "Indicator":
        return (element.get('operator'), wx.BLACK)

    if element.tag == "IndicatorItem":
        color = wx.BLUE

        context = element.find('Context')
        content = element.find('Content')
        
        condition = element.get('condition')
        search_type = context.get('type')
        search_path = context.get('search')
        search_text = content.text
        
        if "preserve-case" in element.keys():
            if element.get('preserve-case') == "true":
                color = "#009900"

        negate = ""
        if "negate" in element.keys():
            if element.get('negate') == "true":
                negate = " NOT"
                if element.get('preserve-case') == "true":
                    color = "#7300FF"
                else:
                    color = wx.RED


        if condition == "isnot":
            condition = "is"
            negate = " NOT"
            color = wx.RED

        if condition == "containsnot":
            condition = "contains"
            negate = " NOT"
            color = wx.RED
        
        label = negate + " " + search_type + ":" + search_path + " " + condition + " " + search_text
        return (label, color)
    return "Bad Indicator"

class IOC():
    def __init__(self, ioc_xml):
        self.working_xml = copy.copy(ioc_xml)
        self.orig_xml = copy.copy(ioc_xml)

        self.attributes = self.working_xml.attrib

        print 

        if self.working_xml.nsmap[None] == "http://schemas.mandiant.com/2010/ioc":
            self.version = "1.0"
            self.name = self.working_xml.find('short_description')
            self.desc = self.working_xml.find('description')
            self.author = self.working_xml.find('authored_by')
            self.created = self.working_xml.find('authored_date')
            self.links = self.working_xml.find('links')
            self.criteria = self.working_xml.find('definition')
            #FIXME Keywords

        elif self.working_xml.nsmap[None] == "http://openioc.org/schemas/OpenIOC_1.1":
            self.version = "1.1"
            self.name = self.working_xml.find('metadata/short_description')
            self.desc = self.working_xml.find('metadata/description')
            self.author = self.working_xml.find('metadata/authored_by')
            self.created = self.working_xml.find('metadata/authored_date')
            self.links = self.working_xml.find('metadata/links')
            self.criteria = self.working_xml.find('criteria')

    def get_uuid(self):
        return self.attributes['id']

    def get_name(self):
        return self.name.text

    def set_name(self, name):
        self.name.text = name

    def get_modified(self):
        return self.attributes['last-modified']

    def set_modified(self):
        self.attributes['last-modified'] = ioc_et.get_current_date()

    def get_author(self):
        return self.author.text

    def set_author(self, author):
        self.author.text = author

    def get_created(self):
        return self.created.text

    def set_created(self):
        self.created.text = ioc_et.get_current_date()

    def get_metadata(field):
        pass

    def get_desc(self):
        if self.desc.text is not None:
            return self.desc.text
        else:
            return ""

    def set_desc(self, desc):
        self.desc.text = desc

    def get_links(self):
        pass

    def get_indicator(self):
        pass

class IOCList():
    def __init__(self):
        self.working_dir = None
        self.iocs = {}

    def save_iocs(self, full_path=None):
        if full_path:
            if et.tostring(self.iocs[full_path].working_xml) != et.tostring(self.iocs[full_path].orig_xml):
                self.iocs[full_path].set_modified()
                ioc_xml_string = et.tostring(self.iocs[full_path].working_xml, encoding="utf-8", xml_declaration=True, pretty_print = True)
                ioc_file = open(full_path, 'w')
                ioc_file.write(ioc_xml_string)
                ioc_file.close()
                self.iocs[full_path].orig_xml = copy.copy(self.iocs[full_path].working_xml)
        else:
            for full_path in self.iocs:
                if et.tostring(self.iocs[full_path].working_xml) != et.tostring(self.iocs[full_path].orig_xml):
                    self.iocs[full_path].set_modified()
                    ioc_xml_string = et.tostring(self.iocs[full_path].working_xml, encoding="utf-8", xml_declaration=True, pretty_print = True)
                    ioc_file = open(full_path, 'w')
                    ioc_file.write(ioc_xml_string)
                    ioc_file.close()
                    self.iocs[full_path].orig_xml = copy.copy(self.iocs[full_path].working_xml)

    def clone_ioc(self,current_ioc):
        new_ioc_xml = copy.copy(current_ioc.working_xml)
        new_uuid = ioc_et.get_guid()
        ioc_file = new_uuid + ".ioc"
        full_path = os.path.join(self.working_dir, ioc_file)
        
        new_ioc_xml.attrib['id'] = new_uuid
        self.iocs[full_path] = IOC(new_ioc_xml)
        self.iocs[full_path].set_modified()
        self.iocs[full_path].set_created()
        self.iocs[full_path].orig_xml = et.Element('Clone')

        return full_path

    def add_ioc(self, version):
        new_ioc_xml = ioc_et.make_IOC_root(version=version)

        ioc_file = new_ioc_xml.attrib['id'] + ".ioc"
        full_path = os.path.join(self.working_dir, ioc_file)

        if version == "1.0":
            new_ioc_xml.append(ioc_et.make_short_description_node(name = "*New IOC*"))
            new_ioc_xml.append(ioc_et.make_description_node(text="PyIOCe Generated IOC"))
            new_ioc_xml.append(ioc_et.make_authored_by_node(author = 'PyIOCe'))
            new_ioc_xml.append(ioc_et.make_authored_date_node())
            new_ioc_xml.append(ioc_et.make_links_node())
            new_ioc_xml.append(ioc_et.make_definition_node(ioc_et.make_Indicator_node("OR")))
        elif version == "1.1":
            new_ioc_xml.append(ioc_et.make_metadata_node( name = "*New IOC*", author = "PyIOCe", description = "PyIOCe Generated IOC"))
            new_ioc_xml.append(ioc_et.make_criteria_node(ioc_et.make_Indicator_node("OR")))
            new_ioc_xml.append(ioc_et.make_parameters_node())

        self.iocs[full_path] = IOC(new_ioc_xml)
        self.iocs[full_path].orig_xml = et.Element('New')

        return full_path

    def open_ioc_path(self,dir):
        self.iocs = {}
        self.working_dir = dir
        for base, sub, files in os.walk(self.working_dir):
            for filename in files:
                if os.path.splitext(filename)[1][1:].lower() == "ioc":
                    full_path = os.path.join(base, filename)

                    ioc_file = open(full_path, 'r')

                    ioc_xml = et.fromstring(ioc_file.read())

                    clean_ioc_xml = strip_namespace(ioc_xml)

                    self.iocs[full_path] = IOC(clean_ioc_xml)