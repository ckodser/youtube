import sqlite3

DATABASE_NAME = 'Youtube.db'
MANAGER = {'username': 'manager', 'password': 'supreme_manager#2022', 'type': 'manager',
                       'striked': 0, 'approved': 1}

class Database:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
        self.cursor = self.conn.cursor()


    def first_time_setup(self):
        with self.conn:
            self.cursor.execute("""CREATE TABLE videos (
                            address TEXT,
                            name TEXT,
                            username TEXT, 
                            tag TEXT,
                            deleted INT
                        )""")

            self.cursor.execute("""CREATE TABLE video_like (
                            video_id INT,
                            username TEXT,
                            liked INT
                        )""")

            self.cursor.execute("""CREATE TABLE video_comment (
                            video_id INT,
                            username TEXT,
                            comment TEXT
                        )""")

            self.cursor.execute("""CREATE TABLE tokens (
                            username TEXT,
                            time BLOB
                        )""")

            self.cursor.execute("""CREATE TABLE users (
                            username TEXT,
                            password TEXT,
                            type TEXT, 
                            striked INT,
                            approved INT
                        )""")

            self.cursor.execute("""CREATE TABLE tickets (
                            time BLOB,
                            username TEXT,
                            type TEXT,
                            status TEXT,
                            message TEXT
                        )""")

            self.cursor.execute("INSERT INTO users VALUES (:username, :password, :type, :striked, :approved)",
                                (MANAGER['username'], MANAGER['password'], MANAGER['type'], MANAGER['striked'], MANAGER['approved']))




