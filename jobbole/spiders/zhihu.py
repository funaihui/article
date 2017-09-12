# -*- coding: utf-8 -*-
import scrapy
import re
import time
import os
import datetime
import json
from scrapy.loader import ItemLoader
from urllib import parse
from jobbole.items import ZhihuQusetionItem, ZhihuAnswerItem

try:
    from PIL import Image
except:
    pass
from scrapy.http import Request, FormRequest


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    account = "18317773572"
    passwd = ""
    agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/60.0.3112.113 Chrome/60.0.3112.113 Safari/537.36"
    header = {
        "Host": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "User-Agent": agent
    }
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]

        for all_url in all_urls:
            match_object = re.match("(.*zhihu.com/question/(\d+))(/|$).*", all_url)
            if match_object:
                request_url = match_object.group(1)
                question_id = match_object.group(2)
                yield Request(url=request_url, callback=self.parse_question, meta={"question_id": question_id},
                              headers=self.header)
            else:
                yield Request(url=all_url, callback=parse, headers=self.header)
                pass

    # 解析问题的内容
    def parse_question(self, response):
        """
        class ZhihuQusetionItem(scrapy.Item):
        zhihu_id = scrapy.Field()
        title = scrapy.Field()
        url = scrapy.Field()
        topics = scrapy.Field()
        content = scrapy.Field()
        notice_num = scrapy.Field()
        click_num = scrapy.Field()
        answer_num = scrapy.Field()
        crawl_time = scrapy.Field()
        crawl_update_time = scrapy.Field()

        """
        zhihu_id = response.meta.get("question_id", "")

        item_load = ItemLoader(item=ZhihuQusetionItem(), response=response)
        item_load.add_value("zhihu_id", zhihu_id)
        item_load.add_css("title", ".QuestionHeader-title::text")
        item_load.add_value("url", response.url)
        item_load.add_css("topics", ".QuestionHeader-tags .Popover div::text")
        item_load.add_css("content", ".QuestionHeader-detail")
        item_load.add_css("notice_num", ".NumberBoard-value::text")
        item_load.add_css("click_num", ".NumberBoard-value::text")
        item_load.add_css("comments_num", ".QuestionHeader-Comment button::text")
        item_load.add_css("answer_num", ".List-headerText span::text")
        question_load = item_load.load_item()
        yield Request(url=self.start_answer_url.format(zhihu_id, 20, 0), callback=self.parse_answer,
                      headers=self.header)
        yield question_load

    def parse_answer(self, response):
        answer_json = json.loads(response.text)
        is_end = answer_json["paging"]["is_end"]
        totals = answer_json["paging"]["totals"]
        next_url = answer_json["paging"]["next"]
        for answer in answer_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
        yield answer_item
        if not is_end:
            yield Request(url=next_url, callback=self.parse_answer, headers=self.header)
        pass

    # 相当于初始化，类开始时最先执行的函数
    def start_requests(self):
        # return [scrapy.Request("https://www.zhihu.com", callback=self.login, headers=self.header)]
        t = str(int(time.time() * 1000))

        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        # setting = "https://www.zhihu.com/settings/profile"
        return [scrapy.Request(url=captcha_url, callback=self.get_captcha, headers=self.header)]
        # return [scrapy.Request(url=setting, callback=self.is_login, headers=self.header)]

    # 进行登录
    def login(self, response):

        html = response.text
        pattern = r'name="_xsrf" value="(.*?)"'
        # 这里的_xsrf 返回的是一个list
        xsrf = re.findall(pattern, html)[0]
        post_data = {
            "_xsrf": xsrf,
            "password": self.passwd,
            'captcha': response.meta['captcha'],
            "phone_num": self.account
        }
        # 利用FormRequest进行表单提交
        return [scrapy.FormRequest(
            url="https://www.zhihu.com/login/phone_num",
            formdata=post_data,
            headers=self.header,
            callback=self.check_login
        )]

    # 判断是否登录成功
    def check_login(self, response):
        login_page = response.text
        login_code = json.loads(login_page)
        print(login_code['msg'])
        if login_code['r'] == 0:
            for url in self.start_urls:
                yield Request(url, dont_filter=True, headers=self.header)

    # 获取验证码
    def get_captcha(self, response):

        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
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
        # 手动输入验证码后进行登录
        return Request("https://www.zhihu.com", headers=self.header, callback=self.login, meta={'captcha': captcha})
