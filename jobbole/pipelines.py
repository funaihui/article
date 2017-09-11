# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
from scrapy.exporters import JsonItemExporter
import MySQLdb
from twisted.enterprise import adbapi
import MySQLdb.cursors


class JobbolePipeline(object):
    def process_item(self, item, spider):
        return item


# 获取保存图片的路径
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_img_url" in item:
            for ok, value in results:
                img_file_path = value["path"]
            item["front_img_path"] = img_file_path
        return item


# 使用json保存数据
class JSONWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


# 使用JSONExporter保存数据
class JSONExporterPipeline(object):
    def __init__(self):
        self.file = open("article.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# 使用同步的方式进行数据的保存
class MySQLPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('192.168.0.118', "root", "wizardev", "jobbole_spider", charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = "insert into article(title,front_img_url,front_img_path,content,url_object_id)" \
                     "VALUES (%s,%s,%s,%s,%s)"
        self.cursor.execute(insert_sql, (
            item["title"], item["front_img_url"], item["front_img_path"], item["content"], item["url_object_id"]))
        self.conn.commit()
        return item


# 使用异步的方式进行数据的保存
class MySQLTwistPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handler_error,item)  # 处理异常

    def handler_error(self, failure,item):
        print(failure,item)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        print(insert_sql,params)
        cursor.execute(insert_sql, params)
