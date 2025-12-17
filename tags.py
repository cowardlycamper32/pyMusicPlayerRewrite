import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import ffmpeg
import string

class TagManager:
    def __init__(self, song_dir, path):
        self.path = path
        self.songDir = song_dir
        self.regularObject = MP3(f"{song_dir}{self.path}", ID3=EasyID3)
        self.coverObject = MP3(song_dir + self.path)
        self.title = self.getTitle()
        self.artist = self.getArtist()
        self.coverData = self.getCover()
        self.length = self.getLength()
        print(self.coverObject.keys())

    def getTitle(self):
        title = self.regularObject.get("title")
        if not title:
            return self.path
        else:
            return title[0]

    def getArtist(self):
        artist = self.regularObject.get("artist")
        if not artist:
            return "Unknown Artist"
        else:
            return artist[0]

    def getCover(self):
        coverData = self.coverObject.get("APIC:Cover")
        if coverData is None:
            getString = f"APIC:Cover of {self.getTitle()} by {self.getArtist()}"
            getString = self.parseSpecialChars(getString)
            print(getString)
            coverData = self.coverObject.get(getString)
            print(coverData)
            if not coverData:
                return open("images/placeholder.png", "br").read()
            else:
                return coverData.data
        else:
            return coverData.data

    def getLength(self):
        try:
            length = self.regularObject.info.length
            if not length:
                print(f"File {self.path} has no length metadata, falling back to ffmpeg")
                probe = ffmpeg.probe(f"{self.songDir}{self.path}")
                stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
                length = int(float(stream['duration']))
                print(f"ffmpeg read file as {length}")
            return length
        except Exception as e:
            print(e)
            raise Exception("Corrupt Metadata in " + self.path)

    def printAllMetadata(self, toFile=False, filePath=None):
        if toFile:
            if not filePath:
                raise AttributeError("missing filePath arg")
            file = open("metadata.txt", "w+")
            file.write(self.regularObject.tags)
            file.close()
        else:
            print(self.regularObject.tags)
            print(self.regularObject.info.length)

    def parseSpecialChars(self, inputString):
        inputString = inputString.replace("’", "\\x19")
        #print(inputString)
        return inputString
