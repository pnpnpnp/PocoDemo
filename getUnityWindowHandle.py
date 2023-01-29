# -*- coding: utf-8 -*-

#��ע:auto_setup()�������þ�����Բ���Ҫ��window���ھ��ܻ�ȡUI�������ǵ���ؼ���������ʾ
#���ǶԿؼ�����Ϥ����Ȼ���������ڣ�Ҳ���Բο�unity.hierarchy

#���Ż�:�޷�����ͬ��Unity����
from win32gui import *
import win32gui

unityWindowList = []
def findUnityWindow(hwnd,mouse):
    if GetClassName(hwnd) == 'UnityContainerWndClass':
        unityWindowList.append(hwnd)

EnumWindows(findUnityWindow, 0)

for unityWindow in unityWindowList:
    unityWindowChildList = []
    win32gui.EnumChildWindows(unityWindow, lambda hwnd, param: param.append(hwnd), unityWindowChildList)
    for child in unityWindowChildList:
        print('ParentTitleName:' + GetWindowText(unityWindow))
        print('ClassName:' + GetClassName(child))
        print('TitleName:' + GetWindowText(child))
        print('handle:' + str(child) + '\n')