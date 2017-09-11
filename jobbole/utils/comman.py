# -*- coding: utf-8 -*-
# @Time    : 17-9-7 下午2:56
# @Author  : wizardev
# @Email   : wizarddev@163.com
# @File    : comman.py
# @Software: PyCharm
import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


if __name__ == "__main__":
    print(get_md5("http://www.baidu.com"))
