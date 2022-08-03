import socket

from database import Database, Proxy_Database
from templates.utils import http_ok_header, get_proxy_account


def proxy_home(request_dict):
    with open("templates/proxyHome/home.html") as f:
        return http_ok_header() + f.read()


def proxy_login(request_dict):
    username = request_dict["form_parts"][0][1].decode().split("\r\n")[0]
    password = request_dict["form_parts"][1][1].decode().split("\r\n")[0]
    d = Proxy_Database()
    user = d.get_account_by_username(username)
    if user['password'] == password:
        token = d.get_a_new_token_for_user({"username": user["username"]})
        request_dict["proxytoken"] = token

        new_cookies = [("proxytoken", request_dict["proxytoken"])]
        url = "home"
        if user["type"] == "manager":
            url = "proxy_account_build"
        return http_ok_header(
            new_cookies) + f'''
                <html> <head> <meta http-equiv="refresh" content="0; url=/{url}" /> <body>  </body> </head> </html>
                '''


def proxy_account_build(request_dict):
    user = get_proxy_account(request_dict)
    if user["type"] == "manager":
        with open("templates/proxyHome/build_account.html") as f:
            return http_ok_header() + f.read()
    return None


def proxy_build_account_action(request_dict):
    user = get_proxy_account(request_dict)
    if user["type"] == "manager":
        username = request_dict["form_parts"][0][1].decode().split("\r\n")[0]
        password = request_dict["form_parts"][1][1].decode().split("\r\n")[0]
        d = Proxy_Database()
        try:
            d.insert_user({"username": username,
                           "password": password,
                           "type": "admin"}
                          )
        except:
            pass
        return http_ok_header() + f'''
                    <html> <head> <meta http-equiv="refresh" content="0; url=/proxy_account_build" /> <body>  </body> </head> </html>
                    '''
    return None


def forward_func(request_dict):
    user = get_proxy_account(request_dict)
    if user is not None and user["type"] == "manager" or user["type"] == "admin":
        TCP_IP = "127.0.0.2"
        TCP_PORT = 8081
        BUFFER_SIZE = 500000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(request_dict["packet"])
        data = s.recv(BUFFER_SIZE)
        s.close()
        return data
    else:
        return None

