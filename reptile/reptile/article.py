# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 16:59:00 2017

@author: Star
"""
import os
import re
import time
import chardet
import requests
import valuearticle
from reptile import getlinks
from bs4 import BeautifulSoup
from constants import HEADERS


class FindArticle(object):
    articlepostlocaltime = ''
    articletitle = ''
    articlepostime = ''
    articlexcerpt = ''
    articlecontent = ''
    articleclass = ''
    pageurlcode = ''

    def __init__(self, articlepage):
        # articlepage: requests的返回值
        print ('-----Processing article-----')
        code = chardet.detect(articlepage.content)
        coding = code['encoding']
        articlepage.encoding = coding
        articlepagecode = articlepage.text
        articlepagecode = self.removeunnecessarycode(articlepagecode)
        # 文章页的html源代码
        soup = BeautifulSoup(articlepagecode,'html.parser')    #the page parse by Beautifulsoup
        # ---need add an site(article) recording---
        try:
            title = soup.select_one('title').text.replace('\n', '')
        except AttributeError:
            return
        title_final = re.sub('[|?*><]','_',title)
        urlcode = ''
        for c in soup.select_one('title').text[:2]:
            urlcode += str(ord(c))
        urlcode += str(int(time.time()))
        # 为此篇文章生成一个唯一的值，作为其在网站上url的后半部分：标题前两个字的编码+此时的unix时间转化为int再转化为str后的值
        self.pageurlcode = urlcode
        title_final = re.sub('[\xa0\u3000\t]', '', title_final.split('_')[0])
        self.articletitle = str(title_final).replace('\'', "\"")
        allelements = (soup.select("div"))  # type of part:<class 'bs4.element.ResultSet'>
        self.findarticlecontent(allelements)

    # proceeding with data
    def findarticlecontent(self, elements, coderatelimit=0.7):    #1
        coderatequeue = []
        for element in elements:
            elementlength = len(''.join(re.findall('<.*?>', str(element))))
            alllength = len(re.sub('\s{5,}', '', str(element)))
            elementext = element.text
            coderate = elementlength / alllength
            if coderate > coderatelimit:
                # coderatelimit越大，要求越松，因为更大的代码占比也能通过
                continue
            if len(elementext) != 0:
                if len(elementext) < 200:
                    continue
                elementextlength = len(elementext)
                coderatequeue.append((element, coderate, elementextlength))
        try:
            if not coderatequeue:
                print('there is no article')
                return
            coderatequeue = [c for c in sorted(coderatequeue, key=lambda d: d[1])[:10]]
            timemark = 0
            # for each in coderatequeue:
            #     unixtime = self.detectime(each[0])
            #     if unixtime:
            #         if unixtime > timemark:
            #             timemark = unixtime
            # if timemark == 0:
            #     if coderatelimit <= 0.85:
            #         coderatelimit += 0.05
            #         self.findarticlecontent(elements, coderatelimit)
            #         return
            #     else:
            #         print('maybe there is no article')
            #         return
            # timemark = int(timemark)
            self.articlepostime = timemark
            self.articlepostlocaltime = time.localtime(timemark)
            # html代码在总长度中占的比例，越小越有可能是正文
            articlelement = coderatequeue[0][0]
        except IndexError:
            print('didn\'t found an article')
            return
        self.getexcerpt(articlelement)
        articlelement = self.processpicandjs(articlelement)
        articletext = articlelement.text
        # --------------------文章题材判定-------------------
        articleclassname = valuearticle.value(articletext)
        if not articleclassname:
            print('not target article')
            return
        self.articleclass = articleclassname
        # -------------
        picl = set(getlinks.getpiclinks(articletext))
        for piclink in picl:
            if re.search('<div>', piclink):
                continue
            articletext= articletext.replace(piclink, '<div align="center"><img '+piclink+'/></div>')
        if not re.search('no article found', articletext):
            articletext = re.sub('[\xa0\u3000\t]', '', articletext)
            articletext = re.sub('[\n\r]{2,}', '\n', articletext)
            articletext = (''.join(('<p>', re.sub('\n', '</p><p>', articletext), '</p>'))).replace('<p></p>', '')
            self.articlecontent = articletext.replace('\'', "\"")

    @staticmethod
    def detectime(soup):
        unixtime = valuearticle.detecttime(soup)
        # 经过把检测到的所有类似日期的数组都转换为unix时间戳并与当前的时间戳对比后，得到代表最晚合法时间的时间，再转换成普通格式输出
        if isinstance(unixtime, str):
            return
        return unixtime

    def processpicandjs(self, articlelement):
        # 把图片和JS这两个不相关的东西放在一起处理是为了节省计算资源，都是在转换到str，处理完之后再转换回BeautifulSoup格式的
        partpicturepath = r'/static/pic/{0}/{1}/{2}/{3}'.format(self.articlepostlocaltime.tm_year, self.articlepostlocaltime.tm_mon, self.articlepostlocaltime.tm_mday,
                                                                            self.pageurlcode)
        picturepath = '/home/pi/Documents/an_automatic_website/blogsite'+partpicturepath
        if not os.path.exists(picturepath):
            os.makedirs(picturepath)
        os.chdir(picturepath)
        picnum = 1
        stringarticlecode = str(articlelement)
        matchresult = re.search('</p>.*?<p>', stringarticlecode)
        while matchresult:
            result = matchresult.group()
            stringarticlecode = stringarticlecode.replace(result, '</p>\n<p>')
            matchresult = re.search('</p>.*?<p>', stringarticlecode)
        stringarticlecode = re.sub('</p>.*?<p>', '</p>\n<p>', stringarticlecode)
        # 防止换行不对的情况出现
        try:
            while True:
                matchresultgroup = re.search('<img.*?src=[\'\"](.*?)[\'\"].*?>', stringarticlecode)
                # 如果先去除html代码，得到文章text，则会把图片的html代码也一并去掉，所以要先把源代码转成string格式，去除图片代码的格式后再BeautifulSoup处理，这样提取text的时候就不会去掉了
                if matchresultgroup:
                    wholecode = matchresultgroup.group(0)
                    href = matchresultgroup.group(1)
                    filename = self.downloadpic(href, picnum)
                    if filename:
                        filename = filename.split('?')[0]
                        picnum += 1
                        stringarticlecode = stringarticlecode.replace(wholecode,
                                                                      "src='{0}'".format(partpicturepath + '/' + re.sub('[/]', '', filename)))
                    else:
                        stringarticlecode = stringarticlecode.replace(wholecode, '')
                else:
                    break
        except Exception as e:
            print('picture process had some problem', e)
        articlelement = BeautifulSoup(stringarticlecode, 'html.parser')
        # piclinks = [c.attrs['src'] for c in articlelement.select('img')]
        # articletext = self.findandgetpics(articletext, piclinks, picturepath)   #piclinks type:list , contains html format links
        return articlelement

    @staticmethod
    def downloadpic(piclink, picnum):    #3
        try:
            headers = {'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'}
            # requests下载图片
            try:
                picres = requests.get(piclink, headers=headers, stream=True)
            except:
                picres = requests.get(re.sub('/{3,}', '//', 'http://'+piclink), headers=headers, stream=True)
            if len(picres.content) < 25600:
                print('picture is too small, return')
                # 太小的图，有可能是公众号二维码，或者一些图标
                return
            if picres.status_code == 200:
                extension = re.search('\.(jpg|png|jpeg|bmp|tiff|gif)', piclink, re.I).group(1)
                filename = '{0}.{1}'.format(picnum, extension)
                with open(filename, 'wb') as f:
                    for chunk in picres.iter_content(1024):
                        f.write(chunk)
                return filename
            # urllib.request.urlretrieve(piclink,path+'/'+r'%s.%s' % (filenum, extension))
        except Exception as e:
            print ('one pic download failed: {0}, because of: {1}'.format(piclink, str(e)))

    def getexcerpt(self, element):
        l = element.select('p')
        excerpt = ''
        for paragraph in l:
            excerpt = excerpt + paragraph.text + ' '
            length = len(excerpt)
            if length > 70:
                excerpt = excerpt[:290]
                # 有时候一段超级长，要防止这种情况（60+500什么的）
                break
        if len(excerpt) > 260:
            excerpt += '...'
        self.articlexcerpt = re.sub('[\u3000\n]', ' ', excerpt.replace('\'', "\""))

    @staticmethod
    def removeunnecessarycode(articlepagecode):
        scriptexts = re.findall('<script.*?</script>', articlepagecode, re.DOTALL)
        # 使用中发现re.sub不能很好的替换所有的跨行script标签，所以先找到所有，再一个个替换掉
        for script in scriptexts:
            articlepagecode = articlepagecode.replace(script, '')
        articlepagecode = re.sub('<script.*?</script>', '', articlepagecode)
        styles = re.findall('<style.*?</style>', articlepagecode, re.DOTALL)
        for style in styles:
            articlepagecode = articlepagecode.replace(style, '')
        articlepagecode = re.sub('<style.*?</style>', '', articlepagecode)
        return articlepagecode


if __name__ == '__main__':
    # sitelist = [
    #             'http://tech.sina.com.cn/it/2018-01-30/doc-ifyqzcxi1944824.shtml','http://tech.163.com/17/1114/07/D36F3B6I00097U7R.html', 'http://tech.163.com/17/1211/11/D5CCMVM6000995G1.html', 'http://tech.163.com/17/1012/00/D0GN4VA500097U81.html', 'http://tech.163.com/17/1009/00/D08VUQCI00097U81.html'
    #             ]
    sitelist = ['http://tech.163.com/17/1114/07/D36F3B6I00097U7R.html', 'http://tech.163.com/17/1211/11/D5CCMVM6000995G1.html', 'http://tech.163.com/17/1012/00/D0GN4VA500097U81.html', 'http://tech.163.com/17/1009/00/D08VUQCI00097U81.html']
    for articleurl in sitelist:
        articleinstance = FindArticle(requests.get(articleurl, headers=HEADERS))
        if articleinstance.articleclass:
            print('title:', articleinstance.articletitle)
            print('excerpt:', articleinstance.articlexcerpt)
            print('length of excerpt:', len(articleinstance.articlexcerpt))
            print('articlecontent:', articleinstance.articlecontent)
            # print('-----posting article-----')
            # postgresql.Connpsql().writedata('article', {'article_title': articleinstance.articletitle, 'article_url': articleurl,
            #                                             'release_time_detected': articleinstance.articlepostime, 'article_excerpt': articleinstance.articlexcerpt,
            #                                             'article_content': articleinstance.articlecontent, 'article_class': articleinstance.articleclass})
