# pip install aircv -i https://pypi.tuna.tsinghua.edu.cn/simple
# cv2：https://pypi.tuna.tsinghua.edu.cn/simple/opencv-python/
import aircv as ac
from PIL import ImageGrab
import time
import os

class ImageAuto():
    # 初始化
    def __init__(self,imsrc_dir,imobj_dir,flash = 1,timeout = 5,format = 'png',threshold = 0.5):
        # 搜索图片路径
        self.imsrc_dir = imsrc_dir
        # 查找的图片路径
        self.imobj_dir = imobj_dir
        # 保存的图片名称,后期遍历删除
        self.destroy_file_list = []
        # 查找频率
        self.flash = flash
        # 超时时间
        self.timeout = timeout
        # 图片格式
        self.format = format
        # 相似度
        self.threshold = threshold


    # 保存当前屏幕
    def get_current(self,bbox=None):
        '''
        :param bbox: (x1, y1, x2,y2)
        :return:(path,(x+,y+))
        '''
        file_name = str(time.time()).replace('.','_')
        # 有范围的截图
        if bbox:
            im = ImageGrab.grab(bbox)
        # 全图
        else:
            im = ImageGrab.grab()
        im_path = self.imsrc_dir + r'\\' + file_name +'.' + self.format
        im.save(im_path)
        self.destroy_file_list.append(im_path)

        if bbox:
            return (file_name,(bbox[0],bbox[1]))
        else:
            return (file_name,(0,0))


    # 删除保存的图片
    def close(self):
        for i in self.destroy_file_list:
            os.remove(i)


    # 主函数
    def main(self,imobj,imsrc = None,bbox = None):
        start_time = time.time()
        while (time.time()-start_time)<=self.timeout:
            new_time = time.time()
            if imsrc:
                match_result = self.match_img(imgsrc=imsrc,imgobj = imobj,threshold=self.threshold)
            else:
                current = self.get_current(bbox=bbox)
                match_result = self.match_img(imgsrc = current[0],imgobj=imobj,threshold=self.threshold)

            if match_result:
                return match_result
            else:
                use_time = time.time()-new_time
                print(use_time)
                if use_time < self.flash:
                    time.sleep(self.flash-use_time)
                else:
                    continue
        else:
            raise TimeoutError('超时未找到图片')


    # 查找图片
    def match_img(self,imgsrc, imgobj, threshold=None):
        '''
        :param imgsrc: 原始图像
        :param imgobj: 待查找的图片
        :param confidencevalue: 最低相识度
        :return:{'result': (1482.0, 748.5),
                'rectangle': ((1445, 708), (1445, 789), (1519, 708), (1519, 789)),
                'confidence': 0.9999999403953552,
                'shape0': (1920, 1080), 'shape1': (74, 81)}
        '''
        imsrc = ac.imread(self.imsrc_dir +r'\\'+imgsrc+'.'+self.format)
        imobj = ac.imread(self.imobj_dir +r'\\'+imgobj+'.'+self.format)

        # 是否有指定相识度
        if threshold:
            match_result = ac.find_template(imsrc, imobj,threshold=threshold)
        else:
            match_result = ac.find_template(imsrc, imobj, threshold=self.threshold)

        if match_result is not None:
            match_result['shape0'] = (imsrc.shape[1], imsrc.shape[0])  # 0为高，1为宽
            match_result['shape1'] = (imobj.shape[1], imobj.shape[0])  # 0为高，1为宽
            match_result['imgsrc_name'] = imgsrc

        return match_result


# try:
#     # 实例化，指定文件夹
#     a = ImageAuto(imsrc_dir=r"D:\wjwork\code\image_auto\0",imobj_dir=r"D:\wjwork\code\image_auto\1")
#     # 查找3图片在当前页面的坐标
#     r= a.main(imobj='3')
#     print(r)
#     # pip install PyUserInput -i https://pypi.tuna.tsinghua.edu.cn/simple
#     # https://www.jianshu.com/p/7e0158b99497
#     from pymouse import PyMouse
#     # 获取鼠标
#     mymouse = PyMouse()
#     # 鼠标当前的位置
#     print(mymouse.position())
#     # 鼠标移动到指定坐标
#     mymouse.move(int(r["result"][0]),int(r["result"][1]))
#     print(mymouse.position())
#
# finally:
#     # 删除截图的图片
#     a.close()






