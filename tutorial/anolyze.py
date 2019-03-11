'''
	* 对内容进行分词，录入invert_index数据表，为后端查询倒排索引做准备
'''
import jieba
import jieba.analyse
import pymysql
import pymysql.cursors
import codecs
import sys


#保存进invert_index表
def save(url,words,tf_idf):
	db = pymysql.connect(
    host = "127.0.0.1",
    user = "root",
    password = "mimamima",
    database = "news",
    charset = 'utf8',
    cursorclass = pymysql.cursors.DictCursor)
	cursor = db.cursor()
	data = (url,words,tf_idf)
	#print (tf_idf)
	sql = "INSERT INTO invert_index (url, words, tf_idf) VALUES(%s,%s,%s)"
	try:
		cursor.execute(sql,data)
		db.commit()
	except:
		info = sys.exc_info()
		print( info[0], ":", info[1])
		db.rollback()
	cursor.close()
	db.close()

#分词
def  extract_word():
	db = pymysql.connect(
    host = "127.0.0.1",
    user = "root",
    password = "mimamima",
    database = "news",
    charset = 'utf8',
    cursorclass = pymysql.cursors.DictCursor)

	cursor = db.cursor()
	sql="select * from properties;"
	print(sql)
	try:
		cursor.execute(sql)
		data = cursor.fetchall()
		for row in data:
			text=''+row["title"]+row["keywords"]+row["description"]+row['content']
			seg_list = jieba.analyse.extract_tags(text  ,topK=30,withWeight=True)
			for line in seg_list:
				save(row["url"],line[0], line[1])
			#time.sleep(3)
	except:
		info = sys.exc_info()
		print( info[0], ":", info[1])
		db.rollback()
	cursor.close()
	db.close()

if __name__=="__main__":
	extract_word()



