#! /usr/bin/python
# -*- coding: utf-8 -*-

#
# tkinter example for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#
"""
A simple example for VLC python bindings using tkinter. Uses python 3.4

Author: Patrick Fay
Date: 23-09-2015
"""

# import external libraries
import vlc
import sys

if sys.version_info[0] < 3:
    import Tkinter as tk
    import ttk
    from tkFileDialog import askopenfilename
else:
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename

# import standard libraries
import os
import pathlib
from threading import Timer,Thread,Event
from PIL import Image,ImageTk,ImageFile,ImageFont,ImageDraw
import time
import platform

class ttkTimer(Thread):
    """a class serving same function as wxTimer... but there may be better ways to do this
    """
    def __init__(self, callback, tick):
        Thread.__init__(self)
        self.callback = callback
        #print("callback= ", callback())
        self.stopFlag = Event()
        self.tick = tick
        self.iters = 0

    def run(self):
        while not self.stopFlag.wait(self.tick):
            self.iters += 1
            self.callback()
            #print("ttkTimer start")

    def stop(self):
        self.stopFlag.set()

    def get(self):
        return self.iters

# def doit():
#    print("hey dude")

# code to demo ttkTimer
#t = ttkTimer(doit, 1.0)
#t.start()
#time.sleep(5)
#print("t.get= ", t.get())
#t.stop()
#print("timer should be stopped now")

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=False)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Player,StartPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
            

        self.show_frame("StartPage")
        
    def get_page(self, page_class):
        return self.frames[page_class]

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        
    def stop_all(self):
        
        #if x in locals() or x in globals():
        print("coming soon")
        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        bottom = tk.Frame(self)
        
        button1 = tk.Button(self, text="Video",width=19,command=lambda: controller.show_frame("Player"))
        button2 = tk.Button(self, text="Webcam",width=19)
        button3 = tk.Button(self, text="Quit",width=19)
        
        button1.pack(in_=bottom,side=tk.LEFT)
        button2.pack(in_=bottom,side=tk.LEFT)
        button3.pack(in_=bottom,side=tk.LEFT)
        
        bottom.pack(fill=tk.BOTH,side=tk.BOTTOM,expand=False,padx=1)
        
class Player(tk.Frame):
    """The main window has to deal with events.
    """        
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
   
        self.parent = parent
        self.controller = controller    

        # The second panel holds controls
        self.player = None
        self.videopanel = tk.Frame(self)
        self.canvas = tk.Canvas(self.videopanel).pack(fill=tk.BOTH,expand=1)
        self.videopanel.pack(fill=tk.BOTH,expand=1)

        ctrlpanel = tk.Frame(self)
        pause  = tk.Button(ctrlpanel, text="Pause", command=self.OnPause)
        play   = tk.Button(ctrlpanel, text="Play", command=self.OnPlay)
        stop   = tk.Button(ctrlpanel, text="Stop", command=self.OnStop)
        volume = tk.Button(ctrlpanel, text="Volume", command=self.OnSetVolume)
        pause.pack(side=tk.LEFT)
        play.pack(side=tk.LEFT)
        stop.pack(side=tk.LEFT)
        volume.pack(side=tk.LEFT)
        self.volume_var = tk.IntVar()
        self.volslider = tk.Scale(ctrlpanel, variable=self.volume_var, command=self.volume_sel,
                from_=0, to=100, orient=tk.HORIZONTAL, length=100)
        self.volslider.pack(side=tk.LEFT)
        ctrlpanel.pack(side=tk.BOTTOM)

        ctrlpanel2 = tk.Frame(self)
        self.scale_var = tk.DoubleVar()
        self.timeslider_last_val = ""
        self.timeslider = tk.Scale(ctrlpanel2, variable=self.scale_var, command=self.scale_sel,
                from_=0, to=1000, orient=tk.HORIZONTAL, length=500)
        self.timeslider.pack(side=tk.BOTTOM, fill=tk.X,expand=1)
        self.timeslider_last_update = time.time()
        ctrlpanel2.pack(side=tk.BOTTOM,fill=tk.X)


        # VLC player controls
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        # below is a test, now use the File->Open file menu
#        media = self.Instance.media_new('video2.avi')
#        self.player.set_media(media)
#        self.player.play() # hit the player button

        #self.player.video_set_deinterlace(str_to_bytes('yadif'))

        self.timer = ttkTimer(self.OnTimer, 1.0)
        self.timer.start()
        self.parent.update()

        #self.player.set_hwnd(self.GetHandle()) # for windows, OnOpen does does this

    def OnExit(self, evt):
        """Closes the window.
        """
        self.Close()

    def OnOpen(self):
        """Pop up a new dialow window to choose a file, then play the selected file.
        """
        # if a file is already running, then stop it.
        #self.OnStop()

        # Create a file dialog opened in the current home directory, where
        # you can display all kind of files, having as title "Choose a file".
        p = pathlib.Path(os.path.expanduser("~"))
        #fullname =  askopenfilename(initialdir = p, title = "choose your file",filetypes = (("all files","*.*"),("mp4 files","*.mp4")))
        fullname = "/home/shiangyoung/Desktop/Badminton/video2.avi"
        if os.path.isfile(fullname):
            print (fullname)
            splt = os.path.split(fullname)
            dirname  = os.path.dirname(fullname)
            filename = os.path.basename(fullname)
            # Creation
            self.Media = self.Instance.media_new(str(os.path.join(dirname, filename)))
            self.player.set_media(self.Media)
            # Report the title of the file chosen
            #title = self.player.get_title()
            #  if an error was encountred while retriving the title, then use
            #  filename
            #if title == -1:
            #    title = filename
            #self.SetTitle("%s - tkVLCplayer" % title)

            # set the window id where to render VLC's video output
            if platform.system() == 'Windows':
                self.player.set_hwnd(self.GetHandle())
            else:
                self.player.set_xwindow(self.GetHandle()) # this line messes up windows
            # FIXME: this should be made cross-platform
            self.OnPlay()

            # set the volume slider to the current volume
            #self.volslider.SetValue(self.player.audio_get_volume() / 2)
            self.volslider.set(self.player.audio_get_volume())

    def OnPlay(self):
        """Toggle the status to Play/Pause.
        If no file is loaded, open the dialog window.
        """
        # check if there is a file to play, otherwise open a
        # Tk.FileDialog to select a file
        if not self.player.get_media():
            self.OnOpen()
        else:
            # Try to launch the media, if this fails display an error message
            if self.player.play() == -1:
                self.errorDialog("Unable to play.")

    def GetHandle(self):
        return self.videopanel.winfo_id()

    #def OnPause(self, evt):
    def OnPause(self):
        """Pause the player.
        """
        self.player.pause()

    def OnStop(self):
        """Stop the player.
        """
        self.player.stop()
        # reset the time slider
        self.timeslider.set(0)

    def OnTimer(self):
        """Update the time slider according to the current movie time.
        """
        if self.player == None:
            return
        # since the self.player.get_length can change while playing,
        # re-set the timeslider to the correct range.
        length = self.player.get_length()
        dbl = length * 0.001
        self.timeslider.config(to=dbl)

        # update the time on the slider
        tyme = self.player.get_time()
        if tyme == -1:
            tyme = 0
        dbl = tyme * 0.001
        self.timeslider_last_val = ("%.0f" % dbl) + ".0"
        # don't want to programatically change slider while user is messing with it.
        # wait 2 seconds after user lets go of slider
        if time.time() > (self.timeslider_last_update + 2.0):
            self.timeslider.set(dbl)

    def scale_sel(self, evt):
        if self.player == None:
            return
        nval = self.scale_var.get()
        sval = str(nval)
        if self.timeslider_last_val != sval:
            # this is a hack. The timer updates the time slider.
            # This change causes this rtn (the 'slider has changed' rtn) to be invoked.
            # I can't tell the difference between when the user has manually moved the slider and when
            # the timer changed the slider. But when the user moves the slider tkinter only notifies
            # this rtn about once per second and when the slider has quit moving.
            # Also, the tkinter notification value has no fractional seconds.
            # The timer update rtn saves off the last update value (rounded to integer seconds) in timeslider_last_val
            # if the notification time (sval) is the same as the last saved time timeslider_last_val then
            # we know that this notification is due to the timer changing the slider.
            # otherwise the notification is due to the user changing the slider.
            # if the user is changing the slider then I have the timer routine wait for at least
            # 2 seconds before it starts updating the slider again (so the timer doesn't start fighting with the
            # user)
            #selection = "Value, last = " + sval + " " + str(self.timeslider_last_val)
            #print("selection= ", selection)
            self.timeslider_last_update = time.time()
            mval = "%.0f" % (nval * 1000)
            self.player.set_time(int(mval)) # expects milliseconds


    def volume_sel(self, evt):
        if self.player == None:
            return
        volume = self.volume_var.get()
        if volume > 100:
            volume = 100
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")



    def OnToggleVolume(self, evt):
        """Mute/Unmute according to the audio button.
        """
        is_mute = self.player.audio_get_mute()

        self.player.audio_set_mute(not is_mute)
        # update the volume slider;
        # since vlc volume range is in [0, 200],
        # and our volume slider has range [0, 100], just divide by 2.
        self.volume_var.set(self.player.audio_get_volume())

    def OnSetVolume(self):
        """Set the volume according to the volume sider.
        """
        volume = self.volume_var.get()
        print("volume= ", volume)
        #volume = self.volslider.get() * 2
        # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
        if volume > 100:
            volume = 100
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")

    def errorDialog(self, errormessage):
        """Display a simple error dialog.
        """
        edialog = tk.tkMessageBox.showerror(self, 'Error', errormessage)

def Tk_get_root():
    if not hasattr(Tk_get_root, "root"): #(1)
        Tk_get_root.root= tk.Tk()  #initialization call is inside the function
    return Tk_get_root.root
       
def _quit():
    print("_quit: bye")
    root = Tk_get_root()
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    os._exit(1)

if __name__ == "__main__":
    # Create a Tk.App(), which handles the windowing system event loop

    playerApp = SampleApp()
    # show the player window centred and run the application
    playerApp.mainloop()
    
