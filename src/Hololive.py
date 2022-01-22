import requests
import re
from .CONFIG import TIMEZONE
from .Stream import Stream


class Hololive:

    """
    A class responsible for web scrapping from HoloLive Schedule webpage.
    Specified timezone can be modified in CONFIG.py.
    """

    hololive_url = 'https://schedule.hololive.tv/simple'
    # TODO: Change scarping by api. https://github.com/krichbanana/ytc-autodownloader/issues/1

    def __init__(self):
        self.page_resources = None
        self.streams = []
        self.filtered_streams = []

    def scrape_raw(self):
        """
        Scrape the schedule webpage and trim a little bit first.
        :return: None
        """
        self.page_resources = requests.get(self.hololive_url, cookies=TIMEZONE)
        self.page_resources = self.page_resources.text.split('\n')
        self.page_resources = [i.replace(" ", "").replace("\r", "") for i in self.page_resources]
        body_index = self.page_resources.index('<divclass="holodulenavbar-text"style="letter-spacing:0.3em;">')
        self.page_resources = self.page_resources[body_index:]

    @staticmethod
    def get_title_keywords():
        f = open('./title_keywords.txt', 'r', encoding='utf-8')
        return f.read().splitlines()

    @staticmethod
    def get_name_keywords():
        f = open('./name_keywords.txt', 'r', encoding='utf-8')
        return f.read().splitlines()

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

    def update(self):
        """
        Get un-filtered list of streams on YouTube, Twitch, radio station, etc.
        :return: None. self.streams is modified.
        """
        self.scrape_raw()
        f = open('./hololive_name.txt', 'r', encoding='utf-8')
        name_list = f.read().splitlines()
        regex_pair = {'date': r'^(0[1-9]|1[0-2])\/(0[1-9]|1\d|2\d|3[01])$',
                      'weekday': r'\([\u0080-\uFFFF]\)',
                      'time': r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$',
                      'url': r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])'}

        date = None
        _time = None
        url = None
        date_time = None

        # Loop through the page resources to find our targeted information
        for s in self.page_resources:

            for k, v in regex_pair.items():

                dummy = re.search(v, s)
                if dummy:

                    if k == 'date':
                        date = dummy.group()

                    elif k == 'time':
                        _time = dummy.group()
                        date_time = date + " " + _time

                    elif k == 'url':
                        url = dummy.group()

            if s in name_list:
                streamer = s
                # Check whether there's a duplicate before creating a Stream object.
                # This minimizes the number of requests call.
                if not self.duplicate_stream(url):
                    stream = Stream(start_time=date_time,
                                    streamer=streamer,
                                    url=url)
                    # print(stream)
                    self.streams.append(stream)

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
