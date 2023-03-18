import re
import time
from reptile import mysql_connector

allcontents = mysql_connector.Connpsql().readfromtable('article')
connection = mysql_connector.Connpsql(maintainconnect=True)
for content in allcontents:
    if not re.search('-', content[2]):
        continue
    timenow = content[2]
    timetuple = tuple([int(s) for s in timenow.split('-')])+(0,0,0,0,0,0)
    unixtime = time.mktime(timetuple)
    updateresult = connection.updateinfo('article', {'article_title': content[0]}, {'release_time_detected': str(unixtime)})
    if updateresult:
        connection = mysql_connector.Connpsql(maintainconnect=True)
