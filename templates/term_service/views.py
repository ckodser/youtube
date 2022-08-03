from database import Database
from templates.utils import http_ok_header, get_account
from templates.utils import get_file_packet
from urllib.parse import unquote_plus


def get_term_service(request_dict):
    with open("templates/term_service/term.html") as f:
        return http_ok_header() + f.read()