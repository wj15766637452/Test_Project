# -*- coding:utf-8 -*-
import pytest
from config import CONFIG
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from functions import *
import time
import os


driver = None

# 断言失败的时候截图到html报告里
@pytest.mark.hookwrapper
def pytest_runtest_makereport(item):
    """
    Extends the PyTest Plugin to take and embed screenshot in html report, whenever test fails.
    :param item:
    """
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    if report.when == 'call' or report.when == "setup":
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            dirpng = CONFIG.get('dir_png','./')
            if os.path.exists(dirpng) and os.path.isdir(dirpng):
                pass
            else:
                os.mkdir(dirpng)
            file_name = dirpng + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time())) + ".png"
            file_name1 = CONFIG.get('dir_png_html','./') + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))+ ".png"
            _capture_screenshot(file_name)
            if file_name:
                html = '<div><img src="%s" alt="screenshot" style="width:304px;height:228px;" ' \
                       'onclick="window.open(this.src)" align="right"/></div>' % file_name1
                extra.append(pytest_html.extras.html(html))
        report.extra = extra


# 断言失败插入截图
def _capture_screenshot(name):
    # selenium内置截图
    driver.get_screenshot_as_file(name)


# 优先执行并赋值，每次只执行一次，返回(浏览器，配置)
@pytest.fixture(scope="session",autouse=True)
def data():
    try:
        global driver
        # 获取浏览器
        chrome_ops = Options()
        driver = webdriver.Chrome(options = chrome_ops)
        # 隐式等待
        driver.implicitly_wait(CONFIG.get('implicitly_wait',5))
        driver.maximize_window()
        # 登录页面
        driver.get(CONFIG.get('url',''))
    # 创建浏览器失败则断言失败重新运行
    except Exception as e:
        driver.close()
        pytest.skip(msg='创建浏览器失败：'+ getError(),allow_module_level=True)

    # 校验是否登录成功
    try:
        # 输入账号
        input_name = waitFind(driver,By.XPATH,'''//*[@id="app"]/div/form/div[2]/div/div/input''')
        input_name.clear()
        input_name.send_keys(CONFIG.get('username',''))
        # 输入密码
        input_passwork = waitFind(driver, By.XPATH, '''//*[@id="app"]/div/form/div[3]/div/div/input''')
        input_passwork.clear()
        input_passwork.send_keys(CONFIG.get('passwork',''))
        # 点击登录
        log_in = waitFind(driver, By.XPATH, '''//button[@class='el-button el-button--primary']''')
        log_in.click()
        ass = waitFind(driver, By.XPATH, '''//*[@id="tags-view-container"]/div/div[1]/div/span''')
        # 判断是否登录成功
        if ass.text.strip() != '个人中心':
            driver.close()
            raise Exception('登陆系统失败')

        # 获取从cookies中获取token
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == 'vue_admin_template_token':
                CONFIG['token'] = cookie['value']
                break

    # 异常处理
    except Exception as e:
        driver.close()
        # 失败直接跳过全部用例
        pytest.skip(msg = '登陆系统失败：'+ getError(),allow_module_level= True)

    return driver,CONFIG