from database import Database
from templates.utils import http_ok_header

def user_home(request_dict, user_name, user_info):
    return http_ok_header()+f'''
            <html> <head> <body> <h1> Hello {user_name}</h1> <br> <a href="/videos> videos </a> <br>
            <a href="/tikets"> tikets </a> </body> <br>
            <input type="file">            
            </head> </html>
                        '''

def admin_home(request_dict, user_name, user_info):
    pass
def func_home(request_dict):
    print(request_dict)
    token_id=request_dict["Cookie"]["token"]
    d=Database()
    user_name=d.get_token_by_id(token_id)["username"]
    user_info=d.get_account_by_username({"username": user_name})
    user_type=user_info["type"]
    if user_type=="admin":
        return admin_home(request_dict, user_name, user_info)
    elif user_type=="user":
        return user_home(request_dict, user_name, user_info)