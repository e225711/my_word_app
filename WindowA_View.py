import tkinter as tk

class View:
    def __init__(self, window: tk.Tk):
        label_frame = tk.Frame(window)
        self.display_label = tk.Label(label_frame, text="ジャンル")
        self.display_label.pack()
        label_frame.pack()
        botton_frame = tk.Frame(window)
        self.plus_button = tk.Button(botton_frame, text="＋", command=self.on_button_click)
        self.plus_button.pack()
        botton_frame.pack(side=tk.RIGHT, anchor=tk.NE)

    def on_button_click():
        print("ボタンがクリックされました")
                                  
    