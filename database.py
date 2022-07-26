import sqlite3

DATABASE_NAME = 'Youtube.db'
MANAGER = {'username': 'manager', 'password': 'supreme_manager#2022', 'type': 'manager',
                       'striked': 0, 'approved': 1}

class Database:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
        self.cursor = self.conn.cursor()

    def close_database(self):
        self.conn.close()

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

### Users' methods

    def insert_user(self, user_dict):
        type = user_dict['type']
        if type not in ['admin', 'user']:
            raise Exception("Invalid type!")

        if 'striked' not in user_dict.keys():
            user_dict['striked'] = 0

        if 'approved' not in user_dict.keys():
            if type == 'admin':
                user_dict['approved'] = 0
            else:
                user_dict['approved'] = 1
        with self.conn:
            columns = ', '.join(user_dict.keys())
            placeholders = ':' + ', :'.join(user_dict.keys())
            query = 'INSERT INTO users (%s) VALUES (%s)' % (columns, placeholders)
            # print(query)
            self.cursor.execute(query, user_dict)

    def approve_admin(self, username):
        with self.conn:
            self.cursor.execute("""UPDATE users SET approved=:approved
                                   WHERE username=:username AND type=:type""",
                                {'username': username, 'type': 'admin', 'approved': 1})

    def get_account_by_username(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username=:username", {'username': username})
        founds = self.cursor.fetchall()
        if founds:
            assert len(founds) == 1
            user = founds[0]
            user_dict = {"username": user[0], "password": user[1], "type": user[2], "striked": user[3], "approved": user[4]}
        else:
            return None

    def get_all_admins(self):
        self.cursor.execute("SELECT * FROM users WHERE type=:type", {'type': 'admin'})
        founds = self.cursor.fetchall()
        admins = []
        for user in founds:
            user_dict = {"username": user[0], "password": user[1], "type": user[2], "striked": user[3],
                         "approved": user[4]}
            admins.append(user_dict)
        return admins

    def get_all_users(self):
        self.cursor.execute("SELECT * FROM users WHERE type=:type", {'type': 'user'})
        founds = self.cursor.fetchall()
        users = []
        for user in founds:
            user_dict = {"username": user[0], "password": user[1], "type": user[2], "striked": user[3],
                         "approved": user[4]}
            users.append(user_dict)
        return users

    def delete_user(self, username):
        with self.conn:
            self.cursor.execute("""DELETE FROM users WHERE username=:username""",
                                {'username': username})

    def change_strike_status_of_user(self, username, strike):
        with self.conn:
            self.cursor.execute("""UPDATE users SET striked=:striked
                                   WHERE username=:username AND type=:type""",
                                {'username': username, 'type': 'client', 'striked': strike})

