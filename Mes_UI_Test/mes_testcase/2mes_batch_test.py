# -*- coding:utf-8 -*-
import pytest
from functions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import json

# 根据工艺创建工单，批次，审核批次
class Test_batch2():

    # 创建工单
    @pytest.mark.run(order=3)
    def test_create_workorder(self, data):
        try:
            # 点击生产管理
            find_title(data[0], 1, '生产管理').click()
            # 点击工单管理
            find_title(data[0],2,'工单管理').click()
            # 判断当前页面是否在工单管理里面
            waitFind(data[0],By.XPATH,'//span[@class="tags-view-item router-link-exact-active router-link-active active" and contains(text(),"工单管理")]')

            # 点击新增
            new1 = waitFind(data[0],By.XPATH,'//span[contains(text(),"新增")]')
            new1.click()
            # 等待1秒，点击下拉新增
            time.sleep(0.5)
            new2 = waitFind(data[0],By.XPATH,'/html/body/ul/li[1]')
            # 循环判断等待元素可点击
            click(new2)

            # 判断是否在弹出的新增工单页面
            waitFind(data[0],By.XPATH,'//span[@class="el-dialog__title" and contains(text(),"新增工单")]')
            # 遍历输入框
            input_list = data[0].find_elements_by_xpath('//div[@class="el-form-item is-required"]')
            for e in input_list:
                label_data = e.find_element_by_xpath('./div[1]/label').get_attribute('innerText').strip()
                # 输入工单编号
                if  label_data== '工单编号':
                    e.find_element_by_xpath('./div[2]/div[1]/input').send_keys(data[1]['word_order_code'])
                # 输入工单名
                elif label_data == '工单名':
                    e.find_element_by_xpath('./div[2]/div[1]/input').send_keys(data[1]['word_order_name'])
                # 选择部门
                elif label_data == '所属部门':
                    select_input = e.find_element_by_xpath('./div[2]/div/div/input')
                    select_input.click()
                    time.sleep(0.5)
                    waitFind(data[0],By.XPATH,'/html/body/div[3]/div[1]/div[1]/ul/li[1]').click()
                # 输入产量
                elif label_data == '产量':
                    e.find_element_by_xpath('./div[2]/div[1]/input').send_keys(data[1]['yield'])
            # 点击确认按钮
            save = waitFind(data[0],By.XPATH,'//button[@class="el-button el-button--primary el-button--small"]')
            save.click()
            # 获取结果
            result_data = waitFind(data[0],By.XPATH,'//p[@class="el-message__content"]').get_attribute('innerText').strip()
            # 操作成功则直接断言成功
            if result_data == '操作成功!':
                pass
            # 已存在的话点击取消按钮，断言成功
            elif result_data == '新增工单失败!工单编号已存在':
                cancel = waitFind(data[0], By.XPATH, '//button[@class="el-button el-button--default el-button--small"]')
                cancel.click()
            # 否则则点击取消，断言失败
            else:
                cancel = waitFind(data[0], By.XPATH, '//button[@class="el-button el-button--default el-button--small"]')
                cancel.click()
                raise Exception(result_data)
        except Exception as e:
            assert 0,"创建工单失败：" + getError()
        else :
            assert 1


    # 创建批次
    @pytest.mark.run(order=4)
    def test_create_batch(self, data):
        try:
            # 点击批次管理
            find_title(data[0],2,'批次管理').click()
            # 判断当前页面是否在工单管理里面
            waitFind(data[0], By.XPATH,'//span[@class="tags-view-item router-link-exact-active router-link-active active" and contains(text(),"批次管理")]')

            # 点击新增按钮
            click(waitFind(data[0],By.XPATH,'//button[@class="el-button el-button--text el-button-link"]/span[contains(text(),"新增")]'))
            waitFind(data[0],By.XPATH,'//header[@class="el-drawer__header"]/span[contains(text(),"新增批次")]')
            for div in data[0].find_elements_by_xpath('//div[@class="el-col el-col-12"]'):
                div_label = div.find_element_by_xpath('./div/label').get_attribute('innerText').strip()
                if div_label == '工单编号':
                    # 点击工单输入框
                    div.find_element_by_xpath('./div/div/div/input').click()
                    # 搜索框输入工单编号
                    time.sleep(0.5)
                    work_order = waitFind(data[0],By.XPATH,'//input[@class="el-input__inner" and @placeholder="请输入工单编号"]')
                    work_order.send_keys(data[1]['word_order_code'])
                    # 输入回车
                    work_order.send_keys(Keys.ENTER)
                    # 找到那行工单
                    time.sleep(0.5)
                    order = waitFind(data[0],By.XPATH,'//tr[@class="el-table__row"]/td[2]/div[text()="%s"]'%data[1]['word_order_code'])
                    # 选中
                    td_1 = order.find_element_by_xpath('../../td[1]')
                    td_1.find_element_by_xpath('./div/label/span/span').click()
                    # 点击确定
                    waitFind(data[0],By.XPATH,'//span[@class="dialog-footer"]/button[@class="el-button el-button--primary el-button--small"]').click()

                elif div_label == '半成品编号':
                    # 点击半成品编号输入框
                    div.find_element_by_xpath('./div/div/div/input').click()
                    # 搜索框输入工单编号
                    time.sleep(0.5)
                    wip_code_input = waitFind(data[0], By.XPATH,'//input[@class="el-input__inner" and @placeholder="请输入半成品编号"]')
                    wip_code_input.send_keys(data[1]['wip_code'])
                    # 输入回车
                    wip_code_input.send_keys(Keys.ENTER)
                    # 找到那行半成品
                    time.sleep(0.5)
                    wip = waitFind(data[0], By.XPATH,'//tr[@class="el-table__row"]/td[2]/div[text()="%s"]' % data[1]['wip_code'])
                    # 选中
                    td_1 = wip.find_element_by_xpath('../../td[1]')
                    td_1.find_element_by_xpath('./div/label/span/span').click()
                    # 点击确定
                    waitFind(data[0], By.XPATH,'//span[@class="dialog-footer"]/button[@class="el-button el-button--primary el-button--small"]').click()

                elif div_label == '配方版本':
                    # 点击半成品编号输入框
                    div.find_element_by_xpath('./div/div/div/div/input').click()
                    # 遍历列表找到所要的版本,点击
                    time.sleep(0.5)
                    ul = waitFind(data[0],By.XPATH,'/html/body/div[3]/div[1]/div[1]/ul')
                    lis = ul.find_elements_by_xpath('./li')
                    for li in lis:
                        if li.find_element_by_xpath('./span[1]').get_attribute('innerText').strip() == data[1]['wip_version']:
                            li.click()
                            break
                    # 找不到则报错
                    else:
                        raise Exception('找不到配方版本%s'%data[1]['wip_version'])

                elif div_label == '设备组编号':
                    # 点击设备组编号输入框
                    div.find_element_by_xpath('./div/div/div/div/input').click()
                    # 遍历列表找到所要的版本,点击
                    time.sleep(0.5)
                    ul = waitFind(data[0], By.XPATH, '/html/body/div[4]/div[1]/div[1]/ul')
                    lis = ul.find_elements_by_xpath('./li')
                    for li in lis:
                        if li.find_element_by_xpath('./span[1]').get_attribute('innerText').strip() == data[1]['device_group']:
                            li.click()
                            break
                    # 找不到则报错
                    else:
                        raise Exception('找不到设备组%s' % data[1]['device_group'])

                # 输入产量
                elif div_label == '设备产量区间':
                    yield_input=div.find_element_by_xpath('./div[2]/div/div[1]/input')
                    yield_input.send_keys(data[1]['yield'])

                # 输入批次编号
                elif div_label == '批次编号':
                    yield_input = div.find_element_by_xpath('./div/div/div[1]/input')
                    yield_input.send_keys(data[1]['batch_code'])

                # 计划开始时间
                elif div_label == '计划开始时间':
                    # 下拉滚动条
                    date_input=div.find_element_by_xpath('./div/div/div/input')
                    data[0].execute_script("arguments[0].scrollIntoView();", date_input)
                    time.sleep(0.5)
                    # 点击输入框
                    date_input.click()
                    time.sleep(0.5)
                    # 点击此刻
                    waitFind(data[0],By.XPATH,'/html/body/div[5]/div[2]/button[1]').click()

                # 计划结束时间
                elif div_label == '计划结束时间':
                    # 点击输入框
                    div.find_element_by_xpath('./div/div/div/input').click()
                    time.sleep(0.5)
                    # 点击此刻
                    waitFind(data[0], By.XPATH, '/html/body/div[6]/div[2]/button[1]').click()

                # 选择部门
                elif div_label == '所属部门':
                    select = div.find_element_by_xpath('./div/div/div/div/input')
                    # 把进度条下拉
                    data[0].execute_script("arguments[0].scrollIntoView();", select)
                    time.sleep(0.5)
                    # 点击选择框
                    select.click()
                    # 遍历列表找到所要的版本,点击
                    time.sleep(0.5)
                    # 点击第一个选择
                    li = waitFind(data[0], By.XPATH, '/html/body/div[7]/div[1]/div[1]/ul/li[1]')
                    li.click()

            # 找到‘确认’按钮并点击
            buttons = data[0].find_elements_by_xpath("//button[@class='el-button el-button--primary el-button--small']")
            for b in buttons:
                if b.find_element_by_xpath('./span').get_attribute('innerText').strip() == '确 定':
                    b.click()
                    break
            # 找不到的话则报错
            else:
                raise Exception('找不到确认按钮')

            # 获取结果判断是否成功
            result_data = waitFind(data[0], By.XPATH, '//p[@class="el-message__content"]').get_attribute('innerText').strip()
            # 如果结果不为成功则断言失败
            if result_data != '操作成功!':
                raise Exception('创建批次失败：%s'%result_data)

            # 搜索批次
            search_input = waitFind(data[0],By.XPATH,'//input[@class="el-input__inner" and @placeholder="请输入查询内容"]')
            search_input.send_keys(data[1]['batch_code'])
            search_button = waitFind(data[0],By.XPATH,'//button[@class="el-button margin-left-16 el-button--primary el-button--mini"]')
            search_button.click()

            # 审核批次
            # 获取字段列表元素
            title_col_e = data[0].find_elements_by_xpath("//thead[@class='has-gutter']/tr/th")
            # 字段所在的下标
            title_col = dict()
            i = 0
            for e in title_col_e:
                title_col[e.get_attribute('innerText').strip()] = i
                i += 1
            # 遍历第一行
            row_1 = data[0].find_elements_by_xpath('//tr[@class="el-table__row" or @class="el-table__row el-table__row--striped" or @class="el-table__row current-row"]')[-1]
            batch_code = row_1.find_elements_by_xpath("./td")[title_col['批次编号']].find_element_by_xpath("./div/span").get_attribute('innerHTML').strip()
            if batch_code != data[1]['batch_code']:
                raise Exception('第一行列表找不到批次%s'%data[1]['batch_code'])
            # 选中
            row_1.find_element_by_xpath('./td[1]/div/label/span/span').click()
            # 审核通过
            time.sleep(1)
            buttons = data[0].find_elements_by_xpath('//button[@class="el-button el-button--text el-button-link" or @class="el-button el-button--text is-disabled"]')
            for b in buttons:
                if b.find_element_by_xpath('./span').get_attribute('innerText').strip() == '审批通过':
                    click(b)
                    time.sleep(1)
                    # 点击确定
                    waitFind(data[0],By.XPATH,'//button[@class="el-button el-button--default el-button--small el-button--primary "]').click()
                    break
            else:
                raise Exception('找不到审核通过确认按钮')
            # 判断是否成功
            result_data = waitFind(data[0], By.XPATH, '//p[@class="el-message__content"]').get_attribute('innerText').strip()
            # 如果结果不为成功则断言失败
            if result_data != '操作成功!':
                raise Exception('审核批次失败：%s' % result_data)

        except Exception as e:
            assert 0,"创建批次失败：" + getError()
        else :
            assert 1


    # 获取配料批次
    @pytest.mark.run(order=5)
    def test_get_materials_batch(self, data):
        try:
            # 选中第一行
            row_1 = data[0].find_elements_by_xpath(
                '//tr[@class="el-table__row" or @class="el-table__row el-table__row--striped" or @class="el-table__row current-row"]')[-1]
            row_1.find_element_by_xpath('./td[1]/div/label/span/span').click()
            # 点击配料清单
            time.sleep(1)
            buttons = data[0].find_elements_by_xpath(
                '//button[@class="el-button el-button--text el-button-link" or @class="el-button el-button--text is-disabled"]')
            for b in buttons:
                if b.find_element_by_xpath('./span').get_attribute('innerText').strip() == '配料清单':
                    click(b)
                    time.sleep(1)
                    break
            else:
                raise Exception('找不到配料清单按钮')
            # 遍历获取原料编号的下标
            thead = data[0].find_elements_by_xpath('//*[@id="app"]/div/div[2]/div[2]/section/div/div[2]/div/div[2]/div[1]/div[2]/table/thead')[-1]
            ths = thead.find_elements_by_xpath('./tr/th')
            i=0
            for th in ths:
               if th.find_element_by_xpath('./div/span').get_attribute('innerText').strip() =='原料编号':
                   break
               else:
                   i+=1
            # 遍历获取需要称量的物料
            table = data[0].find_elements_by_xpath('//div[@class="el-table__body-wrapper is-scrolling-left"]/table[@class="el-table__body"]')[-1]
            trs = table.find_elements_by_xpath('./tbody/tr')
            for tr in trs:
                # 将物料编号加入到字典里
                m_code = tr.find_elements_by_xpath('./td')[i].find_element_by_xpath('./div/span').get_attribute('innerText').strip()
                if m_code:
                    data[1]['materials_code'][m_code]=''

            # 查看是否存在物料批次，有则保存第一个无则新增再保存
            # get获取批次列表
            get_materials_batch_url = data[1]['weighing_url']+'/fbi/burden-site/stock-material'
            request = requests.Session()
            headers = {
                        'Accept':'application/json, text/plain, */*',
                        'Accept-Encoding':'gzip,deflate',
                        'Accept-Language':'zh-CN,zh;q=0.9',
                        'authorization':data[1]['token'],
                        'Connection':'keep-alive',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
            }

            # post创建物料批次
            create_materials_batch_url = data[1]['url']+'/fbi/stock/material'
            post_headers = headers.copy()
            new_headers = {
                            'Content-Type':'application/json;charset=UTF-8',
                            'Host':data[1]['url'][7:],
                            'Content-Length':''
            }
            # 在原有的头部信息上增加一些字段，Content-Length为len(str(post_data))-2*len(post_data)+1
            post_headers.update(new_headers)
            post_data = {"amount":"1","casNo":"","density":"","enterBatch":"","expirationDate":time.strftime("%Y-%m-%d", time.localtime(time.time()+86400*365)),
                         "materialCode":"","productionDate":"","purchaseDate":time.strftime("%Y-%m-%d", time.localtime(time.time())),"storageLocation":"",
                         "unit":"kg","volume":"","specification":"1","materialId":""}# 批次重量1kg，分包1kg,当天生产，过期时间为365天

            # 审核批次
            put_url = data[1]['url']+'/fbi/stock/material/audited'

            # 获取库存id
            id_url = data[1]['url']+ '/fbi/stock/material?current=1&size=20&queryParams=%5B%7B%22columnName%22%3A%22enterBatch%22%2C%22selectCondition%22%3A%22%3D%22%2C%22val%22%3A%5B%22{0}%22%5D%7D%2C%7B%22columnName%22%3A%22type%22%2C%22selectCondition%22%3A%22%3D%22%2C%22val%22%3A%5B%22material%22%5D%7D%5D&_t=1'

            # 遍历需要的原料
            for material in data[1]['materials_code']:
                response = request.get(url=get_materials_batch_url,params={'materialCode':material},headers=headers,timeout=10)
                response_json = response.json()
                if response_json['code'] == '200':
                    batch_lists = response_json['data']['list']
                    # 有库存，且原料编号等于要找的原料编号
                    if batch_lists and batch_lists[0]['materialCode'] == material:
                        data[1]['materials_code'][material] = data[1]['print_template'].format(material,batch_lists[0]['enterBatch'])
                    # 否则需要创建库存
                    else:
                        # 创建post的body
                        enterBatch = material+'-'+time.strftime("%m%d%H%M%S", time.localtime(time.time()))
                        new_data = {"materialCode":material,"materialId":batch_lists[0]['materialId'],"enterBatch":enterBatch}
                        post_data.update(new_data)
                        # 计算Content-Length为len(str(post_data))-2*len(post_data)+1
                        c_l = str(len(str(post_data))-2*len(post_data)+1)
                        post_headers['Content-Length']=c_l
                        # 提交请求
                        response = request.post(url=create_materials_batch_url,data=json.dumps(post_data),headers=post_headers,timeout=10)
                        # 创建异常
                        if response.json()['code'] != '200':
                            raise Exception('创建原料批次异常：%s'%str(response.json()))

                        # 获取库存id
                        response = request.get(url=id_url.format(enterBatch),headers=headers,timeout=10)
                        if response.json()['code'] != '200':
                            raise Exception('审核原料批次ID异常：%s' % str(response.json()))
                        ID = response.json()['data']['list'][0]['stockId']
                        # 审批物料批次
                        put_data = {"stockIdList":[ID]}
                        post_headers['Content-Length'] = str(len(json.dumps(put_data))-1)
                        response = request.put(url=put_url,headers=post_headers,data=json.dumps(put_data),timeout=10)
                        if response.json()['code'] != '200':
                            raise Exception('审核原料批次异常：%s'%str(response.json()))
                        # 保存批次进字典
                        data[1]['materials_code'][material] = data[1]['print_template'].format(material,enterBatch)

                # 状态码不为200时
                else:
                    raise Exception('接口获取批次异常：%s'%response_json)

        except Exception as e:
            assert 0, "获取物料批次失败：" + getError()
        else:
            assert 1
