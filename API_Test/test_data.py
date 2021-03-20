# -*- coding:utf-8 -*-
import time

# 基本参数
# 先设置本机ip为生产设备组
info={
"workOrderCode":'TEST_ORDER_' + str(int(time.time()))[1:],
'batchCode':'TEST_BATCH_' + str(int(time.time()))[1:],
"server_ip":"",
"username":"",
"password":"",
"planStartTime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
'bom':"92003-00",
'yield':'3000',
"belongDepartment":"",
"belongDepartmentId":"20005",
# 现设备组
'produce_device_name':'010',
'produce_device_ip':'172.16.1.29',# 临时ip（172.16.1（+1）.155）
# 预混站
'mix_device_name':'ep',
'mix_device_ip':'',
# log config
'path':r'C:\Users\PLK-HT\Desktop',
# 管道物料
'94000002':'YL,1317380453845491713,94000002,,1338672553991884802',
'94000002_enterBatch':'01202501',
'94000002_packageCode':'1-1',
'94000002_packageId':'1338672553991884802',
'94000001':'YL,1317380452725612545,94000001,,1343741664262410242',
'94000001_enterBatch':'01228602',
'94000001_packageCode':'1-1',
'94000001_packageId':'1343741664262410242',
#######################################################################################
'burden_list':[],
"workOrderId":"",
"materialId":"",
"bomVersion":'',
"bomId":"",
"bomVersionId":"",
'deviceGroup':'',
"groupId":"",
"groupName":"",
'materialCode':"",
"batchId":""
}

# 如果没配置路径则将当前路径当做log保存路径
if info.get('path','') == '':
    import os
    info['path'] =os.getcwd()

# api
request_lists=[
['登录获取授权','POST','/fbi/security/account/login',"{'username':'<username>','password':'<password>'}",['操作成功!']],
['创建工单','POST','/fbi/produce/work-order','{"workOrderCode":"<workOrderCode>","workOrderName":"","yield":"<yield>","client":"","planStartTime":"","planEndTime":"","remark":"","belongDepartment":"<belongDepartment>","belongDepartmentId":"<belongDepartmentId>"}',['新增工单成功!']],
['获取工单代码','GET','/fbi/produce/work-order','''{'current': '1','size':'30','queryParams':'[{"columnName":"workOrderCode","selectCondition":"=","val":["<workOrderCode>"]}]'}''',['操作成功!'],[(["data","list",0],{"workOrderId":"workOrderId"})]],
['获取创建参数','GET','/fbi/tech/version','''{'current': '1','size':'30','queryParams': '[{"columnName":"bomGroupCode","selectCondition":"=","val":["<bom>"]},{"columnName":"originalStatus","selectCondition":"=","val":["original"]}]'}''',['操作成功!'],[(["data","list",0],{"groupId":"groupId","techVersionId":"techVersionId","groupName":"groupName","typeName":"typeName","typeId":"typeId","bomVersionId":"bomVersionId","version":"bomVersion","bomId":"bomId","materialId":"materialId","materialCode":"materialCode"})]],
['创建批次','POST','/fbi/produce/batch','''{"workOrderId":"<workOrderId>","materialId":"<materialId>","bomVersionId":"<bomVersionId>","groupId":"<groupId>","techVersionId":"<techVersionId>","yield":"<yield>","batchCode":"<batchCode>","batchName":"","actualYield":"","potCode":"","planStartTime":"<planStartTime>","planEndTime":"","remark":"","belongDepartmentId":"<belongDepartmentId>","belongDepartment":"<belongDepartment>","typeId":"<typeId>","workOrderCode":"<workOrderCode>","workOrderName":"<workOrderCode>","materialCode":"<materialCode>","materialName":"<materialCode>","bomVersion":"<bomVersion>","groupName":"<groupName>","typeName":"<typeName>"}''',['新增批次成功!']],
['获取批次参数','GET','/fbi/produce/batch','''{'current': '1','size':'30','isAsc':'true','sortColumns':'planStartTime','queryParams':'[{"columnName":"batchCode","selectCondition":"=","val":["<batchCode>"]}]'}''',['操作成功!'],[(["data","list",0],{"batchId":"batchId"})]],
['审核批次','PUT','/fbi/produce/batch/audited/<batchId>','{}',["审核通过成功!"]],
['获取设备参数','GET','/fbi/burden-site/device','''{}''',['操作成功!'],[(['data',0],{'deviceGroupId':"deviceGroupId",'deviceId':'deviceId','groupCode':'deviceGroup'})]],
['配料与复核','GET','/fbi/burden-site/burden/work-order/material-burden/<batchId>','''{'current':'1','size':'100','type':'3','totalPage':'1','pageSize':'1'}''',['操作成功!'],[],'burden_function'],
['自动化生产','GET','/fbi/automation/feeding/batch-by-status','''{'deviceGroup':'<deviceGroup>'}''',['操作成功!'],[],'auto_produce'],
]



__all__ = ["info","request_lists"]