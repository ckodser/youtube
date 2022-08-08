import random
import sqlite3
import datetime
import string

DATABASE_NAME = 'Youtube.db'
PROXY_DATABASE_NAME = 'ProxyYoutube.db'
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
                            username TEXT
                        )""")

            self.cursor.execute("""CREATE TABLE token_time (
                            token_id TEXT,
                            time BLOB
                        )""")

            self.cursor.execute("""CREATE TABLE ip_time (
                            ip TEXT,
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
                            conv_id TEXT,
                            time BLOB,
                            username TEXT,
                            message TEXT
                        )""")

            self.cursor.execute("""CREATE TABLE conversations (
                            conv_id TEXT,
                            sender TEXT,
                            receiver TEXT,
                            status TEXT,
                            time BLOB
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

    def get_all_pending_admin(self):
        self.cursor.execute("SELECT * FROM users WHERE type=:type AND approved=:approved",
                            {'type': 'admin', "approved": 0})
        founds = self.cursor.fetchall()
        users = []
        for user in founds:
            user_dict = {"username": user[0], "password": user[1], "type": user[2], "striked": user[3],
                         "approved": user[4]}
            users.append(user_dict)
        return users

    def get_all_striked_users(self):
        self.cursor.execute("SELECT * FROM users WHERE type=:type AND striked=:striked",
                            {'type': 'user', "striked": 1})
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
                                   WHERE username=:username""",
                                {'username': username, 'type': 'user', 'striked': strike})

    ### Videos' methods
    def insert_video(self, video_dict):
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

        self.cursor.execute("""SELECT rowid, username FROM videos
                                                   WHERE rowid=:video_id""", {'video_id': video_id})
        id, username = self.cursor.fetchone()
        print(username)
        self.cursor.execute("""SELECT rowid, username, deleted FROM videos
                                       WHERE username=:username""", {'username': username})
        founds = self.cursor.fetchall()
        print(founds)
        strike_flag = False
        for video in founds:
            deleted = video[2]
            if deleted:
                if strike_flag:
                    self.change_strike_status_of_user(username, strike=1)
                    break
                else:
                    strike_flag = True
            else:
                strike_flag = False

    def get_video_by_id(self, video_id):
        self.cursor.execute("""SELECT rowid, * FROM videos
                               WHERE rowid=:video_id""", {'video_id': video_id})
        founds = self.cursor.fetchall()
        if founds:
            assert len(founds) == 1
            video = founds[0]
            video_dict = {"video_id": video[0], "address": video[1], "name": video[2], "username": video[3],
                          "tag": video[4], "deleted": video[5]}
            # if video_dict["deleted"] == 1:
            #     print("VIDEO DELETED")
            #     return None
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
            if video_dict["deleted"]==0:
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
        with self.conn:
            token_id = ''.join(
                random.choice(string.digits + string.ascii_uppercase + string.ascii_lowercase) for i in range(10))
            user_dict["token_id"] = token_id
            columns = ', '.join(user_dict.keys())
            placeholders = ':' + ', :'.join(user_dict.keys())
            query = 'INSERT INTO tokens (%s) VALUES (%s)' % (columns, placeholders)
            # print(query)
            self.cursor.execute(query, user_dict)

            token_dict = {'token_id': token_id, 'time': datetime.datetime.now()}
            columns = ', '.join(token_dict.keys())
            placeholders = ':' + ', :'.join(token_dict.keys())
            query = 'INSERT INTO token_time (%s) VALUES (%s)' % (columns, placeholders)
            self.cursor.execute(query, token_dict)
        return token_id

    def delete_token(self, token_id):
        with self.conn:
            self.cursor.execute("""DELETE FROM tokens WHERE token_id=:token_id""",
                                {'token_id': token_id})

    # def update_token_time(self, token_id):
    #     dt = datetime.datetime.now()
    #     with self.conn:
    #         self.cursor.execute("""UPDATE tokens SET time=:time
    #                                            WHERE token_id=:token_id""",
    #                             {'token_id': token_id, 'time': dt})

    def get_token_by_id(self, token_id):
        with self.conn:
            token_dict = {'token_id': token_id, 'time': datetime.datetime.now()}
            columns = ', '.join(token_dict.keys())
            placeholders = ':' + ', :'.join(token_dict.keys())
            query = 'INSERT INTO token_time (%s) VALUES (%s)' % (columns, placeholders)
            self.cursor.execute(query, token_dict)

        self.cursor.execute("""SELECT * FROM tokens
                                               WHERE token_id=:token_id""",
                            {'token_id': token_id})
        founds = self.cursor.fetchall()
        if founds:
            assert len(founds) == 1
            token = founds[0]
            token_dict = {'token_id': token[0], 'username': token[1]}
            return token_dict
        else:
            return None

    def check_token(self, token_id):
        self.refresh_token_times()
        self.cursor.execute("""SELECT * FROM token_time WHERE token_id=:token_id""",
                            {'token_id': token_id})
        founds = self.cursor.fetchall()
        if len(founds) == 0:
            self.delete_token(token_id)
            raise Exception("Your token is either invalid or depricated due to long inactivity!")
        elif len(founds) > 20000:
            raise Exception("Your connection is showing a suspicious pattern!")
        else:
            self.get_token_by_id(token_id)

    def check_ip(self, ip):
        self.refresh_ip_times()
        self.cursor.execute("""SELECT * FROM ip_time WHERE ip=:ip""",
                            {'ip': ip})
        founds = self.cursor.fetchall()
        if len(founds) > 100:
            raise Exception("DDoS protection activated!")
        else:
            with self.conn:
                ip_dict = {'ip': ip, 'time': datetime.datetime.now()}
                columns = ', '.join(ip_dict.keys())
                placeholders = ':' + ', :'.join(ip_dict.keys())
                query = 'INSERT INTO ip_time (%s) VALUES (%s)' % (columns, placeholders)
                self.cursor.execute(query, ip_dict)


    def refresh_token_times(self):
        a_minute_ago = datetime.datetime.now() - datetime.timedelta(minutes=100)
        with self.conn:
            self.cursor.execute("""DELETE FROM token_time WHERE time < ?""", [a_minute_ago])

    def refresh_ip_times(self):
        a_minute_ago = datetime.datetime.now() - datetime.timedelta(minutes=1)
        with self.conn:
            self.cursor.execute("""DELETE FROM ip_time WHERE time < ?""", [a_minute_ago])

    ### Ticket and Conversation methods

    def insert_conv(self, conv_dict):
        if 'conv_id' not in conv_dict.keys():
            conv_dict['conv_id'] = ''.join(
                random.choice(string.digits + string.ascii_uppercase + string.ascii_lowercase) for i in range(10))
        if 'receiver' not in conv_dict.keys():
            conv_dict['receiver'] = ''
        if 'status' not in conv_dict.keys():
            conv_dict['status'] = 'waiting'
        if 'time' not in conv_dict.keys():
            conv_dict['time'] = datetime.datetime.now()
        assert 'sender' in conv_dict.keys()

        with self.conn:
            columns = ', '.join(conv_dict.keys())
            placeholders = ':' + ', :'.join(conv_dict.keys())
            query = 'INSERT INTO conversations (%s) VALUES (%s)' % (columns, placeholders)
            self.cursor.execute(query, conv_dict)

        return conv_dict['conv_id']

    def update_conv_status(self, conv_id, status):
        if status in ["new", "waiting", "solved", "closed"]:
            with self.conn:
                self.cursor.execute("""UPDATE conversations SET status=:status WHERE conv_id=:conv_id""",
                                    {'conv_id': conv_id, 'status': status})
        else:
            raise Exception("Invalid ticket status!")

    def update_conv_receiver(self, conv_id, receiver):
        with self.conn:
            self.cursor.execute("""UPDATE conversations SET receiver=:receiver WHERE conv_id=:conv_id""",
                                {'conv_id': conv_id, 'receiver': receiver})

    def get_conv_by_id(self, conv_id):
        self.cursor.execute("""SELECT * FROM conversations
                                               WHERE conv_id=:conv_id""",
                            {'conv_id': conv_id})
        founds = self.cursor.fetchall()
        if founds:
            assert len(founds) == 1
            conv = founds[0]
            conv_dict = {'conv_id': conv[0], 'sender': conv[1], 'receiver': conv[2], 'status': conv[3], 'time': conv[4]}
            return conv_dict
        else:
            return None

    def get_all_convs_by_sender(self, sender):
        self.cursor.execute("""SELECT * FROM conversations
                                               WHERE sender=:sender""",
                            {'sender': sender})
        founds = self.cursor.fetchall()
        convs = []
        for conv in founds:
            conv_dict = {'conv_id': conv[0], 'sender': conv[1], 'receiver': conv[2], 'status': conv[3], 'time': conv[4]}
            convs.append(conv_dict)
        return convs

    def get_all_convs_by_receiver(self, receiver):
        self.cursor.execute("""SELECT * FROM conversations
                                               WHERE receiver=:receiver""",
                            {'receiver': receiver})
        founds = self.cursor.fetchall()
        convs = []
        for conv in founds:
            conv_dict = {'conv_id': conv[0], 'sender': conv[1], 'receiver': conv[2], 'status': conv[3], 'time': conv[4]}
            convs.append(conv_dict)
        return convs

    def get_tickets_by_conv(self, conv_id):
        self.cursor.execute("""SELECT * FROM tickets
                                               WHERE conv_id=:conv_id""",
                            {'conv_id': conv_id})
        founds = self.cursor.fetchall()
        tickets = []
        for ticket in founds:
            ticket_dict = {'conv_id': ticket[0], 'time': ticket[1], 'username': ticket[2], 'message': ticket[3]}
            tickets.append(ticket_dict)
        return tickets

    def insert_ticket(self, ticket_dict):
        if 'time' not in ticket_dict.keys():
            ticket_dict['time'] = datetime.datetime.now()

        assert 'conv_id' in ticket_dict.keys()
        assert 'username' in ticket_dict.keys()
        assert 'message' in ticket_dict.keys()

        with self.conn:
            columns = ', '.join(ticket_dict.keys())
            placeholders = ':' + ', :'.join(ticket_dict.keys())
            query = 'INSERT INTO tickets (%s) VALUES (%s)' % (columns, placeholders)
            self.cursor.execute(query, ticket_dict)



class Proxy_Database(Database):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect(PROXY_DATABASE_NAME)
        self.cursor = self.conn.cursor()

    def first_time_setup(self):
        with self.conn:
            self.cursor.execute("""CREATE TABLE tokens (
                            token_id TEXT,
                            username TEXT
                        )""")

            self.cursor.execute("""CREATE TABLE token_time (
                            token_id TEXT,
                            time BLOB
                        )""")

            self.cursor.execute("""CREATE TABLE users (
                            username TEXT,
                            password TEXT,
                            type TEXT, 
                            striked INT,
                            approved INT
                        )""")

            self.cursor.execute("INSERT INTO users VALUES (:username, :password, :type, :striked, :approved)",
                                (MANAGER['username'], MANAGER['password'], MANAGER['type'], MANAGER['striked'],
                                 MANAGER['approved']))
