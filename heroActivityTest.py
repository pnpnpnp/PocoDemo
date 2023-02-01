# -*- encoding=utf8 -*-
__author__ = "huanghonghong"

# PythonVersion = 3.6.8
# AirtestIDEVersion = 1.2.13
# PythonDependencyLibrary: airtest、pocoui、openpyxl、configparser
# TestPlatform: unity3d v2017.4.33
# ScreenResolution = 1080*2340
# 无嵌入连接

from airtest.core.api import *
from poco.drivers.unity3d import *
from poco.freezeui import *
from airtest.cli.parser import cli_setup

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=["Windows:///19732712"])

import configparser

import valueTable as vt
import configTable as ct
import translateTable as tt

############################-------------初始化-------------############################

poco = UnityPoco()
# freeze() --获取当前UI树的一个静态副本
# 不过这种方法也是有局限性的，那就是如果是频繁切换界面，并且在当前界面的操作很少的话，不推荐使用
freeze = poco.freeze()

#是否翻译
isTranslate = False

#定位活动界面的字典（待优化，考虑遍历初始化Dict或读配置）
activityDict = {'精英召唤':'01','礼包':'02','抽卡主题任务':'03','每日登录':'04','大富翁':'11','活跃主题任务':'12','高抽特权卡':'13'}

############################-------------常用方法-------------############################

dollarToRMBDict = {'$4.99':'30','$9.99':'68','$14.99':'98','$19.99':'128','$29.99':'198','$49.99':'328','$69.99':'448','$99.99':'648'}

#自定义断言
def assertEqual_canPass(first,second,msg):
    try:
        assert_equal(first,second)
    except AssertionError:
        print(msg)
        pass

#根据道具tips获取道具名字
def getItemName(item):
    #一般情况点击icon属性都能弹出tips
    item.offspring('icon').click()
    itemName = ''
    #一般道具
    if poco('ItemInfoUI').exists():
        itemName = poco('ItemInfoUI').child('infoPanel').child('name').get_text()
        poco('ItemInfoUI').focus([0.5,1.5]).click()
    #自选道具
    elif poco('UseTabItemPickOneUI').exists():
        itemName = poco('UseTabItemPickOneUI').child('ItemInfo').child('name').get_text()
        poco('UseTabItemPickOneUI').child('layoutContent').child('btn').click()
    #符文道具
    elif poco('RuneTipSimpleUI').exists():
        itemName = poco('RuneTipSimpleUI').child('top').child('name').get_text()
        poco('RuneTipSimpleUI').focus([0.5,1.5]).click()
    #英雄
    elif poco('HeroTipUI').exists():
        itemName = poco('HeroTipUI').child('name').get_text()
        poco('HeroTipUI').focus([0.5,2.5]).click()
    #待补充..................
    
    if itemName == '':
        print('调用getItemName失败，点击道具tips获取不到道具名字')

    if isTranslate:
        return tt.getCNSName(itemName)

    return itemName

#获取道具数量
def getItemNum(item):
    itemNum = item.offspring('num').get_text()
    #部分可能不展示数量
    if itemNum == '':
        return '1'
    if 'K' in itemNum:
        return itemNum.strip('K') + '000'
    return itemNum
    
#跳转到指定的活动界面
def gotoActivityInterface(activityName):
    x = activityDict[activityName][0]
    y = activityDict[activityName][1]
    poco('ComboActivityBaseUI').offspring('group' + x).child('item(Clone)').focus([0.5,1]).click()
    poco('ComboActivityBaseUI').offspring('item' + y).focus([0.5,1]).click()

#对比两个List打印差异
def compareResult(resultName,compareList,beCompareList):
    surplusList = list(set(compareList) - set(beCompareList))
    missingList = list(set(beCompareList) - set(compareList))
    print(resultName)
    if len(compareList) == 0 or len(beCompareList) == 0:
        print('验证失败，有一个List为空')
        return
    if len(surplusList) != 0:
        print('多出的：')
        print(surplusList)
    if len(missingList) != 0:
        print('缺少的：')
        print(missingList)
    if len(surplusList) == 0 and len(missingList) == 0:
        print('验证成功')

#验证道具跳转路径（检验跳转后的tabList名字，仅活动相关道具）
def checkJump(curGotoInterfaceName):
    for item in poco('ComboActivityBaseUI').child('tabList').children():
        if item.child('select').exists():
            assertEqual_canPass(item.child('Text').get_text(),curGotoInterfaceName,'道具跳转名字不对')
            break

#获取价格对应rmb价格
def getCNSPrice(price):
    if '$' in price:
        return dollarToRMBDict[price]
    else:
        return "".join(list(filter(str.isdigit,price)))

#gm--server
def doGMServer(content):
    keyevent('{F2}')
    poco('GMUI').child('input').child('Placeholder').click()
    
    #确保输入的括号是英文的
    keyevent('+9')
    if poco('GMUI').child('input').child('Text').get_text() == '（':
        keyevent('{VK_SHIFT}')
        keyevent('{BACKSPACE}')
    else:
        keyevent('{BACKSPACE}')
    
    keyevent(content)
    poco('GMUI').child('btnserver').click()
    poco('GMUI').child('btncancel').click()

############################-------------精英召唤用例-------------############################
def eliteCallTestCase():
    gotoActivityInterface('精英召唤')
    # 1、验证投放的英雄、主打英雄是否正确

    #遍历并记录精英召唤中的所有英雄和主打英雄
    compareList = [poco('EliteCallUI').offspring('heroInfo').offspring('Text').get_text() + ',' + '1']
    for i in range(len(poco('EliteCallUI').child('heroGroup').child('hero').children()) - 1):
        poco('EliteCallUI').child('changeBtn').child('rightBtn').focus([0,0.5]).click()
        heroName = poco('EliteCallUI').offspring('heroInfo').offspring('Text').get_text()
        compareList.append(heroName)

    #读数值表中的投放英雄
    beCompareList = vt.getValueTableData('投放英雄',['英雄名称','本期主打英雄'])
    for i in range(len(beCompareList)):
        if '5星' in beCompareList[i]:
            beCompareList[i] = beCompareList[i].lstrip('5星')

    #对比
    compareResult('投放英雄验证：',compareList,beCompareList)

    # 2、抽奖道具跳转

    poco('EliteCallUI').offspring('CMCurrencyItem').child('icon').click()
    poco('ItemInfoUI').offspring('Text').focus([0.5,2]).click()

    #遍历道具所有跳转途径
    gatewayNum = len(poco('GatewayUI').offspring('content').children())
    for i in range(gatewayNum):

        if i == 3:
            poco('GatewayUI').swipe([0,-0.5])
        curGroup = poco('GatewayUI').offspring('content').child('group' + str(i))
        curGotoInterfaceName = curGroup.offspring('name').get_text()
        curGroup.offspring('btn').focus([0.5,0.8]).click()

        checkJump(curGotoInterfaceName)

        #返回精英召唤抽奖道具跳转界面
        gotoActivityInterface('精英召唤')
        if i == gatewayNum - 1:
            break
        poco('EliteCallUI').offspring('CMCurrencyItem').child('icon').click()
        poco('ItemInfoUI').offspring('Text').focus([0.5,2]).click()

    # 3、验证奖池

    #打开奖池界面
    poco('EliteCallUI').child('awardDetailBtn').child('Text').click()

    compareList = []

    groups = poco('EliteCallAwardDetailUI').offspring('content').children()
    for group in groups:
        items = group.children()
        for item in items:
            compareList.append(getItemName(item) + ',' + getItemNum(item))

    beCompareList = vt.getValueTableData('精英召唤奖励',['道具','数量'])

    compareResult('精英召唤奖池验证：',compareList,beCompareList)

    #关闭奖池界面
    poco('ComboActivityTopBaseUI').child('close').click()

    # 4、英雄预览

    #进入英雄预览
    poco('EliteCallUI').child('previewBtn').child('Text').click()

    #等待
    sleep(6)

    #不太好的方法：根据CacheEffectRoot里的资源名称来判断up的英雄是否在战斗预览中
    resName = ct.getResName(vt.getValueTableData('投放英雄',['英雄名称'])[0].lstrip('5星'))
    if poco('CacheEffectRoot').child(resName).exists():
        print('战斗预览中有主打英雄')

    #退出英雄预览
    poco('BattleTopInfoUI').child('exitBtn').child('Text').click()

############################-------------礼包用例-------------############################
def superValueTestCase():
    # 1、礼包奖励，数量，限购，价格
    # 2、购买礼包

    #注意：可能有礼包过多没加载出来的group

    gotoActivityInterface('礼包')

    #记录限购为1的礼包数量
    limitEqualToOneValueCount = 0

    compareList = []

    for i in range(len(poco('SuperValueUI').offspring('content').children())):
        index1 = 'group' + str(i - limitEqualToOneValueCount)
        curGroup = poco('SuperValueUI').offspring(index1)
        curValueLimit = curGroup.offspring('limit').get_text()
        curValuePrice = curGroup.offspring('price').get_text()

        compareStr = "".join(list(filter(str.isdigit,curValueLimit))) + ',' + getCNSPrice(curValuePrice) + ','

        for j in range(len(poco('SuperValueUI').offspring(index1).offspring('awards').children())):
            index2 = 'Item_' + str(j + 1)
            curItem = poco('SuperValueUI').offspring(index1).offspring(index2)
            compareStr = compareStr + getItemName(curItem) + ',' + getItemNum(curItem) + ','

        compareList.append(compareStr.strip(','))
        #购买礼包
        poco('SuperValueUI').offspring(index1).offspring('btns').focus([0.5,1]).click()
        if not poco('ReceiveItemUI').exists():
            print('购买礼包失败')

        #关闭奖励弹窗
        poco('ComboActivityTopBaseUI').child('close').click()

        #取消vip升级弹窗
        if poco('VipLevelUpUI').exists():
            #动画
            sleep(5)
            poco('ComboActivityTopBaseUI').child('close').click()

        #限购为1的礼包购买完后group数会置底,value的index不增加
        if "".join(list(filter(str.isdigit,curValueLimit))) == '1':
            limitEqualToOneValueCount = limitEqualToOneValueCount + 1

    beCompareList = vt.getValueTableData('礼包',['最大购买个数','礼包价格/RMB','奖励1','数量','奖励2','数量','奖励3','数量','奖励4','数量'])

    compareResult('礼包验证：',compareList,beCompareList)

############################-------------抽卡主题任务用例-------------############################
def themeTaskTestCase():
    # 1、任务描述，奖励，数量

    #抽卡主题任务完成累计次数
    gotoActivityInterface('抽卡主题任务')

    compareList_task = []
    compareList_award = []

    heroGroup = vt.getValueTableData('投放英雄',['英雄名称'])
    for hero in range(len(heroGroup)):
        if '5星' in heroGroup[hero]:
            heroGroup[hero] = heroGroup[hero].lstrip('5星')

    for group in poco('ThemeTaskActivityUI').offspring('content').children():

        #任务描述
        taskDesc = group.offspring('condition').get_text()
        for j in range(len(heroGroup)):
            if heroGroup[j] not in taskDesc:
                print('当期精英召唤投放的英雄不在抽卡主题任务描述中')
        #进度描述
        progressDesc = group.offspring('progress').get_text()

        if "".join(list(filter(str.isdigit,taskDesc))) != progressDesc.lstrip('0/'):
            print('任务描述与进度描述不相符，取进度描述作为实际')
        compareList_task.append(progressDesc.lstrip('0/'))

        #任务奖励、数量
        curItem = group.offspring('CMItem')
        compareList_award.append(getItemName(curItem) + ',' + getItemNum(curItem))

        #任务跳转
        group.offspring('btn').focus([0.5,0.8]).click()
        if not poco('EliteCallUI').exists():
            print('抽卡主题任务跳转不对')
        gotoActivityInterface('抽卡主题任务')

    beCompareList_task = vt.getValueTableData('抽卡主题任务',['任务内容'])
    beCompareList_award = vt.getValueTableData('抽卡主题任务',['奖励1','数量','奖励2','数量'])

    for i in range(len(beCompareList_task)):
        taskDigit = "".join(list(filter(str.isdigit,beCompareList_task[i])))
        beCompareList_task[i] = taskDigit

    compareResult('抽卡主题任务描述验证：',compareList_task,beCompareList_task)
    compareResult('抽卡主题任务奖励验证：',compareList_award,beCompareList_award)

    # 2、抽英雄，看进度是否增加

    gotoActivityInterface('精英召唤')

    #加砖石
    poco('ComboActivityBaseUI').offspring('gold').child('icon').focus([0.5,2]).click()
    poco('ItemInfoUI').offspring('gmGet').focus([0.5,2]).click()
    poco('ComboActivityTopBaseUI').child('close').click()

    #加抽奖道具
    poco('EliteCallUI').offspring('CMCurrencyItem').child('icon').click()
    poco('ItemInfoUI').offspring('gmGet').focus([0.5,2]).click()
    poco('ComboActivityTopBaseUI').child('close').click()

    heroGroup = vt.getValueTableData('投放英雄',['英雄名称'])
    for hero in range(len(heroGroup)):
        if '5星' in heroGroup[hero]:
            heroGroup[hero] = heroGroup[hero].lstrip('5星')

    for i in range(len(heroGroup)):
        switchCount = 0
        #切换英雄
        while poco('EliteCallUI').offspring('heroInfo').offspring('Text').get_text() != heroGroup[i]:
            poco('EliteCallUI').offspring('rightBtn').focus([0,0.5]).click()
            switchCount = switchCount + 1
            if switchCount >= len(heroGroup):
                print('精英召唤找不到数值表中的投放英雄')
        #设置为心仪英雄
        if poco('EliteCallUI').offspring('setBtn').exists():
            poco('EliteCallUI').offspring('setBtn').click()
            poco('AlertUI').child('yesBtn').focus([0.5,1]).click()
        #十连抽直到出英雄为止
        poco('EliteCallUI').offspring('tenBtn').click()
        #抽卡动画
        sleep(5)
        while not poco('GetHeroUI').exists():
            poco('EliteCallAwardUI').offspring('againBtn').focus([0.5,1]).click()
            #抽卡动画
            sleep(5)
        assertEqual_canPass(poco('GetHeroUI').offspring('name').get_text(),heroGroup[i],'抽到的英雄不是设置的心仪英雄')
        poco('GetHeroUI').click()
        poco('EliteCallAwardUI').offspring('okBtn').focus([0.5,1]).click()
        #去任务界面确认进度是否增加
        gotoActivityInterface('抽卡主题任务')
        lastGroup = poco('ThemeTaskActivityUI').offspring('group4')
        lastProgress = lastGroup.offspring('progress').get_text()
        assertEqual_canPass(lastProgress,str(i + 1) + '/9','抽到英雄后任务进度没增加')
        if i == len(heroGroup) - 1:
            break
        lastGroup.offspring('btn').focus([0.5,0.8]).click()

############################-------------每日登录用例-------------############################
def dailyTaskTestCase():
    gotoActivityInterface('每日登录')

    # 1、验证奖励
    compareList = []
    for group in poco('ThemeTaskActivityUI').offspring('sv').child('content').children():
        curTaskContent = group.offspring('condition').get_text()
        curItem = group.offspring('CMItem')
        compareList.append(curTaskContent + ',' + getItemName(curItem) + ',' + getItemNum(curItem))

    beCompareList = vt.getValueTableData('每日任务',['任务内容','奖励1','数量'])

    compareResult('每日任务验证：',compareList,beCompareList)

    # 2、领取登入游戏奖励
    poco('ThemeTaskActivityUI').offspring('group0').offspring('get').focus([0.5,1]).click()
    if not poco('ReceiveItemUI').exists():
        print('领取登入游戏奖励失败')
    poco('ComboActivityTopBaseUI').child('close').click()

    # 3、日常活跃任务跳转，领取奖励，返回，验证活跃度是否增加
    activeTaskGroupName = ''
    for group in poco('ThemeTaskActivityUI').offspring('sv').child('content').children():
        if "".join(list(filter(str.isdigit,group.offspring('condition').get_text()))) != '':
            activeTaskGroupName = group.attr('name')
            group.offspring('btn').focus([0.5,1]).click()
            break
    poco('TaskDailyUI').offspring('group0').offspring('getBtn').focus([0.5,1]).click()
    #返回活动界面
    poco('festivalActivity').focus([0.5,1]).click()
    poco('festivalActivity').focus([0.5,1]).click()
    progressStr = poco('ThemeTaskActivityUI').offspring(activeTaskGroupName).offspring('progress').get_text()
    assertEqual_canPass(progressStr,'5/100','活动每日任务活跃度没增加')

############################-------------大富翁用例-------------############################
def monoPolyTestCase():
    # 1、购买高级骰子

    gotoActivityInterface('大富翁')

    #gm清空背包
    doGMServer('GM_ClearPackage+91,3,4,5,6,7+0')

    #加砖石
    poco('ComboActivityBaseUI').offspring('gold').child('icon').focus([0.5,2]).click()
    poco('ItemInfoUI').offspring('gmGet').focus([0.5,2]).click()
    poco('ComboActivityTopBaseUI').child('close').click()

    #切换到高级骰子购买一次
    poco('MonoPolyActivityUI').offspring('add').focus([-0.1,0.5]).click()
    if not poco('BuyItemUI').exists():
        poco('ComboActivityTopBaseUI').child('close').click()
        poco('MonoPolyActivityUI').offspring('small').click()
        poco('MonoPolyActivityUI').offspring('add').focus([-0.1,0.5]).click()
    poco('BuyItemUI').child('btn').focus([0.5,1]).click()
    if not poco('ReceiveItemUI').exists():
        print('购买高级骰子失败')
    poco('ComboActivityTopBaseUI').child('close').click()
    curHighDiceNum = poco('MonoPolyActivityUI').offspring('CMCurrencyItem').child('num').get_text()
    assertEqual_canPass(curHighDiceNum,'1','购买一次高级骰子后,数量没增加')

    # 2、骰子跳转

    #加普通骰子
    poco('MonoPolyActivityUI').offspring('small').click()
    poco('MonoPolyActivityUI').offspring('CMCurrencyItem').child('icon').click()
    poco('ItemInfoUI').offspring('gmGet').focus([0.5,2]).click()
    poco('ComboActivityTopBaseUI').child('close').click()

    #去背包界面进行跳转验证
    poco('ComboActivityTopBaseUI').child('close').click()
    poco('MainUIBottomBtnUI').offspring('package').click()
    for item in poco('PackageUI').child('sv').offspring('group0').children():
        item.click()
        poco('ItemInfoUI').offspring('Text').focus([0.5,2]).click()
        diceGotoInterfaceName = poco('GatewayUI').offspring('group0').offspring('name').get_text()
        poco('GatewayUI').offspring('group0').offspring('btn').focus([0.5,0.8]).click()

        checkJump(diceGotoInterfaceName)

        poco('ComboActivityTopBaseUI').child('close').click()

    #回到大富翁界面
    poco('MainUIBottomBtnUI').offspring('city').click()
    poco('festivalActivity').focus([0.5,1]).click()
    gotoActivityInterface('大富翁')

    # 3、关卡奖励

    compareList = []

    #坑位
    for i in range(len(poco('MonoPolyActivityUI').child('posList').children())):
        pos = poco('MonoPolyActivityUI').child('posList').child('posItem ' + '(' + str(i + 1) + ')')
        if i == 29:
            pos = poco('MonoPolyActivityUI').child('posList').child('posItem')
        #pos为怪物
        if pos.child('anim').exists():
            pos.child('anim').click()
            compareStr = ''
            for group in poco('MonoPolyChallengeUI').offspring('award').offspring('content').children():
                compareStr = compareStr + getItemName(group) + ',' + getItemNum(group) + ','
            compareList.append(compareStr.strip(','))
            #关闭challenge界面
            poco('MonoPolyActivityUI').offspring('ponitBtn').click()
            continue
        #pos为奖励
        compareList.append(getItemName(pos) + ',' + getItemNum(pos))

    #boss
    poco('MonoPolyActivityUI').offspring('ponitBtn').click()
    poco('MonoPolyMonsterPointUI').child('item').click()
    compareStr = ''
    for group in poco('MonoPolyChallengeUI').offspring('award').offspring('content').children():
        compareStr = compareStr + getItemName(group) + ',' + getItemNum(group) + ','
    compareList.append(compareStr.strip(','))
    #关闭据点界面
    poco('MonoPolyChallengeUI').offspring('okBtn').focus([0.5,1]).click()
    poco('MonoPolyActivityUI').offspring('ponitBtn').click()

    beCompareList = vt.getValueTableData('大富翁关卡奖励',['奖励1','数量','奖励2','数量','奖励3','数量'])

    compareResult('大富翁关卡奖励验证：',compareList,beCompareList)

    # 4、怪物（废弃，不需要验证）

############################-------------活跃主题任务用例-------------############################
# 1、验证阶段奖励
def activeTaskTestCase():
    gotoActivityInterface('活跃主题任务')

    compareList = []

    for box in poco('ActiveTaskActUI').offspring('boxList').children():
        box.offspring('Image').click()
        compareStr = box.offspring('num').get_text() + ','
        for item in poco('AwardPreviewUI').offspring('group0').children():
            compareStr = compareStr + getItemName(item) + ',' + getItemNum(item) + ','
        compareList.append(compareStr.strip(','))
        poco('AwardPreviewUI').child('okBtn').focus([0.5,1]).click()

    beCompareList = vt.getValueTableData('阶段奖励',['活跃度目标','奖励1','数量','奖励2','数量','奖励3','数量'])

    compareResult('阶段奖励验证：',compareList,beCompareList)

    # 2、领取活跃道具，看活跃进度是否增加
    poco('ActiveTaskActUI').offspring('taskList').offspring('group0').child('taskItem(Clone)')[0].child('CMTaskState').click()
    poco('ComboActivityTopBaseUI').child('close').click()
    activeTotal = poco('ActiveTaskActUI').offspring('state').child('num').get_text()
    assertEqual_canPass(activeTotal,'10','领取活跃道具，活跃度没有增加')

    # 3、活跃道具跳转

    #gm清空背包
    doGMServer('GM_ClearPackage+91,3,4,5,6,7+0')

    #加活跃道具
    poco('ActiveTaskActUI').offspring('taskList').offspring('group0').child('taskItem(Clone)')[0].child('CMItem').click()
    poco('ItemInfoUI').offspring('gmGet').focus([0.5,2]).click()
    poco('ComboActivityTopBaseUI').child('close').click()

    #去背包界面进行跳转验证
    poco('ComboActivityTopBaseUI').child('close').click()
    poco('MainUIBottomBtnUI').offspring('package').click()
    poco('PackageUI').child('sv').offspring('group0').child('item(Clone)')[0].click()
    poco('ItemInfoUI').offspring('Text').focus([0.5,2]).click()
    activeItemInterfaceName = poco('GatewayUI').offspring('group0').offspring('name').get_text()
    poco('GatewayUI').offspring('group0').offspring('btn').focus([0.5,0.8]).click()
    checkJump(activeItemInterfaceName)

    # 4、领取阶段奖励
    for box in poco('ActiveTaskActUI').offspring('boxList').children():
        if not box.child('canGetSfx').exists():
            print('加了活跃道具后，奖励仍不可领取')
            break
        else:
            box.offspring('Image').click()
            poco('ComboActivityTopBaseUI').child('close').click()

############################-------------高抽特权卡用例-------------############################
def highDrawPrivilegeTestCase():
    # 1、价格验证
    gotoActivityInterface('高抽特权卡')
    highDrawPrice = poco('TimeLimitWeeklyUI').offspring('label').get_text()
    valueTablePrice = vt.getValueTableCellData(vt.highDrawPrivilegeCardPriceIndex)
    assertEqual_canPass(getCNSPrice(highDrawPrice),valueTablePrice,'高抽特权卡价格不对')

    # 2、高抽数量验证

    compareList = []

    for i in range(len(poco('TimeLimitWeeklyUI').offspring('group').children())):
        index = 'item (' + str(i + 1) + ')'
        curItemNum = poco('TimeLimitWeeklyUI').offspring('group').child(index).offspring('num').get_text()
        compareList.append(curItemNum)

    beCompareList = vt.getValueTableData('高抽特权卡',['高抽'])

    compareResult('高抽特权卡数量验证：',compareList,beCompareList)

    # 3、购买高抽特权卡

    poco('TimeLimitWeeklyUI').offspring('btn').click()
    #取消vip升级弹窗
    if poco('VipLevelUpUI').exists():
        #动画
        sleep(5)
        poco('ComboActivityTopBaseUI').child('close').click()
    if not poco('TimeLimitWeeklyUI').offspring('getBtn').exists():
        print('高抽特权卡购买失败')
    poco('TimeLimitWeeklyUI').offspring('getBtn').click()
    if not poco('ReceiveItemUI').exists():
        print('高抽特权卡领取奖励失败')
    #关闭奖励弹窗
    poco('ComboActivityTopBaseUI').child('close').click()

    # 4、验证奖励道具是否是高抽（暂时想不到好的解耦的方法）

############################-------------全民竞技-------------############################
# 1、英雄库
# 2、首达奖励
# 3、排名奖励
# 4、每日奖励
# 5、购买挑战次数
# 6、挑战一次


############################-------------其他-------------############################
# 1、新英雄图鉴
# 2、活动开启条件（开服天数没有限制）
# 3、活跃任务模板不能影响正在开的活跃任务模板
# 4、验证活动专属道具是否正确（texture、名字等）
# 5、活跃主题任务刷新
# 6、每日登录刷新
# 7、回收道具


############################-------------执行用例-------------############################

# #从主界面进入活动
poco('festivalActivity').focus([0.5,1]).click()

print(vt.getValueTableData('精英召唤奖励',['道具','数量']))
eliteCallTestCase()
# superValueTestCase()
# themeTaskTestCase()
# dailyTaskTestCase()
# monoPolyTestCase()
# activeTaskTestCase()




