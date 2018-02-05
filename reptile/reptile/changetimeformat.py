import re
import time
from reptile import postgresql

allcontents = postgresql.Connpsql().readfromtable('article')
connection = postgresql.Connpsql(maintainconnect=True)
for content in allcontents:
    if not re.search('-', content[2]):
        continue
    timenow = content[2]
    timetuple = tuple([int(s) for s in timenow.split('-')])+(0,0,0,0,0,0)
    unixtime = time.mktime(timetuple)
    updateresult = connection.updateinfo('article', {'article_title': content[0]}, {'release_time_detected': str(unixtime)})
    if updateresult:
        connection = postgresql.Connpsql(maintainconnect=True)
