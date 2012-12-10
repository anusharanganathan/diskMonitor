# -*- coding: utf-8 -*-
"""
    Database helper class for the disk monitor

    Copyright: (c) 2012 by Anusha Ranganathan.
"""

import sqlite3
import os

class dbHandler():

    def __init__(self, database='example.db', table='dataOnDisk'):
        self.table = table
        self.database = database
        self.conn = sqlite3.connect(self.database)
        self.db = self.conn.cursor()
        self.db.execute('''create table if not exists %s
                     (path text, name text, type text, size text, size_human text, ATime text, CTime text, MTime text)'''%self.table)
        self.conn.commit()

    def connect(self):
        self.conn = sqlite3.connect(self.database)

    def create(self, stats):
        self.db.execute('''INSERT INTO %s VALUES ("%s","%s","%s","%s","%s","%s","%s","%s")'''%
                       (self.table, stats['path'], stats['name'], stats['type'], stats['size'], stats['size_human'], stats['ATime'], stats['CTime'], stats['MTime']))
        self.conn.commit()

    def delete(self, path):
        self.db.execute('delete from %s where path="%s"'%(self.table, path)) 
        self.conn.commit()

    def modify(self, stats):
        self.delete(stats['path'])
        self.create(stats)

    def getRecords(self, start=0, rows=100):
        try:
            start = int(start)
        except:
            start = 0
        try:
            rows = int(rows)
        except:
            rows = 100
        
        self.db.execute('''SELECT count(path) FROM %s'''%self.table)
        count = self.db.fetchone()[0]
        if start >= count: 
            start = 0
        self.db.execute('''SELECT * FROM %s LIMIT %d,%d'''%(self.table, start, rows))
        header = self.db.description
        header = tuple([x[0] for x in header])
        answer = self.db.fetchall()
        answer.insert(0, header)
        return answer

    def getRecord(self, path):        
        self.db.execute('''SELECT * FROM %s WHERE path="%s"'''%(self.table, path))
        header = self.db.description
        header = tuple([x[0] for x in header])
        answer = self.db.fetchall()
        ans = {}
        if len(answer) == 1:    
            for i in range(len(header)):
                ans[header[i]] = answer[0][i]
        return ans

    def close(self):
        self.conn.close()

