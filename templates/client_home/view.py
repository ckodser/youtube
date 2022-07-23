def http_ok_header(cookies=None):
    if cookies is None:
        return "HTTP/1.1 200 OK\r\n\r\n"
    else:
        ans = f"HTTP/1.1 200 OK\r\n"
        for cookie_name, cookie_value in cookies:
            ans += f"Set-Cookie: {cookie_name}={cookie_value}\r\n"
        ans += "\r\n"
        return ans

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
