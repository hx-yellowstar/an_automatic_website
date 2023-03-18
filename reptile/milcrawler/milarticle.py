import re
import jieba
import chardet
import requests
from reptile import article
import jieba.posseg as posseg
from bs4 import BeautifulSoup

def start(url):
    response = requests.get(url)
    code = chardet.detect(response.content)['encoding']
    response.encoding = code
    text = article.FindArticle.removeunnecessarycode(response.text)
    soup = BeautifulSoup(text, 'html.parser')
    if re.search('sina\.com\.cn', url):
        title = soup.find_all('h1', _class='.main_title')[0].text
        articlecontent = re.sub('\n{2,}', '\n', soup.select_one('#article').text)
    else:
        return
    parsetitle(title)
    # parsecontent(articlecontent)

def parsetitle(title):
    wordlist = [(w.word, w.flag) for w in posseg.cut(title) if not re.search('(x|p|uj)', w.flag)]
    print(wordlist)

def parsecontent(articlecontent):
    wordlist = [(w.word, w.flag) for w in posseg.cut(articlecontent) if not re.search('(x|p|uj)', w.flag)]
    wordict = {}
    for word in wordlist:
        try:
            wordict[word] += 1
        except KeyError:
            wordict[word] = 1
    sequence = sorted([[key, wordict[key]] for key in wordict.keys() if wordict[key] > 1], key=lambda x: x[1], reverse=True)
    print(sequence)
    sentences = []
    sentence = ''
    for word in articlecontent:
        if re.search('[,.;:，。；：]', word):
            sentences.append(sentence)
            sentence = ''
        else:
            sentence += word
    searchwords = '('+'|'.join([s[0][0] for s in sequence[:10]])+')'
    for sentence in sentences:
        if len(re.findall(searchwords, sentence)) > 1:
            print(sentence)

if __name__ == '__main__':
    start('http://mil.news.sina.com.cn/2018-02-27/doc-ifyrvaxf1459053.shtml')