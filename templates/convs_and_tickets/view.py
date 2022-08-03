from database import Database
from templates.utils import http_ok_header, get_account
from templates.error.view import error_page
from urllib.parse import unquote_plus, parse_qs


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

    response = http_ok_header() + f'''
    <html> <head> <body>
    <a href="/home"> Back to home </a>
    '''

    if user_type != "manager":
        response += f'''
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
        response += '''
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
        response += '''
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
        response += '''
        <h1> Open tickets: </h1>
        <ul> {} </ul>
        '''.format(html_open_conversations)

    response += f'''
    </body> </head> </html>
    '''
    return response


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

    response = http_ok_header() + f'''
    <html> <head> <body>
    <a href="/tickets"> Back to tickets list </a>
    <h3> status:{conv['status']}<h3> 
    '''

    body_dict = parse_qs(request_dict["body"])

    if 'takeTicket' in body_dict:
        Database().update_conv_status(conv_id, "new")
        Database().update_conv_receiver(conv_id, user_name)
        response += f'''
        <h1> Ticket taken </h1>
        '''

    if 'statusClosed' in body_dict:
        Database().update_conv_status(conv_id, "closed")
        response += f'''
        <h1> Ticket closed </h1>
        '''

    if 'newMessage' in body_dict:
        Database().insert_ticket({'conv_id': conv_id, 'username': user_name,
                                  'message': unquote_plus(body_dict["ticket"][0])})
        status = conv['status']
        if user_name == conv["receiver"]:
            status = 'solved'
        if user_name == conv["sender"] and status != 'waiting':
            status = 'new'
        Database().update_conv_status(conv_id, status)
        response += f'''
        <h1> New message added </h1>
        '''

    conv = Database().get_conv_by_id(conv_id)

    if user_type == "admin" and conv['receiver'] == '':
        response += f'''
        <form action="/conversation/{conv_id}" method="post"> <input type="submit" name="takeTicket" value="Take this ticket"> </form>
        '''

    if conv['receiver'] == user_name and conv['status'] != 'closed':
        response += f'''
        <form action="/conversation/{conv_id}" method="post"> <input type="submit" name="statusClosed" value="Change status to Closed"> </form>
        '''

    if user_name in [conv['sender'], conv['receiver']] \
            and conv['status'] != "closed":
        response += f'''
        <h1>New message:</h1>
        <form action="/conversation/{conv_id}" method="post">
        <textarea rows = "5" cols = "60" name = "ticket">description</textarea>
        <input type="submit" name="newMessage" value="Create">
        </form>
        '''

    tickets = Database().get_tickets_by_conv(conv_id)
    html_tickets = ""
    for ticket in tickets:
        html_tickets += '''
        <li>
        <hr>
        <hr>
        Date:{} - Username of sender:{}
        <hr>
        <p>
        {}
        </p></li>
        '''.format(ticket["time"], unquote_plus(ticket["username"]), ticket["message"])

    response += '''
    <h1> Tickets: </h1>
    <ul> {} </ul>
    </body> </head> </html>
    '''.format(html_tickets)

    return response
