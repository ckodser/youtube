from ..utils import get_file_packet


def http_ok_header(cookies=None):
    if cookies is None:
        return "HTTP/1.1 200 OK\r\n\r\n"
    else:
        ans = f"HTTP/1.1 200 OK\r\n"
        for cookie_name, cookie_value in cookies:
            ans += f"Set-Cookie: {cookie_name}={cookie_value}\r\n"
        ans += "\r\n"
        return ans


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
    email = url[email_end:pass_end - 6]
    pass_word = url[pass_end:]
    print(email, pass_word)
