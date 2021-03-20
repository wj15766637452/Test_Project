# -*- coding:utf-8 -*-
import time

CONFIG ={
         # 基础配置
         'url':'',# 服务器url
         'username':'',# 账号
         'passwork':'',# 密码
         'token':'',# token
         'screenshot_dir':'.\\screenshot\\',# 自动截图路径
         'dir_png':'./report/png/',# 失败自动截图路径
         'dir_png_html':'./png/',# html截图路径
         # 浏览器配置
         'implicitly_wait':5,# 隐式等待时间(秒)
         'explicit_time':5,# 显式等待时间(秒)
         'explicit_flash':0.5,# 显式等待刷新时间(秒)
         # 工艺配置
         'select_tech':False,# 是否指定工艺，不指定则查找第一个正本审核启用
         'wip_code':'',# 指定的半成品编号
         'wip_version':'',# 指定的半成品编号版本
         'device_group':'',# 指定的生产线编号
         'yield':'',# 指定的产量,无指定则使用最大值
         'tech_version':'',# 工艺版本
         # 工单批次配置
         'word_order_code':'TEST_ORDER_' + str(int(time.time()))[1:],# 工单编号
         'word_order_name':'自动化测试工单',# 工单名
         'batch_code':'TEST_BATCH_' + str(int(time.time()))[1:],# 批次编号
         'batch_name':'自动化测试批次',# 批次名
         # 配料站配置
         'weighing_url':'',# 配料站url
         'weighing_username':'',# 配料站登录账号
         'weighing_passwork':'',# 配料站密码
         'materials_code':dict(),# 物料批次
         'print_template':'ZH-{0}!#-{1}!#-',# 标签格式(原料编号，原料批号)
         }
