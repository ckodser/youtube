import copy
import os
import random
import socket
import threading
from templates.utils import http_ok_header
from templates.login.view import login, login_helper, login_action
from templates.signin.view import signin, signin_helper
from templates.client_home.view import client_home
from templates.error.view import error_page, error_file
from templates.Home.view import func_home, approved, unstriked, upload_video
from templates.favicon.view import favicon
from templates.video.view import all_videos, video_frame, video_page, add_comment, like, dislike, video_file, remove_video
from templates.convs_and_tickets.view import func_conversations, func_ticket
from database import Database
from html import unescape

HOST = "127.0.0.2"  # Standard loopback interface address (localhost)
USERPORT = 8080  # Port to listen on (non-privileged ports are > 1023)
ADMINPORT = 8081  # Port to listen on (non-privileged ports are > 1023)
global database


def get_database():
    return database


def to_request_dict(data):
    request_dict = {}
    for row in data:
        if row.find(":") != -1:
            request_dict[row[:row.find(":")]] = row[row.find(":") + 2:].rstrip("\r")
    if "Cookie" in request_dict:
        cookies = request_dict["Cookie"].split(";")
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie.split("=")[0].lstrip().rstrip()] = cookie.split("=")[1].lstrip().rstrip()
        request_dict["Cookie"] = cookies_dict

    if "Content-Disposition" in request_dict:
        cookies = request_dict["Content-Disposition"].split(";")
        cookies_dict = {}
        for cookie in cookies:
            if "=" in cookie:
                cookies_dict[cookie.split("=")[0].lstrip().rstrip()] = cookie.split("=")[1].lstrip().rstrip().lstrip(
                    '"').rstrip('"')
        request_dict["Content-Disposition"] = cookies_dict
    return request_dict


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


def start_listening(HOST, PORT, function_url_list, admin):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        while True:
            s.listen()
            conn = None
            try:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(50000000)
                    form_parts = []
                    if not "multipart/form-data".encode() in data:
                        data = data.decode()
                    else:
                        content_length_start = data.find("Content-Length".encode()) + 16
                        content_length_length = data[content_length_start:].find("\r\n".encode())
                        content_length = data[
                                         content_length_start:content_length_start + content_length_length].decode()
                        content_length = int(content_length)
                        while len(data) < content_length:
                            data += conn.recv(50000000)
                        header_end = data.find("\r\n\r\n".encode())
                        header = data[:header_end].decode()
                        rest = data[header_end + 4:]

                        while len(rest) > 0:
                            header_end = rest.find("\r\n\r\n".encode())
                            form_header = rest[:header_end].decode().split("\n")[1:]
                            rest = rest[header_end + 4:]
                            if rest.find("\r\nContent-Disposition: form-data; name=".encode()) != -1:
                                end_data = rest.find("\r\nContent-Disposition: form-data; name=".encode())
                                form_data = rest[:end_data]
                                rest = rest[end_data + 2:]
                            else:
                                break
                            form_parts.append((form_header, form_data))
                        data = header

                    if len(data) == 0:
                        continue
                    split_data = data.split()
                    request_dict = to_request_dict(data.split("\n")[1:])
                    method = split_data[0]
                    url = split_data[1]
                    request_dict["method"] = method
                    request_dict["url"] = url
                    request_dict["body"] = data[data.find("\r\n\r\n") + 4:]
                    request_dict["form_parts"] = form_parts
                    request_dict["admin"]=admin
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
            except KeyboardInterrupt:
                if conn is not None:
                    conn.close()
                break
    print("Server stopped, Good Bye!")


if __name__ == "__main__":
    global database
    database = Database()
    try:
        database.first_time_setup()
    except:
        pass

    function_list=[
                        (client_home, "/home/<id>"),
                        (favicon, "/favicon.ico"),
                        (login, "/login"),
                        (login_helper, "/templates/login/<+>"),
                        (login_action, "/<login?email=+>"),
                        (signin, "/signinuser"),
                        (signin_helper, "/templates/signin/<+>"),
                        (signin, "/signinadmin"),
                        (func_home, "/home"),
                        (unstriked, "/unstrike/<username>"),
                        (approved, "/approve/<username>"),
                        (upload_video, "/video_upload"),
                        (all_videos, "/videos"),
                        (video_frame, "/videoFrame/<id>"),
                        (func_conversations, "/tickets"),
                        (func_ticket, "/conversation/<conv_id>"),
                        (video_page, "video/<id>"),
                        (add_comment, "/add_comment/<id>"),
                        (like, "/like/<id>"),
                        (dislike, "/dislike/<id>"),
                        (video_file, "videosFILE/<id>"),
                        (danger_tag, "/danger_tag/<id>"),
                        (remove_video, "/remove_video/<id>")
                    ]
    # database.insert_video(video_dict={"address": "1.mp4", "name": "rain"})
    print("user open site by: ", "http://" + str(HOST) + ":" + str(USERPORT) + "/home")
    print("admin open site by: ", "http://" + str(HOST) + ":" + str(ADMINPORT) + "/home")

    x = threading.Thread(target=start_listening, args=(HOST, USERPORT, function_list, False))
    y = threading.Thread(target=start_listening, args=(HOST, ADMINPORT, function_list, True))
    x.start()
    y.start()
    x.join()
    y.join()