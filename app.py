import sqlite3
import tkinter as tk
from typing import Type

class Model:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()


        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY,
                genre_id INTEGER,
                word TEXT,
                details TEXT,
                confidence BOOLEAN,
                FOREIGN KEY(genre_id) REFERENCES genres(id)
            )
        ''')
        self.connection.commit()

    def add_genre(self, name: str):
        self.cursor.execute('''INSERT INTO genres (name) VALUES (?)''', (name,))
        self.connection.commit()

    def get_genres(self):
        self.cursor.execute('''SELECT * FROM genres''')
        return self.cursor.fetchall()

class FrameSwitcher:
    def __init__(self, parent, model: Model, *args):
        self.parent = parent
        self.current_frame: tk.Frame = None
        self.model = model

    def switchTo(self, frame_class: Type[tk.Frame], *args):
        # 受け取ったクラスを利用してインスタンスを生成
        frame = frame_class(self, self.model, *args)
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)


class StartFrame(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model):
        super().__init__(switcher.parent)
        self.switcher = switcher

        tk.Label(self, text="ジャンル").pack()

        self.plus_button = tk.Button(self, text="＋", command=self.on_plus_button_click)
        self.plus_button.place(relx=1.0, rely=0.0, anchor='ne')

        for genre in model.get_genres():
            tk.Button(self, text=genre[1],command=lambda g=genre: self.on_genre_button_click(g)).pack()

        self.update()

    def on_plus_button_click(self):
        print("plus Button clicked!")
        switcher.switchTo(AddGenreFrame)

    def on_genre_button_click(self, genre: list):
        print("ジャンルButton clicked!")
        switcher.switchTo(WordListFrame, genre)

class AddGenreFrame(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model):
        super().__init__(switcher.parent)
        self.model = model

        # This frame will be used to center the widgets
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(self.center_frame, text="追加するジャンル名").grid(row=0, column=0, columnspan=2, pady=5)
        self.genre_name_entry = tk.Entry(self.center_frame)
        self.genre_name_entry.grid(row=1, column=0, columnspan=2, pady=5)

        self.add_button = tk.Button(self.center_frame, text="完了", command=self.on_add_genre_button_click)
        self.add_button.grid(row=2, column=1, pady=5)

        self.cancel_button = tk.Button(self.center_frame, text="キャンセル", command=self.on_cancel_button_click)
        self.cancel_button.grid(row=2, column=0, pady=5)
        self.update()

    def on_cancel_button_click(self):
        print("キャンセルbutton clicked!")
        switcher.switchTo(StartFrame)

    def on_add_genre_button_click(self):
        print("完了button clicked!")
        genre_name = self.genre_name_entry.get()
        self.model.add_genre(genre_name)

        switcher.switchTo(StartFrame)




class WordListFrame(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list):
        super().__init__(switcher.parent)
        self.genre = genre
        self.model = model
        self.switcher = switcher

        tk.Label(self, text="選んだジャンル名").pack()

        self.plus_button = tk.Button(self, text="＋", command=self.on_plus_button_click)
        self.plus_button.place(relx=1.0, rely=0.0, anchor='ne')

        self.back_button = tk.Button(self, text="戻る", command=self.on_back_button_click)
        self.back_button.place(relx=0.0, rely=0.0, anchor='nw')

        # 3つのボタンを作成
        self.sort_frame = tk.Frame(self)
        self.sort_frame.place(relx=0.5, rely=0.1, anchor='center')


        self.sort_all_button = tk.Button(self.sort_frame, text="全て", command=self.on_sort_all_button_click)
        self.sort_confidence_button = tk.Button(self.sort_frame, text="自信あり⚪︎", command=self.on_sort_confidence_button_click)
        self.sort_no_confidence_button = tk.Button(self.sort_frame, text="自信なし×", command=self.on_sort_no_confidence_button_click)

        self.sort_all_button.grid(row=1, column=0, padx=5)
        self.sort_confidence_button.grid(row=1, column=1, padx=5)
        self.sort_no_confidence_button.grid(row=1, column=2, padx=5)

        self.understand_check_button = tk.Button(self, text="理解度チェック", command=self.on_understand_check_button_click)
        self.understand_check_button.place(relx=0, rely=1, anchor='sw')
        self.update()

    def on_plus_button_click(self):
        print("追加Button clicked!")
        switcher.switchTo(AddWordFrame, self.genre)

    def on_back_button_click(self):
        print("戻るButton clicked!")
        switcher.switchTo(StartFrame)

    def on_sort_all_button_click(self):
        print("全てButton clicked!")

    def on_sort_confidence_button_click(self):
        print("自信ありButton clicked!")

    def on_sort_no_confidence_button_click(self):
        print("自信なしButton clicked!")

    def on_understand_check_button_click(self):
        print("理解度チェックButton clicked!")


class AddWordFrame(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list):  # 追加: model: Model
        super().__init__(switcher.parent)
        self.model= model
        self.genre = genre

        # This frame will be used to center the widgets
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(self.center_frame, text="単語名").grid(row=0, column=0, columnspan=2, pady=5)
        self.genre_name_entry = tk.Entry(self.center_frame)
        self.genre_name_entry.grid(row=1, column=0, columnspan=2, pady=5)

        tk.Label(self.center_frame, text="単語の詳細").grid(row=2, column=0, columnspan=2, pady=5)
        self.genre_name_entry = tk.Entry(self.center_frame)
        self.genre_name_entry.grid(row=3, column=0, columnspan=2, pady=5)

        self.add_button = tk.Button(self.center_frame, text="完了", command=self.on_add_button_click)
        self.add_button.grid(row=4, column=1, pady=5)

        self.cancel_button = tk.Button(self.center_frame, text="キャンセル", command=self.on_cancel_button_click)
        self.cancel_button.grid(row=4, column=0, pady=5)

        self.update()

    def on_cancel_button_click(self):
        print("キャンセルbutton clicked!")
        switcher.switchTo(WordListFrame, self.genre)


    def on_add_button_click(self):
        print("完了button clicked!")
        switcher.switchTo(WordListFrame, self.genre)
        # データベースに関する処理
    pass


window = tk.Tk()
window.title("My単語帳")
window.geometry("500x500")
window.resizable(False, False)

model = Model("test.db")

switcher = FrameSwitcher(window, model)
switcher.switchTo(StartFrame)
# switcher.switchTo(AddGenreFrame)
# switcher.switchTo(WordListFrame)
# switcher.switchTo(AddWordFrame)

window.mainloop()
