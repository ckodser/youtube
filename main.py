import random
import socket

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


def error_page(request_dict, function_url_list):
    list = ""
    for function, url in function_url_list:
        url = url.replace("<", "*")
        url = url.replace(">", "*")
        list += f"<li> {url} </li>\n"

    return http_ok_header([("bardia1", 4), ("bardia2",
                                            "rtrt")]) + f"<html> <head> <body> <h1> URL {request_dict['url']} DOESN'T MATCH ANY OF \n <br> <ul> {list} </ul> </h1> </body> </head> </html>"


def get_parameters(url, split_url):
    url = url.lstrip("/").split("/")
    dict = {}
    for i, part in enumerate(url):
        if part[0] == "<":
            dict[part[1:-1]] = split_url[i]
    return dict


def is_match(url, split_url):
    url = url.lstrip("/").split("/")
    if len(url) != len(split_url):
        return False
    for i, part in enumerate(url):
        if part[0] == "<":
            pass
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
                print(f"Connected by {addr}")
                data = ""
                while True:
                    data = conn.recv(10240).decode()
                    break
                split_data = data.split()
                method = split_data[0]
                url = split_data[1]
                request_dict = to_request_dict(data.split("\n")[1:])
                print(method, url, request_dict)
                request_dict["method"] = method
                request_dict["url"] = url
                split_url = url.lstrip("/").split("/")
                answer = error_page(request_dict, function_url_list)
                for function, url in function_url_list:
                    if is_match(url, split_url):
                        parameters = get_parameters(url, split_url)
                        parameters["request_dict"] = request_dict
                        answer = function(**parameters)
                        break
                if answer.__class__ == str:
                    answer = answer.encode()
                conn.sendall(answer)


def client_home(request_dict, id):
    list = ""
    for k in request_dict.keys():
        if k != "Cookie":
            list += f"<li> {k}={request_dict[k]}</li>\n"
    cookie_list = ""
    if "Cookie" in request_dict:
        for cookie_name in request_dict["Cookie"].keys():
            cookie_list += f"<li> {cookie_name}={request_dict['Cookie'][cookie_name]}</li>\n"
    return http_ok_header() + f"<html> <head> <body> <h1> id={id}</h1> <ul>{list} </ul> <h2> cookies </h2> <ul> {cookie_list}</ul> </body> </head> </html>"


def favicon(request_dict):
    with open("favicon.ico", "rb") as f:
        ans = 'HTTP/1.1 200 OK\r\n'.encode()
        ans += "Content-Type: image/jpeg\r\n".encode()
        ans += "Accept-Ranges: bytes\r\n\r\n".encode()
        ans += f.read()
        return ans


start_listening(HOST, PORT, [(client_home, "/home/<id>"), (favicon, "/favicon.ico")])
