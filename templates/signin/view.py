from ..utils import get_file_packet
from ..client_home.view import client_home
from database import Database
from ..login.view import login
from templates.utils import http_ok_header


def signin(request_dict):
    if request_dict["method"] == "GET":
        with open("templates/signin/index.html", "r", encoding="utf-8") as index:
            return http_ok_header() + index.read()
    else:
        info = {}
        data = request_dict["body"].split("&")
        for field in data:
            field = field.split("=")
            info[field[0]] = field[1]
        if info["password"] != info["re_password"] or "agree-term" not in info or info["submit"] != 'Sign+up':
            with open("templates/signin/index.html", "r", encoding="utf-8") as index:
                return http_ok_header() + index.read()
        d = Database()
        print("SIGN IN",info["email"])
        try:
            d.insert_user({"username": info["email"],
                           "password": info["password"],
                           "type": request_dict["url"].lstrip("/signin")})
            return http_ok_header() + f'''
                               <html> <head> <meta http-equiv="refresh" content="0; url=/login" /> <body>  </body> </head> </html>
                               '''
        except:
            with open("templates/signin/index.html", "r", encoding="utf-8") as index:
                return http_ok_header() + index.read()


def signin_helper(request_dict, rest):
    file_location = "templates/signin/" + "/".join(rest)
    return get_file_packet(file_location)
