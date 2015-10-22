#-*- coding: utf-8 -*-
import sqlite3
from itertools import combinations

class DBTable:
    def __init__(self, db, tablename, attributes):
        self.db = db
        self.tablename = tablename
        self.attributes = attributes
        
        checkTable = "SELECT count(*) FROM sqlite_master WHERE type='table' and name=?;"
        if self.db.execute(checkTable, (self.tablename,)).fetchone( )[0] != 1:
            self.create()

    def create(self):
        createTable = "CREATE TABLE %s (%s);"
        attr = ', '.join([k + ' ' + v for k, v in self.attributes])
        self.db.execute(createTable % (self.tablename, attr))

    def insert(self, *values, **ivalues):
        if values is ():
            values = ivalues.items()
        insertValue = "INSERT INTO %s" % self.tablename
        key, val = zip(*values)
        insertValue += "(%s) VALUES" % ", ".join(key)
        insertValue += "(%s)" % ", ".join(('?' for i in range(len(values))))
        self.db.execute(insertValue, val)

    def select(self, query, where=None, values=()):
        selectValue = "SELECT %s" % query
        selectValue +=  " FROM %s" % self.tablename
        if where is not None:
            selectValue += " WHERE %s" % where
        return self.db.execute(selectValue, values).fetchall()

class Similarity:
    def __init__(self, dbname=':memory:'):
        self.con = sqlite3.connect(dbname)

        #Check Table
        table_list = {
            'user_list':(('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'), ('name', 'TEXT')),
            'keyword_list':(('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'), ('keyword', 'TEXT')),
            'cor_word_keyword':(('word', 'TEXT PRIMARY KEY'), ('keyword_id', 'INTEGER')),
            'cor_user_keyword':(('user_id', 'INTEGER'), ('keyword_id', 'INTEGER'))
            }

        for t in table_list:
            setattr(self, t, DBTable(self.con, t, table_list[t]))

    def insertCorWordKeyword(self, word, keyword):
        keyword_id = self.keyword_list.select('id', "keyword=?", (keyword,))
        if keyword_id == []:
            self.keyword_list.insert(('keyword', keyword))
            keyword_id = self.keyword_list.select('id', "keyword=?",(keyword,))
        self.cor_word_keyword.insert(('word', word), ('keyword_id', keyword_id[0][0]))


    def insertCorUserKeyword(self, name, word):
        user_id = self.user_list.select("id", "name=?", (name,))[0][0]
        keyword_id = self.cor_word_keyword.select("keyword_id", "word=?", (word,))[0][0]
        self.cor_user_keyword.insert(('user_id', user_id), ('keyword_id', keyword_id))

    def getSimilarity(self, namex, namey):
        x_id = self.user_list.select("id", "name=?", (namex,))[0][0]
        y_id = self.user_list.select("id", "name=?", (namey,))[0][0]
        x_set = set([i[0] for i in self.cor_user_keyword.select("keyword_id", "user_id=?", (x_id,))])
        y_set = set([i[0] for i in self.cor_user_keyword.select("keyword_id", "user_id=?", (y_id,))])
        return len(x_set & y_set)

    def getAllSimilarity(self):
        user_list = [i[0] for i in self.user_list.select("name")]
        return {(i, j): self.getSimilarity(i, j) for i, j in combinations(user_list, 2)}

def test():
    db = Similarity()
    print(db.con.execute("SELECT * FROM sqlite_master").fetchall())
    
    for i in range(ord('A'), ord('Z')+1):
        # db.user_list.insert(("name", chr(i))) #tuple or keyword
        db.user_list.insert(name=chr(i))
    print(db.user_list.select("*"))
    
    for i in range(ord('a'), ord('z')+1):
        db.insertCorWordKeyword(chr(i), chr(i))
    print(db.keyword_list.select("*"))
    print(db.cor_word_keyword.select("*"))
    
    for i,j in zip(range(ord('A'), ord('Z')+1), range(ord('a'), ord('z')+1)):
        db.insertCorUserKeyword(chr(i), chr(j))
    for i,j in [('A', 'b'), ('A', 'c'), ('A', 'z'), ('B', 'c'), ('B', 'z'), ('B', 'g')]:
        db.insertCorUserKeyword(i, j)
    print(db.cor_user_keyword.select("*"))

    print(db.getSimilarity('A', 'B'))
    print(db.getAllSimilarity())

if __name__ == '__main__':
    test()