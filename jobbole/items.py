# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import datetime, re
from scrapy.loader import ItemLoader
from jobbole.utils.comman import extract_num
from jobbole.settings import SQL_DATETIME_FORMAT
class JobboleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    try:
        create_time = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_time = datetime.datetime.now().date()

    return create_time


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


def return_value(value):
    return value


def remove_comment_tags(value):
    # 去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


class ArticleItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    front_img_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_img_path = scrapy.Field()
    content = scrapy.Field()
    create_time = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    vote_num = scrapy.Field()
    fav_num = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_num = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field(
    )
    tags = scrapy.Field(
        output_processor=Join(","),
        input_processor=MapCompose(remove_comment_tags)
    )

    def get_insert_sql(self):
        # ON DUPLICATE KEY UPDATE content=VALUES(fav_num)这句话的意思是再下一次插入数据时，如果主键冲突，则进行指定内容的更新
        insert_sql = """
            insert into jobbole_article(title, front_img_url,front_img_path,content,create_time,vote_num,fav_num,
             comment_num,url, url_object_id, tags )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s) ON DUPLICATE KEY UPDATE content=VALUES(fav_num)
        """

        front_img_url = ""
        # content = remove_tags(self["content"])

        if self["front_img_url"]:
            front_img_url = self["front_img_url"][0]
        params = (self["title"], front_img_url, self["front_img_path"], self["content"],
                  self["create_time"], self["vote_num"], self["fav_num"], self["comment_num"], self["url"],
                  self["url_object_id"], self["tags"])

        return insert_sql, params

    pass


class ZhihuQusetionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    topics = scrapy.Field()
    content = scrapy.Field()
    notice_num = scrapy.Field()
    click_num = scrapy.Field()
    comments_num = scrapy.Field()
    answer_num = scrapy.Field()
    crawl_time = scrapy.Field()
    # crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        # ON DUPLICATE KEY UPDATE content=VALUES(fav_num)这句话的意思是再下一次插入数据时，如果主键冲突，则进行指定内容的更新
        insert_sql = """
            insert into zhihu_question(zhihu_id, title,url,topics,content,notice_num,click_num ,comments_num,answer_num,
           crawl_time )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE notice_num=VALUES(notice_num),
            click_num=VALUES(click_num),comments_num=VALUES(comments_num),answer_num=VALUES(answer_num)
        """


        zhihu_id = "".join(self["zhihu_id"])
        title = "".join(self["title"])
        url = "".join(self["url"])
        topics = "".join(self["topics"])
        content = "".join(self["content"])
        notice_num = self["click_num"][0]
        click_num = self["click_num"][1]
        comments_num = extract_num("".join(self["comments_num"]))
        answer_num = extract_num("".join(self["answer_num"]))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (zhihu_id, title, url,topics, content,notice_num,click_num,comments_num,answer_num,crawl_time)

        return insert_sql, params

    pass


class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    content = scrapy.Field()
    author_id = scrapy.Field()
    comments_num = scrapy.Field()
    praise_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        # ON DUPLICATE KEY UPDATE content=VALUES(fav_num)这句话的意思是再下一次插入数据时，如果主键冲突，则进行指定内容的更新
        insert_sql = """
               insert into zhihu_answer(zhihu_id,url,question_id,content,author_id,comments_num,praise_num,
              create_time,update_time,crawl_time )
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content=VALUES(content),
               comments_num=VALUES(comments_num),praise_num=VALUES(praise_num),update_time=VALUES(update_time)
           """
        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (self["zhihu_id"], self["url"],self["question_id"],self["content"] ,self["author_id"],self["comments_num"]
                  , self["praise_num"],create_time,update_time,crawl_time)

        return insert_sql, params

    pass
