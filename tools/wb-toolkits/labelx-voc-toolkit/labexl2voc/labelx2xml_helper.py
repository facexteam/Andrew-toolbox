# -*- coding:utf-8 -*-
import os
import sys
import json
import time
import random
from lxml import etree
import  gen_imagesets
import image_helper
import xml_helper
import labelxJson_helper
import utils
import cv2


def process_labelx_jsonFile_Fun(json_file_absolutePath=None, tempSaveDir=None, vocpath=None,renamePrefix=None):
    # 下载 对应的image,保存下载的图片到 vocpath+'/JPEGImages'
    image_helper.downloadImage_By_urllist(labelxjson=json_file_absolutePath, tempSaveDir=tempSaveDir, vocpath=vocpath)
    # 将 labelx 标注的数据 转换 pascal voc xml 文件
    # 对待下载失败的图片，添加处理方式
    xml_helper.convertLabelxJsonListToXmlFile(
        jsonlistFile=json_file_absolutePath, datasetBasePath=vocpath)
    # rename imame and xml file
    filePrefix = renamePrefix
    if not filePrefix:
        filePrefix  = "Terror-detect-"+utils.getTimeFlag(flag=1)
    res, resInfo = gen_imagesets.renamePascalImageDataSet(
        vocpath=vocpath, filePrefix=filePrefix)
    if not res:
        print(resInfo)
        resInfo = "rename pascal image error"
        return (False, resInfo)
    # 这个是生成 pascal voc 格式的数据集 xml  jpg txt
    gen_imagesets.gen_imagesets(vocpath=vocpath)
    pass


def covertLabelxMulFilsToVoc_Fun(labelxPath=None, vocResultPath=None, renamePrefix=None):
    """
        将指定目录下的所有打标过的json 文件转换成 pascal xml 格式数据
    """
    inputDir = labelxPath
    tempSaveDir = labelxPath+"-xmlNeedTempFileDir"
    vocpath = vocResultPath
    if not os.path.exists(tempSaveDir):
        os.makedirs(tempSaveDir)
    if not os.path.exists(vocpath):
        os.makedirs(vocpath)
    # 1 : mergeAllJsonListFileToOneFile 将多个jsonlist 合并成一个，并按照url 去重
    finalOneFile = labelxJson_helper.mergeAllJsonListFileToOneFile(
        inputDir=inputDir, tempSaveDir=tempSaveDir)
    # 2 : 根据整合生成的一个总文件，开始下载图片，生成 xml 文件
    process_labelx_jsonFile_Fun(
        json_file_absolutePath=finalOneFile, tempSaveDir=tempSaveDir, vocpath=vocpath, renamePrefix=renamePrefix)
    pass





def mergePascalDataset(littlePath=None, finalPath=None):
    if not os.path.exists(finalPath):
        os.makedirs(finalPath)
    if not os.path.exists(os.path.join(finalPath, 'JPEGImages')):
        os.makedirs(os.path.join(finalPath, 'JPEGImages'))
    if not os.path.exists(os.path.join(finalPath, 'Annotations')):
        os.makedirs(os.path.join(finalPath, 'Annotations'))
    if not os.path.exists(os.path.join(finalPath, 'ImageSets', 'Main')):
        os.makedirs(os.path.join(finalPath, 'ImageSets', 'Main'))
    # merge image and merge xml
    littlePath_image = os.path.join(littlePath, 'JPEGImages')
    finalPath_image = os.path.join(finalPath, 'JPEGImages')
    littlePath_image_count = utils.getFileCountInDir(littlePath_image)[0]
    littlePath_xml = os.path.join(littlePath, 'Annotations')
    finalPath_xml = os.path.join(finalPath, 'Annotations')
    littlePath_xml_count = utils.getFileCountInDir(littlePath_xml)[0]
    if littlePath_image_count != littlePath_xml_count:
        print("ERROR : %s JPEGImages-nums unequals Annotations-nums" %(littlePath))
        return "error"
    # cmdStr_cp_image = "cp %s/* %s" % (littlePath_image, finalPath_image)
    cmdStr_cp_image = "for i in `ls %s`;do cp \"%s/\"$i %s;done;" % (
        littlePath_image, littlePath_image, finalPath_image)
    # cmdStr_cp_xml = "cp %s/* %s" % (littlePath_xml, finalPath_xml)
    cmdStr_cp_xml = "for i in `ls %s`;do cp \"%s/\"$i %s;done;" % (
        littlePath_xml, littlePath_xml, finalPath_xml)
    res = os.system(cmdStr_cp_image)
    if res != 0:
        print("ERROR : %s" % (cmdStr_cp_image))
        return "error"
    else:
        print("SUCCESS : %s" % (cmdStr_cp_image))
    res = os.system(cmdStr_cp_xml)
    if res != 0:
        print("ERROR : %s" % (cmdStr_cp_xml))
        return "error"
    else:
        print("SUCCESS : %s" % (cmdStr_cp_xml))
    # merge txt file
    littlePath_main = os.path.join(littlePath, 'ImageSets', 'Main')
    finalPath_main = os.path.join(finalPath, 'ImageSets', 'Main')
    textFile_list = utils.getFileCountInDir(dirPath=littlePath_main)[1]
    for i in textFile_list:
        little_file = os.path.join(littlePath_main,i)
        final_file = os.path.join(finalPath_main, i)
        cmdStr = "cat %s >> %s" % (little_file, final_file)
        res = os.system(cmdStr)
        if res != 0:
            print("ERROR : %s" % (cmdStr))
            return 'error'
    # recode log
    record_log_file = os.path.join(finalPath,'update_log.log')
    with open(record_log_file,'a') as f:
        f.write("update info : %s add dataset ::: %s\n" % (getTimeFlag(), littlePath.split('/')[-1]))
        littlePath_readme = os.path.join(littlePath, 'readme.txt')
        littlePath_readme_dict = json.load(open(littlePath_readme,'r'))
        f.write(json.dumps(littlePath_readme_dict)+'\n')
    little_readme_file = os.path.join(littlePath, 'readme.txt')
    little_readme_file_dict = json.load(open(little_readme_file, 'r'))
    final_readme_file = os.path.join(finalPath, 'readme.txt')
    if not os.path.exists(final_readme_file):
        cmdStr = "cp %s %s" % (little_readme_file, final_readme_file)
        res = os.system(cmdStr)
        if res != 0:
            return 'error'
    else:
        final_readme_file_dict = json.load(open(final_readme_file, 'r'))
        final_imageInfo_dict = final_readme_file_dict['imageInfo']
        little_imageInfo_dict = little_readme_file_dict['imageInfo']
        for key in final_imageInfo_dict.keys():
            if key == "date":
                final_imageInfo_dict[key] = getTimeFlag()
            if key == "dataInfo":
                for i in little_imageInfo_dict[key]:
                    final_imageInfo_dict[key].append(i)
            if key == "author":
                final_imageInfo_dict[key] = 'Ben'
            elif key in ['total_num', 'trainval_num', 'test_num']:
                final_imageInfo_dict[key] = final_imageInfo_dict[key] + \
                    little_imageInfo_dict[key]
        final_bboxInfo_dict = final_readme_file_dict['bboxInfo']
        little_bboxInfo_dict = little_readme_file_dict['bboxInfo']
        for i_key in final_bboxInfo_dict.keys():
            if isinstance(final_bboxInfo_dict[i_key],dict):
                for i_i_key in final_bboxInfo_dict[i_key].keys():
                    if isinstance(final_bboxInfo_dict[i_key][i_i_key],int):
                        if i_i_key in little_bboxInfo_dict[i_key]:
                            final_bboxInfo_dict[i_key][i_i_key] += little_bboxInfo_dict[i_key][i_i_key]
                        else:
                            final_bboxInfo_dict[i_key][i_i_key] += 0
        with open(final_readme_file,'w') as f:
            json.dump(final_readme_file_dict, f, indent=4)
    pass


def getTimeFlag():
    return time.strftime("%Y-%m-%d-%H-%M-%s", time.localtime())

# 根据 图片 和 xml 文件 生成 Main 目录下的 trainval.txt  test.txt
def gen_imageset_Fun(vocPath=None):
    gen_imagesets.gen_imagesets(vocpath=vocPath)
    pass

# 统计数据集中的bbox的信息
def statisticBboxInfo_Fun(vocPath=None):
    mainDir = os.path.join(vocPath, 'ImageSets/Main')
    if not os.path.exists(mainDir):
        print("ImageSets/Main  not exist , so first create")
        gen_imageset_Fun(vocPath=vocPath)
    xmlPath = os.path.join(vocPath, 'Annotations')
    trainval_file = os.path.join(vocPath, 'ImageSets/Main', 'trainval.txt')
    trainval_file_res_dict = gen_imagesets.statisticBboxInfo(
        imagelistFile=trainval_file, xmlFileBasePath=xmlPath, printFlag=True)
    test_file = os.path.join(vocPath, 'ImageSets/Main', 'test.txt')
    test_file_res_dict = gen_imagesets.statisticBboxInfo(
        imagelistFile=test_file, xmlFileBasePath=xmlPath, printFlag=True)
    # write the statistic bbox info to file
    statisLogFile = os.path.join(vocPath,'statistic-bbox-log.log')
    with open(statisLogFile,'a') as f:
        f.write('*'*10+getTimeFlag()+'*'*10+'\n')
        keys = trainval_file_res_dict.keys() if len(trainval_file_res_dict.keys()) > len(
            test_file_res_dict.keys()) else test_file_res_dict.keys()
        for i in sorted(keys):
            count = 0
            if i in trainval_file_res_dict.keys():
                count += trainval_file_res_dict.get(i)
            if i in test_file_res_dict.keys():
                count += test_file_res_dict.get(i)
            line = "%s\t%d\n" % (i.ljust(30,' '),count)
            f.write(line)
    pass


def drawImageWithBbox(absoluteImagePath=None, absoluteXmlFilePath=None, savePath=None):
    print("absoluteImagePath is %s ;\tabsoluteXmlFilePath is %s" %
          (absoluteImagePath, absoluteXmlFilePath))
    print("savePath : %s" % (savePath))
    tree = etree.parse(absoluteXmlFilePath)
    rooTElement = tree.getroot()
    object_list = []
    for child in rooTElement:
        if child.tag == "filename":
            if child.text != absoluteImagePath.split('/')[-1]:
                print("%s != %s" % (child.text, absoluteImagePath))
        elif child.tag == "object":
            one_object_dict = {}
            one_object_dict['name'] = child.xpath('name')[0].text
            one_object_dict['xmin'] = child.xpath(
                'bndbox')[0].xpath('xmin')[0].text
            one_object_dict['ymin'] = child.xpath(
                'bndbox')[0].xpath('ymin')[0].text
            one_object_dict['xmax'] = child.xpath(
                'bndbox')[0].xpath('xmax')[0].text
            one_object_dict['ymax'] = child.xpath(
                'bndbox')[0].xpath('ymax')[0].text
            object_list.append(one_object_dict)
            pass
        pass
    color_black = (0, 0, 0)
    im = cv2.imread(absoluteImagePath)
    for object in object_list:
        color = (random.randint(0, 256), random.randint(
            0, 256), random.randint(0, 256))
        cv2.rectangle(im, (int(object.get('xmin')), int(object.get('ymin'))), (int(
            object.get('xmax')), int(object.get('ymax'))), color=color, thickness=1)
        cv2.putText(im, '%s' % (object.get('name')), (int(object.get('xmin')), int(object.get(
            'ymin')) + 10), color=color_black, fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5)
    cv2.imwrite(savePath, im)
    pass
    pass

def drawImageWithBbosFun(vocPath=None):
    xmlFilePath = os.path.join(vocPath, 'Annotations')
    imageFilePath = os.path.join(vocPath, 'JPEGImages')
    drawImageSavePath = vocPath+'-draw'
    if not os.path.exists(drawImageSavePath):
        os.makedirs(drawImageSavePath)
    xmlList = os.listdir(xmlFilePath) # get xml file
    random_xml_list = random.sample(xmlList, len(xmlList)//1000)
    for xml_name in random_xml_list:
        xmlFile = os.path.join(xmlFilePath, xml_name)
        imageFile = os.path.join(imageFilePath, xml_name[:xml_name.rfind('.')]+'.jpg')
        saveImageFile = os.path.join(
            drawImageSavePath, xml_name[:xml_name.rfind('.')]+'.jpg')
        drawImageWithBbox(absoluteImagePath=imageFile,
                          absoluteXmlFilePath=xmlFile, savePath=saveImageFile)
        pass
    pass
    pass

