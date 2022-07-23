import socket

HOST = "127.0.0.2"  # Standard loopback interface address (localhost)
PORT = 8080  # Port to listen on (non-privileged ports are > 1023)

http_ok_header = "HTTP/1.1 200 OK\r\n\r\n"


def to_request_dict(data):
    request_dict = {}
    for row in data:
        if row.find(":") != -1:
            request_dict[row[:row.find(":")]] = row[row.find(":") + 2:].rstrip("\r")
    return request_dict


def error_page():
    return "<html> <head> <body> <h1> URL DONT MATCH ANYTHING! </h1> </body> </head> </html>"


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
    print(split_url, url)
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
                function = split_data[0]
                url = split_data[1]
                request_dict = to_request_dict(data.split("\n")[1:])
                print(function, url, request_dict)
                split_url = url.lstrip("/").split("/")
                answer = error_page()
                for function, url in function_url_list:
                    if is_match(url, split_url):
                        parameters = get_parameters(url, split_url)
                        parameters["request_dict"] = request_dict
                        answer = function(**parameters)
                        break
                answer = http_ok_header + answer
                conn.sendall(answer.encode())


def client_home(request_dict, id):
    list = ""
    for k in request_dict.keys():
        list += f"<li> {k}={request_dict[k]}</li>\n"
    return f"<html> <head> <body> <h1> id={id}</h1> <ul>{list} </ul></body> </head> </html>"


start_listening(HOST, PORT, [(client_home, "/home/<id>")])
