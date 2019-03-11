import scrapy
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from tutorial.items import SearchingItem
import jieba

def stopwordslist(filepath):
	stopwords = [line.strip() for line in open(filepath, 'r', encoding = 'utf-8').readlines()]
	return stopwords

#对句子去除停用词
def movestopwords(seg_list):
	stopwords = stopwordslist('stopwords.txt')
	outstr = ''
	for word in seg_list:
		if word not in stopwords:
			if word != '\t' and '\n':
				outstr += word
	return outstr

class SSpider(scrapy.Spider):
	name="Searching"
	allowd_domains = ['https://news.sina.com.cn/world/',
	#'http://news.sina.com.cn/china/',
	#'piyao.sina.com',
	#'https://mil.news.sina.com.cn/',
	#'http://cul.news.sina.com.cn/',
	]
	start_urls = [
	'https://news.sina.com.cn/world',
	]

	def fenci(self, sentence):
		seg_list = jieba.cut_for_search(''.join(sentence))
		return movestopwords(seg_list)

	def parse(self, response):

		sel = Selector(response)
		site = sel.xpath('//head')
		
		t = site.xpath('//title/text()').extract()
		title = ''.join(str(x) for x in t).split()
		title = self.fenci(title)

		k = site.xpath('//meta[@name="keywords"]/@content').extract()
		keywords = ''.join(str(x) for x in k).split()
		keywords = self.fenci(keywords)

		d = site.xpath('//meta[@name="description"]/@content').extract()
		description = ''.join(str(x) for x in d).split()
		description=self.fenci(description)
		
		c = sel.xpath('//div[@class="article"]/p/text()').extract()
		content=''.join(str(x) for x in c).split()
		content=self.fenci(content)

		if title =='':
			return
		if description =='':
			return
		item = SearchingItem()
		item['url'] = str(response.url)
		item['title'] = title
		item['keywords'] = keywords
		item['description'] = description
		item['content'] = content
		yield item

		urls = sel.xpath('//li/a[@target="_blank"]/@href').extract()
		for url in urls:
			print (url)
			yield Request(url,callback = self.parse)

