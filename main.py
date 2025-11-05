import os
from tkinter import *
from tkinter import ttk, PhotoImage
import just_playback
from math import ceil

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
frm = ttk.Frame(root, padding=10)
IMAGE_DIR = execDir + delimiter + "images"
SONG_DIR = "F:/Music"
print(IMAGE_DIR)
frm.grid()
volume = []
volumeMuted = []
isMuted = False
for file in os.listdir(IMAGE_DIR):
    if file.endswith(".png"):
        if "volume" in file and "Muted" not in file:
            temp = PhotoImage(file=f"{IMAGE_DIR}/{file}")
            volume.insert(int(file[6]), temp)
        elif "volume" in file and "Muted" in file:
            temp = PhotoImage(file=f"{IMAGE_DIR}/{file}")
            volumeMuted.insert(int(file[11]), temp)





class Manager:
    def __init__(self, songs):
        self.actualVolume = 1.0
        self.pos = 0
        self.songs = songs
        self.queueHeader = 0
        self.mixer = self.playSong()
        self.loopPlaylist = False
        self.isDialogOpen = False
    def Mute(self):
        global isMuted
        global volumeLabel
        isMuted = not isMuted
        if isMuted:
            self.mixer.set_volume(0.0)
        else:
            self.mixer.set_volume(self.actualVolume)
        self.displayVolume()

    def VolumeUp(self):
        self.actualVolume += 0.1
        self.actualVolume = min(max(self.actualVolume, 0), 1)
        self.mixer.set_volume(self.actualVolume)
        self.displayVolume()

    def displayVolume(self):
        global isMuted
        global volumeLabel
        print(self.actualVolume)
        if not isMuted:
            print(self.actualVolume)
            print(ceil(self.actualVolume))
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
        self.mixer = just_playback.Playback(f"{SONG_DIR}/{self.songs[self.queueHeader]}")
        self.mixer.play()
        self.mixer.set_volume(self.actualVolume)
        return self.mixer

    def isNotPlaying(self):
        if not self.mixer.active:
            self.nextSong()
        frm.after(1000, self.isNotPlaying)

songs = []

for file in os.listdir("F:/Music"):
    if file.endswith(".mp3"):
        songs.append(file)



manager = Manager(songs)

volumeLabel = ttk.Label(frm, image=volume[int(manager.mixer.volume*5)])
volumeLabel.grid(row=0, column=0)

muteButton = (ttk.Button(frm, text="Mute", command=manager.Mute))
muteButton.grid(row=0, column=1)
pausePlayButton = ttk.Button(frm, text="pause/play", command=manager.pausePlay)
pausePlayButton.grid(row=0, column=2)
volumeUpButton = ttk.Button(frm, text="Volume Up", command=manager.VolumeUp)
volumeUpButton.grid(row=0, column=3)
volumeDownButton = ttk.Button(frm, text="Volume Down", command=manager.VolumeDown)
volumeDownButton.grid(row=0, column=4)
prevSongButton = ttk.Button(frm, text="Previous song", command=manager.prevSong)
prevSongButton.grid(row=0, column=5)
nextSongButton = ttk.Button(frm, text="Next song", command=manager.nextSong)
nextSongButton.grid(row=0, column=6)
manager.playSong()
frm.after(1000, manager.isNotPlaying)
root.mainloop()