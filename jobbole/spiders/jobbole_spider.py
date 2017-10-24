# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse
from jobbole.items import JobBoleArticleItem,ArticleItemLoader
from jobbole.utils.comman import get_md5
from scrapy.loader import ItemLoader
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

class JobboleSpiderSpider(scrapy.Spider):
    name = 'jobbole_spider'
    allowed_domains = ['jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="/home/wizardev/article/chromedriver")
        super(JobboleSpiderSpider, self).__init__()
        # spider_closed一定不能带括号
        dispatcher.connect(self.spider_closed,signals.spider_closed)

    def spider_closed(self,spider):
        print("closed")
        self.browser.quit()

    def parse(self, response):
        pass

        # post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        # for post_node in post_nodes:
        #     img_url = post_node.css("img::attr(src)").extract_first("")
        #     post_url = post_node.css("::attr(href)").extract_first("")
        #     yield Request(url=parse.urljoin(response.url, post_url), meta={"front_img_url": img_url},
        #                   callback=self.parse_tetail)
        # next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        # if next_url:
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_tetail(self, response):
        # article_item = JobBoleArticleItem()#初始化item
        # title = response.css(".entry-header h1::text").extract()[0]
        #
        # vote_num = int(response.css(".vote-post-up h10::text").extract()[0].strip().replace("·", "").strip())
        # fav_num = response.css(".bookmark-btn::text").extract()[0].strip()  # 点赞
        # content = response.css("div.entry").extract()
        # tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # str = re.match(r".*(\d+).*", fav_num)
        # if str:
        #     fav_num = int(str.group(1))
        # else:
        #     fav_num = 0
        # comment_num = response.css("a[href='#article-comment'] span::text").extract()[0]
        # match_str = re.match(r".*(\d+).*", comment_num)
        # if match_str:
        #     comment_num = int(match_str.group(1))
        # else:
        #     comment_num = 0
        # article_item["title"] = title
        # article_item["front_img_url"] = [front_img_url]
        # article_item["content"] = content
        # try:
        #     create_time = datetime.datetime.strptime(create_time, "%Y/%m/%d").date()
        # except Exception as  e:
        #     create_time = datetime.datetime.now().date()
        # article_item["create_time"] = create_time
        # article_item["vote_num"] = vote_num
        # article_item["fav_num"] = fav_num
        # article_item["comment_num"] = comment_num
        # article_item["url"] = response.url
        # article_item["tags"] = tags
        # article_item["url_object_id"] = get_md5(response.url)
        article_item_loader = ArticleItemLoader(item=JobBoleArticleItem(),response=response)
        front_img_url = response.meta.get("front_img_url", "")
        create_time = response.css(".entry-meta .entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·","").strip()
        article_item_loader.add_css("title",".entry-header h1::text")
        article_item_loader.add_value("front_img_url",[front_img_url])
        article_item_loader.add_value("url",response.url)
        article_item_loader.add_value("url_object_id",get_md5(response.url))
        article_item_loader.add_css("content","div.entry")
        article_item_loader.add_value("create_time",create_time)
        article_item_loader.add_css("vote_num",".vote-post-up h10::text")
        article_item_loader.add_css("fav_num",".bookmark-btn::text")
        article_item_loader.add_css("comment_num","a[href='#article-comment'] span::text")
        article_item_loader.add_css("tags","p.entry-meta-hide-on-mobile a::text")

        article_item = article_item_loader.load_item()
        yield article_item
