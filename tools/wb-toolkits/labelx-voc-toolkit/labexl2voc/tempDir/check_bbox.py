# -*- coding:utf-8 -*-
import os
import sys
import json
from lxml import etree
"""
这个函数的作用是
检测 bbox 的 position
"""


def get_object_list(xmlFile=None):
    tree = etree.parse(xmlFile)
    rooTElement = tree.getroot()
    object_list = []
    w_h_d_list = None
    for child in rooTElement:
        if child.tag == "object":
            bbox_label = child.xpath('name')[0].text
            xmin = child.xpath('bndbox')[0].xpath('xmin')[0].text
            ymin = child.xpath('bndbox')[0].xpath('ymin')[0].text
            xmax = child.xpath('bndbox')[0].xpath('xmax')[0].text
            ymax = child.xpath('bndbox')[0].xpath('ymax')[0].text
            bbox_position = [float(xmin), float(ymin), float(xmax), float(ymax)]
            bbox_position = [int(i) for i in bbox_position]
            object_list.append([bbox_label, bbox_position])
        elif child.tag == "size":
            width = child.xpath('width')[0].text
            height = child.xpath('height')[0].text
            depth = child.xpath('depth')[0].text
            w_h_d_list = [float(width), float(height), float(depth)]
            w_h_d_list = [int(i) for i in w_h_d_list]
    return (w_h_d_list,object_list)


def check_xml_file(xml_file=None):
    w_h_d_list, object_list = get_object_list(xmlFile=xml_file)
    w = w_h_d_list[0]
    h = w_h_d_list[1]
    d = w_h_d_list[2]
    for i_bbox in object_list:
        babel = i_bbox[0]
        xmin = i_bbox[1][0]
        ymin = i_bbox[1][1]
        xmax = i_bbox[1][2]
        ymax = i_bbox[1][3]
        if xmin >= xmax or ymin >= ymax or xmin < 0 or ymin < 0 :
            print(xml_file)
            print(i_bbox)
            print(w_h_d_list)
        elif ((xmax - xmin) * (ymax - ymin)) < 2:
            print("*"*100)
            print(xml_file)
            print(i_bbox)
            print(w_h_d_list)
        elif (xmax - xmin) == 1 or (ymax - ymin) == 1:
            print("-"*100)
            print(xml_file)
            print(i_bbox)
            print(w_h_d_list)
    pass

def main():
    xmlFileNewPath = '/workspace/data/BK/terror-dataSet-Dir/TERROR-DETECT-V1.0/Annotations'
    xml_file_list = [os.path.join(xmlFileNewPath, i)
                     for i in os.listdir(xmlFileNewPath) if i[0] != '.']
    for xml_file in xml_file_list:
        check_xml_file(xml_file=xml_file)



if __name__ == '__main__':
    main()
