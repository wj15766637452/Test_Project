# -*- coding:utf-8 -*-
import pytest
from functions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Test_weighing3():

    # 登录配料页面
    @pytest.mark.run(order=6)
    def test_weighing_in(self, data):
        try:
            # 进入配料站页面
            data[0].get(CONFIG.get('weighing_url', ''))
            # 输入账户
            name_input = waitFind(data[0],By.XPATH,'//input[@class="el-input__inner" and @name="username"]')
            name_input.send_keys(data[1].get('weighing_username', 'plkadmin'))
            # 输入密码
            password_input = waitFind(data[0],By.XPATH,'//input[@class="el-input__inner" and @name="password"]')
            password_input.send_keys(data[1].get('weighing_password', '123456'))
            # 关掉键盘
            waitFind(data[0],By.XPATH,'//*[@id="keyboard"]/div/div[5]/span[3]').click()
            # 点击确认键
            login_buttons = data[0].find_elements_by_xpath('//button[@class="el-button filter-item el-button--primary el-button--large"]')
            for button in login_buttons:
                if button.find_element_by_xpath('./span').get_attribute('innerText').strip() == '登录':
                    button.click()
                    break
            else:
                raise Exception('找不到登录按钮')

            # 判断是否登录成功
            result_data = waitFind(data[0],By.XPATH,'//input[@class="提示信息 提示信息背景红" or @class="提示信息 提示信息背景白"]').get_attribute('value').strip()
            if result_data != '请选择工单对应的原料进行配料称量':
                raise Exception('登录失败：%s'%result_data)

        except Exception as e:
            assert 0,"登录配料站失败：" + getError()
        else :
            assert 1


    # 强制称量
    @pytest.mark.run(order=7)
    def test_weighing(self, data):
        try:
            # 搜索批次号
            search_input = waitFind(data[0],By.XPATH,'//div[@class="el-col el-col-18"]/div/form/div/div/input[@class="search-code-input el-input__inner"]')
            search_input.send_keys(data[1]['batch_code'])
            search_input.send_keys(Keys.ENTER)
            # 关掉键盘
            waitFind(data[0], By.XPATH, '//*[@id="keyboard"]/div/div[5]/span[3]').click()
            # 断言有没找到该批次
            batch_th = data[0].find_elements_by_xpath('//th[contains(@class,"el-table_1_column_")]')

            batch_index = 0
            # 遍历表格表头，找批次的下标位置
            for th in batch_th:
                label_data = th.find_element_by_xpath('./div').get_attribute('innerText').strip()
                if label_data == '批号':
                    break
                else:
                    batch_index +=1
            else:
                raise Exception('找不到批号所在下标')
            td = data[0].find_elements_by_xpath('//tr[@class="el-table__row row-class current-row"]/td')[batch_index]
            select_batch = td.find_element_by_xpath('./div').get_attribute('innerText').strip()
            # 判断当前选中的行的批号是否需要找的
            if select_batch != data[1]['batch_code']:
                raise Exception('所选中的批号不为：%s'%data[1]['batch_code'])

            # 秤料量
            weight_number = 0
            # 遍历选中第一个配料直到没有
            while True:
                # 点击第一行
                select_first = data[0].find_elements_by_xpath('//tr[@class="el-table__row select row-class" or @class="el-table__row row-class"]')[0]
                select_first.click()
                time.sleep(1)
                buttons = data[0].find_elements_by_xpath('//div[@class="el-dialog el-dialog--small"]/div/form/div/button[@class="el-button filter-item el-button--primary"]')
                for b in buttons:
                    if b.find_element_by_xpath('./span').get_attribute('innerText').strip() == '强制配料':
                        b.click()
                        break
                else:
                    raise Exception('找不到强制配料按钮')
                # 等待页面加载
                time.sleep(1)
                if data[0].find_elements_by_xpath('//div[@class="clearfix"]/span')[0].get_attribute('innerText').strip() != '目标原料信息':
                    raise Exception('当前不是强制配料页面')
                # 查找所需重量
                need_weight = 0
                divs = data[0].find_elements_by_xpath('//div[@class="el-form-item materiaInfo"]')
                for div in divs:
                    if div.find_element_by_xpath('./label').get_attribute('innerText').strip() == '实际误差:':
                        need_weight =div.find_element_by_xpath('./div/div/input').get_attribute('value').strip()
                        break
                else:
                    raise Exception('找不到所需的重量')
                # 扫描二维码
                input2 = waitFind(data[0],By.XPATH,'//input[@class="burden-form-input-code el-input__inner"]')
                input2.send_keys('YL,1317380453719662593,74000024,,1338672845521178626')#???
                input2.send_keys(Keys.ENTER)
                # 输入重量
                divs = data[0].find_elements_by_xpath('//div[@class="el-form-item materiaInfo is-required"]')
                for div in divs:
                    if div.find_element_by_xpath('./label').get_attribute('innerText').strip() == '强制重量:':
                        div.find_element_by_xpath('./div/div/input').send_keys(need_weight)
                        break
                else:
                    raise Exception('找不到输入重量框')
                break
        except Exception as e:
            assert 0,"配料失败：" + getError()
        else :
            assert 1

