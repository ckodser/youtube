from database import Database
from templates.utils import http_ok_header


def all_videos(request_dict):
    database = Database()
    videos = database.get_all_videos()
    links = ""
    for video in videos:
        links += '<li> <a href="/video/{}"> {} </a></li>\n'.format(video["video_id"], video["name"])
    with open("templates/video/all_videos.html") as f:
        return http_ok_header() + f.read().replace("{{LIST}}", links)
