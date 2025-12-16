import ffmpeg

probe = ffmpeg.probe("/home/nova/Music/dj-Nate - Final Theory.mp3")
stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
length = float(stream['duration'])

print(length)