def get_file_packet(file_location):
    if file_location.find("?") != -1:
        file_location = file_location[:file_location.find("?")]
        print(file_location)
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
        else:
            print(file_location)
            raise ValueError
        ans += "Accept-Ranges: bytes\r\n\r\n".encode()
        ans += f.read()
        return ans
