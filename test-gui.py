#Created on May 18, 2016

import Tkinter as tk
from PIL import ImageTk, Image

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "click me"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")
        canvas = tk.Canvas(self)
        canvas.grid(row = 0, column = 0)
        photo = tk.PhotoImage(Image.open('/tmp/xx.jpg'))
        #photo = tk.PhotoImage(file='/tmp/xx.png')
        canvas.create_image(0,0, image=photo)

        self.QUIT = tk.Button(self, text="QUIT", fg="red", command=root.destroy)
        self.QUIT.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")


if __name__ == '__main__':

    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()