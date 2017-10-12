# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 01:33:51 2017

@author: Shiangyoung
"""
from tkinter import *
import tkinter as tk
from tkinter import filedialog
import os

def browse_file():
    fname = filedialog.askopenfilename()
    fileE.config(state='normal')
    nextB.config(state='normal')
    fileE.insert('0',fname)
    print(fname)
    
def close_window():
    roots.destroy()

roots = Tk()
roots.title('Browse File')
instruction = Label(roots,text="Please select a file:")
instruction.grid(row=0,column=0,padx=(4,0),pady=(6,0),sticky=W)

fileE = Entry(roots,width=50,bg="white")
fileE.config(state='disabled')
fileE.grid(row=1,column=0,padx=(6,3),pady=(5,5),columnspan=3)

fileB = Button(roots,text="Browse...",command=browse_file,height = 1,width=10)
fileB.grid(row=1,column=4,padx=(4,6))

nextB = Button(roots,text="Next",width=10)
nextB.config(state='disabled')
nextB.grid(row=2,column=2,sticky=E,pady=(20,5),padx=(0,5))

cancelB = Button(roots,text="Cancel",width=10,command=close_window)
cancelB.grid(row=2,column=4,sticky=W,pady=(20,5),padx=(4,6))

roots.mainloop()

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        instruction = Label(self,text="Please select a file:")
        instruction.grid(row=0,column=0,padx=(4,0),pady=(6,0),sticky=W)
        
        self.fileE = Entry(self,width=50,bg="white")
        self.fileE.config(state='disabled')
        self.fileE.grid(row=1,column=0,padx=(6,3),pady=(5,5),columnspan=3)
        
        fileB = Button(self,text="Browse...",command=self.browse_file,height = 1,width=10)
        fileB.grid(row=1,column=4,padx=(4,6))
        
        self.nextB = Button(self,text="Next",width=10)
        self.nextB.config(state='disabled')
        self.nextB.grid(row=2,column=2,sticky=E,pady=(20,5),padx=(0,5))
        
        cancelB = Button(self,text="Quit",width=10,command=self.close_window)
        cancelB.grid(row=2,column=4,sticky=W,pady=(20,5),padx=(4,6))
        
    def browse_file(self):
        fname = filedialog.askopenfilename()
        self.fileE.config(state='normal')
        self.nextB.config(state='normal')
        self.fileE.delete('0',END)
        self.fileE.insert('0',fname)
        print(fname)
        
    def close_window(self):
        self.destroy()
    