from database import Database
from templates.utils import http_ok_header, get_account
from templates.utils import get_file_packet
from urllib.parse import unquote_plus


def all_videos(request_dict):
    database = Database()
    videos = database.get_all_videos()
    links = ""
    for video in videos:
        links += '<li> <a href="/video/{}"> <img src="videoFrame/{}">  <br> name: {} \t by user: {} </a></li>\n'.format(
            video["video_id"], video["video_id"], video["name"], video["username"])
    with open("templates/video/all_videos.html") as f:
        return http_ok_header() + f.read().replace("{{LIST}}", links)


def video_frame(request_dict, id):
    database = Database()
    video = database.get_video_by_id(id)
    video_first_frame_address = video["address"] + ".jpg"
    return get_file_packet(video_first_frame_address)


def video_file(request_dict, id):
    database = Database()
    video = database.get_video_by_id(id)
    video_first_frame_address = video["address"] + ".mp4"
    return get_file_packet(video_first_frame_address)


def video_page(request_dict, id):
    database = Database()
    video = database.get_video_by_id(id)
    with open("templates/video/video.html") as f:
        text = f.read()
    comments_list = ""
    comments = database.get_video_comments(id)
    for comment in comments:
        comments_list += f'''<li> 
        user:{comment["username"]} <br>
        {unquote_plus(comment["comment"])}
        </li>'''
    user_info = get_account(request_dict)
    if user_info["type"] != "user":
        admin_buttons = f'''    
        <form action="/remove_video/{id}" method="post">
            <input type="submit" value="removevideo">
        </form>
        '''
    else:
        admin_buttons = ""

    tags = video["tag"]
    user_buttons = ""
    if user_info["type"] == "user":
        user_buttons = f'''
        <form action="/like/{id}" method="post">
            <input type="submit" value="like">
        </form>
    
        <form action="/dislike/{id}" method="post">
            <input type="submit" value="dislike">
        </form>
        '''
    replace_list = [
        ("video_id", id),
        ("video_name", video["name"]),
        ("like_count", database.get_video_likes(id)['likes']),
        ("dislikes_count", database.get_video_likes(id)['dislikes']),
        ("comments_list", comments_list),
        ("admin_buttons", admin_buttons),
        ("tag", tags),
        ("user_buttons", user_buttons)
    ]
    for key, value in replace_list:
        text = text.replace("{{" + key + "}}", str(value))
    return http_ok_header() + text


def dislike(request_dict, id):
    database = Database()
    user_info = get_account(request_dict)
    if user_info["type"] == "user":
        database.add_change_liked_status_of_video(id, user_info["username"], 0)
    return http_ok_header() + f'''
                            <html> <head> <meta http-equiv="refresh" content="0; url=/video/{id}" /> <body>  </body> </head> </html>
                            '''


def like(request_dict, id):
    database = Database()
    user_info = get_account(request_dict)
    if user_info["type"] == "user":
        database.add_change_liked_status_of_video(id, user_info["username"], 1)
    return http_ok_header() + f'''
                        <html> <head> <meta http-equiv="refresh" content="0; url=/video/{id}" /> <body>  </body> </head> </html>
                        '''


def remove_video(request_dict, id):
    database = Database()
    user_info = get_account(request_dict)
    if user_info["type"] != "user":
        print("DELETE VIDEO", id)
        database.delete_video(id)

    return http_ok_header() + f'''
                            <html> <head> <meta http-equiv="refresh" content="0; url=/videos" /> <body>  </body> </head> </html>
                            '''


def add_comment(request_dict, id):
    database = Database()
    user_info = get_account(request_dict)
    comment = request_dict["body"].lstrip("comment=").replace("+", " ")
    if user_info["type"] == "user":
        database.add_comment_on_video(id, user_info["username"].replace("%40", "@"), comment)
    else:
        database.tag_the_video(id, comment)
    return http_ok_header() + f'''
                        <html> <head> <meta http-equiv="refresh" content="0; url=/video/{id}" /> <body>  </body> </head> </html>
                        '''
