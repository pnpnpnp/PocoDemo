# -*- encoding=utf8 -*-
__author__ = "huanghonghong"

import configparser
config = configparser.ConfigParser()
config.read("config.ini")

def getCNSName(name):
    file = open(config.get('translateTable', 'translateTablePath'), encoding='utf16')
    tableList = []
    for line in file.readlines():
        tableList.append(line.strip('\n').split('\t'))
    file.close()
    for list in tableList:
        if list[1] == name:
            return list[0]
    return 'Data Not Found'

print(getCNSName('Prophet Orb'))
