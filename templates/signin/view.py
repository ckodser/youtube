from ..utils import get_file_packet
from ..client_home.view import client_home

def http_ok_header(cookies=None):
    if cookies is None:
        return "HTTP/1.1 200 OK\r\n\r\n"
    else:
        ans = f"HTTP/1.1 200 OK\r\n"
        for cookie_name, cookie_value in cookies:
            ans += f"Set-Cookie: {cookie_name}={cookie_value}\r\n"
        ans += "\r\n"
        return ans


def signin(request_dict):
    if request_dict["method"] == "GET":
        with open("templates/signin/index.html", "r", encoding="utf-8") as index:
            return http_ok_header() + index.read()
    else:
        return client_home(request_dict, "SIGNIN POST")


def signin_helper(request_dict, rest):
    file_location = "templates/signin/" + "/".join(rest)
    return get_file_packet(file_location)

