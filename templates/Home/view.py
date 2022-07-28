from database import Database
from templates.utils import http_ok_header

def user_home(request_dict, user_name, user_info):
    user_name_cool=user_name.replace("%40","@")
    return http_ok_header()+f'''
            <html> <head> <body> <h1> Hello USER {user_name_cool}</h1> 
            <br>
             <a href="/videos"> videos </a> 
             <br>
            <a href="/tikets"> tikets </a> 
            <br>
            <input type="file">
            
            </body>             
            </head> </html>
                        '''

def admin_home(request_dict, user_name, user_info):
    user_name_cool = user_name.replace("%40", "@")
    return http_ok_header() + f'''
            <html> <head> <body> <h1> Hello ADMIN {user_name_cool}</h1> 
            <br>
             <a href="/videos"> videos </a> 
             <br>
            <a href="/tikets"> tikets </a> 
            <br>
            </body>             
            </head> </html>
                        '''

def manager_home(request_dict):
    d=Database()
    list="<li>"+str(d.get_all_pending_admin())+"</li>"
    return http_ok_header() + f'''
            <html> <head> <body> <h1> Hello BOSS</h1> 
            <br>
            <a href="/tikets"> tikets </a> 
            <br>
            <ul>
            {list}
            </ul>
            </body>             
            </head> </html>
                        '''

def func_home(request_dict):
    print("REQUEST DICT FUNC HOME", request_dict)
    try:
        token_id=request_dict["Cookie"]["token"]
    except:
        token_id="2"
    d=Database()
    user_name=d.get_token_by_id(token_id)["username"]
    print("USERNAME FUNC HOME",user_name)
    user_info=d.get_account_by_username(user_name)
    print("USERINFO FUNC HOME",user_info)
    user_type=user_info["type"]
    if user_type=="admin":
        return admin_home(request_dict, user_name, user_info)
    elif user_type=="user":
        return user_home(request_dict, user_name, user_info)
    elif user_type=="manager":
        return manager_home(request_dict)