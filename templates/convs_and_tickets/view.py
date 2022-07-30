from database import Database
from templates.utils import http_ok_header, get_account
from templates.error.view import error_page
from urllib.parse import unquote_plus


def func_conversations(request_dict):
    user_info = get_account(request_dict)
    if user_info is None:
        return error_page(request_dict, [])
    print("USERINFO FUNC CONV", user_info)

    user_type = user_info["type"]

    if request_dict["method"] == "POST":
        conv_id = None
        if user_type == "user":
            conv_id = Database().insert_conv({'sender': user_info["username"]})
        elif user_type == "admin":
            conv_id = Database().insert_conv({'sender': user_info["username"], 'receiver': 'manager'})
        Database().insert_ticket({'conv_id': conv_id, 'username': user_info["username"],
                                  'message': unquote_plus(request_dict["body"][len("ticket="):])})

    responce = http_ok_header() + f'''
    <html> <head> <body>
    '''

    if user_type != "manager":
        responce += f'''
        <h1> Create new ticket </h1>
        <form action="/tickets" method="post">
        <textarea rows = "5" cols = "60" name = "ticket">description</textarea>
        <input type="submit" value="Create">
        </form>
        '''
        opened_conversations = Database().get_all_convs_by_sender(user_info["username"])
        html_created_conversations = ""
        for conv in opened_conversations:
            html_created_conversations += '''
            <li> <a href="/conversation/{}"> {} - Status: {} - Date created: {} </a></li>
            '''.format(conv["conv_id"], conv["conv_id"], conv["status"], conv["time"])
        responce += '''
        <h1> Created tickets: </h1>
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
        <h1> History of tickets: </h1>
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
        <h1> Open tickets: </h1>
        <ul> {} </ul>
        '''.format(html_open_conversations)

    responce += f'''
    </body> </head> </html>
    '''
    return responce


def func_ticket(request_dict, conv_id):
    user_info = get_account(request_dict)
    if user_info is None:
        return error_page(request_dict, [])
    print("USERINFO FUNC TICKET", user_info)

    user_type = user_info["type"]
    user_name = user_info["username"]

    conv = Database().get_conv_by_id(conv_id)
    if conv is None or \
            (conv["sender"] != user_name and conv["receiver"] != user_name and
             not (user_type == "admin" and conv["receiver"] == "")):
        return error_page(request_dict, [])

    responce = http_ok_header() + f'''
    <html> <head> <body>
    '''

    tickets = Database().get_tickets_by_conv(conv_id)
    html_tickets = ""
    for ticket in tickets:
        html_tickets += '''
        <li>Date:{} - Username of sender:{}
        <hr>
        <p>
        {}
        </p></li>
        '''.format(ticket["time"], ticket["username"], ticket["message"])

    responce += '''
    <h1> Tickets: </h1>
    <ul> {} </ul>
    </body> </head> </html>
    '''.format(html_tickets)

    return responce
