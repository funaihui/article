# -*- coding: utf-8 -*-
# @Time    : 17-10-24 上午9:48
# @Author  : wizardev
# @Email   : wizarddev@163.com
# @File    : crawl_xici_ip.py
# @Software: PyCharm
import requests
from scrapy.selector import Selector


def crawl_ips():
    agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/60.0.3112.113 Chrome/60.0.3112.113 Safari/537.36"

    header = {
        "User-Agent": agent
    }
    # for i in range(2472):
        # re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=header)
    re = requests.get("http://www.xicidaili.com/nn/", headers=header)
    select = Selector(text=re.text)
    all_trs = select.css("#ip_list tr")
    ip_list = []
    for tr in all_trs[1:]:
        speed_str = tr.css(".bar::attr(title)").extract()[0]
        if speed_str:
            speed = float(speed_str.split("秒")[0])
        all_texts = tr.css("td::text").extract()
        ip = all_texts[0]
        port = all_texts[1]
        proxy_type = all_texts[5]
        ip_list.append(ip, port, proxy_type, speed)
        print(all_texts)

if __name__ == "__main__":

    print(crawl_ips())
