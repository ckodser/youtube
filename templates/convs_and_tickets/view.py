from database import Database
from templates.utils import http_ok_header, get_account
from templates.error.view import error_page


def func_conversations(request_dict):
    user_info = get_account(request_dict)
    if user_info is None:
        return error_page(request_dict, [])
    print("USERINFO FUNC CONV", user_info)

    user_type = user_info["type"]

    responce = http_ok_header() + f'''
    <html> <head> <body>
    '''

    if user_type != "manager":
        responce += f'''
        <h1> Create new ticket (kargaran mashghule kar hastand) </h1>
        '''
        opened_conversations = Database().get_all_convs_by_sender(user_info["username"])
        html_created_conversations = ""
        for conv in opened_conversations:
            html_created_conversations += '''
            <li> <a href="/conversation/{}"> {} - Status: {} - Date created: {} </a></li>
            '''.format(conv["conv_id"], conv["conv_id"], conv["status"], conv["time"])
        responce += '''
        <h2> Created tickets: </h2>
        <ul> {} </ul>
        '''.format(html_created_conversations)

    if user_type != "user":
        answered_conversations = Database().get_all_convs_by_receiver(user_info["username"])
        html_answered_conversations = ""
        for conv in answered_conversations:
            html_answered_conversations += '''
            <li> <a href="/conversation/{}"> {} - Status: {} - Date created: {} </a></li>
            '''.format(conv["conv_id"], conv["conv_id"], conv["status"], conv["time"])
        responce += '''
        <h3> History of tickets: </h3>
        <ul> {} </ul>
        '''.format(html_answered_conversations)

    if user_type == "admin":
        opened_conversations = Database().get_all_convs_by_receiver("")
        html_open_conversations = ""
        for conv in opened_conversations:
            html_open_conversations += '''
            <li> <a href="/conversation/{}"> {} - Status: {} - Date created: {} </a></li>
            '''.format(conv["conv_id"], conv["conv_id"], conv["status"], conv["time"])
        responce += '''
        <h3> Open tickets: </h3>
        <ul> {} </ul>
        '''.format(html_open_conversations)

    return responce
