from database import Database
from templates.utils import http_ok_header


def proxy_home(request_dict):
    with open("templates/proxyHome/home.html") as f:
        return http_ok_header() + f.read()


def proxy_login(request_dict):
    username = request_dict["form_parts"][0][1].decode().split("\r\n")[0]
    password = request_dict["form_parts"][1][1].decode().split("\r\n")[0]
    d = Database(proxy=True)
    user = d.get_account_by_username(username)
    if user['password'] == password:
        token = d.get_a_new_token_for_user({"username": user["username"]})
        request_dict["token"] = token

        new_cookies = [("token", request_dict["token"])]
        return http_ok_header(
            new_cookies) + f'''
                <html> <head> <meta http-equiv="refresh" content="0; url=/home" /> <body>  </body> </head> </html>
                '''


def forward_func(request_dict):
    pass
