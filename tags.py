import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

class TagManager:
    def __init__(self, song_dir, path):
        self.path = path
        self.regularObject = MP3(f"{song_dir}{self.path}", ID3=EasyID3)
        self.coverObject = MP3(song_dir + self.path)
        self.title = self.getTitle()
        self.artist = self.getArtist()
        self.coverData = self.getCover()
        self.length = self.getLength()

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
        if not coverData:
            coverData = self.coverObject.get(f"APIC:Cover of {self.getTitle()} by {self.getArtist()}")
            if not coverData:
                return open("images/placeholder.png", "br").read()
        else:
            return coverData.data

    def getLength(self):
        try:
            length = self.regularObject.info.length
            return length
        except:
            raise Exception("Corrupt Metadata in " + self.path)