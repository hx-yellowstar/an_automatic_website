import re
from reptile import mysql_connector

results = mysql_connector.Connpsql().readfromtable('article_article')
connection = mysql_connector.Connpsql(maintainconnect=True)
for result in results:
    title = result[0]
    classnow = result[-2]
    if not re.search('general', classnow):
        classnew = classnow+'general,'
        connection.updateinfo('article_article', {'article_title': title}, {'article_class': classnew})