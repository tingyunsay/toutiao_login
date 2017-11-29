#!/usr/bin/env python
# !coding:utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import sys, os
import re, logging
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging
from PIL import Image
from pyquery import PyQuery
import base64
from io import StringIO
import requests
from yundama import get_verifycode
import urllib

#author -- tingyun
#done 2017-11-29 22:00

dcap = dict(DesiredCapabilities.PHANTOMJS)

'''
# 移动端的ua，这里我们先跑通这个流程再说,pc端换一份代码
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0"
    " Mobbile Safari/533.1"
)
'''
#pc端的ua，调试通过
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.94 Ch"
    "rome/62.0.3202.94 Safari/537.36"
        )

logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)

# 获取头条验证码的二进制数据，一次一张图片
def get_content(url):
    res = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.94 Chrome/62.0.3202.94 Safari/537.36"}).content
    # res = PyQuery(res.content)
    img_content = re.search("(?<=captcha: \').*(?=\')", res, re.S).group()
    content = base64.b64decode(img_content)
    return content

def save2file(browser):
    data = browser.page_source
    with open("nima.html", "wb") as f:
        f.write(data)
        f.close()

def run(login_url,user,pwd):
    user = user
    pwd = pwd
    browser = webdriver.PhantomJS(desired_capabilities=dcap,
                                  executable_path='/home/node/node_modules/phantomjs-prebuilt/bin/phantomjs')
    #解决无法点击（非button）的事件
    browser.set_window_size(1124, 850)
    # browser = webdriver.Firefox()
    browser.get(login_url)
    time.sleep(1)
    #browser.save_screenshot("pc_first.png")

    # 切换到邮箱登录
    switch = browser.find_element_by_xpath("//li[@data-pid=\"mail_phone\"]")
    switch.click()
    #browser.save_screenshot("pc_switch.png")

    username = browser.find_element_by_name("account")
    username.clear()
    username.send_keys(user)
    #browser.save_screenshot("pc_user.png")

    password = browser.find_element_by_xpath('//input[@type="password"]')
    password.clear()
    password.send_keys(pwd)
    #browser.save_screenshot("pc_pass.png")
    try:
        code = browser.find_element_by_name("captcha")
        code.clear()
        img = browser.find_element_by_xpath("//div[@class=\"captcha-wrap\"]/img").get_attribute("src")
        img_content = re.sub("data:image/gif;base64,","",img.encode('utf-8'))
        img_content = base64.b64decode(img_content)
        with open("temp.png", "wb") as f:
            f.write(img_content)
            f.close()
        fuck_code = get_verifycode()
        time.sleep(1)
        code.send_keys(fuck_code)
        #browser.save_screenshot("pc_code.png")
    except Exception, e:
        logging.warning(e)
        logging.warning("没有验证码.....")
        pass

    commit = browser.find_element_by_name("submitBtn")
    commit.click()
    time.sleep(2)
    #browser.save_screenshot("fuck.png")

    cookie = {}
    if "今日头条" in browser.title.encode('utf-8'):
        for elem in browser.get_cookies():
            cookie[elem["name"]] = elem["value"]
        logging.warning("Get Cookie Success!( Account:%s )" % user)
    return cookie


if __name__ == '__main__':
    #just for test , for get captcha
    # url = "https://sso.toutiao.com/login/?service=https://mp.toutiao.com/sso_confirm/?redirect_url=JTJGY29yZSUyRmFydGljbGUlMkZtZWRpYV9hcnRpY2xlX2xpc3QlMkY="
    # content = get_content(url)
    login_url = "https://sso.toutiao.com/login/"
    #输入账号密码
    user = ""
    pwd = ""

    #上面获取的cookie,需要一定时间，大概5 ～ 7 秒
    cookies = run(login_url,user,pwd)

    url = "http://mp.toutiao.com/search_media_article_list/?search_word=%s&offset=0&limit=10&from_time=0"%(urllib.quote("周深 浅浅"))
    res = requests.get(url,cookies=cookies).json()

    id = "6481470281280913934"
    hello = {}
    for i in res['data']['articles']:
        if i['id'].encode('utf8') == id:
            hello['push'] = i['impression_count']
            hello['play'] = i['go_detail_count']
            hello['comment_count'] = i['comment_count']
            hello['share_count'] = i['share_count']
            hello['favorite_count'] = i['favorite_count']

    print hello

