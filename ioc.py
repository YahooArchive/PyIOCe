import os
from lxml import etree as et
import copy
import ioc_et

def strip_namespace(ioc_xml):
    if ioc_xml.tag.startswith('{'):
        ns_length = ioc_xml.tag.find('}')
        namespace = ioc_xml.tag[0:ns_length+1]
        ioc_xml.attrib['xmlns'] = namespace[1:ns_length]
    for element in ioc_xml.getiterator():
        if element.tag.startswith(namespace):
            element.tag = element.tag[len(namespace):]  
    return ioc_xml

class IOC():
    def __init__(self, ioc_xml):
    # def __init__(self, dummyname, dummyuuid, dummymodified):
        # if filenotexists:
        #     createemptyioc

        self.working_xml = copy.copy(ioc_xml)
        self.orig_xml = copy.copy(ioc_xml)

        self.attributes = self.working_xml.attrib

        if self.attributes['xmlns'] == "http://schemas.mandiant.com/2010/ioc":
            self.version = "1.0"
            self.name = self.working_xml.find('short_description')
            self.desc = self.working_xml.find('description')
            self.author = self.working_xml.find('authored_by')
            self.created = self.working_xml.find('authored_date')
            self.links = self.working_xml.find('links')
            self.criteria = self.working_xml.find('definition')
            #FIXME Keywords

        elif self.attributes['xmlns'] == "http://openioc.org/schemas/OpenIOC_1.1":
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

    def get_modified(self):
        return self.attributes['last-modified']

    def get_author(self):
        return self.author.text

    def get_created(self):
        return self.created.text

    def get_metadata(field):
        pass

    def get_desc(self):
        if self.desc.text is not None:
            return self.desc.text
        else:
            return ""

    def get_links(self):
        pass

    def get_indicator(self):
        pass

class IOCList():
    def __init__(self):
        self.working_dir = None
        self.iocs = {}

    def add(self, version="1.1"):
        ioc_file = None

        new_ioc_xml = ioc_et.make_IOC_root(version=version)

        ioc_file = new_ioc_xml.attrib['id'] + ".ioc"
        full_path = os.path.join(self.working_dir, ioc_file)

        if version == "1.0":
            pass#FIXME
        elif version == "1.1":
            new_ioc_xml.append(ioc_et.make_metadata_node( name= "*New IOC*", author = "PyIOCe", description = "PyIOCe Generated IOC"))
            new_ioc_xml.append(ioc_et.make_criteria_node(ioc_et.make_Indicator_node("OR")))
            new_ioc_xml.append(ioc_et.make_parameters_node())

        self.iocs[full_path] = IOC(new_ioc_xml)

        return full_path

    #Save IOCs, check self.working_dir    

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