import time
from threading import Thread
from article.models import Article
from django.shortcuts import render
from visitorecord.recordvisitorinfo import recordinfo

# Create your views here.

def articlesite(request, urlcode):
    t = Thread(target=recordinfo, args=(request,))
    t.start()
    ctx = {}
    if request.method == 'GET':
        # articlecontents = postgresql.Connpsql().readfromtable('article', columnofselect='page_urlcode', contentofselect=urlcode)[0]
        articlecontents = Article.objects.get(page_urlcode=urlcode)
        ctx['article_title'] = articlecontents.article_title
        ctx['article_url'] = articlecontents.article_url
        structime = time.localtime(articlecontents.release_time_detected)
        articlepostime = '-'.join((str(structime.tm_year), str(structime.tm_mon), str(structime.tm_mday)))
        ctx['release_time'] = articlepostime
        ctx['article_content'] = articlecontents.article_content
    return render(request, 'articlesite.html', ctx)

# def articlesearch(request):
#     if request.method == 'GET':
#         searchword =