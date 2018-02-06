import time
from threading import Thread
from blogsite import postgresql
from django.shortcuts import render
from blogsite.recordvisitorinfo import recordinfo

# Create your views here.

def articlesite(request, urlcode):
    t = Thread(target=recordinfo, args=(request,))
    t.start()
    ctx = {}
    if request.method == 'GET':
        articlecontents = postgresql.Connpsql().readfromtable('article', columnofselect='page_urlcode', contentofselect=urlcode)[0]
        ctx['article_title'] = articlecontents[0]
        ctx['article_url'] = articlecontents[1]
        structime = time.localtime(articlecontents[2])
        articlepostime = '-'.join((str(structime.tm_year), str(structime.tm_mon), str(structime.tm_mday)))
        ctx['release_time'] = articlepostime
        ctx['article_content'] = articlecontents[4]
    return render(request, 'articlesite.html', ctx)
