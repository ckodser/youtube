from database import Database


def get_account(request_dict):
    try:
        d = Database()
        token_id = request_dict["Cookie"]["token"]
        user_name = d.get_token_by_id(token_id)["username"]
        user_info = d.get_account_by_username(user_name)
        if user_info["type"] != "user" and not request_dict["admin"]:
            print("PROXY NOT SET")
            return None
        return user_info
    except:
        return None


def http_ok_header(cookies=None):
    if cookies is None:
        return "HTTP/1.1 200 OK\r\n\r\n"
    else:
        ans = f"HTTP/1.1 200 OK\r\n"
        for cookie_name, cookie_value in cookies:
            ans += f"Set-Cookie:{cookie_name}={cookie_value}\r\n"
        ans += "\r\n"
        return ans


def get_file_packet(file_location):
    if file_location.find("?") != -1:
        file_location = file_location[:file_location.find("?")]
    with open(file_location, "rb") as f:
        ans = 'HTTP/1.1 200 OK\r\n'.encode()
        if file_location.endswith("css"):
            ans += "Content-Type: text/css\r\n".encode()
        elif file_location.endswith("js"):
            ans += "Content-Type: application/javascript\r\n".encode()
        elif file_location.endswith("png"):
            ans += "Content-Type: image/png\r\n".encode()
        elif file_location.endswith("ttf"):
            ans += "Content-Type: font/ttf\r\n".encode()
        elif file_location.endswith("ico"):
            ans += "Content-Type: image/jpeg\r\n".encode()
        elif file_location.endswith("jpg"):
            ans += "Content-Type: image/jpg\r\n".encode()
        elif file_location.endswith("woff2"):
            ans += "Content-Type: font/woff2\r\n".encode()
        elif file_location.endswith("mp4"):
            ans += "Content-Type: video/mp4\r\n".encode()
        else:
            print(file_location)
            raise ValueError
        ans += "Accept-Ranges: bytes\r\n\r\n".encode()
        ans += f.read()
        return ans
