import os
import tkinter as tk
import tkinter.font as tkFont

from tkinter import *
#from PIL import ImageTk, Image
from tkinter import filedialog

import customtkinter as cTK



class App:
    def __init__(self, root):
        #setting title
        root.title("ConcanteM8er")
        #setting window size
        width=500
        height=250
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        GLabel_230=tk.Label(root)
        ft = tkFont.Font(family='Arial',size=22)
        GLabel_230["font"] = ft
        GLabel_230["fg"] = "#333333"
        GLabel_230["justify"] = "center"
        GLabel_230["text"] = "ConcateM8er"
        GLabel_230.place(x=50,y=10,width=155,height=55)

        GButton_334=tk.Button(root)
        GButton_334["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Arial',size=10)
        GButton_334["font"] = ft
        GButton_334["fg"] = "#000000"
        GButton_334["justify"] = "center"
        GButton_334["text"] = "Exit"
        GButton_334.place(x=420,y=210,width=70,height=25)
        GButton_334["command"] = self.GButton_334_command

        GButton_123=tk.Button(root)
        GButton_123["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Arial',size=10)
        GButton_123["font"] = ft
        GButton_123["fg"] = "#000000"
        GButton_123["justify"] = "center"
        GButton_123["text"] = "Select Audio Files"
        GButton_123.place(x=120,y=160,width=120,height=25)
        GButton_123["command"] = self.GButton_123_command

        GButton_482=tk.Button(root)
        GButton_482["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Arial',size=10)
        GButton_482["font"] = ft
        GButton_482["fg"] = "#000000"
        GButton_482["justify"] = "center"
        GButton_482["text"] = "Concetenate"
        GButton_482.place(x=270,y=160,width=100,height=25)
        GButton_482["command"] = self.GButton_482_command

        GMessage_198=tk.Message(root)
        ft = tkFont.Font(family='Arial',size=10)
        GMessage_198["font"] = ft
        GMessage_198["fg"] = "#333333"
        GMessage_198["justify"] = "center"
        GMessage_198["text"] = "Message"
        GMessage_198.place(x=340,y=50,width=80,height=25)

        GLabel_705=tk.Label(root)
        ft = tkFont.Font(family='Arial',size=10)
        GLabel_705["font"] = ft
        GLabel_705["fg"] = "#333333"
        GLabel_705["justify"] = "center"
        GLabel_705["text"] = "Sliced Kit Maker"
        GLabel_705.place(x=20,y=50,width=154,height=30)

    def GButton_334_command(self):
        print("Exit")


    def GButton_123_command(self):
        print("Select_Files")


    def GButton_482_command(self):
        print("Do_it")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
