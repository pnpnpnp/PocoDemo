# -*- encoding=utf8 -*-
__author__ = "huanghonghong"


import string

def getResName(heroName):
    file = open(r'E:\20210820_eu\conf\TabFile\specialEffect.txt',encoding='utf-16')
    result = ''
    for line in file.readlines():
        if heroName in line:
            result = line.split('\t')[2]
    file.close()
    return result

# def getTableCellData(tableName,keyword,fieldName):
#     cellData = ''
#     tableList = []
#     file = open(r'E:\20210820_eu\conf\TabFile/' + tableName + '.txt',encoding='utf-16')
#     for line in file.readlines():
#         # 过滤空行和注释行
#         if (line[0] == '/' and line[1] == '/') or line[0] == '\t':
#             continue
#         # 过滤数据类型行
#         if line.strip('\n').split('\t')[0] == 'int':
#             continue
#         tableList.append(line.strip('\n').split('\t'))
#     file.close()
#     for list in tableList:
#         if list[0].isdigit():
#             # 遍历每一列数据
#             for cell in list:
#                 # 匹配关键字
#                 if keyword in cell:
#                     # 遍历字段行
#                     for index in range(len(tableList[0])):
#                         if tableList[0][index] == fieldName:
#                             return list[index]
#         else:
#             continue
#     return 'Data Not Found'
#
# if __name__ == '__main__':
#     print(getTableCellData('specialEffect','赫拉','name'))