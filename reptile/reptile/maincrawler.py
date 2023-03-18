import os.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import time
import random
from reptile import article
from threading import Thread
from reptile import urlmanage
from reptile import mysql_connector


def start(url):
    parser = urlmanage.UrlAcquire(maxdepth=3)
    while True:
        urlnextstatus = parser.start(url)
        if urlnextstatus is None:
            print('Search end')
            break
        else:
            if not re.search('(article|doc)', urlnextstatus.targeturl):
                print('page {0} seems not an article page, pass'.format(urlnextstatus.targeturl))
                continue
            writeresult = mysql_connector.Connpsql().writedata('crawledurls', {'url': urlnextstatus.targeturl})
            if writeresult:
                time.sleep(random.uniform(3,5))
                continue
            articleinstance = article.FindArticle(urlnextstatus.sourcecode)
            time.sleep(random.uniform(1,2))
            if articleinstance.articleclass:
                print('This seems target article, Prepare Writing')
                articletitle = articleinstance.articletitle
                print('title:', articletitle)
                excerpt = articleinstance.articlexcerpt
                print('excerpt:', excerpt)
                articlecontent = articleinstance.articlecontent
                articleurl = urlnextstatus.targeturl
                releasetime = articleinstance.articlepostime
                articleclass = articleinstance.articleclass
                pageurlcode = articleinstance.pageurlcode
                print('-----posting article-----')
                while True:
                    writeresult = mysql_connector.Connpsql().writedata('articlesite_article',
                                                    {'article_title': articletitle, 'article_url': articleurl, 'release_time_detected': releasetime,
                                                     'article_excerpt': excerpt, 'article_content': articlecontent, 'article_class': articleclass, 'page_urlcode': pageurlcode})
                    if writeresult:
                        if re.search('page_urlcode', writeresult):
                            pageurlcode = str(int(pageurlcode) + 1)
                            continue
                    break


if __name__ == '__main__':
    urls = ['http://tech.163.com/', 'http://tech.sina.com.cn']
    for urlo in urls:
        t = Thread(target=start, args=(urlo,))
        t.start()
        time.sleep(random.uniform(2, 3))

