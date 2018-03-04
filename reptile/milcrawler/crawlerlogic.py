import re
import chardet
import requests
from reptile import article
from bs4 import BeautifulSoup
from milcrawler import milarticle

def startcrawl():
    pagelisturl = 'http://roll.mil.news.sina.com.cn/col/gjjq/index.shtml'
    response = requests.get(pagelisturl)
    code = chardet.detect(response.content)['encoding']
    response.encoding = code
    text = article.FindArticle.removeunnecessarycode(response.text)
    soup = BeautifulSoup(text, 'html.parser')
    if re.search('sina\.com\.cn', pagelisturl):
        articlelistpart = soup.select_one('.fixList')
        articlelist = articlelistpart.select('li')
        titleinfolist = []
        for titlepart in articlelist:
            titleinfolist.append((titlepart.select_one('a').text, titlepart.select_one('a').attrs['href']))
    else:
        return
    for info in titleinfolist:
        title = info[0]
        wlist = milarticle.parsetitle(title)
        print(title)
        print(wlist)

if __name__ == '__main__':
    startcrawl()