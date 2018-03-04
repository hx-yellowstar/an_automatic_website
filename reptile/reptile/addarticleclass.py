import re
from reptile import postgresql

results = postgresql.Connpsql().readfromtable('article_article')
connection = postgresql.Connpsql(maintainconnect=True)
for result in results:
    title = result[0]
    classnow = result[-2]
    if not re.search('general', classnow):
        classnew = classnow+'general,'
        connection.updateinfo('article_article', {'article_title': title}, {'article_class': classnew})