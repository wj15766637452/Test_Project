# -*- coding:utf-8 -*-
import pytest
from functions import *
from selenium.webdriver.common.by import By

# 查找工艺 or 指定工艺
class Test_tech1():

    # 进入工艺页面
    @pytest.mark.run(order = 1)
    def test_tech_in(self,data):
        # 如果已经指定了工艺
        if data[1].get('select_tech',0):
            # 判断是否每个参数都有了，都有的话则直接断言成功
            if data[1]['wip_code'] and data[1]['wip_version'] and data[1]['device_group'] and data[1]['yield'] and data[1]['tech_version']:
                assert 1
                return

        # 进入工艺页面
        try:
            # 点击工艺管理
            find_title(data[0],1,'工艺管理').click()
            # 点击工艺编写
            find_title(data[0],2, '工艺编写').click()
            # 断言是否在工艺编写页面
            waitFind(data[0], By.XPATH,'//span[@class="tags-view-item router-link-exact-active router-link-active active" and contains(text(),"工艺编写")]')

        except Exception as e:
            assert 0,'进入工艺页面失败：' + getError()
        else:
            assert 1


    # 获取工艺
    @pytest.mark.run(order = 2)
    def test_selectTech(self,data):
        '''
        判断是否指定工艺
        是1：查找是否有该工艺
        不是0：默认使用第一个正本工艺
        updateCONFIG的参数
        'assign_tech':0,# 是否指定工艺
        'wip_code':'',# 指定的半成品编号
        'wip_version':0,# 指定的半成品编号版本
        'device_group':'',# 指定的生产线编号
        'yield':0,# 指定的产量
        '''
        # 指定工艺
        if data[1].get('select_tech',0):
            # 断言是否个参数都有了
            assert data[1]['wip_code'] and data[1]['wip_version'] and data[1]['device_group'] and data[1]['yield'] and data[1]['tech_version'], '指定工艺失败'


        # 不指定工艺找第一个正本工艺
        else:
            try:
                # import time
                # time.sleep(5)
                # 获取字段列表元素
                title_col_e = data[0].find_elements_by_xpath("//thead[@class='has-gutter']/tr/th")
                # 字段所在的下标
                title_col = dict()
                i = 0
                for e in title_col_e:
                    title_col[e.get_attribute('innerText').strip()] = i
                    i += 1

                # 判断能否点击下一页，能的话点击下一页
                while True:
                    # 所有的工艺
                    tech_list_e = data[0].find_elements_by_xpath('//*[@id="app"]/div/div[2]/div[2]/section/div/div[2]/div[2]/div[3]/table/tbody/tr')
                    l_list = []
                    # 遍历每一行
                    for l in tech_list_e:
                        i = 0
                        # 遍历每一个列
                        for e in l.find_elements_by_xpath('./td'):
                            if i!= title_col['是否启用']:
                                l_list.append(e.get_attribute('innerText').strip())
                            else:
                                l_list.append(str(e.find_element_by_xpath('./div/div').get_attribute('aria-checked')).strip())
                            i += 1
                        # 判断这行是否为需要的工艺
                        if l_list[title_col['工艺正本']] == '正本' and l_list[title_col['状态']] == '审核通过' and l_list[title_col['是否启用']] == 'true':
                            break
                        # 不符合则重置
                        else:
                            l_list = []
                    # 如果找到工艺了则退出循环
                    if l_list:
                        break
                    # 下一页是否可点击，如果可点击则点击，否则退出循环
                    btn_next_button = waitFind(data[0],By.XPATH,"//button[@class='btn-next']")
                    if btn_next_button.is_enabled():
                        btn_next_button.click()
                    else:
                        break

                if l_list:
                    data[1]['wip_code'] = l_list[title_col['半成品编号']]
                    data[1]['wip_version'] = l_list[title_col['配方版本']]
                    data[1]['device_group'] = l_list[title_col['设备组名称']]
                    data[1]['yield'] = l_list[title_col['最大产量（kg）']]
                    data[1]['tech_version'] = l_list[title_col['工艺版本']]
            # 如果中途报错则断言失败
            except Exception as e:
                assert 0,'获取工艺失败：' + getError()
            # 如果没有报错，则断言
            else:
                assert data[1]['wip_code'] and data[1]['wip_version'] and data[1]['device_group'] and data[1]['yield'] and data[1]['tech_version'],'获取工艺失败'