# -*- coding: utf-8 -*-
# @Time    : 17-10-24 上午11:53
# @Author  : wizardev
# @Email   : wizarddev@163.com
# @File    : selenium_spider.py
# @Software: PyCharm
from selenium import webdriver

browser = webdriver.Chrome(executable_path="/home/wizardev/article/chromedriver")
browser.get('https://www.zhihu.com/#signin')

# browser.find_element_by_css_selector(".qrcode-signin-step1 span.signin-switch-password]").click()

browser.find_element_by_xpath("/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/span").click()
browser.find_element_by_css_selector(".view-signin input[name='account']").send_keys("18317773572")
browser.find_element_by_css_selector(".view-signin input[name='password']").send_keys("1151631351fnh")
browser.find_element_by_tag_name('button').click()

