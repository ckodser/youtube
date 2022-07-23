def favicon(request_dict):
    with open("favicon.ico", "rb") as f:
        ans = 'HTTP/1.1 200 OK\r\n'.encode()
        ans += "Content-Type: image/jpeg\r\n".encode()
        ans += "Accept-Ranges: bytes\r\n\r\n".encode()
        ans += f.read()
        return ans