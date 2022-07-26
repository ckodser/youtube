from ..utils import get_file_packet
from database import Database
from templates.utils import http_ok_header
from urllib.parse import unquote_plus

def login(request_dict):
    with open("templates/login/index.html", "r", encoding="utf-8") as index:
        return http_ok_header() + index.read()


def login_helper(request_dict, rest):
    file_location = "templates/login/" + "/".join(rest)
    return get_file_packet(file_location)


def login_action(request_dict, rest):
    url: str = rest[0]
    email_end = url.find("email=") + 6
    pass_end = url.find("pass=") + 5
    email = unquote_plus(url[email_end:pass_end - 6])
    pass_word = unquote_plus(url[pass_end:].replace("%23", "#"))
    d = Database()
    user = d.get_account_by_username(email)
    try:
        if user['password'] == pass_word and user['striked'] == 0 and user['approved'] == 1:
            token = d.get_a_new_token_for_user({"username": user["username"]})
            request_dict["token"] = token

            new_cookies = [("token", request_dict["token"])]
            return http_ok_header(
                new_cookies) + f'''
                <html> <head> <meta http-equiv="refresh" content="0; url=/home" /> <body>  </body> </head> </html>
                '''
        else:
            print(user['password'], pass_word)
            print("wrong pass")
    except:
        print("some error in login/view.py")
        pass
    request_dict["status"] = "wrong username/password"
    return http_ok_header() + f'''
                       <html> <head> <meta http-equiv="refresh" content="0; url=/login" /> <body>  </body> </head> </html>
                       '''
