from templates.utils import http_ok_header

def error_page(request_dict, function_url_list):
    list = ""
    for function, url in function_url_list:
        url = url.replace("<", "*")
        url = url.replace(">", "*")
        list += f"<li> {url} </li>\n"
    with open("templates/error/index.html") as index:
        return http_ok_header([("bardia1", 4), ("bardia2","rtrt")])+index.read().replace("{{LIST}}", list).replace("{{URL}}", request_dict['url'])

def error_file(request_dict, name):
    with open(f"templates/error/404-not-found-page/src/assets/{name}", "rb") as f:
        ans = 'HTTP/1.1 200 OK\r\n'.encode()
        ans += "Content-Type: image/jpeg\r\n".encode()
        ans += "Accept-Ranges: bytes\r\n\r\n".encode()
        ans += f.read()
        return ans