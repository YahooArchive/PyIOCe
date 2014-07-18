import uuid
import os
from lxml import etree as et
import copy

def strip_namespace(ioc_xml):
    if ioc_xml.tag.startswith('{'):
        namespace = ioc_xml.tag[0:ioc_xml.tag.find('}')+1]
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

        self.name = self.working_xml.find('metadata/short_description')
        self.desc = self.working_xml.find('metadata/description')
        self.author = self.working_xml.find('metadata/authored_by')
        self.created = self.working_xml.find('metadata/authored_date')
        self.links = self.working_xml.find('metadata/links')
        self.attributes = self.working_xml.attrib
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
        self.working_dir = ""
        self.iocs = {}

    def add_ioc(self,dir):
        pass
        #add IOC to list

    #Save IOCs, check self.working_dir    

    def open_ioc_path(self,dir):
        self.iocs = {}
        self.working_dir = dir
        for base, sub, files in os.walk(self.working_dir):
            for filename in files:
                if os.path.splitext(filename)[1][1:].lower() == "ioc":
                    fullpath = os.path.join(base, filename)

                    ioc_file = open(fullpath, 'r')

                    ioc_xml = et.fromstring(ioc_file.read())

                    clean_ioc_xml = strip_namespace(ioc_xml)

                    self.iocs[fullpath] = IOC(clean_ioc_xml)