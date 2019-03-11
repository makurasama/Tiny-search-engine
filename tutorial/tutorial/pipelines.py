from scrapy import log
import pymysql
import pymysql.cursors
import codecs
from twisted.enterprise import adbapi

index = 1 
class TutorialPipeline(object):

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            port=settings['MYSQL_PORT'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)


    def __init__(self,dbpool):
        self.dbpool=dbpool

    #pipeline默认调用
    def process_item(self,item,spider):
        d=self.dbpool.runInteraction(self._conditional_insert,item)#调用插入的方法
        global index
        index+=1
        log.msg("-------------------%d连接好了-------------------"%(index))
        d.addErrback(self._handle_error,item,spider)#调用异常处理方法
        d.addBoth(lambda _: item)
        return d

    def _conditional_insert(self,cursor,item):
        log.msg("-------------------%d打印-------------------"%(index))
        
        sql="insert into properties (url, title, keywords, description,content) values(%s,%s,%s,%s,%s)"
        #sql="insert into properties ( url, title, keywords, description, content) values(%s, %s, %s, %s, %s)"
        #params = (item['url'], str(item['title']), str(item['keywords']), str(item['description']), str(term['content']))
        params = (str(item['url']), str(item['title']), str(item['keywords']),str(item['description']) ,str(item['content']) )
        cursor.execute(sql, params)
        log.msg("------------------- %d 轮循环完毕-------------------"%(index))
    def _handle_error(self, failue, item, spider):
        print('--------------database operation exception!!-----------------')
        print(failue)