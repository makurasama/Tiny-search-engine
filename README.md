# Tiny-search-engine

小型搜索引擎

1   需求分析

搜索引擎是一种根据一定的策略，运用特定的计算机程序从互联网上搜集信息。在对信息进行处理后对用户提供检索服务，将相关信息展示给用户。网络上有大量信息，当用户只想搜索特定信息时，就变得相对比较困难，用户更关心如何能高效的搜索到有用的信息。本搜索引擎之特定可搜索新浪网页上的新闻，并以爬取网页当天时间的新闻为主体。大大减少了用户搜索的时间。

2   开发与执行环境

操作系统：macOS High Sierra

爬虫开发语言及所需要的库：python3 scrapy 1.5.1 

数据库：MySQL

后端开发环境：Apache+PHP+MySQL

前端开发语言及所需要的库：JavaScript+CSS+HTML5 jQuery

 

3   总体设计

基于python3的Scrapy爬虫框架，结巴分词，php，mysql，JavaScript，html5，css构造实现的小型搜索引擎。代码分为了预处理部分（爬虫部分、分词部分），倒排索引部分，前端和后端。爬取后的网页数据和建立的倒排索引都存储在MySQL的news数据库中。

步骤：

１．爬虫爬取网页数据，保存在数据库中，

２．python读取文件内容，存到数据库表中，使用结巴分词对网页内容进行分词，并获得TF-IDF值，构建倒排索引保存到数据库中。

３．前端界面接受用户输入，使用POST请求将数据发送到后端。

４．后端接受到数据进行分词，然后在倒排索引数据库查询，结果取并集，然后根据倒排索引数据库结果在结果数据库中查询，返回网页的具体信息。

５．前端收到返回后，将结果呈现出来。

 

4   概要设计

4.1  爬虫

爬虫实用的是python3的爬虫库scrapy，虽然自己也写了一个小型的爬虫但不论是在速度上还是存储到数据库等操作上，显然使用scrapy更加快捷。

主要获取的网站信息有URL，title，keywords，description，content部分，如下：

   t = site.xpath('//title/text()').extract()

   k = site.xpath('//meta[@name="keywords"]/@content').extract()

   d = site.xpath('//meta[@name="description"]/@content').extract()

   c = sel.xpath('//div[@class="article"]/p/text()').extract()

同时在爬取网页时，进行了初步的分词，利用了jieba中文分词库，使用如下：

    def fenci(self, sentence):
                  seg_list = jieba.cut_for_search(''.join(sentence))
                  return movestopwords(seg_list)

为了保存数据，需要定义items，在items.py中添加如下：

    url = scrapy.Field()
    title = scrapy.Field()
    keywords = scrapy.Field()
    description = scrapy.Field()
    content = scrapy.Field()

为了将爬取数据存入数据库中在settings文件中设置数据库信息

    MYSQL_HOST = 'localhost'
    MYSQL_DBNAME = 'news'         #数据库名字，请修改
    MYSQL_USER = 'root'             #数据库账号，请修改
    MYSQL_PASSWD = 'mimamima'         #数据库密码，请修改
    MYSQL_PORT = 3306               #数据库端口

 

4.2  分词

分词用的是python3环境下的jieba分词，安装简单。并且衍生出了不同版本的jieba分词。在后端中用了PHP环境下的分词组件。Jieba分词直接提供了基于TF-IDF的关键字提取功能。可直接获得关键字，及其TF-IDF值

    seg_list = jieba.analyse.extract_tags(text  ,topK=30,withWeight=True)

4.3  数据库

使用MySQL数据库，数据库名news，密码：mimamima

有两个表：properties、invert_index

爬虫爬取的，并进行初步与处理（去停止词，分词）的数据存储在properties表中。字段：url、title、keywords、description、content.

在anolyze.py文件中，从表properties中读取读取每一条数据，并保存到invert_index表中。

查询时，将查询语句分词。将每个关键字到invert_index表中查询。结果取并集，并到properties表中查询其他信息。利用TF-IDF值之和进行页面排序。

4.4  前端

前端仿照了google的界面进行了设计，输入框改变触发<input type='text>的input事件，利用方法get方法将数据传至result.html。result.html通过函数

    function oneValues(){
                           var result;
                           var url=window.location.search; //获取url中"?"符后的字串  
                           if(url.indexOf("?")!=-1){
                                    result = decodeURI(url.substr(url.indexOf("=")+1));
                           }
                           return result;
                  }

来得到url中的信息，然后通过jQuery库的方法POST至后端，并捕获后台test.php所查询到的信息。处理数据后动态生成结果页面。

    function postq(question)
                  {
                           $.post("test.php",
                      {
                        question:question
                      },
                      function(data,status){
                        //alert("数据：" + data + "\n状态：" + status);
                        console.log(data);
                        var item=data;
                   //console.log(item);
                   for(var i=0;i<item.length;i++){
                           var url=item[i].url;
                           var title=item[i].title;
                           var description=item[i].description;
                           var keywords=item[i].keywords;
                           console.log(url);
                     var a = ['<div class="block"> <a href="'+url+'"> <h3 class="title" >'+title+'</h3> <div style="display:inline-block"> <cite class="iUh30"> '+url+'</cite></div></a> <div class="content" >'+description+'</div> </div>'].join(' ');
                     $('#req').append(a);
     
                   }
                   var s = ['<script>$(".content").textSearch("'+question+'"); $(".title").textSearch("'+question+'");<\/script>'].join(' ');
                     $('#req').append(s);
                      });
                  }

4.5  后端

在后端也需要分词，将传过来的查询词进行分词，使用PHP版的jieba分词。这个过程十分耗时，因为引用文件时初始化十分耗时。导致出现结果界面需要等待三秒左右。

    Jieba::init();

find函数在invert_index里找关键词

分词后得到的关键词按照查询后的TF-IDF值进行排序，

    arsort($result_array);

search函数以url在properties寻找

将url到properties表中查询，查询结果以json形式返回前端。

echo json_encode($return_array , JSON_UNESCAPED_UNICODE), "\n";

 

5   数据来源

爬取了新浪网11月29日的1000条新闻

6   核心算法 

6.1  TF—IDF概述

TF-IDF是一种统计方法，用以评估一字词对于一个文件集或一个语料库中的其中一份文件的重要程度。字词的重要性随着它在文件中出现的次数成正比增加，但同时会随着它在语料库中出现的频率成反比下降。即一个词语在一篇文章中出现次数越多**, 同时在所有文档中出现次数越少, 越能够代表该文章.**

6.2  词频

词频 (term frequency, TF) 指的是某一个给定的词语在该文件中出现的次数。这个数字通常会被归一化(一般是词频除以文章总词数), 以防止它偏向长的文件。（同一个词语在长文件里可能会比短文件有更高的词频，而不管该词语重要与否。） 



6.3  逆向文件频率

逆向文件频率 (inverse document frequency, IDF) IDF的主要思想是：如果包含词条t的文档越少, IDF越大，则说明词条具有很好的类别区分能力。某一特定词语的IDF，可以由总文件数目除以包含该词语之文件的数目，再将得到的商取对数得到。 



6.4     TF—IDF 公式




 

7    

7文件结构



8    使用说明

 8.1  数据库环境配置

（1）首先下载安装MySQL，并设置配置文件，支持UTF-8编码方式

（2）代码文件setting中的MYSQL_PASSWD、MYSQL_USER、MYSQL_HOST改成自己设置的。或者执行命令

    set PASSWORD =PASSWORD(‘mimamima’);

将密码设为mimamima

（3）在终端执行命令

    mysql -u root -p

（4）创建数据库news 

    create database news; 
    use news;

（5）创建properties和invert_index 表单

    create table properties (url varchar(255) not null, title varchar(255), keywords varchar(1000), description varchar(1000), content varchar(10000));
     
    create table invert_index (url varchar(255) not null, words varchar(255) not null, tf_idf varchar(20));

 

8.1  python3环境配置及爬虫代码运行

（1）用pip3安装scrapy包 

    pip3 install scrapy

（2）网上下载安装python3的jieba分词库

（3）命令行进入searching/tutorial/tutorial目录下执行

    scrapy crawl Searching

 

（1）代码中没有设置爬取页数。所以当爬取到一定数量的网页后，control+c退出程序

 

8.3  建立倒排索引数据库

（1）  命令行进入searching/tutorial目录下执行anolyze.py文件

如果数据库的用户名与密码与代码中的不一致，请修改代码

执行：

    python3 anolyze.py

8.4  前端环境配置和执行

（1）启动apache sudo apachectl start  请配置好PHP运行环境

将front文件夹复制到/Library/WebServer/Documents 文件夹下

打开chrome浏览器地址框输入http://localhost/front/index.html

搜索框中输入搜索内容

（5）等待几秒 更新出搜索结果页面

（6）搜索结果页面中还有搜索框可以继续进行搜索

9   执行结果




