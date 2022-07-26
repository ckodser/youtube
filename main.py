import random
import socket
from templates.login.view import login, login_helper, login_action
from templates.signin.view import signin, signin_helper
from templates.client_home.view import client_home
from templates.error.view import error_page, error_file
from templates.favicon.view import favicon

HOST = "127.0.0.2"  # Standard loopback interface address (localhost)
PORT = 8080  # Port to listen on (non-privileged ports are > 1023)


def to_request_dict(data):
    request_dict = {}
    for row in data:
        if row.find(":") != -1:
            request_dict[row[:row.find(":")]] = row[row.find(":") + 2:].rstrip("\r")
    if "Cookie" in request_dict:
        cookies = request_dict["Cookie"].split(";")
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie.split("=")[0]] = cookie.split("=")[1]
        request_dict["Cookie"] = cookies_dict
    return request_dict


def http_ok_header(cookies=None):
    if cookies is None:
        return "HTTP/1.1 200 OK\r\n\r\n"
    else:
        ans = f"HTTP/1.1 200 OK\r\n"
        for cookie_name, cookie_value in cookies:
            ans += f"Set-Cookie: {cookie_name}={cookie_value}\r\n"
        ans += "\r\n"
        return ans


def get_parameters(url, split_url):
    url = url.lstrip("/").split("/")
    dict = {}
    for i, part in enumerate(url):
        if part[0] == "<":
            if part[len(part) - 2] == "+":
                dict["rest"] = split_url[i:]
                break
            else:
                dict[part[1:-1]] = split_url[i]
    return dict


def is_match(url, split_url):
    url = url.lstrip("/").split("/")
    for i, part in enumerate(url):
        if len(split_url) <= i:
            return False
        if part[0] == "<":
            if part[len(part) - 2] == "+":
                if split_url[i].startswith(part[1:-2]):
                    return True
                return False
        else:
            if part != split_url[i]:
                return False
    return True


def start_listening(HOST, PORT, function_url_list):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        while True:
            s.listen()
            conn, addr = s.accept()
            with conn:
                data = ""
                while True:
                    data = conn.recv(10240).decode()
                    break
                if len(data) == 0:
                    continue
                split_data = data.split()
                method = split_data[0]
                url = split_data[1]
                request_dict = to_request_dict(data.split("\n")[1:])
                request_dict["method"] = method
                request_dict["url"] = url
                request_dict["body"] = data[data.find("\r\n\r\n") + 4:]
                split_url = url.lstrip("/").split("/")
                answer = 404
                for function, url in function_url_list:
                    if is_match(url, split_url):
                        parameters = get_parameters(url, split_url)
                        parameters["request_dict"] = request_dict
                        answer = function(**parameters)
                        break
                if answer is None:
                    conn.close()
                    continue
                if answer == 404:
                    print(f"Connected by {addr}")
                    print(method, url, request_dict)
                    print("ERROR")
                    answer = error_page(request_dict, function_url_list)
                if answer.__class__ == str:
                    answer = answer.encode()
                conn.sendall(answer)


print("open site by: ", "http://" + str(HOST) + ":" + str(PORT) + "/login")
start_listening(HOST, PORT,
                [(client_home, "/home/<id>"), (favicon, "/favicon.ico")
                    , (login, "/login"), (login_helper, "/templates/login/<+>"), (login_action, "/<login?email=+>"),
                 (signin, "/signin"), (signin_helper, "/templates/signin/<+>"),
                 ])
