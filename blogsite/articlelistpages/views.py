import re
import math
import json
import time
import random
from threading import Thread
from article.models import Article
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from visitorecord.recordvisitorinfo import recordinfo
# Create your views here.

nav = ['<li class=""><a href="/">首页</a></li>',
       '<li class=""><a href="/classify/general">全部</a></li>',
       '<li class=""><a href="/classify/smartphone">手机</a></li>',
       '<li class=""><a href="/classify/bat">BAT</a></li>',
       '<li class=""><a href="/classify/bikesharing">共享单车</a></li>',
       '<li class=""><a href="/classify/ai">人工智能</a></li>',
       '<li class=""><a href="/classify/hardware">硬件</a></li>']

def index(request):
    t = Thread(target=recordinfo, args=(request,))
    t.start()
    ctx = {}
    contents = Article.objects.all()
    # contents = postgresql.Connpsql().readfromtable('article_article')
    recommend = []
    while len(recommend) < 5:
        content = random.choice(contents)
        recommend.append([content.article_title, content.page_urlcode])
    articleindatabase = contents[:3]
    articles = []
    for content in articleindatabase:
        articlepostime = caculocaltime(content.release_time_detected)
        articles.append([content.article_title, content.article_url, articlepostime, content.article_excerpt, content.article_content, content.page_urlcode])
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
        # 因为选择了通过后台来改变已选中元素的状态的方法，所以需要在后台处理一些html代码
        navout = changenav(nav, classesname)
        articles = Article.objects.filter(article_class__contains=classesname)
        articlelist = []
        for articleinfo in articles[:10]:
            articlepostime = caculocaltime(articleinfo.release_time_detected)
            articlelist.append([articleinfo.article_title, articleinfo.article_url, articlepostime, articleinfo.article_excerpt, articleinfo.article_content, articleinfo.page_urlcode])
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
        postargs = request.POST
        nextpage = int(postargs.get('targetindex', None))
        maxpage = int(postargs.get('maxpagenum', None))
        if nextpage < 1:
            nextpage = 1
        if nextpage > maxpage:
            nextpage = maxpage
        if maxpage:
            ctx['pagelist'] = [x for x in range(1, maxpage + 1)]
        start = 10*(nextpage-1)
        stop = 10*(nextpage-1)+10
        articlecontents = Article.objects.filter(article_class__contains=classesname).order_by('-release_time_detected')[start: stop]
        return_json = {}
        articledictlist = []
        for content in articlecontents:
            articlepostime = caculocaltime(content.release_time_detected)
            articledictlist.append({'article_title':content.article_title, 'article_url':content.article_url, 'release_time': articlepostime, 'article_excerpt':content.article_excerpt, 'article_content':content.article_content, 'page_urlcode': content.page_urlcode})
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
