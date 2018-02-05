import re
import time
import random
import requests
import tldextract
import collections
from bs4 import BeautifulSoup
from selenium import webdriver

class UrlAcquire(object):
    def __init__(self, maxdepth = 2, browseruse=None):
        URLStatus = collections.namedtuple('URLStatus', ['maxdepth', 'urltosee', 'urlseen'])
        self.urlstatusnow = URLStatus(maxdepth=maxdepth, urlseen=[], urltosee=[])
        # urlseen里面的元素只有网址本身, urltoseestatus里还有当前网址的深度(url, depth)
        self.browserusing = None
        if browseruse is not None:
            if browseruse == 'Firefox':
                self.browserusing = webdriver.Firefox()
            elif browseruse == 'Chrome':
                self.browserusing = webdriver.Chrome()

    def start(self, url, maxparsepagenum=1500):
        if not self.urlstatusnow.urltosee and not self.urlstatusnow.urlseen:
            self.urlstatusnow.urltosee.append((url, 1))
        urlnextstatus = self.writeinurl(maxparsepagenum)
        # urlnextstatus.targeturl: 返回的网址
        # urlnextstatus.depth: 网址的深度
        # urlnextstatus.sourcecode: 当前网址，即urlnextstatus.targeturl的Customresponse格式代码
        # urlnextstatus.urltosee: 仍需遍历的网址数量
        return urlnextstatus

    def writeinurl(self, maxparsepagenum):
        urlnextstatus = self.requireurl()
        if not urlnextstatus:
            return
        # urlnextstatus = list(urlnextstatus)
        urlnext = urlnextstatus.targeturl
        responsecontent = urlnextstatus.sourcecode
        if responsecontent is None and self.browserusing is None:
            return self.writeinurl(maxparsepagenum)
        textcode = responsecontent.text
        if textcode is None or urlnext is None:
            return self.writeinurl(maxparsepagenum)
        depth = urlnextstatus[1]
        soup = BeautifulSoup(textcode, 'html.parser')
        hreflist = []
        contextlist = []
        theseurldepth = depth + 1
        if theseurldepth <= self.urlstatusnow.maxdepth:
            try:
                tags = soup.body.find_all(recursive=False)
                recursived = 0
            except Exception as e:
                print('read page content had some problem,', e)
                tags = soup.select('*')
                recursived = 1
            for tag in tags:
                try:
                    tagname = tag.name
                    if tagname == 'script' or tagname == 'style':
                        continue
                    if recursived == 0:
                        contextlist.append(str(tag))
                        taglist = tag.select('*')
                        for everytag in taglist:
                            href = everytag.attrs.get('href', None)
                            if href:
                                hreflist.append(href)
                    else:
                        href = tag.attrs.get('href', None)
                        if href:
                            hreflist.append(href)
                except Exception as e:
                    print('get href error:', e)
            urlthisextract = tldextract.extract(urlnext)
            m = 0
            for href in hreflist:
                hrefextract = tldextract.extract(href)
                # href 新页面搜索出来的链接
                if re.search('(#|javascript|google.com|pdf|mp4|mp3|zip|rar|tar\.gz|exe|swf|xls)', href):
                    continue
                if re.search('http', href) is None:
                    if hrefextract.domain == '' or hrefextract.subdomain == '' or hrefextract.suffix == '':
                        hrefparts = urlnext.split('/')
                        hrefstart = hrefparts[0] + '//' + hrefparts[2] + '/'
                        href = hrefstart + href
                    else:
                        href = re.sub('/{3,}', '//', ('http://' + href))
                    hrefextract = tldextract.extract(href)
                if urlthisextract.subdomain+urlthisextract.domain+urlthisextract.suffix == hrefextract.subdomain+hrefextract.domain+hrefextract.suffix:
                    if (href not in self.urlstatusnow.urlseen) and (href not in [p[0] for p in self.urlstatusnow.urltosee]):
                        self.urlstatusnow.urltosee.append((href, theseurldepth))
                    else:
                        m += 1
            if m != 0:
                print('There is {0} pages already writtened'.format(str(m)))
        else:
            time.sleep(random.uniform(0.5, 1.5))
        return urlnextstatus

    def requireurl(self):
        if not self.urlstatusnow.urltosee:
            return
        URLNextStatus = collections.namedtuple('URLNextStatus', ['targeturl', 'depth', 'sourcecode', 'urltoseenum'])
        nextarget = self.urlstatusnow.urltosee[0]
        targeturl = nextarget[0]
        depth = nextarget[1]
        self.urlstatusnow.urltosee.remove(nextarget)
        urltoseenum = len(self.urlstatusnow.urltosee)
        print('sites num to be seen:', urltoseenum)
        print('urlnext:', targeturl)
        if self.browserusing is None:
            try:
                responsesourcecode = requests.get(targeturl)
            except Exception as e:
                print('request error:', e)
                return URLNextStatus(targeturl=None, depth=depth, sourcecode=None, urltoseenum=urltoseenum)
        else:
            rn = 0
            while rn < 2:
                try:
                    self.browserusing.get(targeturl)
                    break
                except:
                    rn += 1
            meta = {}
            time.sleep(0.5)
            Request = collections.namedtuple('Request', ['url', 'meta'])
            meta['browserusing'] = self.browserusing
            request = Request(targeturl, meta)
            pagesource = self.browserusing.page_source
            content = pagesource.encode(errors='ignore')
            CustomResponse = collections.namedtuple('CustomResponse', ['url', 'content', 'text', 'encoding', 'request'])
            responsesourcecode = CustomResponse(url=targeturl, content=content, text=pagesource, encoding='utf-8', request=request)
        urlnextstatus = URLNextStatus(targeturl=targeturl, depth=depth, sourcecode=responsesourcecode, urltoseenum=urltoseenum)
        self.urlstatusnow.urlseen.append(urlnextstatus[0])
        return urlnextstatus

if __name__ == '__main__':
    urlo = 'http://www.sina.com.cn/'
    parser = UrlAcquire(maxdepth=2)
    while True:
        urlnextstatuso = parser.start(urlo)
        if urlnextstatuso is None:
            print('Search end')
            break
    # UrlAcquire('test', maxdepth=1).requireurl()