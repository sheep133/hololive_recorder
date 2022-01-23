import requests
import re
from .Stream import Stream


class Hololive:

    """
    A class responsible for web scrapping from HoloLive Schedule webpage.
    Specified timezone can be modified in CONFIG.py.
    """

    hololive_url = 'https://schedule.hololive.tv/simple'

    def __init__(self):
        self.streams = []
        self.filtered_streams = []

    @staticmethod
    def get_title_keywords():
        f = open('./title_keywords.txt', 'r', encoding='utf-8')
        return f.read().splitlines()

    @staticmethod
    def get_name_keywords():
        f = open('./name_keywords.txt', 'r', encoding='utf-8')
        return f.read().splitlines()

    def update(self):
        """
        New scraping method to update the streams by Hololive Schedule API, in light of
        https://github.com/krichbanana/ytc-autodownloader/issues/1.
        :return: None. self.streams is modified
        """
        r = requests.get('https://schedule.hololive.tv/api/list/1').json()
        # print(r)

        for date_group in r.get('dateGroupList'):

            video_list = date_group.get('videoList')

            for video in video_list:

                if not self.duplicate_stream(video.get('url')):

                    # Initialise here in Japan time, will be modified to local time
                    stream = Stream(start_time=video.get('datetime'),
                                    streamer=video.get('name'),
                                    url=video.get('url'),
                                    title=video.get('title'))

                    self.streams.append(stream)

    def filter(self):
        """
        Filter the streams' title or streamer using the keywords specified
        in ./title_keywords.txt and ./name_keywords.txt.
        Then, further filter the streams by checking whether they are upcoming or on live.
        Member limited streams are not included.
        :return: None. self.filtered_streams is modified.
        """
        title_pattern = "|".join(self.get_title_keywords())
        streamer_pattern = "|".join(self.get_name_keywords())

        if not title_pattern:
            self.filtered_streams = [stream for stream in self.streams if re.search(streamer_pattern, stream.streamer, re.IGNORECASE)]
        elif not streamer_pattern:
            self.filtered_streams = [stream for stream in self.streams if re.search(title_pattern, stream.title, re.IGNORECASE)]
        else:
            self.filtered_streams = [stream for stream in self.streams if re.search(streamer_pattern, stream.streamer, re.IGNORECASE) or re.search(title_pattern, stream.title, re.IGNORECASE)]

        self.filtered_streams = [stream for stream in self.filtered_streams if (stream.is_upcoming() or stream.is_live()) and not stream.is_member_only()]

    def duplicate_stream(self, new_url):
        """
        Check whether there's a duplicate by checking the url
        :param new_url: url used for comparison
        :return: Boolean
        """
        for stream in self.streams:
            if stream.url == new_url:
                return True
        return False
