import sqlite3
from itertools import combinations

class InterfaceDB:
    def __init__(self, dbname=':memory:'):
        self.con = sqlite3.connect(dbname)

        #Check Table
        table_list = {
            'user_list':(('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'), ('name', 'TEXT')),
            'keyword_list':(('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'), ('keyword', 'TEXT')),
            'cor_word_keyword':(('word', 'TEXT PRIMARY KEY'), ('keyword_id', 'INTEGER')),
            'cor_user_keyword':(('user_id', 'INTEGER'), ('keyword_id', 'INTEGER'))
            }

        checkTable = "SELECT count(*) FROM sqlite_master WHERE type='table' and name=?;"
        createTable = "CREATE TABLE %s (%s);"

        cur = self.con.cursor()
        for t in table_list:
            cur.execute(checkTable, (t,))
            if cur.fetchone()[0] != 1:
                param = ', '.join([k + ' ' + v for k, v in table_list[t]])
                cur.execute(createTable % (t, param))

    def insertUser(self, name):
        self.con.execute('INSERT INTO user_list (name) VALUES (?)', (name,))

    def insertKeyword(self, keyword):
        self.con.execute('INSERT INTO keyword_list (keyword) VALUES (?)', (keyword,))

    def insertCorWordKeyword(self, word, keyword):
        cur = self.con.cursor()
        cur.execute('SELECT id FROM keyword_list WHERE keyword=?', (keyword,))
        keyword_id = cur.fetchone()
        if keyword_id is None:
            self.insertKeyword(keyword)
            cur.execute('SELECT id FROM keyword_list WHERE keyword=?', (keyword,))
            keyword_id = cur.fetchone()
        self.con.execute('INSERT INTO cor_word_keyword (word, keyword_id) VALUES (?, ?)', (word, keyword_id[0]))

    def insertCorUserKeyword(self, name, word):
        cur = self.con.cursor()
        cur.execute('SELECT id FROM user_list WHERE name=?', (name,))
        user_id = cur.fetchone()[0]
        cur.execute('SELECT keyword_id FROM cor_word_keyword WHERE word=?', (word,))
        keyword_id = cur.fetchone()[0]
        self.con.execute('INSERT INTO cor_user_keyword (user_id, keyword_id) VALUES (?, ?)', (user_id, keyword_id))

    def getSimilarity(self, namex, namey):
        selectUser = 'SELECT id FROM user_list WHERE name=?'
        selectCur = 'SELECT keyword_id FROM cor_user_keyword WHERE user_id=?'
    
        cur = self.con.cursor()
        x_id = cur.execute(selectUser, (namex,)).fetchone()[0]
        y_id = cur.execute(selectUser, (namey,)).fetchone()[0]
        x_set = set([i[0] for i in cur.execute(selectCur, (x_id,)).fetchall()])
        y_set = set([i[0] for i in cur.execute(selectCur, (y_id,)).fetchall()])
    
        return len(x_set & y_set)

    def getAllSimilarity(self):
        user_list = [i[0] for i in self.con.execute('SELECT name FROM user_list').fetchall()]
        return {(i, j): self.getSimilarity(i, j) for i, j in combinations(user_list, 2)}

def test():
    db = InterfaceDB()
    print(db.con.execute("SELECT * FROM sqlite_master").fetchall())
    
    for i in range(ord('A'), ord('Z')+1):
        db.insertUser(chr(i))
    print(db.con.execute("SELECT * FROM user_list").fetchall())
    
    for i in range(ord('a'), ord('z')+1):
        db.insertCorWordKeyword(chr(i), chr(i))
    print(db.con.execute("SELECT * FROM keyword_list").fetchall())
    print(db.con.execute("SELECT * FROM cor_word_keyword").fetchall())
    
    for i,j in zip(range(ord('A'), ord('Z')+1), range(ord('a'), ord('z')+1)):
        db.insertCorUserKeyword(chr(i), chr(j))
    for i,j in [('A', 'b'), ('A', 'c'), ('A', 'z'), ('B', 'c'), ('B', 'z'), ('B', 'g')]:
        db.insertCorUserKeyword(i, j)
    print(db.con.execute("SELECT * FROM cor_user_keyword").fetchall())
    
    print(db.getSimilarity('A', 'B'))
    print(db.getAllSimilarity())

if __name__ == '__main__':
    test()