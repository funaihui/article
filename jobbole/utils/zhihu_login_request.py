# -*- coding: utf-8 -*-
# @Time    : 17-9-9 上午10:31
# @Author  : wizardev
# @Email   : wizarddev@163.com
# @File    : zhihu_login_request.py
# @Software: PyCharm
import requests
import re
import os
import time
import tempfile

try:
    import cookielib
except:
    import http.cookiejar as cookielib
import os.path

try:
    from PIL import Image
except:
    pass
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")
agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/60.0.3112.113 Chrome/60.0.3112.113 Safari/537.36"
header = {
    "Host": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/",
    "User-Agent": agent
}


# 判断是否登录
def is_login():
    setting = "https://www.zhihu.com/settings/profile"
    code = session.get(setting, headers=header, allow_redirects=False).status_code
    if code == 200:
        return True
    else:
        return False


def get_xsrf():
    '''_xsrf 是一个动态变化的参数'''
    index_url = 'https://www.zhihu.com'
    # 获取登录时需要用到的_xsrf
    index_page = session.get(index_url, headers=header)
    html = index_page.text
    pattern = r'name="_xsrf" value="(.*?)"'
    # 这里的_xsrf 返回的是一个list
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]


# 获取验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=header)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("请输入验证码：\n>")
    return captcha


def login(account, passwd):
    # 判断是否是电话登录
    if re.match("^1\d{10}", account):
        print("电话方式登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "password": passwd,
            "phone_num": account
        }
    # 判断是否是邮箱登录
    elif "@" in account:
        print("邮箱方式登录")
        post_url = "https://www.zhihu.com/login/email"
        post_data = {
            "_xsrf": get_xsrf(),
            "password": passwd,
            "email": account
        }
    # response_text = session.post(url=post_url, data=post_data, headers=header)
    # 不需要验证码直接登录成功
    login_page = session.post(post_url, data=post_data, headers=header)
    login_code = login_page.json()
    if login_code['r'] == 1:
        # 不输入验证码登录失败
        # 使用需要输入验证码的方式登录
        post_data["captcha"] = get_captcha()
        login_page = session.post(post_url, data=post_data, headers=header)
        login_code = login_page.json()
        print(login_code['msg'])
    # 保存 cookies 到文件，
    # 下次可以使用 cookie 直接登录，不需要输入账号和密码
    session.cookies.save()


if is_login():
    pass
else:
    login("18317773572", "1151631351fnh")
