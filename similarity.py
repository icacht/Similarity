import sqlite3
class InterfaceDB:
    def __init__(self, dbname=':memory:'):
        self.con = aqlite3.connenct(dbname)

    def insertUser(self, username):
        pass

    def insertKeyword(self, keyword):
        pass

    def insertCorWordKeyword(self, word, keyword):
        pass
    
    def insertCorUserKeyword(self, user, keyword):
        pass