import os
import re
from multiprocessing import Process
import time
from yt_dlp import YoutubeDL
import ffmpeg
from .Hololive import Hololive


class Record(Process):

    """
    A class being responsible for recording the stream, inheriting multiprocess.Process.
    One record process is target at one stream only.
    Multiple processes have to be called in order to parallel-record multiple streams at a time.
    The number of process that can be run depends on the number of CPU.
    """
    # TODO: Fix the messy terminal by introducing Lock(). https://docs.python.org/3.7/library/multiprocessing.html#synchronization-between-processes
    def __init__(self, url):
        super(Record, self).__init__()
        self.url = url

    def run(self):
        """
        ydl_opts lists the configuration for YoutubeDL object.
        The downloaded files will not be merged, and it is a known issue for yt-dlp.
        The merging process will be done by the Background class instead.
        The terminal may get a little messy even though quiet is set to be True.
        This issue arises from the live_from_start option.
        Further configuration can be found on https://github.com/yt-dlp/yt-dlp.
        :return: None
        """
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'live_from_start': True,
            "outtmpl": "./video/%(id)s",
            "quiet": True
        }

        ydl = YoutubeDL(ydl_opts)
        ydl.download([self.url])


class Background:

    """
    A class responsible for managing the record process and the files merging process.
    """

    def __init__(self):
        """
        Initialise three queues.
        """
        self.waiting = []
        self.recording = []
        self.process = []

    def delete_after_merge(self, video_id):
        """
        Delete all unnecessary files after merging like the .part and .ytdl files,
        leaving just the .mp4 files.
        :param video_id: video id on YouTube and an identifier for downloaded files
        :return: None
        """
        for (_, _, files) in os.walk('./video'):
            for file in files:
                if video_id in file:
                    if file.endswith('.part') or file.endswith('.ytdl'):
                        os.remove('./video/' + file)

    def merge(self, video_id, video_title):
        """
        Merge the .part files together to output a .mp4 file.
        :param video_id: video id on YouTube and an identifier for downloaded files
        :param video_title: video title on YouTube and is used to rename to output
        :return:
        """
        if os.path.isfile('./video/%s.f299.mp4.part' % video_id):
            video = ffmpeg.input('./video/%s.f299.mp4.part' % video_id)
        else:
            video = ffmpeg.input('./video/%s.f137.mp4.part' % video_id)

        audio = ffmpeg.input('./video/%s.f140.mp4.part' % video_id)

        # Replace any illegal characters for file name.
        video_title = re.sub(r'[\\/*?:"<>|]', '_', video_title)

        (
            ffmpeg
            .output(video, audio, './video/%s.mp4' % video_title, codec='copy')
            .global_args('-loglevel', 'quiet')
            .run()
        )

        self.delete_after_merge(video_id.replace('.mp4', ''))

    def loop(self):
        """
        Loop the whole program until the waiting queue and the recording queue is empty.
        Check the stream's condition time by time.
        :return: None
        """
        holo = Hololive()

        while True:

            # Append any new stream to the waiting list
            holo.update()
            holo.filter()
            dummy_list = [d.id for d in self.waiting + self.recording]
            for stream in holo.filtered_streams:
                if stream.id not in dummy_list:
                    self.waiting.append(stream)

            print("\nWait list: ", self.waiting)

            # Kick-start the recording process when a stream goes live
            for stream in self.waiting[:]:
                if stream.is_live():
                    print("\nkick-start", stream.title, stream.url)
                    process = Record(url=stream.url)
                    process.name = stream.id
                    process.start()
                    self.process.append(process)
                    self.recording.append(stream)
                    self.waiting.remove(stream)

            time.sleep(10)

            print("\nRecord list: ", self.recording)

            # Stop the recording process if the stream goes down
            for stream in self.recording[:]:
                if not stream.is_live():
                    stream.stop_count += 1
                    if stream.stop_count == 2:
                        print("\nStopping: ", stream.title, stream.url)
                        # Find the corresponding process
                        for process in self.process:
                            if process.name == stream.id:
                                process.kill()
                                process.join()
                                self.process.remove(process)
                                time.sleep(20)
                        print("\nMerging: ", stream.title, stream.url)
                        self.merge(stream.id, stream.title)
                        self.recording.remove(stream)

            if not self.waiting and not self.recording:
                break

            time.sleep(120)
