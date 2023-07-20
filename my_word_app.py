import tkinter as tk
from WindowA_View import View

class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("My単語帳（仮）")
        self.window.geometry("300x300")

        

        View(self.window)

    def run(self):
        self.window.mainloop()

App().run()