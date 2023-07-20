from __future__ import annotations
import tkinter as tk
from typing import Type
from dataclasses import dataclass

@dataclass
class Item:
    name: str
    price: int

class Model:
    """
    モデルクラス : Itemのリストの保持、取得、追加の機能を持つ
    """
    def __init__(self):
        self.items: list[Item] = [Item("コーラ", 170), Item("コーヒー", 120)]

    def getItems(self) -> list[Item]:
        return self.items

    def addItem(self, item: Item):
        self.items.append(item)


class FrameSwitcher:
    def __init__(self, parent, model):
        self.parent = parent
        self.current_frame: tk.Frame = None
        self.model = model

    def switchTo(self, new_frame: Type[tk.Frame]):
        if self.current_frame is not None:
            self.current_frame.destroy()

        frame = new_frame(self, model)
        self.current_frame = frame
        self.current_frame.pack()


class ShowInYenView(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model):
        super().__init__(switcher.parent)

        tk.Label(self, text="**Items**").pack()

        for item in model.getItems():
            tk.Label(self, text=f"{item.name} {item.price}円").pack()

        tk.Button(self, text="Show in US Dollars",
                command=lambda: switcher.switchTo(ShowInDollersView)).pack()
        tk.Button(self, text="商品を追加",
                command=lambda: switcher.switchTo(Editer)).pack()


class ShowInDollersView(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model):
        super().__init__(switcher.parent)

        tk.Label(self, text="**Items in US Dollars**").pack()

        for item in model.getItems():
            tk.Label(self, text=f"{item.name} ${item.price / 100}").pack()

        tk.Button(self, text="円で表示",
                command=lambda: switcher.switchTo(ShowInYenView)).pack()


class Editer(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model):
        super().__init__(switcher.parent)

        tk.Label(self, text="商品名").pack()
        name_entry = tk.Entry(self, fg='gray', bg="white")
        name_entry.pack()
        tk.Label(self, text="価格").pack()
        price_entry = tk.Entry(self)
        price_entry.insert(0, "0")
        price_entry.pack()

        self.update()

        def addItems():
            name = name_entry.get()

            try:
                price = int(price_entry.get())
            except ValueError as e:
                print(e)

            model.addItem(Item(name, price))
            switcher.switchTo(ShowInYenView)

        tk.Button(self, text="追加", command=addItems).pack()


window = tk.Tk()
window.geometry("300x300")
window.title("change_frame")

model = Model()
switcher = FrameSwitcher(window, model)
switcher.switchTo(ShowInYenView)

window.mainloop()
