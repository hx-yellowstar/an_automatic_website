import sys
sys.path.append('/home/star/Documents/reptile')
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
                print('-----posting article-----')
                print('article_title', articletitle)
                print('article_url', articleurl)
                print('release_time_detected', releasetime)
                print('article_excerpt', excerpt)
                print('article_content', articlecontent)

if __name__ == '__main__':
    urls = ['http://tech.ifeng.com/']
    for urlo in urls:
        t = Thread(target=start, args=(urlo,))
        t.start()
        time.sleep(random.uniform(2,3))
