import os
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
SONG_DIR = "/home/nova/Music/"
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
        self.isDialogOpen = False
        self.currentSong = None
        self.coverImage = PhotoImage("images/placeholder.png")
        self.inputTimer = 0
        self.inputListener = keyboard.Listener(on_press=self.onKeyPress)
        self.inputListener.start()
        self.currentTime = "0:00"
        self.progBarPercent = 0


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
        songProgresBar.step(100-self.progBarPercent)
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
        print(self.percent)
        songProgresBar.step(temppercent-self.percent)
        print("progbar stepped: " + str(temppercent-self.percent))
        self.percent = temppercent


    def displayCover(self):
        with open("cover.jpeg", "wb+") as cover:
            cover.write(self.tagManager.coverData)
        global coverDisplayLabel
        placeholderImage = Image.open("cover.jpeg")
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

songs = []

for file in os.listdir("/home/nova/Music/"):
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

manager = Manager(songs)

volumeLabel = ttk.Label(frm, image=volume[int(manager.mixer.volume*5)])
volumeLabel.grid(row=1, column=0)

muteButton = (ttk.Button(frm, text="Mute", command=manager.Mute))
muteButton.grid(row=2, column=1)
pausePlayButton = ttk.Button(frm, text="pause/play", command=manager.pausePlay)
pausePlayButton.grid(row=2, column=2)
volumeUpButton = ttk.Button(frm, text="Volume Up", command=manager.VolumeUp)
volumeUpButton.grid(row=2, column=3)
volumeDownButton = ttk.Button(frm, text="Volume Down", command=manager.VolumeDown)
volumeDownButton.grid(row=2, column=4)
prevSongButton = ttk.Button(frm, text="Previous song", command=manager.prevSong)
prevSongButton.grid(row=2, column=5)
nextSongButton = ttk.Button(frm, text="Next song", command=manager.nextSong)
nextSongButton.grid(row=2, column=6)
shuffleButton = ttk.Button(frm, text="Shuffle", command=manager.Shuffle)
shuffleButton.grid(row=2, column=7)







#linux test harcode song
#manager.songs = ["dj-Nate - Final Theory.mp3"]
manager.playSong()
#manager.tagManager.printAllMetadata()
frm.after(500, manager.isNotPlaying)
root.mainloop()