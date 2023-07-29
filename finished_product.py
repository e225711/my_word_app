import sqlite3
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from typing import Type
import random
import tkinter.messagebox as messagebox


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
        # 自信有無は追加必要
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

    def edit_genre(self, id: int, genre_name: str):
        self.cursor.execute('''
        UPDATE genres
        SET name=?
        WHERE id=?
        ''', (genre_name, id))
        self.connection.commit()

    def delete_genre(self, genre_id: int):
        self.cursor.execute('''DELETE FROM words WHERE genre_id = ?''', (genre_id,))
        self.cursor.execute('''DELETE FROM genres WHERE id = ?''', (genre_id,))
        self.connection.commit()

    def get_genres(self):
        self.cursor.execute('''SELECT * FROM genres''')
        return self.cursor.fetchall()

    def add_word(self, genre_id: int, word: str, details: str,confidence: bool = False):
        self.cursor.execute('''INSERT INTO words (genre_id, word, details,confidence) VALUES (?, ?, ?, ?)''', (genre_id, word, details, confidence))
        self.connection.commit()

    def edit_word(self, id:int, word: str, details: str):
        self.cursor.execute('''
        UPDATE words
        SET word=?,details=?
        WHERE id=?
        ''', (word, details,id))
        self.connection.commit()

    def delete_word(self, word_id: int):
        self.cursor.execute('''DELETE FROM words WHERE id = ?''', (word_id,))
        self.connection.commit()

    def get_words(self, genre_id: int):
        self.cursor.execute('''SELECT * FROM words WHERE genre_id = ?''', (genre_id,))
        return self.cursor.fetchall()

    def make_shuffle_list(self, word_list: list):
        # self.cursor.execute('''SELECT id, word, details, confidence FROM words WHERE genre_id = ?''', (genre_id,))
        # shuffle_list = self.cursor.fetchall()
        shuffle_list = word_list
        random.shuffle(shuffle_list)
        return shuffle_list

    def update_word_confidence(self, word_id: int, new_confidence: bool):
        self.cursor.execute('''UPDATE words SET confidence = ? WHERE id = ?''', (new_confidence, word_id))
        self.connection.commit()

    def sort_confidence(self, genre_id: int):
        self.cursor.execute('''SELECT * FROM words WHERE genre_id = ? AND confidence = ?''', (genre_id, True))
        return self.cursor.fetchall()

    def sort_no_confidence(self, genre_id: int):
        self.cursor.execute('''SELECT * FROM words WHERE genre_id = ? AND confidence = ?''', (genre_id, False))
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
        self.model = model

        tk.Label(self, text="ジャンル").pack()

        self.plus_button = tk.Button(self, text="＋", command=self.on_plus_button_click)
        self.plus_button.place(relx=1.0, rely=0.0, anchor='ne')

        for genre in model.get_genres():
            genre_button = tk.Button(self, text=genre[1])
            genre_button.bind("<Button-1>", lambda event, g=genre: self.on_genre_button_click(event, g))
            genre_button.bind("<Button-2>", lambda event, g=genre: self.on_genre_button_click(event, g))
            genre_button.pack()

        self.update()

    def on_plus_button_click(self):
        print("plus Button clicked!")
        switcher.switchTo(AddGenreFrame)

    def on_genre_button_click(self, event, genre: list):
        word_list = self.model.get_words(genre[0])
        if event.num == 1:
            print("ジャンルButton left_clicked!")
            switcher.switchTo(WordListFrame, genre, word_list)
        elif event.num == 2:
            print("ジャンルButton right_clicked!")
            switcher.switchTo(GenreEditFrame, genre)

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
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list,word_list: list = None):
        super().__init__(switcher.parent)
        self.genre = genre
        self.model = model
        self.switcher = switcher
        self.word_list = word_list

        tk.Label(self, text=genre[1]).pack(pady=(0,50))

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

        self.sort_all_button.pack(side = 'left')
        self.sort_confidence_button.pack(side = 'left')
        self.sort_no_confidence_button.pack(side = 'left')

        self.understand_check_button = tk.Button(self, text="理解度チェック", command=lambda w=self.word_list: self.on_understand_check_button_click(w))
        self.understand_check_button.place(relx=0, rely=1, anchor='sw')


        for word in self.word_list:
            frame = tk.Frame(self)  # create a new frame for each button/checkbutton pair
            frame.pack()  # fill the frame in the x direction

            tk.Button(frame, text=word[2],command=lambda g = genre, w=word: self.on_word_button_click(g, w)).pack(expand=True, side = 'left')

            confidence = tk.IntVar()
            confidence.set(word[4])
            handler = self.make_confidence_change_handler(word, confidence)
            confidence.trace('w', handler)
            confidence_button = tk.Checkbutton(frame, variable=confidence,onvalue=1, offvalue=0)
            confidence_button.pack(side = 'left')


        self.update()


    def on_plus_button_click(self):
        print("追加Button clicked!")
        switcher.switchTo(AddWordFrame, self.genre)

    def on_back_button_click(self):
        print("戻るButton clicked!")
        switcher.switchTo(StartFrame)

    def on_sort_all_button_click(self):
        print("全てButton clicked!")
        self.word_list = self.model.get_words(self.genre[0])
        switcher.switchTo(WordListFrame, self.genre, self.word_list)

    def on_sort_confidence_button_click(self):
        print("自信ありButton clicked!")
        # モデルで絞り込みする処理
        self.word_list = self.model.sort_confidence(self.genre[0])
        switcher.switchTo(WordListFrame, self.genre, self.word_list)


    def on_sort_no_confidence_button_click(self):
        print("自信なしButton clicked!")
        # モデルで絞り込みする処理
        self.word_list = self.model.sort_no_confidence(self.genre[0])
        switcher.switchTo(WordListFrame, self.genre, self.word_list)


    def on_word_button_click(self, genre: list, word: list):
        print("単語Button clicked!")
        switcher.switchTo(WordDetailFrame, genre, word)

    def on_understand_check_button_click(self,word_list):
        print("理解度チェックButton clicked!")
        shuffle_list = self.model.make_shuffle_list(word_list)
        switcher.switchTo(WordCheckFrame, self.genre, shuffle_list, 0)

    def on_confidence_change(self, word,confidence,*args):
        print("自信属性 Button clicked!")
        # 自信属性を変更する処理
        self.model.update_word_confidence(word[0], confidence.get())

    def make_confidence_change_handler(self, word, confidence):
        def handler(*args):
            self.on_confidence_change(word, confidence)
        return handler


class AddWordFrame(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list):  # 追加: model: Model
        super().__init__(switcher.parent)
        self.model= model
        self.genre = genre

        # This frame will be used to center the widgets
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(self.center_frame, text="単語名").grid(row=0, column=0, columnspan=2, pady=5)
        self.word_name_entry = tk.Entry(self.center_frame)
        self.word_name_entry.grid(row=1, column=0, columnspan=2, pady=5)

        tk.Label(self.center_frame, text="単語の詳細").grid(row=2, column=0, columnspan=2, pady=5)
        self.word_detail_entry = ScrolledText(self.center_frame, font=("", 15), height=10, width=30)
        self.word_detail_entry.grid(row=3, column=0, columnspan=2, pady=5)

        self.add_button = tk.Button(self.center_frame, text="完了", command=self.on_add_button_click)
        self.add_button.grid(row=4, column=1, pady=5)

        self.cancel_button = tk.Button(self.center_frame, text="キャンセル", command=self.on_cancel_button_click)
        self.cancel_button.grid(row=4, column=0, pady=5)

        self.update()

    def on_cancel_button_click(self):
        print("キャンセルbutton clicked!")
        word_list = self.model.get_words(self.genre[0])
        switcher.switchTo(WordListFrame, self.genre,word_list)

    def on_add_button_click(self):
        print("完了button clicked!")
        word_name = self.word_name_entry.get()
        word_detail = self.word_detail_entry.get('1.0','end - 1c')
        self.model.add_word(self.genre[0], word_name, word_detail)
        word_list = self.model.get_words(self.genre[0])
        switcher.switchTo(WordListFrame, self.genre,word_list)



class WordDetailFrame(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list, word: list):  # 追加: model: Model
        super().__init__(switcher.parent)
        self.model= model
        self.genre = genre
        self.word = word

        word_name = tk.Label(self,text=word[2],font=("Helvetica",25))
        word_name.place(relx=0.5, rely=0.15, anchor='center')

        tk.Label(self,text="詳細").pack()

        # word_detail = tk.Label(self,text=word[3],font=("Helvetica",20))
        # word_detail.place(relx=0.5, rely=0.5, anchor='center')

        
        word_detail_frame = tk.Frame(self)
        word_detail_frame.place(relx=0.5, rely=0.5, anchor='center')

        # テキストウィジェットの横幅を指定して配置
        word_detail = tk.Text(word_detail_frame, font=("Helvetica", 20), wrap='word', height=10, width=30)
        word_detail.insert('1.0', word[3])
        word_detail.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(word_detail_frame, command=word_detail.yview)
        scrollbar.pack(side='right', fill='y')

        # テキストウィジェットの編集を無効化
        word_detail.config(state='disabled')

        # テキストウィジェットとスクロールバーの連携
        word_detail.config(yscrollcommand=scrollbar.set)



        self.back_button = tk.Button(self, text="単語一覧へ",command=self.on_wordlist_back_button_click)
        self.back_button.place(relx=0.0, rely=0.0, anchor='nw')

        self.edit_button = tk.Button(self, text="編集", command=self.on_edit_button_click)
        self.edit_button.place(relx=1.0, rely=0.0, anchor='ne')

        self.next_word = tk.Button(self, text="次へ", command=lambda g = genre, w=word: self.on_next_button_click(g, w))
        self.next_word.place(relx=1.0, rely=1.0, anchor='se')

        self.before_word  = tk.Button(self, text="前へ", command=lambda g = genre, w=word: self.on_before_button_click(g, w))
        self.before_word.place(relx=0.88, rely=1.0, anchor='se')

        self.update()

    def on_wordlist_back_button_click(self):
        print("単語一覧button clicked!")
        word_list = self.model.get_words(self.genre[0])
        switcher.switchTo(WordListFrame, self.genre, word_list)

    def on_edit_button_click(self):
        print("編集button clicked!")
        switcher.switchTo(WordEditFrame, self.genre,self.word)

    def on_next_button_click(self,genre:list,word:list):
        print("次へbutton clicked!")
        search_word_list=model.get_words(genre[0])
        word_index = search_word_list.index(word)
        len_search_word_list = len(search_word_list)
        if word_index + 1 == len_search_word_list:
            word_index = 0
            switcher.switchTo(WordDetailFrame, genre, search_word_list[word_index])
        else:
            switcher.switchTo(WordDetailFrame, genre, search_word_list[word_index+1])


    def on_before_button_click(self,genre:list,word:list):
        print("前へbutton clicked!")
        search_word_list=model.get_words(genre[0])
        word_index = search_word_list.index(word)
        len_search_word_list = len(search_word_list)
        if word_index == 0:
            word_index = len_search_word_list - 1
            switcher.switchTo(WordDetailFrame, genre, search_word_list[word_index])
        else:
            switcher.switchTo(WordDetailFrame, genre, search_word_list[word_index-1])


class WordCheckFrame(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list, shuffle_list: list, count: int):
        super().__init__(switcher.parent)
        self.genre = genre
        self.model = model
        self.switcher = switcher
        self.shuffle_list = shuffle_list
        self.count = count

        self.back_button = tk.Button(self, text="単語一覧へ", command=self.on_back_button_click)
        self.back_button.place(relx=1.0, rely=0.0, anchor='ne')

        self.answer_button = tk.Button(self, text="解答へ", command=self.on_answer_button_click)
        self.answer_button.place(relx=1.0, rely=1.0, anchor='se')

        if self.count == len(self.shuffle_list):
            label = tk.Label(self,text="終了しました", font=("Helvetica",50))
            label.place(relx=0.5, rely=0.5, anchor='center')
            self.answer_button.destroy()
            # 終了の表示
        else:
            label = tk.Label(self,text=self.shuffle_list[self.count][2],font=("Helvetica",50))
            label.place(relx=0.5, rely=0.5, anchor='center')


    def on_back_button_click(self):
        print("単語一覧Button clicked!")
        word_list = self.model.get_words(self.genre[0])
        switcher.switchTo(WordListFrame, self.genre, word_list)

    def on_answer_button_click(self):
        print("答えButton clicked!")
        switcher.switchTo(WordCheckAnswerFrame, self.genre, self.shuffle_list, self.count)


class WordCheckAnswerFrame(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list, shuffle_list: list, count: int):
        super().__init__(switcher.parent)
        self.genre = genre
        self.model = model
        self.switcher = switcher
        self.shuffle_list = shuffle_list
        self.count = count

        self.back_button = tk.Button(self, text="単語一覧へ", command=self.on_back_button_click)
        self.back_button.place(relx=1.0, rely=0.0, anchor='ne')

        self.next_word_button = tk.Button(self, text="次の単語へ", command=self.on_next_word_button_click)
        self.next_word_button.place(relx=1.0, rely=1.0, anchor='se')

        word_name = tk.Label(self, text=self.shuffle_list[self.count][2], font=("Helvetica", 25))
        word_name.place(relx=0.5, rely=0.2, anchor='center')

        # テキストウィジェットを使用して単語の詳細を表示
        word_detail_frame = tk.Frame(self)
        word_detail_frame.place(relx=0.5, rely=0.5, anchor='center')

        word_detail = tk.Text(word_detail_frame, font=("Helvetica", 20), wrap='word', height=10, width=30)
        word_detail.insert('1.0', self.shuffle_list[self.count][3])
        word_detail.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(word_detail_frame, command=word_detail.yview)
        scrollbar.pack(side='right', fill='y')

        word_detail.config(yscrollcommand=scrollbar.set)


        tk.Label(self, text="自信").place(relx=0.02, rely=0.995, anchor='sw')
        confidence = tk.IntVar()
        confidence.set(self.shuffle_list[self.count][3])
        handler = self.make_confidence_change_handler(self.shuffle_list[self.count], confidence)
        confidence.trace('w', handler)
        confidence_button = tk.Checkbutton(self, variable=confidence,onvalue=1, offvalue=0)
        confidence_button.place(relx=0.08, rely=1.0, anchor='sw')

        self.update()

    def on_back_button_click(self):
        print("単語一覧Button clicked!")
        word_list = self.model.get_words(self.genre[0])
        switcher.switchTo(WordListFrame, self.genre, word_list)

    def on_next_word_button_click(self):
        print("次の単語Button clicked!")
        self.count += 1
        switcher.switchTo(WordCheckFrame, self.genre, self.shuffle_list, self.count)

    def on_confidence_change(self, word, confidence, *args):
        print("自信属性 Button clicked!")
        # 自信属性を変更する処理
        self.model.update_word_confidence(word[0], confidence.get())

    def make_confidence_change_handler(self, word, confidence):
        def handler(*args):
            self.on_confidence_change(word, confidence)
        return handler


class WordEditFrame(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list, word: list):  # 追加: model: Model
        super().__init__(switcher.parent)
        self.model= model
        self.genre = genre
        self.word = word

        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(self.center_frame, text="単語名").grid(row=0, column=0, columnspan=2, pady=5)
        self.word_name_entry = tk.Entry(self.center_frame)
        self.word_name_entry.insert(tk.END,word[2])
        self.word_name_entry.grid(row=1, column=0, columnspan=2, pady=5)

        tk.Label(self.center_frame, text="単語の詳細").grid(row=2, column=0, columnspan=2, pady=5)
        self.word_detail_entry = ScrolledText(self.center_frame, font=("", 15), height=10, width=30)
        self.word_detail_entry.insert(tk.END,word[3])
        self.word_detail_entry.grid(row=3, column=0, columnspan=2, pady=5)

        self.add_button = tk.Button(self.center_frame, text="完了", command=self.on_edit_button_click)
        self.add_button.grid(row=4, column=1, pady=5)

        self.cancel_button = tk.Button(self.center_frame, text="キャンセル", command=self.on_cancel_button_click)
        self.cancel_button.grid(row=4, column=0, pady=5)

        self.delete_button = tk.Button(self, text="削除", command=self.on_delete_button_click)
        self.delete_button.place(relx=1.0, rely=0.0, anchor='ne')

        self.update()


    def on_cancel_button_click(self):
        print("キャンセルbutton clicked!")
        word_list = self.model.get_words(self.genre[0])
        switcher.switchTo(WordListFrame, self.genre, word_list)

    def on_edit_button_click(self):
        print("edit完了button clicked!")
        word_name = self.word_name_entry.get()
        word_detail = self.word_detail_entry.get('1.0','end - 1c')
        self.model.edit_word(self.word[0], word_name, word_detail)
        word_list = self.model.get_words(self.genre[0])
        switcher.switchTo(WordListFrame, self.genre, word_list)

    def on_delete_button_click(self):
        print("削除button clicked!")
        result = messagebox.askyesno("削除確認", f"本当にこの単語({self.word[2]})を削除しますか？")
        if result:
            self.model.delete_word(self.word[0])
            word_list = self.model.get_words(self.genre[0])
            switcher.switchTo(WordListFrame, self.genre, word_list)


class GenreEditFrame(tk.Frame):
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list):
        super().__init__(switcher.parent)
        self.model = model
        self.genre = genre

        # This frame will be used to center the widgets
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(self.center_frame, text="追加するジャンル名").grid(row=0, column=0, columnspan=2, pady=5)
        self.genre_name_entry = tk.Entry(self.center_frame)
        self.genre_name_entry.insert(tk.END, genre[1])
        self.genre_name_entry.grid(row=1, column=0, columnspan=2, pady=5)

        self.add_button = tk.Button(self.center_frame, text="完了", command=self.on_add_genre_button_click)
        self.add_button.grid(row=2, column=1, pady=5)

        self.cancel_button = tk.Button(self.center_frame, text="キャンセル", command=self.on_cancel_button_click)
        self.cancel_button.grid(row=2, column=0, pady=5)
        self.update()

        self.delete_button = tk.Button(self, text="削除", command=self.on_delete_button_click)
        self.delete_button.place(relx=1.0, rely=0.0, anchor='ne')

    def on_cancel_button_click(self):
        print("キャンセルbutton clicked!")
        switcher.switchTo(StartFrame)

    def on_add_genre_button_click(self):
        print("完了button clicked!")
        genre_name = self.genre_name_entry.get()
        self.model.edit_genre(self.genre[0], genre_name)
        switcher.switchTo(StartFrame)

    def on_delete_button_click(self):
        print("削除button clicked!")
        if messagebox.askyesno('確認', f'{self.genre[1]}を削除してもよろしいですか？'):
            self.model.delete_genre(self.genre[0])
            switcher.switchTo(StartFrame)


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
