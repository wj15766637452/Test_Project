# -*- coding:utf-8 -*-

from traceback import format_exc
import requests
import json
import time
import re
import os


# 异常打印的数据
error_print = ''
# 请求接口数量
len_request =0
# 提前创建变量
class Log():
    pass
# 提前创建变量
log = None
# 主动触发的异常
class MY_E(Exception):
    pass

# √引入配制文件
try:
    from test_data import *
    # token
    authorization = ''
    # session
    session = requests.session()
    # 请求头
    head = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8'
    }
    session.headers.update(head)

    # 测试不通过保存log
    class Log():
        # 记录保存日志的位置
        def __init__(self, file_name=info.get('batchCode', '') + '_log.txt', save_path=info.get('path', '')):
            if os.path.isdir(save_path):
                self.file_name = file_name
                self.path = save_path
                self.save_file_path = self.path +'\\'+ self.file_name
                self.data = ''
            else:
                global error_print
                error_print += '保存的路径不是一个文件夹路径'
                raise Exception

        # 写入文档，后缀默认换行
        def write(self, data, end='\n'):
            self.data += str(data)
            self.data += end

        # 保存log
        def save(self,open_file=True):
            f = open(self.save_file_path, 'wt')
            f.write(self.data)
            f.close()
            self.data = ''
            if open_file:
                # 打开log文件
                os.system(self.save_file_path)

# 异常处理
except:
    print("ERROR:同路径下缺少test_data.py配置文件或配置文件不合规！")
    # 打印异常输出的信息
    print(error_print)
    # 打印异常信息
    print(format_exc())


#-----------------------------------------------------分割线------------------------------------------------------------
# √print 的同时也加入到log
def wj_print(data,end='\n'):
    global log
    # 正常打印
    print(data,end=end)
    # 加入
    log.write(data,end=end)


# √输出全部相别信息
def phase_print(p_d):
    d={'0':'等待','1':'开始','2':'结束','3':'暂停','5':'转移'}
    data =''
    for aep in p_d:
        for p in p_d[aep]:
            if data:
                data+=' '
            data+='{0}:{1}({2}/{3})'.format(d[str(p['status'])],p['phaseName'], p['currentStep'],p['totalStep'])
    print('\r'+data,end='')
    log.write(data)

# 更新相别最新状态步骤
def updata_phase(p_d):
    global len_request
    global error_print
    para = {'batch': info['batchCode']}
    response = session.get(url=info['server_ip'] + '/fbi/automation/feeding/step-phase', params=para, timeout=5)
    re_json = response.json()
    len_request += 1
    if '操作成功!' not in str(re_json):
        error_print += '\n更新相别状态异常!'
        return False
    for phase in re_json['data']:
        for p in p_d[phase['phaseType']]:
            if p['phaseName'] == phase['phaseName']:
                p.update(phase)
    return True


# 获取批次以及相别接口
def get_batch_phase(batch,phase,deviceGroup = '',device=''):
    global len_request
    global error_print
    # 检验是否能获取到该批次
    para  = {'deviceGroup' : deviceGroup,'device':device}
    response = session.get(url=info['server_ip']+'/fbi/automation/feeding/batch-by-status',params = para,timeout = 5)
    re_json = response.json()
    len_request+=1
    # 判断是否成功
    if re_json['code'] != '200' or re_json['msg'] != '操作成功!':
        error_print += '\n获取批次列表异常！'
        return False
    # 遍历工单列表查看批次是否在列表内
    for b in re_json['data']:
        if b['batch'] == batch:
            break
    else:
        error_print += '\n获取批次列表异常(没有批次%s)！'%batch
        return False
    # 检验能否获取相别
    if type(phase)==str:
        phase = [phase]
    para = {'batch':batch}
    response = session.get(url=info['server_ip']+'/fbi/automation/feeding/step-phase',params = para,timeout= 5)
    re_json =response.json()
    len_request+=1
    if re_json['code'] != '200' or re_json['msg'] != '操作成功!':
        error_print += '\n获取相别列表异常！'
        return False
    for p in re_json['data']:
        if p['phaseName'] in phase:
            phase.remove(p['phaseName'])
    if phase:
        error_print += '\n获取相别列表异常(还有相别%s无法获取)！'%phase
        return False
    else:
        return True

# 更新相别的最新状态
def phase_update(p,p_d,t=None):
    global error_print
    for ae in p_d:
        for phase in p_d[ae]:
            if phase['phaseName'] == p['phaseName']:
                if t:
                    for tt in t:
                        if str(phase[tt[0]]) != str(tt[1]):
                            error_print += '\n{0}相别状态不符!\n实际值{1}\n校验值{2}'.format(phase['phaseName'],phase,tt)
                            raise MY_E
                p.update(phase)
                break


# 自动化完成相别
def auto_phase(phase,phase_dict,deviceGroup='',device=''):
    global len_request
    global error_print
    phase_print(phase_dict)
    # 获取工艺
    para = {'batch':info['batchCode'],'phaseName':phase['phaseName']}
    if device:
        para['deviceCode'] = device
    response = session.get(url=info['server_ip']+'/fbi/automation/feeding/tech-data-phase',params = para,timeout= 5)
    re_json = response.json()
    len_request+=1
    if re_json['data']['phaseName'] != phase['phaseName']:
        error_print += '\n获取相别%s工艺失败！'%phase['phaseName']
        return False
    tech_data = re_json['data']

    # 开始
    para = {"batch": info['batchCode'],"currentStep": "1","phaseName": phase['phaseName'],"state": "1","username": "api_auto"}
    response = session.put(url = info['server_ip']+'/fbi/automation/feeding/update-phase-status',data=json.dumps(para),timeout=5)
    re_json = response.json()
    len_request+=1
    if '操作成功!' not in str(re_json):
        error_print += '\n开始相别%s不成功'%phase['phaseName']
        return False
    else:
        if not updata_phase(phase_dict):
            return False
        phase_update(phase,phase_dict,[('status','1'),('currentStep','1')])
        phase_print(phase_dict)
    # 遍历直到最后一步
    while int(phase['currentStep']) <= int(phase['totalStep']):
        is_over = False
        while not is_over:
            # 是否需要投料
            para = {'batch':info['batchCode'],'currentStep':phase['currentStep'],'phaseName':phase['phaseName']}
            response = session.get(url=info['server_ip']+'/fbi/automation/feeding/check-feed',params =para,timeout=5)
            re_json = response.json()
            len_request+=1
            if '200' not in str(re_json):
                error_print += '\n检查是否需要投料异常!'
                return False
            feedType = re_json['data']['feedType']
            is_over = re_json['data']['isOver']
            # 投料
            if not is_over and feedType == 'feedMaterial':
                scanCode_list =[]
                for sc in info['burden_list']:
                    step_batch_phase=sc['scanCode'].split(',')[3]
                    step = step_batch_phase.split('--')[0]
                    phasename=step_batch_phase.split('--')[2]
                    if phasename==phase['phaseName'] and step==str(phase['currentStep']):
                        scanCode_list.append(sc['scanCode'])
                if not scanCode_list:
                    error_print += '\n获取不到{0}相第{1}步要投的料！'.format(phase['phaseName'],phase['currentStep'])
                    return False
                # 扫码投料
                for sc in scanCode_list:
                    post_data = {"batch":info['batchCode'],"currentStep":phase['currentStep'],"phaseName": phase['phaseName'],"qrCode":sc,"username": "api_auto"}
                    response = session.post(url=info['server_ip']+'/fbi/automation/feeding/feed',data=json.dumps(post_data),timeout=5)
                    len_request+=1
                    re_json = response.json()
                    if '投料成功!' not in str(re_json):
                        error_print += '\n投料不成功(%s)！'%sc
            # 投外相
            elif not is_over and feedType == 'feedOuterPhase':
                # 查找要投的外相是什么
                OuterPhase = tech_data['stepTechData'][(int(phase['currentStep'])-1)]['phaseCode']
                OuterPhase_phase = dict()
                for aep in phase_dict:
                    for p in phase_dict[aep]:
                        if p['phaseName']==OuterPhase:
                            OuterPhase_phase =p.copy()
                            break
                if not OuterPhase:
                    error_print += '\n找不到相别%s的信息'%OuterPhase
                    return False
                # 如果相别还没完成则递归完成再投
                if str(OuterPhase_phase['status'])=='0':
                    auto_phase(OuterPhase_phase,phase_dict=phase_dict)
                # 点击投外相
                para = {"batch": info['batchCode'], "currentStep": OuterPhase_phase['currentStep'],
                        "phaseName": OuterPhase, "state": "5",
                        "username": "api_auto"}
                response = session.put(url=info['server_ip'] + '/fbi/automation/feeding/update-phase-status',
                                       data=json.dumps(para),
                                       timeout=5)
                re_json = response.json()
                len_request += 1
                if '操作成功!' not in str(re_json):
                    error_print += '\n结束相别%s不成功' % OuterPhase
                    return False
                else:
                    if not updata_phase(phase_dict):
                        return False
                    phase_print(phase_dict)

        # 跳下一步
        if int(phase['currentStep']) < int(phase['totalStep']):
            para = {"batch": info['batchCode'], "currentStep": str(int(phase['currentStep'])+1), "phaseName": phase['phaseName'],
                    "state": phase['status'], "username": "api_auto"}
            response = session.put(url=info['server_ip'] + '/fbi/automation/feeding/update-phase-status',
                                   data=json.dumps(para), timeout=5)
            re_json = response.json()
            len_request += 1
            if '操作成功!' not in str(re_json):
                error_print += '\n跳转下一步不成功!'
                return False
            else:
                if not updata_phase(phase_dict):
                    return False
                phase_update(phase, phase_dict, [('currentStep', int(int(phase['currentStep'])+1))])
                phase_print(phase_dict)
        else:
            break

    # 遍历需要相转移的相
    # 查看该步是否需要相转移
    target_list = []
    for t in tech_data['stepTechData']:
        fun = t['fun']['name']
        target_phase = t['phaseCode']
        if fun == '相转移':
            if target_phase not in target_list:
                target_list.append(target_phase)
    for pp in target_list:
        target_dict = dict()
        for aep in phase_dict:
            for p in phase_dict[aep]:
                if p['phaseName'] == pp:
                    target_dict = p.copy()
                    break
        if not target_dict:
            error_print += '\n找不到相别%s的信息' % pp
            return False
        # 如果相别还没完成则递归完成再投
        if str(target_dict['status']) == '0':
            auto_phase(target_dict, phase_dict=phase_dict)
        # 相转移
        para = {"batch": info['batchCode'], "currentStep": target_dict['currentStep'],
                "phaseName": pp, "state": "5",
                "username": "api_auto"}
        response = session.put(url=info['server_ip'] + '/fbi/automation/feeding/update-phase-status',
                               data=json.dumps(para),
                               timeout=5)
        re_json = response.json()
        len_request += 1
        if '操作成功!' not in str(re_json):
            error_print += '\n结束相别%s不成功' % pp
            return False
        else:
            if not updata_phase(phase_dict):
                return False
            phase_print(phase_dict)


    # 结束
    para = {"batch": info['batchCode'], "currentStep": phase['currentStep'], "phaseName": phase['phaseName'], "state": "2",
            "username": "api_auto"}
    response = session.put(url=info['server_ip'] + '/fbi/automation/feeding/update-phase-status', data=json.dumps(para),
                           timeout=5)
    re_json = response.json()
    len_request += 1
    if '操作成功!' not in str(re_json):
        error_print += '\n结束相别%s不成功' % phase['phaseName']
        return False
    else:
        if not updata_phase(phase_dict):
            return False
        phase_update(phase, phase_dict, [('status', '2')])
        phase_print(phase_dict)

    # 如果自己是主锅这则出料
    if phase['aimsPhaseCode']=='':
        para = {"batch": info['batchCode'], "currentStep": phase['currentStep'], "phaseName": phase['phaseName'],
                "state": "5",
                "username": "api_auto"}
        response = session.put(url=info['server_ip'] + '/fbi/automation/feeding/update-phase-status',
                               data=json.dumps(para),
                               timeout=5)
        re_json = response.json()
        len_request += 1
        if '操作成功!' not in str(re_json):
            error_print += '\n结束相别%s不成功' % phase['phaseName']
            return False
        else:
            if not updata_phase(phase_dict):
                return False
            phase_update(phase, phase_dict, [('status', '5')])
            phase_print(phase_dict)
            print('')
            # 校验批次的状态
            para = {'current': '1','size':'30','isAsc':'true','sortColumns':'planStartTime','queryParams':'[{"columnName":"batchCode","selectCondition":"=","val":["%s"]}]'%info['batchCode']}
            response = session.get(info['server_ip']+'/fbi/produce/batch',params=json.dumps(para),timeout=5)
            len_request+=1
            re_json = response.json()
            if '操作成功!' not in str(re_json):
                error_print += '\n获取批次状态异常!'
                return False
            else:
                d={'alreadyFormulated':'已配制'}
                stat = re_json['data']['list'][0]['status']
                print('批次<{0}>状态为<{1}>!'.format(info['batchCode'],d.get(stat,stat)))

    return True

# 处理函数 配料
def burden_function(jsons):
    try:
        global error_print
        global len_request
        wj_print('配料模拟中:',end='')
        burden_list = jsons['data']['list']
        log.write('配料列表：'+str(burden_list))
        # 遍历配料
        for burden_data in burden_list:
            log.write('现在准备称量%s'%burden_data)
            # 如果没有二维码则去搜索
            if burden_data['materialCode'] not in info:
                log.write('搜索原料')
                para = {'current':'1','size':'6','total':'1','totalPage':'1','materialCode':burden_data['materialCode']}
                response = session.get(url=info['server_ip']+'/fbi/burden-site/stock-material',params = para,timeout =5)
                re_json = response.json()
                len_request += 1
                # 搜索失败
                if '操作成功!' not in str(re_json):
                    error_print += '\n配料函数(搜索物料异常)!\n参数：{0}\n结果：{1}'.format(para,re_json)
                    return MY_E
                for s in re_json['data']['list']:
                    if s['materialCode'] == burden_data['materialCode']:
                        info[s['materialCode']+'_stockId'] = s['stockId']
                        break
                else:
                    error_print += '\n配料函数(没有找到物料%s的库存)!'%burden_data['materialCode']
                    return MY_E
                # 获取二维码
                log.write('获取原料二维码')
                para = {'stockId':info[burden_data['materialCode']+'_stockId'],'startPackageNumber': '1','endPackageNumber': '1','repeatNumber':'1'}
                response = session.get(url=info['server_ip']+'/fbi/burden-site/stock-material/print',params =para,timeout =5)
                re_json = response.json()
                len_request += 1
                if '操作成功!' not in str(re_json):
                    error_print += '\n配料函数(获取%s二维码异常)!'%burden_data['materialCode']
                    return MY_E
                data_dict = re_json['data'][0]
                info[burden_data['materialCode']] =data_dict['scanCode']
                info[burden_data['materialCode']+'_enterBatch'] =data_dict['enterBatch']
                info[burden_data['materialCode']+'_packageCode'] =data_dict['packageCode']
                info[burden_data['materialCode']+'_packageId'] =data_dict['packageId']
            # 二维码解析
            log.write('测试扫描二维码%s'%info[burden_data['materialCode']])
            scancode = info[burden_data['materialCode']]
            para = {'burdenId':burden_data['burdenId'],'scanCode':scancode}
            response = session.get(url=info['server_ip']+'/fbi/burden-site/burden/scan-code',params = para,timeout = 5)
            re_json = response.json()
            len_request += 1
            if '操作成功!' not in str(re_json):
                error_print += '配料函数(二维码解析异常)!'
                raise MY_E
            # 配料
            log.write('开始配料')
            post_data = json.dumps([{'actualNetWeight':str(burden_data['targetNetWeight']),'remark':'api_test','deviceGroupId':str(info['deviceGroupId']),'deviceId':str(info['deviceId']),'packageId':str(info[burden_data['materialCode']+'_packageId']),'enterBatch':str(info[burden_data['materialCode']+'_enterBatch']),'packageCode':info[burden_data['materialCode']+'_packageCode']}])
            post_response = session.post(url=info['server_ip']+'/fbi/burden-site/burden/compulsory/batch/'+burden_data['burdenId'],data=post_data,timeout=5)
            post_re_json = post_response.json()
            len_request += 1
            if '操作成功!' not in str(post_re_json):
                error_print = '配料函数(配料异常%s)!'%post_data
                raise MY_E
            else:
                wj_print('√',end='')
                info['burden_list'].append({'burdenId':burden_data['burdenId'],'scanCode':post_re_json['data'][0]['scanCode'],'materialCode':burden_data['materialCode']})
        # 复核
        wj_print('\r\n复核模拟中:',end='')
        fh_list = info['burden_list']
        log.write('复核列表：'+str(fh_list))
        for burden in fh_list:
            put_data = json.dumps({'batchId':info['batchId'],'storageLocationId':'','scanCode':burden['scanCode']})
            put_response = session.put(url=info['server_ip']+'/fbi/review/review',data=put_data,timeout=5)
            put_re_json = put_response.json()
            len_request += 1
            if '复核成功!' not in str(put_re_json):
                error_print += '配料函数(复核异常%s)!'%put_data
                raise MY_E
            wj_print('√', end='')
        wj_print("")
        return True

    except MY_E:
        return False
    except Exception as E:
        log.write('burden_function：\nlocals：' + str(locals()))
        wj_print('#'*50)
        wj_print(format_exc())
        wj_print('#'*50)
        return False

# 自动化接口测试
def auto_produce(jsons):
    global len_request
    global error_print
    try:
        # 查看批次是否处于待生产
        for batch_data in jsons['data']:
            if batch_data['batch'] == info['batchCode']:
                break
        else:
            error_print += '\n自动化函数(获取不到批次%s)!'%info['batchCode']
            raise MY_E
        # 根据批次获取相别信息
        para = {'batch':info['batchCode']}
        response = session.get(url=info['server_ip']+'/fbi/automation/feeding/step-phase',params =para,timeout=5)
        re_json = response.json()
        len_request+=1
        if '操作成功!' not in str(re_json):
            error_print += '\n自动化函数(获取不到批次%s的相别信息)!' % info['batchCode']
            raise MY_E
        # 保存相别信息
        phase_dict = {'AP':[],'EP':[]}
        for phase in re_json['data']:
            save_obj = None
            if phase['phaseType'] == 'AP':
                save_obj = phase_dict['AP']
            else:
                save_obj = phase_dict['EP']
            save_obj.append(phase)
        # 获取全部工艺，查看相别对应的设备
        response = session.get(url=info['server_ip']+'/fbi/automation/feeding/tech-data',params = {'batch':info['batchCode']})
        re_json = response.json()
        len_request += 1
        if not re_json['data']:
            error_print += '\n自动化函数(获取不到批次%s的工艺数据)!' % info['batchCode']
            raise MY_E
        for P in ['AP','EP']:
            # 遍历内相，外相
            for p in re_json['data'][P]:
                p_name = p['phaseName']
                p_device_code = p['deviceCode']
                if P == 'AP':
                    for ap in phase_dict['AP']:
                        if ap['phaseName'] == p_name :
                            ap['deviceCode'] = p_device_code
                            break
                elif P == 'EP':
                    for ep in phase_dict['EP']:
                        if ep['phaseName'] == p_name :
                            ep['deviceCode'] = p_device_code
                            break
        # 打印相别信息
        for phase_type in phase_dict:
            print(phase_type+'：',end='')
            for p in phase_dict[phase_type]:
                wj_print('{0}({3}){1}/{2}  '.format(p['phaseName'],p['currentStep'],p['totalStep'],p['deviceCode']),end='')
            wj_print('')
        # 切换预混站
        new_numer =info['produce_device_ip'].split('.')
        new_numer[2] = str(int(new_numer[2])+1)
        new_ip = '.'.join(new_numer)
        #     核对自身设备组信息
        para = {'current':'1','size':'30','queryParams':'[{"columnName":"groupName","selectCondition":"=","val":["%s"]}]'%info['produce_device_name']}
        response = session.get(url=info['server_ip']+'/fbi/device/group',params=para,timeout = 5)
        re_json = response.json()
        len_request+=1
        if '操作成功!' not in str(re_json):
            error_print += '\n自动化函数(获取设备组%s数据异常)!'%info['produce_device_name']
            raise MY_E
        # 旧设备组参数
        device_data =re_json['data']['list'][0]
        if device_data['groupName'] != info['produce_device_name']:
            error_print += '\n自动化函数(找不到设备组%s)!' % info['produce_device_name']
            raise MY_E
        # 获取编辑设备组的原始参数
        response = session.get(url=info['server_ip']+'/fbi/device/group/%s'%device_data['groupId'],data=json.dumps(para),timeout=5)
        re_json = response.json()
        len_request += 1
        if '操作成功!' not in str(re_json):
            error_print += '\n自动化函数(获取设备组%s的原始参数异常)!' % info['produce_device_name']
            raise MY_E
        old_device_data = re_json['data']
        # 清理旧参数数据
        old_device_data.pop('createdBy')
        old_device_data.pop('createdTime')
        old_device_data.pop('deviceUnitList')
        old_device_data.pop('fileList')
        old_device_data.pop('isRecipe')
        old_device_data.pop('type')
        old_device_data.pop('updatedBy')
        old_device_data.pop('updatedTime')
        # 改自己的设备组ip
        para =old_device_data.copy()
        para['ip'] = new_ip
        response =session.put(url=info['server_ip']+'/fbi/device/group/%s'%para['groupId'],data=json.dumps(para),timeout=5)
        re_json = response.json()
        len_request+=1
        if '修改设备组成功!' not in str(re_json):
            error_print += '\n自动化函数(修改自身ip不成功设置ip%s)!'%para['ip']
            raise MY_E
        # 记录预混站现ip，以及修改为现设备ip
        para = {'current': '1', 'size': '30',
                'queryParams': '[{"columnName":"groupName","selectCondition":"=","val":["%s"]}]' % info['mix_device_name']}
        response = session.get(url=info['server_ip'] + '/fbi/device/group', params=para, timeout=5)
        re_json = response.json()
        len_request += 1
        if '操作成功!' not in str(re_json):
            error_print += '\n自动化函数(获取预混设备组%s数据异常)!' % info['mix_device_name']
            raise MY_E
        # 预混设备组参数
        device_data = re_json['data']['list'][0]
        if device_data['groupName'] != info['mix_device_name']:
            error_print += '\n自动化函数(找不到设备组%s)!' % info['mix_device_name']
            raise MY_E
        # 获取编辑预混设备组的原始参数
        response = session.get(url=info['server_ip'] + '/fbi/device/group/%s' % device_data['groupId'],
                               data=json.dumps(para), timeout=5)
        re_json = response.json()
        len_request += 1
        if '操作成功!' not in str(re_json):
            error_print += '\n自动化函数(获取设备组%s的原始参数异常)!' % info['mix_device_name']
            raise MY_E
        mix_old_device_data = re_json['data']
        # 清理预混旧参数数据
        mix_old_device_data.pop('createdBy')
        mix_old_device_data.pop('createdTime')
        mix_old_device_data.pop('deviceUnitList')
        mix_old_device_data.pop('fileList')
        mix_old_device_data.pop('isRecipe')
        mix_old_device_data.pop('type')
        mix_old_device_data.pop('updatedBy')
        mix_old_device_data.pop('updatedTime')
        para = mix_old_device_data.copy()
        para['ip'] = info['produce_device_ip']
        response = session.put(url=info['server_ip'] + '/fbi/device/group/%s' % para['groupId'], data=json.dumps(para),timeout=5)
        re_json = response.json()
        len_request += 1
        if '修改设备组成功!' not in str(re_json):
            error_print += '\n自动化函数(修改预混站ip不成功设置ip%s)!' % para['ip']
            raise MY_E
        # 预混站模式
        wj_print('开始模拟预混站操作：')
        # 获取工单以及相别
        ep_list =[]
        for p in phase_dict['EP']:
            ep_list.append(p['phaseName'])
        rs = get_batch_phase(batch=info['batchCode'],phase =ep_list)
        if not rs:
            error_print += '\n预混站获取批次以及相别接口异常！'
            raise MY_E

        # 模拟完成第一个外相
        rs = auto_phase(phase_dict['EP'][0].copy(),deviceGroup='',device='',phase_dict=phase_dict)
        wj_print('')
        if not rs:
            error_print += '\n完成相别%s异常！'%phase_dict['EP'][0]['phaseName']
            raise MY_E
        wj_print('预混站接口测试通过!(已完成相别%s)'%phase_dict['EP'][0]['phaseName'])

        # 预混站改回原先ip
        para = mix_old_device_data.copy()
        response = session.put(url=info['server_ip'] + '/fbi/device/group/%s' % para['groupId'], data=json.dumps(para),
                               timeout=5)
        re_json = response.json()
        len_request += 1
        if '修改设备组成功!' not in str(re_json):
            error_print += '\n自动化函数(预混站改回自身ip不成功设置ip%s)!' % para['ip']
            raise MY_E
        # 改回原先ip
        para = old_device_data.copy()
        response = session.put(url=info['server_ip'] + '/fbi/device/group/%s' % para['groupId'], data=json.dumps(para),timeout=5)
        re_json = response.json()
        len_request += 1
        if '修改设备组成功!' not in str(re_json):
            error_print += '\n自动化函数(改回自身ip不成功设置ip%s)!' % para['ip']
            raise MY_E

        # 乳化机获取工单相别测试
        wj_print('开始模拟乳化机操作：')
        all_p_list = []
        for P in  phase_dict:
            for p in phase_dict[P]:
                all_p_list.append(p['phaseName'])
        rs = get_batch_phase(batch=info['batchCode'], phase=all_p_list)
        if not rs:
            error_print += '\n乳化机获取批次以及相别接口异常！'
            raise MY_E
        # 乳化机生产
        main_phase = dict()
        for p in phase_dict['AP']:
            if p['aimsPhaseCode']=='':
                main_phase = p.copy()
                break
        rs = auto_phase(main_phase, deviceGroup='', device='', phase_dict=phase_dict)
        if not rs:
            error_print += '\n完成相别%s异常！' % main_phase['phaseName']
            raise MY_E
        wj_print('乳化机接口测试通过!')

        return True


    except MY_E:
        return False
    except Exception as E:
        log.write('burden_function：\nlocals：' + str(locals()))
        wj_print('#' * 50)
        wj_print(format_exc())
        wj_print('#' * 50)
        return False

# 解析json将需要的数据加入到info
def get_data(data,para):
    '''
    :param data:json
    :param data:(['data', 'list', 0], {'workOrderId': 'workOrderId'})
    :return:bool
    '''
    index = para[0]
    target = para[1]
    now_data = data
    # 遍历找到最终目标json
    for ind in index:
        now_data = now_data[ind]
    if not now_data:
        return False
    # 遍历将需要的参数加入到info
    for tar in target:
        tar_data = now_data.get(tar,'')
        if tar_data:
            info[tar] = tar_data
        else:
            return False
    # 都正常的话则返回True
    return True



# √替换参数<>
def replace_para(data):
    data = data.strip()
    r = re.compile('<.+?>')
    find_list = r.findall(data)
    for f in find_list:
        data = data.replace(f,info[f[1:-1]])
    return data

# 执行任务方法
def request_task(request):
    '''
                    0模拟名称1请求方式2路径 3表单4断言5提取数据6.处理函数
    :param request:['登录','get','/fbi/stock/material',{'current':1},['提交成功！'],[(["data","list",0],{"workOrderId":"workOrderId"})]]
    :return: None
    '''
    try:
        # 引入全局变量
        global authorization
        global len_request
        global error_print

        wj_print("正在模拟<{0}>{3}({1}/{2})".format(request[0][:10],i,request_quantity,"--"*(11-len(request[0][:10]))))
        method = request[1].lower()
        # 更新表单
        request[3] = replace_para(request[3])
        request[3] = eval(request[3])
        # 更新路径
        request[2] = replace_para(request[2])
        # get
        if  method == 'get':
            response = session.get(url=info['server_ip']+request[2],params=request[3],timeout=5)
        elif method == 'post':
            response = session.post(url=info['server_ip'] + request[2], data=json.dumps(request[3]), timeout=5)
        elif method == 'put':
            response = session.put(url=info['server_ip'] + request[2], data=request[3], timeout=5)
        else:
            error_print = '\n不支持该请求方式(%s)'%method
            raise MY_E
        len_request+=1
        response_json = response.json()

        # 遍历断言
        for a in request[4]:
            if a in str(response_json):
                break
        else:
            error_print += '\n断言失败！\n断言：{0}\n断言数据：{1}'.format(request[4],str(response_json))
            raise MY_E

        # 添加token
        if not authorization:
            authorization = response_json['data']['token']
            session.headers.update({"authorization":authorization})

        # 是否需要提取其中参数
        if len(request)> 5:
            for fask in request[5]:
                if not get_data(response_json,fask):
                    error_print += "\n提取参数失败！\n提取公式：{0}\n提取数据：{1}".format(str(fask),str(response_json))
                    raise MY_E
        # 回调函数
        if len(request)>6:
            if not globals().get(request[6])(response_json):
                error_print += "\n回调函数异常！\n函数：%s"%str(request[6])
                raise MY_E


    except MY_E:
        raise MY_E
    except Exception as E:
        log.write('request_task:：\nlocals：'+str(locals()))
        raise E


#-----------------------------------------------------分割线------------------------------------------------------------

# √如果不是以庫导入时执行
if __name__ == '__main__':
    try:
        # 日志
        log = Log()
        # 请求总数量
        request_quantity = len(request_lists)
        # 当前请求位置
        i = 1
        # 开始的时间
        start_time = time.time()
        # 遍历执行request_lists任务
        for r in request_lists:
            request_task(r)
            i += 1
        # 请求总数
        d1 = len_request
        # 用时
        d2 = round(time.time() - start_time, 2)
        # 平均用时
        d3 = round((time.time() - start_time) / len_request, 2)
        wj_print("全部接口测试通过！共请求{0}个接口,用时{1}s,平均用时{2}s.".format(d1, d2, d3))

    # 捕获主动触发的异常
    except MY_E:
        wj_print('*' * 50)
        wj_print(error_print)
        wj_print('*' * 50)
        log.save()
    # 系统自己触发的异常
    except:
        # 将异常写进日志
        wj_print('#' * 50)
        log.write(format_exc())
        wj_print('#' * 50)
        # 保存日志并打开
        log.save()
        print(format_exc())

