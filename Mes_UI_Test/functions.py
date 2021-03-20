# -*- coding:utf-8 -*-
from config import CONFIG
import random
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from traceback import format_exc

# 查找左侧导航栏
def find_title(driver,level,data):
    # 1级导航栏
    if level == 1:
        title1_list = driver.find_elements_by_xpath('//div[@class="el-submenu__title"]')
        for t in title1_list:
            # 如果是需要找的标题文本则返回这个元素
            if t.find_element_by_xpath('./span').get_attribute('innerText').strip() == data:
                return t
    # 2级导航栏
    elif level == 2:
        title2_list = driver.find_elements_by_xpath('//li[@class="el-menu-item is-active" or @class="el-menu-item"]')
        for t in title2_list:
            # 如果是需要找的标题文本则返回这个元素
            if t.find_element_by_xpath('./span').get_attribute('innerText').strip() == data:
                return t
    # 不是1和2的话则直接报错
    else:
        raise Exception('找不到%s级导航栏%s'%(str(level),data))
    # 找不到所找元素的话报错
    raise Exception('找不到%s级导航栏%s' % (str(level), data))


# 等待可点击再点击
def click(e,times=5,sleep=0.5):
    '''
    等待点击元素
    :param e: 可点击元素
    :param time: 总等待时间
    :param sleep: 睡眠时间
    :return: None
    '''
    new_time = time.time()
    while (time.time()-new_time)<times:
        if e.is_enabled():
            e.click()
            break
        else:
            time.sleep(sleep)
    else:
        raise Exception('点击超时')

# 获取异常详细信息
def getError():
    return format_exc()

# 截图
def screenShot(data,info):
    '''
    截图保存
    :param data:driver,CONFIG
    :param info:信息
    :return: None
    '''
    try:
        data[0].save_screenshot(
            data[1].get('screenshot_dir','./')+
            time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))+
            info+'.png')
    except:
        outPut('保存图片失败')

# 输出操作
def outPut(data,level = 'INFO'):
    '''
    log输出
    :param data:文本
    :param level:输出等级(default'INFO')
    :return:
    '''
    print(data)

# 显式等待元素
def waitFind(driver,by,data):
    '''
    睡眠0.5秒，等待5秒频率0.5秒查找元素
    :param driver: driver
    :param by: 查找条件类型
    :param data: 条件
    :return: 返回元素
    '''
    time.sleep(0.5)
    element = WebDriverWait(driver, CONFIG.get('explicit_time',5), CONFIG.get('explicit_flash',0.5)).until(EC.presence_of_element_located((by,data)))
    return element

# 获取随机字符
class Getdata:
    # 初始化
    def __init__(self):
        self.text = ""

    # a-Z
    def get_aZ(self,count=1):
        for i in range(count):
            self.text += chr(random.randint(ord('A'),ord('z')))
        return self

    # 0-9
    def get_number(self,count=1):
        for i in range(count):
            self.text += chr(random.randint(ord('0'),ord('9')))
        return self

    # `~!@#$%^&*()_+{}|:"<>?-=[]\;',./
    def get_sign(self,count=1):
        sign = r'''`~!@#$%^&*()_+{}|:"<>?-=[]\;',./'''
        lens = len(sign) - 1
        for i in range(count):
            self.text += sign[random.randint(0,lens)]
        return self

    # 中文
    def get_chinese(self,count=1):
        for i in range(count):
            self.text += chr(random.randint(19968,40869))
        return self

    # 完全随机字符
    def get_allrandom(self,count=1):
        for i in range(count):
            self.text += chr(random.randint(1,40869))
        return self
