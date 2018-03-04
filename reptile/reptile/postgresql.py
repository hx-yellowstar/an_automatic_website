# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 12:20:23 2017

@author: star
"""
import re
import time
import psycopg2


class Connpsql(object):
    #除了writedata可以保持连接连续写入外，其他的连接全部都是即用即建，用完即断，因为用Python进行的postgresql连接一出错就会失效

    def __init__(self, database='djangosite', host='localhost', maintainconnect=False):
        self.conn = psycopg2.connect(database=database, user='username', password='password', host=host, port='5432')
        self.cursor = self.conn.cursor()
        self.database = database
        self.exceptionstatus = 0
        self.maintainconnect = maintainconnect

    def executecustomquery(self, order, mode):
        self.cursor.execute(order)
        result = None
        if mode == 'read':
            result = self.cursor.fetchall()
        else:
            self.conn.commit()
        self.conn.close()
        return result

    def readfromtable(self, table, column="*", columnofselect="'*'", contentofselect="*", mode='blurry'):
        # 如果要选择某列的所有行，务必：在column限制要选取的列，columnofselect和contentofselect必须全部为默认值
        # 得到的结果是每个元素都是tuple的list
        try:
            if mode == 'blurry':
                word = "SELECT {0} FROM {1} WHERE {2} LIKE '%{3}%';".format(column, table, columnofselect, contentofselect)
            else:
                word = "SELECT {0} FROM {1} WHERE {2} = '{3}';".format(column, table, columnofselect, contentofselect)
            word = self.__locateint(word)
            self.cursor.execute(word)
            contents = self.cursor.fetchall()
        except Exception as e:
            print('read from table error:', re.sub('\n', '', str(e)))
            contents = str(e)
        if not self.maintainconnect:
            self.closeconn()
        return contents

    def searchtable(self, table, column='*', ifmail=None, rownametuple=(), searchword='', limit=0, offset=0):
        word = 'SELECT {0} FROM {1}'.format(column, table)
        if ifmail or searchword:
            word = word + ' WHERE'
        if ifmail:
            if ifmail != 'all':
                if ifmail == 'confirmed' or ifmail == 'unknow':
                    word = word + " emails LIKE '%@%' AND"
                elif ifmail == 'no':
                    word = word + " (emails = '' OR emails = '[]' OR emails = '未检测到' OR emails = '未检测到-超时' OR emails is Null) AND"
            word = word[:-4]
        if searchword:
            rownamestring = "||' '||".join(rownametuple)
            word += " to_tsvector('english', {0}) @@ to_tsquery('english', '{1}');".format(rownamestring, searchword)
            self.cursor.execute(word)
            results = self.cursor.fetchall()
            resultnum = len(results)
            print('searched result num:', resultnum)
            if limit != 0:
                results = results[offset:offset + limit]
        else:
            if limit != 0:
                word += ' LIMIT {0}'.format(limit)
            if offset != 0:
                word += ' OFFSET {0}'.format(offset)
            word = word + ';'
            self.cursor.execute(word)
            results = self.cursor.fetchall()
            resultnum = 0
        if not self.maintainconnect:
            self.closeconn()
        return results, resultnum

    def writedata(self, table, info):
        # 可以传入单个数据（以字典形式），也可以传入批量数据（以每个元素都是字典的list形式）
        # 对于字典的要求：字典的key为需要写入的column，value为需要写入的值
        if isinstance(info, dict):
            result = self.__writingdata(table, info)
            self.closeconn()
            return result
        elif isinstance(info, list):
            expectlist = []
            num = 0
            while len(info) > 0:
                each = info.pop()
                num += 1
                result = self.__writingdata(table, each)
                if result:
                    # 这一句如果result is None，则表示插入成功时记录该项，如result，则表示插入失败时记录该项，应对不同需求
                    # notepattern = re.search('DETAIL.*', result, re.I)
                    # if notepattern:
                    #     print('Note:', re.sub('\s{2,}', ' ', notepattern.group()))
                    # else:
                    #     print('Error:', result)
                    expectlist.append(each)
                    self.closeconn()
                    self.__init__(self.database)
            self.closeconn()
            if len(expectlist) != 0:
                print('There is {0} error happened when insert this batch of data'.format(len(expectlist)))
                return expectlist

    def __writingdata(self, table, infodict):
        keytuple = ()
        valuetuple = ()
        for key in infodict.keys():
            value = str(infodict[key])
            keytuple += (key,)
            valuetuple += (value,)
        keystring = re.sub('[\'\"]', '', str(keytuple))
        if len(keytuple) == 1:
            keystring = keystring.replace(',', '')
        valuestring = str(valuetuple)
        if len(valuetuple) == 1:
            valuestring = valuestring.replace(',', '')
        valuestring = self.__locateint(valuestring)
        sql_write = "INSERT INTO {0} {1} VALUES {2};".format(table, keystring, valuestring)
        try:
            self.cursor.execute(sql_write)
            self.conn.commit()
        except Exception as e:
            print('Insert data problem:', re.sub('\n', ' ', str(e)))
            return (str(e)).replace('\n', ' ')

    def continuecrawl(self, column, table, condition='', mode=None):
        # condition如果要填，则必须以有两个元素的list形式传入，list的第一项为需筛选的列，第二项为需筛选的内容
        try:
            if condition != '':
                if isinstance(condition, list) and len(condition) == 2:
                    condition = 'WHERE {0} = {1}'.format(condition[0], condition[1])
                else:
                    print('condition format not right')
                    self.closeconn()
                    return
            if mode == 'all':
                column = '*'
            word = "SELECT {0} FROM {1} {2} ORDER BY id DESC LIMIT 1;".format(column, table, condition)
            word = re.sub('\s+', ' ', word)
            self.cursor.execute(word)
            info = self.cursor.fetchone()
            if not self.maintainconnect:
                self.closeconn()
            return info
        except Exception as e:
            print('seems no viewhistory:', e)
            url = None
            if not self.maintainconnect:
                self.closeconn()
            return url

    def ispageseen(self, table, column, content, mode='exact'):
        if content is not None and isinstance(content, str):
            content = content.replace('\'', '-')
        word = ''
        if mode == 'blurry':
            href = content.split('/')[2]
            pagestr = '%' + href + '%'
            word = "SELECT * FROM {0} WHERE {1} like '{2}'".format(table, column, pagestr)
        elif mode == 'exact':
            word = "SELECT * FROM {0} WHERE {1} = '{2}'".format(table, column, content)
        self.cursor.execute(word)
        num = self.cursor.fetchone()
        if not self.maintainconnect:
            self.closeconn()
        if num is None:
            answer = (False, content)
            return answer
        else:
            answer = (True, content)
            return answer

    def updateinfo(self, table, linetoupdate, infodict):
        # linetoupdate构成：一个字典，key(s)为需要更新的列的名称，value(s)指示需要更新哪一行，可以有多个key(为适应多主键的情况)
        # 兼容性：如果更新的限制条件只涉及到一列，也可以将linetoupdate写成一个两个元素的list，这样的话，则list中第一个元素相当于key，第二个相当于value
        # infodict构成：需要更新的列名称和需要更新的值组成的dict，如果有多个值需要更新，则在dict中加入多个值
        titles = infodict.keys()
        if isinstance(linetoupdate, list):
            conditionstring = linetoupdate[0] + "='" + linetoupdate[1] + "'"
        elif isinstance(linetoupdate, dict):
            conditionkeys = linetoupdate.keys()
            conditionstring = ' AND '.join([''.join((key,"='",(linetoupdate[key]),"'")) for key in conditionkeys])
        else:
            print('parameter format not right, return')
            return
        updateproblem = None
        updatestring = ','.join([''.join((key,"='",(infodict[key]).replace('\'', '-*-'),"'")) for key in titles if infodict[key]])
        word = "UPDATE {0} SET {1} WHERE {2};".format(table, updatestring, conditionstring)
        word = self.__locateint(word)
        try:
            self.cursor.execute(word)
            self.conn.commit()
            print('update table compelete')
        except Exception as e:
            print('update table error:', e)
            updateproblem = re.sub('\n', ' ', str(e))
        if not self.maintainconnect:
            self.closeconn()
        return updateproblem

    @staticmethod
    def __locateint(string):
        # postgresql支持直接写入int，但是由于要兼容更新文字的情况，更新int需要当成字符格式化字符串之后再去掉数字两旁的引号
        allnums = re.findall('(\'\d+\'|\"\d+\")', string)
        for num in allnums:
            string = string.replace(num, num[1:-1])
        return string

    def copyintableandfile(self, table, filepath, mode):
        if mode == 'IN':
            word = "COPY {0} FROM '{1}' WITH CSV HEADER;".format(table, filepath)
        else:
            word = "COPY {0} TO '{1}' WITH CSV HEADER;".format(table, filepath)
        self.cursor.execute(word)
        self.conn.commit()
        if not self.maintainconnect:
            self.closeconn()
        print('copy compelete')

    def deleteline(self, table, column, content):
        try:
            # 如批量传入数据，应自主对数据格式负责
            if isinstance(content, str):
                word = "DELETE FROM {0} WHERE {1} = '{2}';".format(table, column, content)
            else:
                word = "DELETE FROM {0} WHERE {1} = {2};".format(table, column, str(content))
            self.cursor.execute(word)
            self.conn.commit()
            print('delete compelete')
            result = None
        except Exception as e:
            print('delete error:', e)
            self.exceptionstatus = 1
            result = str(e)
        if not self.maintainconnect:
            self.closeconn()
        return result

    def createtable(self, table, columndict, primarykeytuple=(), needid=False):
        # columndict: 该字典的key是column的名称，对应的value是这个column的数据类型和长度，如：{'url':'varchar(200)'}
        try:
            columns = list(columndict.keys())
            string = ''
            for key in columns:
                length = columndict[key]
                string = ''.join([string, key, ' ', length, ','])
            string = string[:-1]
            if needid is True:
                idword = 'id serial, '
            else:
                idword = ''
            if primarykeytuple:
                primarykeystring = ', PRIMARY KEY (' + ','.join(primarykeytuple) + ')'
            else:
                primarykeystring = ''
            word = 'CREATE TABLE {0} ({1}{2}{3})'.format(table, idword, string, primarykeystring)
            sql_clear = str(word + ';')
            self.cursor.execute(sql_clear)
            self.conn.commit()
            self.closeconn()
        except Exception as e:
            print('built table error:', e)
            self.closeconn()
            return 'already built'

    def cleartable(self, table):
        word = 'DELETE FROM {0};'.format(table)
        try:
            self.cursor.execute(word)
            self.conn.commit()
        except Exception as e:
            self.exceptionstatus = 1
            print('delete content error:', e)
        word2 = 'ALTER SEQUENCE {0}_id_seq restart with 1;'.format(table)
        word2 = str(word2)
        try:
            self.cursor.execute(word2)
            self.conn.commit()
        except Exception as e:
            self.exceptionstatus = 1
            print('initialize sequence error:', e)
        self.closeconn()

    def droptable(self, table):
        try:
            word = 'DROP TABLE {0};'.format(table)
            self.cursor.execute(word)
            self.conn.commit()
        except Exception as e:
            self.exceptionstatus = 1
            print('drop table error:', e)
        if not self.maintainconnect:
            self.closeconn()

    def gettablenames(self, compileword):
        sql = "SELECT tablename FROM pg_tables WHERE tablename LIKE '%{0}%';".format(compileword)
        self.cursor.execute(sql)
        results = [p[0] for p in self.cursor.fetchall()]
        if not self.maintainconnect:
            self.closeconn()
        return results

    def closeconn(self):
        self.conn.close()

if __name__ == '__main__':
    pass
