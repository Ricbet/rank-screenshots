#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
import string
import time
import os
import shutil

from urllib.parse import quote
from bs4 import BeautifulSoup
from selenium import webdriver
from PIL import Image

# 初始的文件路径，改变工作目录
phantom_os_cwd = os.getcwd()
os.chdir(os.path.abspath('../'))
# init_os_cwd = os.getcwd()
# 全局变量，path指向phantomjs文件目录
driver = webdriver.PhantomJS(executable_path= phantom_os_cwd + "/phantomjs-2.1.1-macosx/bin/phantomjs")
# 设置模拟浏览器的宽高
driver.set_window_size('1024','500')
# 当前时间的对象
time_local_now = time.localtime(time.time())
# 当前年份
time_year = time.strftime('%Y',time_local_now)
# 当前月份
time_month = time.strftime('%m',time_local_now)
# 当前日
time_day = time.strftime('%d',time_local_now)
# 当前时间搓
time_now_rub = time.strftime('%Y%m%d%H%M%S',time_local_now)
# wd:关键词
# pn:0|50   0:从第1条开始取数据    50：从第51条开始取数据
# rn:获取数量 默认50条
def fnKeyRanking(wd = '', web_site='', pn = 0, rn = 10 ):
    time_local_now = time.localtime(time.time())
    # 当前时间搓
    time_now_rub = time.strftime('%Y%m%d%H%M%S', time_local_now)
    print('请稍等')
    # 百度的搜索情况
    def sourceBaidu(pn_baidu = 1,refer_find_baidu = 0):
        r_url = 'http://www.baidu.com/s?rn=%s' % rn + '&pn=%s'%((pn_baidu-1)*rn) + "&wd=%s" % wd
        # 处理带中文的url
        r_url = quote(r_url, safe=string.printable)
        print('第', pn_baidu, '页')
        print(r_url)
        try:
            with requests.get('http://www.baidu.com/s', params={'wd': wd, 'pn': (pn_baidu-1)*rn, 'rn': rn}, timeout=7) as r:
                soup = BeautifulSoup(r.text, 'html.parser')
                driver.get(r_url)
            try:
                # 筛选出含有result类的div，因为这是只包含搜索结果列表的标签数组
                p = re.compile(r'^result')
                # 筛选出含有该域名的列表，并算出排名
                str = re.compile(r'%s' % web_site)
                # 找到所有的搜索结果列表
                contentItem = soup.find(id="content_left").find_all('div', p)
                # 标示
                result = ''
                # 循环遍历域名和关键词在哪一个搜索结果列表当中，计算出下标即可得出排名
                for index, list in enumerate(contentItem):
                    _list = ''.join(re.split(r'\s+', list.get_text()))
                    if str.search(_list):
                        result = 'end'
                        # 定位到对应的位置并标注红框
                        driver.execute_script("""
                                (function(){
                                    var result = document.getElementById(%s)
                                    result.setAttribute('style','border:5px solid red;padding:10px;margin-left:-15px')
                                })()
                            """ %((index + 1)+((pn_baidu-1)*rn)))
                        # 保存为截图，同时命名为根据搜索的结果带上时间搓便于识别
                        out_img_name = 'baidu_' + time_now_rub + ".jpeg"
                        driver.save_screenshot(out_img_name)
                        # 使用PIL处理图片大小
                        im = Image.open(out_img_name)
                        # 获取生成的图片宽度和高度
                        w, h = im.size
                        # 等比例压缩图片
                        im.thumbnail((int(w / 1.5), int(h / 1.5)), Image.ANTIALIAS)
                        # 保存图片
                        try:
                            im.convert('RGB').save(out_img_name, 'JPEG', quality=80)
                        except IOError:
                            print('我是错误：' + im.mode)
                        # 生成目录的函数
                        findDirectory(out_img_name)
                        # 关闭窗口并结束进程
                        # driver.quit()
                        print('百度搜索排名在第', (index + 1)+((pn_baidu-1)*rn), '位')
                        return
                # 排名在100以后的不进行递归
                if result == '' and (pn_baidu - 1) * rn >= 100:
                    print('百度搜索排名在第', '100', '名以后')
                    return
                else:
                    sourceBaidu(pn_baidu + 1)
            except AttributeError as e:
                print('百度搜索的结果有误')
        except:
            refer_find_baidu += 1
            print('百度请求异常，正在重新检索', refer_find_baidu, '次')
            if refer_find_baidu <= 2:
                sourceBaidu(pn_baidu, refer_find_baidu)
            elif pn_baidu < 10:
                refer_find_baidu = 0
                sourceBaidu(pn_baidu + 1, refer_find_baidu)

    # 总是处理异常情况
    try:
        # 开启百度搜索情况
        sourceBaidu()
    except requests.RequestException as e:
        print(e)
    else:
        # 当没有发生异常的时候该语句正常执行
        print()

# 寻找当前目录的方法
def findDirectory( img_name ):
    # 递归查询目录，如果没有就创建目录
    src_item = ['public','uploads',time_year,time_month,time_day,'']
    join_src_item = '/'.join(src_item[0:-1])+'/'
    # 判断当前目录文件是否有uploads
    if( os.path.exists(join_src_item) == False ):
        os.makedirs(join_src_item)
        shutil.move(img_name, join_src_item)
    else:
        shutil.move(img_name, join_src_item)

# 执行该文件的主线程
if __name__ == '__main__':
    # 从第pn条开始读取数据
    pn = 0
    # 每一页列出的搜索数量
    rn = 10
    # 关键词
    wd = input('请输入关键词: ')
    # 目标地址
    url = input('请输入网址：')
    # 启动
    fnKeyRanking( wd, url, pn, rn )
    # 退出driver进程
    driver.quit()



