# Hololive Recorder
Sometimes there maybe unarchived streams that you would like to watch. But due to timezone difference, you could not afford burning the midnight oil. 
And thus, this program will help you record the stream and let you watch it later.

This program mainly uses the `yt-dlp` package on [GitHub](https://github.com/yt-dlp/yt-dlp) and the multiprocess to allow multiple recordings at a time.

Should this infringe any copyright, this responsitory will be immediately deleted.

# Library Required
1. `pip install yt-dlp`
2. `pip install ffmpeg-python`
3. `pip install requests`

# Timezone
Please specifiy your own timezone at `./src/CONFIG.py`. The timezone input is GMT+X, where X is your local timezone. For example, `TIMEZONE = 8` represents GMT+8.

# Filtering
It supports two types of filtering, which are by streamer and by title. All keywords should be placed in `name_keywords.txt` and `title_keywords.txt`, one keyword per line. 
The `hololive_name.txt` provides all the example for you to copy and pasted into 'name_keywords.txt'. 
Unicode characters are supported, that means you can select English, Japanese, etc.

# GOOGLE API KEY
If you prefer to get information using GOOGLE API for a sightly faster performance, 
please go ahead and create one at `Google Cloud Platform` and paste the key at `./src/CONFIG.py`.

# Output
All output will be present in the `./video` folder.

