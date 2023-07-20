import tkinter as tk
from typing import Callable, Type

# フレームを切り替えるクラス
class FrameSwitcher:
    def __init__(self, parent):
        self.parent = parent
        self.current_frame: tk.Frame = None

    def switchTo(self, frame: tk.Frame):
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = frame
        self.current_frame.pack()


class Frame1(tk.Frame):
    def __init__(self, switcher: FrameSwitcher):
        # tk.Frameの__init__を呼び出す。これによりFrameが生成される
        super().__init__(switcher.parent)

        def onChangeFrameButton():
            # Frame2クラスが生成するFrameに遷移する
            switcher.switchTo(Frame2(switcher))

        # 自分自身のFrameにWidgetを追加
        tk.Label(self, text="Frame1").pack()
        tk.Button(self, text="button1").pack()
        tk.Button(self, text="go to Frame2",
                  command=onChangeFrameButton).pack()


class Frame2(tk.Frame):
    def __init__(self, switcher: FrameSwitcher):
        super().__init__(switcher.parent)

        def onChangeFrameButton():
            switcher.switchTo(Frame1(switcher))

        tk.Label(self, text="Frame2").pack()
        tk.Button(self, text="go to Frame1",
                  command=onChangeFrameButton).pack()


window = tk.Tk()
window.title("change_frame")

switcher = FrameSwitcher(window)
switcher.switchTo(Frame1(switcher)) #最初に表示するフレームを指定

window.mainloop()
