# ioc_et.py
#
# Copyright 2013 Mandiant Corporation.  
# Licensed under the Apache 2.0 license.  Developed for Mandiant by William 
# Gibb.
#
# Mandiant licenses this file to you under the Apache License, Version
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
#
# Provides support for ioc_api.
#

import uuid
import datetime

from lxml import etree as et

##############################################
NSMAP = {'xsi' : 'http://www.w3.org/2001/XMLSchema-instance',
            'xsd' : 'http://www.w3.org/2001/XMLSchema', }


def make_IOC_root(id=None, version="1.1"):
    root = et.Element('OpenIOC', nsmap = NSMAP)
    
    if version == "1.0":
        root.attrib['xmlns'] = "http://schemas.mandiant.com/2010/ioc"
    elif version == "1.1":
        root.attrib['xmlns'] = 'http://openioc.org/schemas/OpenIOC_1.1'
    else:
        raise ValueError('Invalid Version')

    if id:
        root.attrib['id'] = id
    else:
        root.attrib['id'] = get_guid()
    # default dates
    root.attrib['last-modified'] = '0001-01-01T00:00:00'
    root.attrib['published-date'] = '0001-01-01T00:00:00'
    return root
    
def make_metadata_node(name = None,
                        description = 'Automatically generated IOC',
                        author = 'IOC_et',
                        links = None,):
    metadata_node = et.Element('metadata')
    metadata_node.append(make_short_description_node(name))
    metadata_node.append(make_description_node(description))
    metadata_node.append(make_keywords_node())
    metadata_node.append(make_authored_by_node(author))
    metadata_node.append(make_authored_date_node())
    metadata_node.append(make_links_node(links))
    return metadata_node
    
def make_keywords_node(keywords = None):
    keywords_node = et.Element('keywords')
    if keywords:
        keywords_node.text = keywords
    return keywords_node
    
def make_short_description_node(name):
    description_node = et.Element('short_description')
    description_node.text=name
    return description_node
    
def update_node_text(node, text):
    node.text = text
    return node
    
def make_description_node(text):
    description_node = et.Element('description')
    description_node.text=text
    return description_node
    
    
def make_authored_by_node(author = 'ioc_et'):
    authored_node = et.Element('authored_by')
    authored_node.text = author
    return authored_node
    
def make_links_node(links = None):
    links_node = et.Element('links')
    if links:
        for rel, href, value in links:
            links_node.append(make_link_node(rel,value, href))
    return links_node
    
def set_root_lastmodified(root_node, date=None):
    if date:
        root_node.attrib['last-modified'] = date
    else:
        root_node.attrib['last-modified'] = get_current_date()

def set_root_published_date(root_node, date=None):
    if date:
        root_node.attrib['published-date'] = date
    else:
        root_node.attrib['published-date'] = get_current_date()

def set_root_created_date(root_node, date=None):
    date_node = root_node.find('.//authored_date')
    if date_node is None:
        raise ValueError('authored_date node does not exist.  IOC is not schema compliant.')
    if date:
        date_node.text = date
    else:
        date_node.text = get_current_date()
        
def make_criteria_node(indicator_node = None):
    definition_node = et.Element('criteria')
    if indicator_node is not None:
        if indicator_node.tag != 'Indicator':
            raise ValueError('IndicatorNode has the incorrect tag.')
        definition_node.append(indicator_node)
    return definition_node
    
def make_parameters_node():
    parameters_node = et.Element('parameters')
    return parameters_node
    
def make_param_node(id,  content, name='comment', type='string',):
    param_node = et.Element('param')
    param_node.attrib['id'] = get_guid()
    param_node.attrib['ref-id'] = id
    param_node.attrib['name'] = name
    value_node = et.Element('value')
    value_node.attrib['type'] = type
    value_node.text = content
    param_node.append(value_node)
    return param_node

def make_Indicator_node(operator, id = None):
    '''
    This makes a Indicator node element.  These allow the construction of a
        logic tree within the IOC.
    
    input
        operator:   'AND' or 'OR'.
        id: a string value.  This is used to provide a GUID for the Indicator.
            The ID should NOT be specified under normal circumstances.
    
    return: elementTree element 
    '''
    Indicator_node = et.Element('Indicator')
    if id:
        Indicator_node.attrib['id'] = id
    else:
        Indicator_node.attrib['id'] = get_guid()
    if operator.upper() not in ['AND','OR']:
        raise ValueError('Indicator operator must be "AND" or "OR".')
    Indicator_node.attrib['operator'] = operator.upper()
    return Indicator_node

def make_IndicatorItem_node(condition,
                            document, 
                            search, 
                            content_type, 
                            content, 
                            preserve_case = False,
                            negate = False,
                            context_type = 'mir', 
                            id = None):
    '''
    This makes a IndicatorItem element.  This contains the actual threat
    intelligence in the IOC.
    
    input
        condition: This is the condition of the item ('is', 'contains', 
            'matches', etc).
        document: String value.  Denotes the type of document to look for
            the encoded artifact in.
        search: String value.  Specifies what attribute of the doucment type
            the encoded value is.
        content_type: This is the display type of the item, which is derived 
            from the iocterm for the search value.
        content: a string value, containing the data to be identified.
        preserve_case: Boolean value.  Specify if the 
            IndicatorItem/content/text() is case sensitive.
        negate: Boolean value.  Specify if the IndicatorItem/@condition is 
            negated, ie:
                @condition = 'is' & @negate = 'true' would be equal to the 
                @condition = 'isnot' in OpenIOC 1.0.
        context_type: a string value, giving context to the document/search
            information.  This defaults to 'mir'.
        id: a string value.  This is used to provide a GUID for the IndicatorItem
            The ID should NOT be specified under normal circumstances.
            
    returns
        an elementTree Element item
    
    '''
    # validate condition
    if condition not in valid_indicatoritem_conditions:
        raise ValueError('Invalid IndicatorItem condition [%s]' % str(condition))
    IndicatorItem_node = et.Element('IndicatorItem')
    if id:
        IndicatorItem_node.attrib['id'] = id
    else:
        IndicatorItem_node.attrib['id'] = get_guid()
    IndicatorItem_node.attrib['condition'] = condition
    if preserve_case:
        IndicatorItem_node.attrib['preserve-case'] = 'true'
    else:
        IndicatorItem_node.attrib['preserve-case'] = 'false'
    if negate:
        IndicatorItem_node.attrib['negate'] = 'true'
    else:
        IndicatorItem_node.attrib['negate'] = 'false'
    context_node = make_context_node(document, search, context_type)
    content_node = make_content_node(content_type, content)
    IndicatorItem_node.append(context_node)
    IndicatorItem_node.append(content_node)
    return IndicatorItem_node

    
##############################################

def make_authored_date_node():
    authored_node = et.Element('authored_date')
    authored_node.text = get_current_date()
    return authored_node
    
def make_link_node(rel, value, href=None):
    link_node = et.Element('link')
    link_node.attrib['rel'] = rel
    if href:
        link_node.attrib['href'] = href
    link_node.text = value
    return link_node

def make_context_node(document,search,context_type='mir'):
    context_node = et.Element('Context')
    context_node.attrib['document'] = document
    context_node.attrib['search'] = search
    if context_type:
        context_node.attrib['type'] = context_type
    return context_node
    
def make_content_node(type, content):
    content_node = et.Element('Content')
    content_node.attrib['type'] = type
    content_node.text = content
    return content_node

    
##############################################
    
def get_guid():
    return str(uuid.uuid4())
    
def get_current_date():
    # xsdDate format.  not TZ format.
    time = datetime.datetime.utcnow()
    timestring = time.strftime('%Y-%m-%dT%H:%M:%S')
    return timestring
    
    