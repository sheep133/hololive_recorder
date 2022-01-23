import re
from urllib.parse import urlparse, parse_qs
import requests
import datetime
import json
from .CONFIG import GOOGLE_APIKEY, TIMEZONE


class Stream:

    """
    A class that contains information of one stream.
    Any non-Youtube stream is not supported for recording.
    The get_title() and is_live() method can be carried out
    with or without Google API Key. In case of API quota limit
    or any error, the two methods will resort to another way
    with sightly longer response time.
    Modify your Google API key in CONFIG.py.
    """

    def __init__(self, start_time, streamer, url, title):
        self.start_time_str = start_time
        self.start_time_str_to_local_timezone()
        self.start_time_obj = self.start_time_str_to_obj()
        self.streamer = streamer
        self.url = url
        self.title = title
        self.id = self.get_id()
        self.stop_count = 0  # A count to double-check whether the stream stops. Prevents accidentally stopping the recording.

    def __repr__(self):
        """
        :return: a json-formatted string listing all necessary attributes
        """
        return json.dumps({'start_time': self.start_time_str,
                           'streamer': self.streamer,
                           'url': self.url,
                           'title': self.title,
                           'id': self.id},
                          indent=4,
                          ensure_ascii=False).encode('utf-8').decode()

    def is_upcoming(self):
        """
        Determine if the stream is later than current time
        :return: Boolean
        """
        curr_time = datetime.datetime.now().replace(second=0, microsecond=0)
        if self.start_time_obj >= curr_time:
            return True
        return False

    def is_live(self):
        """
        Check if the stream is live with or without Google API.
        Only support YouTube.
        :return: Boolean
        """
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
        """
        Get stream's id on YouTube.
        :return: Stream's id. Else, empty string.
        """
        if self.is_youtube():
            parsed_url = urlparse(self.url)
            return parse_qs(parsed_url.query).get('v')[0]
        return ""

    def start_time_str_to_local_timezone(self):
        dummy = datetime.datetime.strptime(self.start_time_str, '%Y/%m/%d %H:%M:%S') + datetime.timedelta(hours=TIMEZONE - 9)
        self.start_time_str = datetime.datetime.strftime(dummy, '%Y/%m/%d %H:%M:%S')

    def start_time_str_to_obj(self):
        return datetime.datetime.strptime(self.start_time_str, '%Y/%m/%d %H:%M:%S')

    def is_member_only(self):
        """
        Check whether the stream is limited to member.
        :return: Boolean
        """
        headers = {"Accept-Language": "en-US"}
        r = requests.get(self.url, headers=headers)
        r = r.content.decode()
        if re.search(r'"Members only"', r):
            return True
        return False
