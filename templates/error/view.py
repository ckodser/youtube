from templates.utils import http_ok_header

def error_page(request_dict, function_url_list):
    print("request dict", len(request_dict), request_dict)
    list = ""
    for k in request_dict.keys():
        if k != "Cookie":
            list += f"<li> {k}={request_dict[k]}</li>\n"
    cookie_list = ""
    if "Cookie" in request_dict:
        for cookie_name in request_dict["Cookie"].keys():
            cookie_list += f"<li> {cookie_name}={request_dict['Cookie'][cookie_name]}</li>\n"
    new_cookies = None if "token" not in request_dict else [("token", request_dict["token"])]



    list = ""
    for function, url in function_url_list:
        url = url.replace("<", "*")
        url = url.replace(">", "*")
        list += f"<li> {url} </li>\n"
    with open("templates/error/index.html") as index:
        return http_ok_header([("bardia1", 4), ("bardia2","rtrt")])+index.read().replace("{{LIST}}", list).replace("{{URL}}", request_dict['url']).replace("{{list}}", list).replace("{{cookie_list}}", cookie_list)