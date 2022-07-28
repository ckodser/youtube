from templates.utils import http_ok_header

def client_home(request_dict, id):
    list = ""
    for k in request_dict.keys():
        if k != "Cookie":
            list += f"<li> {k}={request_dict[k]}</li>\n"
    cookie_list = ""
    if "Cookie" in request_dict:
        for cookie_name in request_dict["Cookie"].keys():
            cookie_list += f"<li> {cookie_name}={request_dict['Cookie'][cookie_name]}</li>\n"
    new_cookies=None if "token" not in request_dict else [("token", request_dict["token"])]
    return http_ok_header(new_cookies) + f"<html> <head> <body> <h1> id={id}</h1> <ul>{list} </ul> <h2> cookies </h2> <ul> {cookie_list}</ul> </body> </head> </html>"
