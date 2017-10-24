# -*- coding: utf-8 -*-
# @Time    : 17-9-6 下午2:29
# @Author  : wizardev
# @Email   : wizarddev@163.com
# @File    : main.py
# @Software: PyCharm
from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "jobbole_spider"])
# execute(["scrapy", "crawl", "zhihu"])
