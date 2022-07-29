from database import Database
from templates.utils import http_ok_header, get_account
from templates.error.view import error_page
from templates.client_home.view import client_home
def upload_video(request_dict):
    print(request_dict)
    return client_home(request_dict, "UPLOAD")

def user_home(request_dict, user_name, user_info):
    user_name_cool = user_name.replace("%40", "@")
    return http_ok_header() + f'''
            <html> <head> <body> <h1> Hello USER {user_name_cool}</h1> 
            <br>
             <a href="/videos"> videos </a> 
             <br>
            <a href="/tikets"> tikets </a> 
            <br>
            
            <input type="file" accept="video/*" id="input-tag"/>
            <hr>
            <video controls id="video-tag">
              <source id="video-source" src="splashVideo">
              Your browser does not support the video tag.
            </video>
            
            '''+'''
            <script>
            const videoSrc = document.querySelector("#video-source");
            const videoTag = document.querySelector("#video-tag");
            const inputTag = document.querySelector("#input-tag");
            
            inputTag.addEventListener('change',  readVideo)
            
            function readVideo(event) {
              console.log(event.target.files)
              if (event.target.files && event.target.files[0]) {
                var reader = new FileReader();
                
                reader.onload = function(e) {
                  console.log('loaded')
                  videoSrc.src = e.target.result
                  videoTag.load()
                }.bind(this)
            
                reader.readAsDataURL(event.target.files[0]);
              }
            }
            </script>

            </body>             
            </head> </html>
                        '''


def admin_home(request_dict, user_name, user_info):
    user_name_cool = user_name.replace("%40", "@")
    return http_ok_header() + f'''
            <html> <head> <body> <h1> Hello ADMIN {user_name_cool}</h1> 
            <br>
             <a href="/videos"> videos </a> 
             <br>
            <a href="/tikets"> tikets </a> 
            <br>
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
    if user_info is None or user_info["type"] != "manager":
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
            <a href="/tikets"> tikets </a> 
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
