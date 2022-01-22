import os
import re
from multiprocessing import Process
import time
from yt_dlp import YoutubeDL
import ffmpeg
from .Hololive import Hololive


class Record(Process):
    def __init__(self, url):
        super(Record, self).__init__()
        self.url = url

    def run(self):
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'live_from_start': True,
            "outtmpl": "./video/%(id)s",
            "quiet": True
        }

        ydl = YoutubeDL(ydl_opts)
        ydl.download([self.url])


class Background:

    def __init__(self):
        self.waiting = []
        self.recording = []
        self.process = []

    def delete_after_merge(self, video_id):
        for (_, _, files) in os.walk('./video'):
            for file in files:
                if video_id in file:
                    if file.endswith('.part') or file.endswith('.ytdl'):
                        os.remove('./video/' + file)

    def merge(self, video_id, video_title):
        for (_, _, files) in os.walk('./video'):
            for file in files:
                if video_id in file:
                    if file.endswith('.f299.mp4.part'):
                        video = ffmpeg.input('./video/' + file)
                    elif file.endswith('.f140.mp4.part'):
                        audio = ffmpeg.input('./video/' + file)

        video_title = re.sub(r'[\\/*?:"<>|]', '_', video_title)

        (
            ffmpeg
            .output(video, audio, './video/%s.mp4' % video_title, codec='copy')
            .global_args('-loglevel', 'quiet')
            .run()
        )

        self.delete_after_merge(video_id.replace('.mp4', ''))

    def loop(self):

        holo = Hololive()

        while True:

            holo.update()
            holo.filter()
            dummy_list = [d.id for d in self.waiting + self.recording]
            for stream in holo.filtered_streams:
                if stream.id not in dummy_list:
                    self.waiting.append(stream)

            print("\nWait list: ", self.waiting)

            for stream in self.waiting[:]:
                if stream.is_live():
                    print("\nkick_start", stream.title, stream.url)
                    process = Record(url=stream.url)
                    process.name = stream.id
                    process.start()
                    self.process.append(process)
                    self.recording.append(stream)
                    self.waiting.remove(stream)

            time.sleep(10)

            print("\nRecord list: ", self.recording)

            for stream in self.recording[:]:
                if not stream.is_live():
                    print("\nKilling: ", stream.title, stream.url)
                    for process in self.process:
                        if process.name == stream.id:
                            process.kill()
                            process.join()
                            self.process.remove(process)
                            time.sleep(5)
                    print("\nMerging: ", stream.title, stream.url)
                    self.merge(stream.id, stream.title)
                    self.recording.remove(stream)

            if not self.waiting and not self.recording:
                break

            time.sleep(120)
