import sqlite3
import appUsageApp2
reload(appUsageApp2)
import os

def updateDatabase(appName = 'testApp'):
    userName = os.environ['USERNAME']
    if userName in ['qurban.ali', 'talha.ahmed', 'hussain.parsaiyan']:
       return
    appUsageApp2.updateDatabase(appName, userName)
    conn = sqlite3.connect(r'\\nas\storage\.db\Qurban\AppsUsageData\my.db')
    #conn.execute('create table appUsage (id INTEGER PRIMARY KEY, appName varchar(30), used INTEGER)')
    #conn.commit()
    res = conn.execute('select appName from appUsage;')
    flag = False
    for record in res.fetchall():
        if appName == record[0]:
            flag = True
    if not flag:
        conn.execute('insert into appUsage values(NULL, \'{0}\', \'1\')'.format(appName))
        conn.commit()
        return
    res = conn.execute('select used from appUsage where appName =\'{0}\';'.format(appName))
    val = None
    val = res.fetchone()[0]
    if val is not None:
        val += 1
        conn.execute('UPDATE appUsage SET used = \'{0}\' WHERE appName = \'{1}\';'.format(val, appName))
        conn.commit()
    conn.close()
