# -*- coding:utf-8 -*-
# 导入gui模块
from tkinter import Tk,Label,Button,Entry,StringVar,DISABLED,NORMAL
# from tkinter.ttk import Separator
from tkinter.filedialog import askopenfilename
from threading import Thread
from os import path,getcwd,listdir
from time import localtime,strftime
from xlrd import open_workbook
from xlwt import Workbook

# 配置
default = {
    # *标题名字
    "WindowName" : "安舍Excel合成",
    # *窗口大小
    "WindowSize" : "600x450",
    # *窗口位置
    "WindowLocation" : "10+10",
    # A表格列表
    "Alist":['a.xlsx','A.xlsx','a.XLSX','A.XLSX'],
    # B表格列表
    "Blist":['b.xlsx','B.xlsx','b.XLSX','B.XLSX'],
    # 当前路径
    "path":getcwd(),
    # 误差
    'error':0.005
}



class Wj_Window():
    # 初始化
    def __init__(self,default):
        # 创建窗口
        self.window = Tk()
        # 保存元素对象（字典）
        self.element = dict()
        self.default = default
        # 是否已经获取a，b表
        self.A = None
        self.A_Data_list = []
        self.B = None
        self.B_Data_dict = dict()
        # 绑定标题名字
        self.window.title(self.default["WindowName"])
        # 窗口大小以及位置
        self.window.geometry(self.default["WindowSize"] + "+" + self.default["WindowLocation"])
        # 创建A,B模块
        self.createLabel('A', 1)
        self.createLabel('B', 6)
        # ab是否导入
        a = Button(self.window, text='配料列表', font=('default font', 14), width=10, height=1,bg='pink')
        self.element['A'] = a
        a.grid(row=11, column=0)
        b = Button(self.window, text='半成品列表', font=('default font', 14), width=10, height=1,bg='pink')
        self.element['B'] = b
        b.grid(row=11, column=1)
        # 合并按钮
        merge = Button(self.window,text = '合并',font=('default font', 14), width=10,height=1,command=self.mergButton)
        self.element['merge' + 'Button'] = merge
        merge.grid(row=11, column=2)
        self.window.grid_rowconfigure(11, minsize=50)
        # 合并信息标签
        mergeLabel = Label(self.window, font=('default font', 14), text="",
                          justify='left', width=59, height=3, relief='groove', anchor='w')
        self.element['merge' + 'Datalabel'] = mergeLabel
        mergeLabel.grid(row=12, column=0, rowspan=3, columnspan=5)

        # 刚打开程序就搜索有没ab文件
        self.startFile(self.default['Alist'], 'A')
        self.startFile(self.default['Blist'], 'B')


    # 设置行列之间的距离
    def setConfigure(self,rawlong,columnlong):
        # 获取总行和列
        col_count, row_count= self.window.grid_size()

        for row in range(row_count):
            self.window.grid_rowconfigure(row, minsize=rawlong)

        for col in range(col_count):
            self.window.grid_columnconfigure(col, minsize=columnlong)




    # 创建模块
    def createLabel(self,name,index):
        # 大标题【A表格】
        biglabel = Label(self.window, text= name+"表格", font=("microsoft yahei", 18),anchor='w')
        # 将标签放入窗口（第一行的第一个）
        biglabel.grid(row=index, column=0,rowspan =1)

        # 小标题【文件名】
        smalllabel = Label(self.window, text="文件路径：", font=('default font', 14))
        # 将标签放入窗口（第一行的第一个）
        smalllabel.grid(row=index+1, column=0)

        # 文本框【AEntry,AEntryString】
        entryString = StringVar()
        entry = Entry(self.window, textvariable=entryString,width=36,font=('default font', 14),state=DISABLED)
        self.element[name+'Entry'] = entry
        self.element[name+'EntryString'] = entryString
        entry.grid(row=index+1, column=1,columnspan=3)



        # 按钮【选择文件】AButton
        button = Button(self.window,text = '选择文件'+name,font=('default font', 14), width=12,height=1,command=lambda :self.selectButton(name))
        self.element[name + 'Button'] = button
        button.grid(row=index+1, column=4)

        # 详细数据ADatalabel
        datalabel = Label(self.window,font=('default font', 14), text= "",justify='left',width=59,height=3,relief='groove',anchor='w')
        self.element[name+'Datalabel'] = datalabel
        datalabel.grid(row=index+2, column=0,rowspan =3,columnspan=5)

        # 分割线
        # Separator(self.window, orient='horizontal').grid(row=index + 5, column=0,columnspan=5,sticky="we")

    # 合并文件按钮
    def mergButton(self):
        if self.A and self.B:
            try:
                # 创建
                work_book = Workbook(encoding='utf-8')
                sheet1 = work_book.add_sheet('sheet1')
                head_list = ['订单','物料编号','物料描述','订单数量 (GMEIN)','物料','物料描述','需求数量 (EINHEIT)', '撤回数量 (EINHEIT)', '短缺 (EINHEIT)', '未清数量 (EINHEIT)', '基本计量单位 (=EINHEIT)', '工厂', '系统状态', '库存地点', '需求日期','误差']
                # 创建表头
                for i in range(len(head_list)):
                    sheet1.write(0,i,head_list[i])
                # 填数据
                for i in range(1,len(self.A_Data_list)+1):
                    datalist = self.A_Data_list[i-1]
                    batch = str(self.A_Data_list[i-1][0])
                    sheet1.write(i,0,batch)
                    sheet1.write(i, 1, self.B_Data_dict.get(batch,['','',''])[0])
                    sheet1.write(i, 2, self.B_Data_dict.get(batch,['','',''])[1])
                    sheet1.write(i, 3, self.B_Data_dict.get(batch,['','',''])[2])
                    satrt=4
                    for x in datalist[1:]:
                        sheet1.write(i,satrt,x)
                        satrt+=1


                # 生成文件
                work_book.save('C.xls')


                self.element['merge' + 'Datalabel'].config(text='成功合并文件C.xls')

            # 异常输出erro
            except Exception as e:
                print(e)
                self.element['merge' + 'Datalabel'].config(text='ERRO：'+str(e)+'\n\n')

        # 还不够数据
        else:
            self.element['merge' + 'Datalabel'].config(text ='还欠缺数据，无法合并！\n\n')

    # 选择文件按钮函数
    def selectButton(self,name):
        # 设置按钮不可点击，和修改按钮字体
        self.element[name+'Button'].configure(state=DISABLED)
        self.element[name + 'Button'].configure(text='正在读取文件')
        # 线程
        thread = Thread(target=self.selectFile,args=(name,))
        # 守护进程
        thread.setDaemon(True)
        thread.start()


    # 线程执行选择文件按钮
    def selectFile(self,name):
        # 选择文件
        path_ = askopenfilename()
        # 设置文本框的内容为文件的路径
        self.element[name + 'EntryString'].set(path_)
        # 设置按钮正常
        self.element[name + 'Button'].configure(state=NORMAL)
        self.element[name + 'Button'].configure(text='选择文件')
        if path_ == '':
            self.element[name + 'Datalabel'].configure(
                text='')
            if name == 'A':
                self.A = None
                self.A_Data_list = []
                self.element['A'].config(bg = 'pink')
            elif name == 'B':
                self.B = None
                self.B_Data_dict = dict()
                self.element['B'].config(bg='pink')
            return
        # 解析文件
        self.parsFile(path_,path_.split('\\')[-1],name)

    # 开始查看当前路径下的ab
    def startFile(self,filenamelist,name):
        # 不存在文件的话
        if not path.exists(self.default['path']+'\\'+filenamelist[0]):
            self.element[name+'Datalabel'].configure(text='不存在'+name.lower()+'.XLSX\n\n')
        else:
            filelist = listdir(self.default['path'])
            for i in filenamelist:
                if i in filelist:
                    self.element[name+'EntryString'].set(self.default['path']+'\\'+i)
                    # 解析文件
                    self.parsFile(self.default['path']+'\\'+i,i,name)
                    break


    # 解析文件
    def parsFile(self,filepath,filename,name):
        # 获取文件修改时间
        mtime = strftime('%Y-%m-%d %H:%M:%S',localtime(path.getmtime(filepath)))
        # 打开文件
        try:
            # 打开excel
            workbook=open_workbook(filepath)
            # 获取第一个sheet
            sheet1 = workbook.sheet_by_index(0)
            # 第一行字段列表
            row1_list = sheet1.row_values(0)
            # B2的首字符
            dataB2 = sheet1.cell(1,1).value[0]
            # 判断是否为B文件
            if dataB2 == '1' and row1_list[0:4]==['订单', '物料编号', '物料描述', '订单数量 (GMEIN)']:
                return_data = self.parsBFile(sheet1,name)
            # 判断是否为A文件
            elif dataB2 =='9'and row1_list[0:12] == ['订单', '物料', '物料描述', '需求数量 (EINHEIT)', '撤回数量 (EINHEIT)', '短缺 (EINHEIT)', '未清数量 (EINHEIT)', '基本计量单位 (=EINHEIT)', '工厂', '系统状态', '库存地点', '需求日期']:
                return_data = self.parsAFile(sheet1,name)
            # 文件不符合时
            else:
                raise Exception('文件格式不规范')

            self.element[name + 'Datalabel'].configure(text='文件名：'+filename+'【'+return_data+'】'+'\n修改时间：'+mtime+'\n文件行数：'+str(sheet1.nrows))
        # 捕抓异常
        except Exception as E:
            self.element[name + 'Datalabel'].configure(
                text='文件名：' + filename + '\n修改时间：' + mtime + '\nERRO：' + str(E))
            print(name)
            if self.A == name:
                self.A = None
                self.A_Data_list = []
                self.element['A'].config(bg = 'pink')
            elif self.B == name:
                self.B = None
                self.B_Data_dict = dict()
                self.element['B'].config(bg = 'pink')
    # 解析a表，配料表
    def parsAFile(self,sheet,name):
        l = []
        for i in range(1, sheet.nrows):
            ll = sheet.row_values(i)[0:12]
            # 切换单位
            if ll[7] == 'G':
                ll[3] = round(ll[3]*0.001,5)
            # 增加误差
            ll.append(round(ll[3]*self.default['error'],5))
            # 保留最小误差
            ll[3] = format(ll[3], '.5f')
            if format(ll[-1], '.5f') == '0.00000':
                ll[-1] = '0.00001'
            else:
                ll[-1] = format(ll[-1], '.5f')
            l.append(ll)
        if len(l)==0:
            return '半成品数据为空'
        else:
            # 需要覆盖且不为自己
            if self.A != None and self.A != name:
                self.element[self.A + 'EntryString'].set('')
                self.element[self.A + 'Datalabel'].configure(
                    text='')
            # 清空原有的完成
            if self.B == name:
                self.B = None
                self.B_Data_dict = dict()
                self.element['B'].config(bg='pink')

            self.A = name
            self.A_Data_list = l
            self.element['A'].config(bg='green')
        return '配料列表'+str(len(l))+'条数据'

    # 解析b表，半成品表
    def parsBFile(self,sheet,name):
        d = dict()
        for i in range(1,sheet.nrows):
            datalist = sheet.row_values(i)[0:4]
            if datalist[0] not in d:
                d[datalist[0]] = datalist[1:4]
        if len(d)==0:
            return '半成品数据为空'
        else:
            # 需要覆盖且不为自己
            if self.B != None and self.B != name:
                self.element[self.B + 'EntryString'].set('')
                self.element[self.B + 'Datalabel'].configure(
                    text='')
            # 清空原有的完成
            if self.A == name:
                self.A = None
                self.A_Data_list = []
                self.element['A'].config(bg='pink')

            self.B = name
            self.B_Data_dict = d
            self.element['B'].config(bg='green')
            return '半成品列表'+str(len(d))+'条数据'


    # 进入事件循环（运行）
    def run(self):
        self.window.mainloop()







'''
# 屏幕宽度
windowWidth = top.winfo_screenwidth()
# 屏幕高度
windowHeight = top.winfo_screenheight()
# 窗口虚化程度（值越小虚化程度）
top.attributes("-alpha",1)
'''


# 如果以主进程运行的话则执行
if __name__ == '__main__':
    # 实例化
    main = Wj_Window(default)
    # 进入事件循环
    main.run()
