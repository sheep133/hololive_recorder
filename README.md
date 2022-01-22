# Hololive Recorder
Sometimes there maybe unarchived streams that yoy want to watch. But due to timezone difference, you could not afford burning the midnight oil to watch it. 
And thus, this program will help you record the stream and let you watch it later.

This program mainly uses the `yt-dlp` package on [GitHub](https://github.com/yt-dlp/yt-dlp) and the multiprocess to allow multiple recordings at a time.

Should this infringe any copyright, this responsitory will be immediately deleted.

# Filtering
It supports two types of filtering, which are by streamer and by title. All keywords should be placed in `name_keywords.txt` and `title_keywords.txt`, one keyword per line. 
The `hololive_name.txt` provides all the example for you to copy and pasted into 'name_keywords.txt'.

# Output
All output will be present in the `./video` folder.

