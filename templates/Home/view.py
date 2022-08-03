import random

from database import Database
from templates.utils import http_ok_header, get_account
from templates.error.view import error_page
from templates.client_home.view import client_home
import cv2


def upload_video(request_dict):
    user_info = get_account(request_dict)
    if user_info is None or user_info["type"] != "user" or user_info["striked"] == 1:
        request_dict["file_data"] = "FILE DATA REMOVED"
        return error_page(request_dict, [])
    user_name = user_info["username"].replace("%40", "@")
    video_name = request_dict['form_parts'][0][1].decode().split("\r\n")[0]
    file_address = f'''videos/{user_name.replace('.', '').replace('@', '')}{random.randint(1, 100000000)}{video_name}'''
    with open(file_address + ".mp4", mode="wb") as f:
        f.write(request_dict['form_parts'][1][1])
        print(len(request_dict['form_parts'][1][1]))

    vidcap = cv2.VideoCapture(file_address + ".mp4")
    success, image = vidcap.read()
    if success:
        cv2.imwrite(file_address + ".jpg", image)  # save frame as JPEG file

    database = Database()
    database.insert_video(video_dict={"address": file_address, "name": video_name, "username": user_name})

    return http_ok_header() + f'''
                        <html> <head> <meta http-equiv="refresh" content="0; url=/videos" /> <body>  </body> </head> </html>
                        '''


def user_home(request_dict, user_name, user_info):
    user_name_cool = user_name.replace("%40", "@")
    return http_ok_header() + f'''
            <html> <head> <body> <h1> Hello USER {user_name_cool}</h1> 
            <br>
             <a href="/videos"> videos </a> 
             <br>
            <a href="/tickets"> tickets </a> 
            <br>
                    <form method="post" enctype="multipart/form-data" action="/video_upload" >
                        <input type="text" name="videoName"/>
                        <input type="file" accept="video/mp4" name="videoformat" id="input-tag"/>
                        <input type="submit" name="submit"  />
                    </form>

            </body>             
            </head> </html>
                        '''


def admin_home(request_dict, user_name, user_info):
    user_name_cool = user_name.replace("%40", "@")
    d = Database()
    list = ""
    striked_users = (d.get_all_striked_users())
    for user in striked_users:
        list += f''' <li>  <a href=/unstriked/{user["username"]}> unstriked {user["username"]} </a> </li>\n'''


    return http_ok_header() + f'''
            <html> <head> <body> <h1> Hello ADMIN {user_name_cool}</h1> 
            <br>
             <a href="/videos"> videos </a> 
             <br>
            <a href="/tickets"> tickets </a> 
            <br>
            <ul>
            {list}
            </ul>
            </body>             
            </head> </html>
                        '''


def approved(request_dict, username):
    user_info = get_account(request_dict)
    if user_info is None or user_info["type"] != "manager":
        return error_page(request_dict, [])
    d = Database()
    d.approve_admin(username)
    return http_ok_header() + f'''
                    <html> <head> <meta http-equiv="refresh" content="0; url=/home" /> <body>  </body> </head> </html>
                    '''


def unstriked(request_dict, username):
    user_info = get_account(request_dict)
    if user_info is None or user_info["type"] != "admin":
        return error_page(request_dict, [])

    d = Database()
    d.change_strike_status_of_user(username, 0)
    return http_ok_header() + f'''
                    <html> <head> <meta http-equiv="refresh" content="0; url=/home" /> <body>  </body> </head> </html>
                    '''


def manager_home(request_dict):
    d = Database()
    list = ""
    pend_admin = (d.get_all_pending_admin())
    for admin in pend_admin:
        list += f''' <li>  <a href=/approve/{admin["username"]}> approve {admin["username"]} </a> </li>\n'''
    striked_users = (d.get_all_striked_users())
    for user in striked_users:
        list += f''' <li>  <a href=/unstriked/{user["username"]}> unstriked {user["username"]} </a> </li>\n'''

    return http_ok_header() + f'''
            <html> <head> <body> <h1> Hello BOSS</h1> 
            <br>
            <a href="/tickets"> tickets </a> 
            <br>
            <ul>
            {list}
            </ul>
            </body>             
            </head> </html>
                        '''


def func_home(request_dict):
    user_info = get_account(request_dict)
    if user_info is None:
        return error_page(request_dict, [])
    print("USERINFO FUNC HOME", user_info)
    user_type = user_info["type"]
    if user_type == "admin":
        return admin_home(request_dict, user_info["username"], user_info)
    elif user_type == "user":
        return user_home(request_dict, user_info["username"], user_info)
    elif user_type == "manager":
        return manager_home(request_dict)

# +'''
#             <hr>
#             <video controls id="video-tag">
#               <source id="video-source" src="splashVideo">
#               Your browser does not support the video tag.
#             </video>
#
#             ''' + '''
#             <script>
#             const videoSrc = document.querySelector("#video-source");
#             const videoTag = document.querySelector("#video-tag");
#             const inputTag = document.querySelector("#input-tag");
#
#             inputTag.addEventListener('change',  readVideo)
#
#             function readVideo(event) {
#               console.log(event.target.files)
#               if (event.target.files && event.target.files[0]) {
#                 var reader = new FileReader();
#
#                 reader.onload = function(e) {
#                   console.log('loaded')
#                   videoSrc.src = e.target.result
#                   videoTag.load()
#                 }.bind(this)
#
#                 reader.readAsDataURL(event.target.files[0]);
#               }
#             }
#             </script>
