#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
element_types = ['node', 'way', 'relation']

expected_street_prefix = [
     u'Acces',
     u'Aeroportul',
     u'Aleea',
     u'Autostrada',
     u'Bulevardul',
     u'Calea',
     u'DN7',
     u'Drumul',
     u'Intrarea',
     u'Pasajul',
     u'Pia\u021ba',
     u'Podul',
     u'Prelungirea',
     u'Splaiul',
     u'Strada',
     u'\u0218oseaua']

street_mappings = {
      u'A1': 'Autostrada A1',
      u'acces': u'Acces',
      u'Alee': u'Aleea',
      u'Cale': u'Calea',
      u'Drum': u'Drumul',
      u'Intrare': u'Intrarea',
      u'Intrares': u'Intrarea',
      u'Pasaj': u'Pasajul',
      u'Pia\u021beta': u'Pia\u021ba',
      u'Pod': u'Podul',
      u'Strava': u'Strada',
      u'intrare': u'Intrarea',
      u'\xcentrarea': u'Intrarea',
      u'Soseaua': u'\u0218oseaua',
      u'\u015eoseaua': u'\u0218oseaua'}

def correct_street_name(street):
    first_word = street.split()[0]
    if first_word in street_mappings:
        return street.replace(first_word,street_mappings[first_word])
    return street

def shape_element(element,show=False):
    if element.tag not in element_types:
        return None  
    """ we are skipping tags and all inner xml tags because 
        we process them when we process 'nodes', 'ways' and 'relations' """
    node=element.attrib
    node['type']=element.tag
    node["created"] = {}
    for key in CREATED:
        if node.get(key):
            node["created"][key]=node.pop(key)
    if node.get("lat") and node.get("lon"):
        node["pos"] = [float(node.pop("lat")),float(node.pop("lon"))]
    for tag in element.iter():
        if tag.tag=='tag':
            if element.tag=='way' and tag.attrib['k']=='name':
                node[tag.attrib['k']]=correct_street_name(tag.attrib['v'])
            elif tag.attrib['k'].find('addr')==0:
                node['address']=node.get('address',{})
                addr_attribute = tag.attrib['k'][5:]
                if addr_attribute=='street':
                    node['address']['street']=correct_street_name(tag.attrib['v'])
                else:
                    node['address'][addr_attribute]=tag.attrib['v']
            else:
                node[tag.attrib['k']]=tag.attrib['v']
        if element.tag=='way' and tag.tag=='nd':
            node['node_refs'] = node.get('node_refs',[])+[tag.attrib['ref']]
        if element.tag=='relation' and tag.tag=='member':
            ''' node['members'] is an array of dictionaries, each dictionary
            containing the attributes of one member tag in the osm xml file'''
            node['members'] = node.get('members',[]) + [tag.attrib]
    if show:
        pprint.pprint(node)
    return node



def process_map(file_in, pretty = False,debug=False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        current_elem=None
        for event, element in ET.iterparse(file_in, events=('start','end')):
            if element.tag in element_types and event=='start':
                current_elem=element.tag
            if event=='end' and element.tag==current_elem:
                el = shape_element(element,debug)
                element.clear()
                if el:
                    # data.append(el)
                    if pretty:
                        fo.write(json.dumps(el, indent=2)+"\n")
                    else:
                        fo.write(json.dumps(el) + "\n")

    return data

def test():
    data = process_map('bucharest_romania.osm')
    #pprint.pprint(data)
    
    
if __name__ == "__main__":
    test()