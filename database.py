import random
import sqlite3
import datetime

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
                            token_id TEXT,
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
                                (MANAGER['username'], MANAGER['password'], MANAGER['type'], MANAGER['striked'],
                                 MANAGER['approved']))

    ### Users' methods

    def insert_user(self, user_dict):
        type = user_dict['type']
        if type not in ['admin', 'user']:
            raise Exception("Invalid type!")

        if self.get_account_by_username(user_dict['username']):
            raise Exception("This username is already exist!")

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
            assert len(founds) >= 1
            user = founds[0]
            user_dict = {"username": user[0], "password": user[1], "type": user[2], "striked": user[3],
                         "approved": user[4]}
            return user_dict
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

    ### Videos' methods

    def insert_videos(self, video_dict):
        if 'deleted' not in video_dict.keys():
            video_dict['deleted'] = 0
        if 'tag' not in video_dict.keys():
            video_dict['tag'] = ""

        with self.conn:
            columns = ', '.join(video_dict.keys())
            placeholders = ':' + ', :'.join(video_dict.keys())
            query = 'INSERT INTO videos (%s) VALUES (%s)' % (columns, placeholders)
            # print(query)
            self.cursor.execute(query, video_dict)

    def delete_video(self, video_id):
        with self.conn:
            self.cursor.execute("""UPDATE videos SET deleted=:deleted
                                   WHERE rowid=:video_id""",
                                {'video_id': video_id, 'deleted': 1})

    def get_video_by_id(self, video_id):
        self.cursor.execute("""SELECT rowid, * FROM videos
                               WHERE rowid=:video_id""")
        founds = self.cursor.fetchall()
        if founds:
            assert len(founds) == 1
            video = founds[0]
            video_dict = {"video_id": video[0], "address": video[1], "name": video[2], "username": video[3],
                          "tag": video[4], "deleted": video[5]}
            return video_dict
        else:
            return None

    def get_all_videos(self):
        self.cursor.execute("SELECT rowid, * FROM videos")
        founds = self.cursor.fetchall()
        videos = []
        for video in founds:
            video_dict = {"video_id": video[0], "address": video[1], "name": video[2], "username": video[3],
                          "tag": video[4], "deleted": video[5]}
            videos.append(video_dict)
        return videos

    def tag_the_video(self, video_id, tag):
        with self.conn:
            self.cursor.execute("""UPDATE videos SET tag=:tag
                                   WHERE rowid=:video_id""",
                                {'video_id': video_id, 'tag': tag})

    def add_comment_on_video(self, video_id, username, comment):
        ### A user can submit multiple commnets for a video.
        with self.conn:
            self.cursor.execute('INSERT INTO video_comment VALUES (?,?,?)', (video_id, username, comment))

    def add_change_liked_status_of_video(self, video_id, username, liked):
        self.cursor.execute("""SELECT * FROM video_like
                                       WHERE video_id=:video_id AND username=:username""",
                            {'video_id': video_id, 'username': username})
        founds = self.cursor.fetchall()
        if founds:
            assert len(founds) == 1
            with self.conn:
                self.cursor.execute("""UPDATE video_like SET liked=:liked
                                                   WHERE video_id=:video_id AND username=:username""",
                                    {'video_id': video_id, 'username': username, 'liked': liked})
        else:
            with self.conn:
                self.cursor.execute('INSERT INTO video_like VALUES (?,?,?)', (video_id, username, liked))

    def get_video_comments(self, video_id):
        self.cursor.execute("""SELECT username, comment FROM video_comment
                               WHERE video_id=:video_id""",
                            {'video_id': video_id})
        founds = self.cursor.fetchall()
        comments = []
        for comment in founds:
            comment_dict = {"username": comment[0], "comment": comment[1]}
            comments.append(comment_dict)
        return comments

    def get_video_likes(self, video_id):
        self.cursor.execute("""SELECT username, liked FROM video_like
                                       WHERE video_id=:video_id""",
                            {'video_id': video_id})
        founds = self.cursor.fetchall()
        likes, dislikes = 0, 0
        for like_ent in founds:
            if like_ent[1] == 1:
                likes += 1
            else:
                dislikes += 1
        return {'likes': likes, 'dislikes': dislikes}

    ### Token methods

    def get_a_new_token_for_user(self, user_dict):
        if 'time' not in user_dict.keys():
            user_dict['time'] = datetime.datetime.now()
        with self.conn:
            token_id=random.choice()
            columns = ', '.join(user_dict.keys())
            placeholders = ':' + ', :'.join(user_dict.keys())
            query = 'INSERT INTO tokens (%s) VALUES (%s)' % (columns, placeholders)
            # print(query)
            self.cursor.execute(query, user_dict)
        return token_id

    def delete_token(self, token_id):
        with self.conn:
            self.cursor.execute("""DELETE FROM tokens WHERE rowid=:token_id""",
                                {'token_id': token_id})

    def update_token_time(self, token_id):
        dt = datetime.datetime.now()
        with self.conn:
            self.cursor.execute("""UPDATE tokens SET time=:time
                                               WHERE token_id=:token_id""",
                                {'token_id': token_id, 'time': dt})

    def get_token_by_id(self, token_id):
        print(token_id)
        self.cursor.execute("""SELECT rowid, * FROM tokens
                                               WHERE token_id=:token_id""",
                            {'token_id': token_id})
        founds = self.cursor.fetchall()
        if founds:
            assert len(founds) == 1
            token = founds[0]
            token_dict = {'token_id': token[1], 'username': token[2], 'time': token[3]}
            return token_dict
        else:
            return None
