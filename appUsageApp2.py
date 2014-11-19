import sqlite3
from sqlite3 import OperationalError

def updateDatabase(appName = 'testApp', userName = 'noUser'):
    # get the current user on the windows
    # create connection to the database
    conn = sqlite3.connect(r'\\nas\storage\.db\Qurban\AppsUsageData\my2.db')
    # create table for the application if it does not exist
    try:
        conn.execute('create table {0} (userName varchar(50), cnt INTEGER)'.format(appName))
    except OperationalError:
        pass
    # insert the user to the table, if it does not exist
    flag = False
    res = conn.execute('SELECT userName FROM {0}'.format(appName))
    for record in res.fetchall():
        if userName == record[0]:
            flag = True
            break
    if not flag:
        conn.execute('insert into {0} values(\'{1}\', \'1\')'.format(appName, userName))
        conn.commit()
        return
    # update the record, if it already exists
    res = conn.execute('SELECT cnt FROM {0} WHERE userName =\'{1}\';'.format(appName, userName))
    val = None
    val = res.fetchone()[0]
    if val is not None:
        val += 1
        conn.execute('UPDATE {0} SET cnt = \'{1}\' WHERE userName = \'{2}\';'.format(appName, val, userName))
        conn.commit()
    conn.close()
