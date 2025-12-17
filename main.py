import os
from operator import index
from tkinter import *
from tkinter import ttk, PhotoImage
import just_playback
from math import ceil
import random
from tags import TagManager
from PIL import Image, ImageTk
from pynput import keyboard

if os.name == 'nt':
    delimiter = '\\'
elif os.name == 'posix':
    delimiter = "/"
else:
    delimiter = "/"

temp = __file__.split(delimiter)
temp.pop(-1)
execDir = ""
for i in temp:
    execDir += i + delimiter
temp = None
root = Tk()
root.config(bg="red")

frm = ttk.Frame(root, padding=10)
IMAGE_DIR = execDir + delimiter + "images"
#SONG_DIR = "/home/nova/Music/"
SONG_DIR = "F:/Music/"
print(IMAGE_DIR)
frm.grid()
volume = ["" ,"", "", "", "", ""]
volumeMuted = ["", "", "", "", "", ""]
isMuted = False
for file in os.listdir(IMAGE_DIR):
    if file.endswith(".png"):
        if "volume" in file and "Muted" not in file:
            temp1 = Image.open(f"{IMAGE_DIR}/{file}")
            temp1.thumbnail((temp1.size[0]/2, temp1.size[1]/2))
            temp = ImageTk.PhotoImage(temp1)
            #print(f"{file} -> {temp}")
            volume[int(file[6])] = temp
        elif "volume" in file and "Muted" in file:
            temp1 = Image.open(f"{IMAGE_DIR}/{file}")
            temp1.thumbnail((temp1.size[0]/2, temp1.size[1]/2))
            volumeMuted[int(file[11])] = temp





class Manager:
    def __init__(self, songs):
        self.actualVolume = 1.0
        self.shuffle = False
        self.pos = 0
        self.originalSongs = songs
        self.songs = self.originalSongs
        self.queueHeader = 0
        self.mixer = self.playSong()
        self.loopPlaylist = False
        self.loopMode = "None"
        self.isDialogOpen = False
        self.currentSong = None
        self.coverImage = PhotoImage("images/placeholder.png")
        self.inputTimer = 0
        self.inputListener = keyboard.Listener(on_press=self.onKeyPress)
        self.currentTime = "0:00"
        self.progressBar = 0
        self.inputListener.start()



    def onKeyPress(self, key):
        if key == keyboard.Key.media_next and self.inputTimer <= 0:
            self.inputTimer = 1
            self.nextSong()
        if key == keyboard.Key.media_previous and self.inputTimer <= 0:
            self.inputTimer = 1
            self.prevSong()
        if key == keyboard.Key.media_play_pause and self.inputTimer <= 0:
            self.inputTimer = 1
            self.pausePlay()
        #print(key)


    def Mute(self):
        global isMuted
        global volumeLabel
        isMuted = not isMuted
        if isMuted:
            self.mixer.set_volume(0.0)
        else:
            self.mixer.set_volume(self.actualVolume)
        self.displayVolume()

    def Shuffle(self):
        self.shuffle = not self.shuffle
        if self.shuffle:
            self.songs = self.originalSongs.copy()
            random.shuffle(self.songs)
            self.queueHeader = 0
            self.songs.remove(self.currentSong)
            self.songs.insert(0, self.currentSong)
        else:
            self.songs = self.originalSongs

    def VolumeUp(self):
        self.actualVolume += 0.1
        self.actualVolume = min(max(self.actualVolume, 0), 1)
        self.mixer.set_volume(self.actualVolume)
        self.displayVolume()

    def displayVolume(self):
        global isMuted
        global volumeLabel
        #print(self.actualVolume)
        if not isMuted:
            #print(self.actualVolume)
            volumeLabel.config(image=volume[int(ceil((self.actualVolume*5)*10)/10)])
        else:
            volumeLabel.config(image=volumeMuted[int(ceil((self.actualVolume*5)*10)/10)])

    def VolumeDown(self):
        global isMuted
        self.actualVolume -= 0.1
        self.actualVolume = min(max(self.actualVolume, 0), 1)
        if not isMuted:
            self.mixer.set_volume(self.actualVolume)
        self.displayVolume()


    def pausePlay(self):
        if self.mixer.paused:
            self.mixer.play()
            self.mixer.seek(self.pos)
        else:
            self.pos = self.mixer.curr_pos
            self.mixer.pause()

    def customQuestionBox(self, *, title, message, button1Text, button2Text, button1command, button2command):
        if not self.isDialogOpen:
            self.isDialogOpen = True
            self.win = Toplevel()
            self.win.title(title)
            self.win.resizable(False, False)
            Label(self.win, text=message).pack()
            Button(self.win, text=button1Text, command=button1command).pack()
            Button(self.win, text=button2Text, command=button2command).pack()
            self.win.focus_force()

    def nextSong(self):
        self.mixer.pause()
        if not self.queueHeader + 1 >= len(self.songs) - 1:
            self.queueHeader += 1
            self.playSong()
        else:
            if self.loopPlaylist:
                self.queueHeader = 0
                self.playSong()
            else:
                self.customQuestionBox(title="Playlist has finished", message="Would you like to restart the playlist?", button1Text="Restart?", button1command=self.restartOnFinished, button2Text="Quit?", button2command=frm.quit)

    def prevSong(self):
        self.mixer.pause()
        if self.mixer.curr_pos > 5:
            self.playSong()
            return
        if not self.queueHeader - 1 < 0:
            self.queueHeader -= 1
        elif self.queueHeader - 1 < 0 and self.loopPlaylist:
            self.queueHeader = len(self.songs) - 1
        else:
            self.queueHeader = 0
        self.playSong()


    def restartOnFinished(self):
        self.queueHeader = 0
        self.playSong()
        self.win.destroy()
        self.isDialogOpen = False


    def playSong(self):
        global SONG_DIR
        self.tagManager = TagManager(SONG_DIR, self.songs[self.queueHeader])
        root.title(f"{self.tagManager.title} - {self.tagManager.artist}")
        self.mixer = just_playback.Playback(f"{SONG_DIR}/{self.songs[self.queueHeader]}")
        self.currentSong = self.songs[self.queueHeader]
        self.mixer.play()
        self.mixer.set_volume(self.actualVolume)
        self.displayCover()
        finishTimeLabel.config(text=self.fixTime(int(self.tagManager.length)))
        songNameLabel.config(text=self.tagManager.title)
        songArtistLabel.config(text=self.tagManager.artist)
        try:
            songProgresBar.step(100-self.percent)
            #print(f"Progress bar stepped {100-self.percent}")
        except AttributeError as e:
            print(e)
        self.percent = 0
        return self.mixer

    def isNotPlaying(self):
        if not self.mixer.active:
            self.nextSong()
        self.inputTimer -= 0.5
        self.getCurrentTime()
        self.displayProgBar()
        frm.after(500, self.isNotPlaying)


    def displayProgBar(self):

        temppercent = 100*(int(self.mixer.curr_pos+1)/self.tagManager.length)
        #print(self.percent)
        songProgresBar.step(temppercent-self.percent)
        #print("progbar stepped: " + str(temppercent-self.percent))
        self.percent = temppercent


    def displayCover(self):
        with open("cover.png", "wb+") as cover:
            if self.tagManager.coverData is not None:
                cover.write(self.tagManager.coverData)
            else:
                cover.write(open("images/placeholder.png", "rb").read())
        global coverDisplayLabel
        placeholderImage = Image.open("cover.png")
        placeholderImage.thumbnail((250, 250))
        placeholderPhotoImage = ImageTk.PhotoImage(placeholderImage)
        #try:
        coverDisplayLabel.image = placeholderPhotoImage
        coverDisplayLabel.config(image=placeholderPhotoImage)
        #except Exception as e:
        #    print("CoverDisplayLabel not created yet")
        #    print(e)

    def fixTime(self, secondsIn):

        seconds = int(secondsIn % 60)
        minutes = int(secondsIn / 60)
        if seconds < 10:
            seconds = "0" + str(seconds)

        return f"{minutes}:{seconds}"
    def getCurrentTime(self):


        #print(self.currentTime)
        currentTimeLabel.config(text=self.fixTime(int(self.mixer.curr_pos)))


    def loopButton(self):
        print("Triggered loop button")
        print(self.loopMode)
        if self.loopMode == "None":
            self.setLoopAll()
        elif self.loopMode == "All":
            self.setLoopSong()
        elif self.loopMode == "Song":
            self.setLoopNone()
        loopButton.config(text=self.loopMode)

    def setLoopAll(self):
        self.loopPlaylist = True
        self.loopMode = "All"

    def setLoopSong(self):
        self.songs = [self.currentSong]
        self.loopPlaylist = True
        self.loopMode = "Song"

    def setLoopNone(self):
        self.loopPlaylist = False
        if self.shuffle:
            self.Shuffle()
        else:
            self.songs = self.originalSongs
            self.queueHeader = self.songs.index(self.currentSong)
            print(f"triggered no loop - shuffle at index {self.queueHeader}")
        self.loopMode = "None"

songs = []

for file in os.listdir(SONG_DIR):
    if file.endswith(".mp3"):
        songs.append(file)

placeholderImage = Image.open("images/placeholder.png")
placeholderPhotoImage = ImageTk.PhotoImage(placeholderImage)
coverDisplayLabel = ttk.Label(frm, image=placeholderPhotoImage)
coverDisplayLabel.grid(row=0, column=4)

currentTimeLabel = ttk.Label(frm)
currentTimeLabel.grid(row=1, column=1)
finishTimeLabel = ttk.Label(frm, text="0:00")
finishTimeLabel.grid(row=1, column=7)

songProgresBar = ttk.Progressbar(frm, orient="horizontal")
songProgresBar.grid(row=1, column=4)

songInfoFrame = ttk.Frame(frm)
songInfoFrame.place(relx=0.5, rely=0.6, anchor="n")

songNameLabel = ttk.Label(songInfoFrame)
songNameLabel.grid(row=1, column=0)

songArtistLabel = ttk.Label(songInfoFrame)
songArtistLabel.grid(row=2, column=0)

#songInfoFrame.pack()


manager = Manager(songs)

volumeLabel = ttk.Label(frm, image=volume[int(manager.mixer.volume*5)])
volumeLabel.grid(row=1, column=0)

muteButton = (ttk.Button(frm, text="Mute", command=manager.Mute))
muteButton.grid(row=3, column=1)
pausePlayButton = ttk.Button(frm, text="pause/play", command=manager.pausePlay)
pausePlayButton.grid(row=3, column=4)
volumeUpButton = ttk.Button(frm, text="Volume Up", command=manager.VolumeUp)
volumeUpButton.grid(row=3, column=2)
volumeDownButton = ttk.Button(frm, text="Volume Down", command=manager.VolumeDown)
volumeDownButton.grid(row=3, column=6)
prevSongButton = ttk.Button(frm, text="Previous song", command=manager.prevSong)
prevSongButton.grid(row=3, column=3)
nextSongButton = ttk.Button(frm, text="Next song", command=manager.nextSong)
nextSongButton.grid(row=3, column=5)
shuffleButton = ttk.Button(frm, text="Shuffle", command=manager.Shuffle)
shuffleButton.grid(row=3, column=7)



loopButton = ttk.Button(frm, text=manager.loopMode, command=manager.loopButton)
loopButton.grid(row=3, column=8)

frm.pack(expand=False, fill="both")







#print(manager.progressBar)

#linux test harcode song
#manager.songs = ["41 - MURDER EVERY 1 U KNOW! (feat. takihasdied).mp3"]
manager.playSong()
#manager.tagManager.printAllMetadata()
frm.after(500, manager.isNotPlaying)
root.mainloop()
