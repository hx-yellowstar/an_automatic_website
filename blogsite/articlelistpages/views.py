import re
import math
import json
import time
import random
from threading import Thread
from blogsite import postgresql
from django.shortcuts import render
from django.shortcuts import HttpResponse
from blogsite.recordvisitorinfo import recordinfo
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

nav = ['<li class=""><a href="/">首页</a></li>',
       '<li class=""><a href="/classify/general">全部</a></li>',
       '<li class=""><a href="/classify/smartphone">手机</a></li>',
       '<li class=""><a href="/classify/bat">BAT</a></li>',
       '<li class=""><a href="/classify/bikesharing">共享单车</a></li>',
       '<li class=""><a href="/classify/ai">人工智能</a></li>',
       '<li class=""><a href="/classify/hardware">硬件</a></li>']
# This is very NOT MVC, emm, I'm aware of that

def index(request):
    t = Thread(target=recordinfo, args=(request,))
    t.start()
    ctx = {}
    contents = postgresql.Connpsql().readfromtable('article')
    recommend = []
    while len(recommend) < 5:
        content = random.choice(contents)
        recommend.append([content[0]])
    articleindatabase = contents[:3]
    articles = []
    for content in articleindatabase:
        articlepostime = caculocaltime(content[2])
        articles.append([content[0], content[1], articlepostime, content[3], content[4], content[6]])
        # [0]:标题    # [1]:网址    # [2]:检测发布时间    # [3]:摘要    # [4]:文章内容
    ctx['articles'] = articles
    ctx['recommend'] = recommend
    navout = changenav(nav, '首页')
    ctx['nav'] = ''.join(navout)
    return render(request, 'index.html', ctx)

@csrf_exempt
def articleclasses(request, classesname):
    t = Thread(target=recordinfo, args=(request,))
    t.start()
    ctx = {}
    if request.method=='GET':
        # 因为选择了通过后台来改变已选中元素的状态的方法，所以需要在后台处理一些html代码(嗯，这很不MVC)
        navout = changenav(nav, classesname)
        if classesname == 'general':
            articles = postgresql.Connpsql().readfromtable('article')
        else:
            articles = postgresql.Connpsql().readfromtable('article', columnofselect='article_class', contentofselect=classesname)
        articlelist = []
        for articleinfo in articles[:10]:
            articlepostime = caculocaltime(articleinfo[2])
            articlelist.append([articleinfo[0], articleinfo[1], articlepostime, articleinfo[3], articleinfo[4], articleinfo[6]])
        ctx['articles'] = articlelist
        if len(articles) > 10:
            ctx['class_name'] = classesname
            maxpage = int(math.ceil(len(articles) / 10))
            pagenumlist = [x for x in range(1, maxpage + 1)]
            ctx['pagelist'] = pagenumlist
            ctx['maxpagenum'] = maxpage
            ctx['currentpagenum'] = 1
        else:
            ctx['class_name'] = classesname
        ctx['nav'] = ''.join(navout)
        return render(request, 'classes.html', ctx)
    elif request.method=='POST':
        postargs = dict(request.POST)
        nextpage = int((postargs.get('targetindex', [None]))[0])
        maxpage = int((postargs.get('maxpagenum', [None]))[0])
        if nextpage < 1:
            nextpage = 1
        if nextpage > maxpage:
            nextpage = maxpage
        if maxpage:
            ctx['pagelist'] = [x for x in range(1, maxpage + 1)]
        articlecontents = postgresql.Connpsql().searchtable('article', limit=10, offset=10*(nextpage-1))[0]
        return_json = {}
        articledictlist = []
        for content in articlecontents:
            articlepostime = caculocaltime(content[2])
            articledictlist.append({'article_title':content[0], 'article_url':content[1], 'release_time': articlepostime, 'article_excerpt':content[3], 'article_content':content[4], 'page_urlcode': content[6]})
            # [0]:标题    # [1]:网址    # [2]:检测发布时间    # [3]:摘要    # [4]:文章内容   #[6]:URLcode
        return_json['articles'] = articledictlist
        return_json['maxpagenum'] = maxpage
        return_json['currentpagenum'] = nextpage
        return HttpResponse(json.dumps(return_json), content_type='application/json')
    else:
        return render(request, 'classes.html')

def caculocaltime(intunixtime):
    structime = time.localtime(intunixtime)
    articlepostime = '-'.join((str(structime.tm_year), str(structime.tm_mon), str(structime.tm_mday)))
    return articlepostime

def aboutpage(request):
    t = Thread(target=recordinfo, args=(request,))
    t.start()
    return render(request, 'about.html')

def changenav(navin, classesname):
    for i in range(0, len(navin)):
        thiscontent = navin[i]
        if re.search(classesname, thiscontent):
            navin[i] = re.sub('class=\"\"', 'class="am-active"', thiscontent)
        else:
            navin[i] = re.sub('class="am-active"', 'class=\"\"', thiscontent)
    return navin

if __name__ == '__main__':
    index('')
