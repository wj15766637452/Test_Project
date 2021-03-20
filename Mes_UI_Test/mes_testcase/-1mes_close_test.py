# -*- coding:utf-8 -*-
import pytest


# 最后运行
@pytest.mark.run(order = -1)
# 关闭浏览器
def test_close_webdriver(data):
    try:
        data[0].close()
    # 关闭异常
    except:
        assert 0,'关闭浏览器失败'
    # 如果没操作则执行
    else:
        assert 1
