# -*- coding: utf-8 -*-

#备注:auto_setup()内有设置句柄可以不需要连window窗口就能获取UI树，但是点击控件不会有提示
#除非对控件很熟悉，不然还是连窗口，也可以参考unity.hierarchy

#待优化:无法区分同名Unity窗口
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