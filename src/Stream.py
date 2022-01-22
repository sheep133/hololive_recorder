import re
from urllib.parse import urlparse, parse_qs
import requests
from datetime import datetime
import json
from .CONFIG import GOOGLE_APIKEY


class Stream:

    def __init__(self, start_time, streamer, url):
        self.start_time_str = start_time
        self.start_time_obj = self.start_time_str_to_obj()
        self.streamer = streamer
        self.url = url
        self.title = self.get_title()
        self.id = self.get_id()

    def __repr__(self):
        return json.dumps({'start_time': self.start_time_str,
                           'streamer': self.streamer,
                           'url': self.url,
                           'title': self.title,
                           'id': self.id},
                          indent=4,
                          ensure_ascii=False).encode('utf-8').decode()

    def get_title(self):
        if GOOGLE_APIKEY:
            if self.is_youtube():
                parsed_url = urlparse(self.url)
                video_id = parse_qs(parsed_url.query).get('v')[0]
                r = requests.get("https://www.googleapis.com/youtube/v3/videos",
                                 params={
                                     'part': 'snippet',
                                     'id': video_id,
                                     'key': GOOGLE_APIKEY
                                 })
                if r.status_code == 200:
                    return r.json().get('items')[0].get('snippet').get('title')
        if self.is_youtube():
            r = requests.get('https://noembed.com/embed?url=%s' % self.url)
            return r.json().get('title')
        return ""

    def is_upcoming(self):
        curr_time = datetime.now().replace(second=0, microsecond=0)
        stream_time = datetime.strptime(self.start_time_str, "%m/%d %H:%M").replace(year=curr_time.year)
        if stream_time >= curr_time:
            return True
        return False

    def is_live(self):
        if GOOGLE_APIKEY:
            if self.is_youtube():
                parsed_url = urlparse(self.url)
                video_id = parse_qs(parsed_url.query).get('v')[0]
                r = requests.get("https://www.googleapis.com/youtube/v3/videos",
                                 params={
                                     'part': 'snippet',
                                     'id': video_id,
                                     'key': GOOGLE_APIKEY
                                 })
                if r.status_code == 200:
                    if r.json().get('items')[0].get('snippet').get('liveBroadcastContent') == "live":
                        return True
        if self.is_youtube():
            headers = {"Accept-Language": "en-US"}
            r = requests.get(self.url, headers=headers)
            r = r.content.decode()
            if re.search(r'{"text":" watching now"}', r):
                return True
        return False

    def is_youtube(self):
        return re.search(r'https://www.youtube.com/watch', self.url)

    def get_id(self):
        if self.is_youtube():
            parsed_url = urlparse(self.url)
            return parse_qs(parsed_url.query).get('v')[0]
        return ""

    def start_time_str_to_obj(self):
        return datetime.strptime(self.start_time_str, "%m/%d %H:%M").replace(year=datetime.now().year)

    def is_member_only(self):
        headers = {"Accept-Language": "en-US"}
        r = requests.get(self.url, headers=headers)
        r = r.content.decode()
        if re.search(r'"Members only"', r):
            return True
        return False
