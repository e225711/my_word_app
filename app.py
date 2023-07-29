import sqlite3
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from typing import Type
import random
import tkinter.messagebox as messagebox

# データベース操作のためのクラス
class Model:
    def __init__(self, db_name: str):
        self.db_name = db_name
        # SQLiteデータベースに接続
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

        # ジャンルテーブルが存在しない場合には作成
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')

        # 単語テーブルが存在しない場合には作成。ジャンルテーブルへの外部キーを含む。
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

    # 新たにジャンルを追加
    def add_genre(self, name: str):
        self.cursor.execute('''INSERT INTO genres (name) VALUES (?)''', (name,))
        self.connection.commit()

    # ジャンル名を編集
    def edit_genre(self, id: int, genre_name: str):
        self.cursor.execute('''
        UPDATE genres
        SET name=?
        WHERE id=?
        ''', (genre_name, id))
        self.connection.commit()

    # ジャンルを削除（ジャンルに紐づく単語も削除）
    def delete_genre(self, genre_id: int):
        self.cursor.execute('''DELETE FROM words WHERE genre_id = ?''', (genre_id,))
        self.cursor.execute('''DELETE FROM genres WHERE id = ?''', (genre_id,))
        self.connection.commit()

    # すべてのジャンルを取得
    def get_genres(self):
        self.cursor.execute('''SELECT * FROM genres''')
        return self.cursor.fetchall()

    # 新たに単語を追加
    def add_word(self, genre_id: int, word: str, details: str,confidence: bool = False):
        self.cursor.execute('''INSERT INTO words (genre_id, word, details,confidence) VALUES (?, ?, ?, ?)''', (genre_id, word, details, confidence))
        self.connection.commit()

    # 単語とその詳細を編集
    def edit_word(self, id:int, word: str, details: str):
        self.cursor.execute('''
        UPDATE words
        SET word=?,details=?
        WHERE id=?
        ''', (word, details,id))
        self.connection.commit()

    # 単語を削除
    def delete_word(self, word_id: int):
        self.cursor.execute('''DELETE FROM words WHERE id = ?''', (word_id,))
        self.connection.commit()

    # 特定のジャンルの単語をすべて取得
    def get_words(self, genre_id: int):
        self.cursor.execute('''SELECT * FROM words WHERE genre_id = ?''', (genre_id,))
        return self.cursor.fetchall()

    # 単語リストをシャッフル
    def make_shuffle_list(self, word_list: list):
        shuffle_list = word_list
        random.shuffle(shuffle_list)
        return shuffle_list

    # 単語の自信度を更新
    def update_word_confidence(self, word_id: int, new_confidence: bool):
        self.cursor.execute('''UPDATE words SET confidence = ? WHERE id = ?''', (new_confidence, word_id))
        self.connection.commit()

    # 自信がある単語を取得
    def sort_confidence(self, genre_id: int):
        self.cursor.execute('''SELECT * FROM words WHERE genre_id = ? AND confidence = ?''', (genre_id, True))
        return self.cursor.fetchall()

    # 自信がない単語を取得
    def sort_no_confidence(self, genre_id: int):
        self.cursor.execute('''SELECT * FROM words WHERE genre_id = ? AND confidence = ?''', (genre_id, False))
        return self.cursor.fetchall()


# フレームの切り替えを行うクラス
class FrameSwitcher:
    # 初期化
    def __init__(self, parent, model: Model, *args):
        # 親ウィジェットを保存
        self.parent = parent
        # 現在のフレーム（初期状態ではNone）
        self.current_frame: tk.Frame = None
        # データベース操作のためのModelを保存
        self.model = model

    # 指定したフレームに切り替えるメソッド
    def switchTo(self, frame_class: Type[tk.Frame], *args):
        # 受け取ったクラスを利用してインスタンスを生成
        frame = frame_class(self, self.model, *args)
        # 現在のフレームが存在すれば破棄する
        if self.current_frame is not None:
            self.current_frame.destroy()

        # 新しいフレームを現在のフレームに設定し、画面に表示
        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)


# スタート画面のフレームを表現するクラス
class StartFrame(tk.Frame):
    # 初期化
    def __init__(self, switcher: FrameSwitcher, model: Model):
        super().__init__(switcher.parent)
        # フレーム切り替えのためのFrameSwitcherを保存
        self.switcher = switcher
        # データベース操作のためのModelを保存
        self.model = model

        # "ジャンル"というラベルを作成
        tk.Label(self, text="ジャンル").pack()

        # ＋ボタンを作成
        self.plus_button = tk.Button(self, text="＋", command=self.on_plus_button_click)
        self.plus_button.place(relx=1.0, rely=0.0, anchor='ne')

        # データベースから取得した各ジャンルに対してボタンを作成
        for genre in model.get_genres():
            genre_button = tk.Button(self, text=genre[1])
            # 左クリックと右クリック時にはそれぞれ異なるイベントを発生させる
            genre_button.bind("<Button-1>", lambda event, g=genre: self.on_genre_button_click(event, g))
            genre_button.bind("<Button-2>", lambda event, g=genre: self.on_genre_button_click(event, g))
            genre_button.pack()

        self.update()

    # ＋ボタンがクリックされた時の処理
    def on_plus_button_click(self):
        print("plus Button clicked!")
        # ジャンル追加画面に切り替え
        self.switcher.switchTo(AddGenreFrame)

    # ジャンルボタンがクリックされた時の処理
    def on_genre_button_click(self, event, genre: list):
        # 選択したジャンルの単語リストを取得
        word_list = self.model.get_words(genre[0])
        if event.num == 1:
            print("ジャンルButton left_clicked!")
            # 左クリックの場合、単語リスト画面に切り替え
            self.switcher.switchTo(WordListFrame, genre, word_list)
        elif event.num == 2:
            print("ジャンルButton right_clicked!")
            # 右クリックの場合、ジャンル編集画面に切り替え
            self.switcher.switchTo(GenreEditFrame, genre)

# ジャンル追加画面のフレームを表現するクラス
class AddGenreFrame(tk.Frame):
    # 初期化
    def __init__(self, switcher: FrameSwitcher, model: Model):
        super().__init__(switcher.parent)
        # データベース操作のためのModelを保存
        self.model = model
        self.switcher = switcher

        # ウィジェットを中央に配置するためのフレームを作成
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        # "追加するジャンル名"というラベルを作成
        tk.Label(self.center_frame, text="追加するジャンル名").grid(row=0, column=0, columnspan=2, pady=5)
        # ジャンル名を入力するためのエントリーを作成
        self.genre_name_entry = tk.Entry(self.center_frame)
        self.genre_name_entry.grid(row=1, column=0, columnspan=2, pady=5)

        # "完了"ボタンを作成
        self.add_button = tk.Button(self.center_frame, text="完了", command=self.on_add_genre_button_click)
        self.add_button.grid(row=2, column=1, pady=5)

        # "キャンセル"ボタンを作成
        self.cancel_button = tk.Button(self.center_frame, text="キャンセル", command=self.on_cancel_button_click)
        self.cancel_button.grid(row=2, column=0, pady=5)
        self.update()

    # "キャンセル"ボタンがクリックされた時の処理
    def on_cancel_button_click(self):
        print("キャンセルbutton clicked!")
        # スタート画面に切り替え
        self.switcher.switchTo(StartFrame)

    # "完了"ボタンがクリックされた時の処理
    def on_add_genre_button_click(self):
        print("完了button clicked!")
        # エントリーからジャンル名を取得
        genre_name = self.genre_name_entry.get()
        # 新しいジャンルをデータベースに追加
        self.model.add_genre(genre_name)
        # スタート画面に切り替え
        self.switcher.switchTo(StartFrame)



# 単語リスト表示フレームを表現するクラス
class WordListFrame(tk.Frame):
    # 初期化
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list, word_list: list = None):
        super().__init__(switcher.parent)
        # 選択したジャンルとデータベース操作のためのModel、フレームスイッチャー、単語リストを保存
        self.genre = genre
        self.model = model
        self.switcher = switcher
        self.word_list = word_list

        # ジャンル名を表示するラベルを作成
        tk.Label(self, text=genre[1]).pack(pady=(0,50))

        # "＋"ボタンを作成
        self.plus_button = tk.Button(self, text="＋", command=self.on_plus_button_click)
        self.plus_button.place(relx=1.0, rely=0.0, anchor='ne')

        # "戻る"ボタンを作成
        self.back_button = tk.Button(self, text="戻る", command=self.on_back_button_click)
        self.back_button.place(relx=0.0, rely=0.0, anchor='nw')

        # "全て"、"自信あり⚪︎"、"自信なし×"の3つのボタンを作成
        self.sort_frame = tk.Frame(self)
        self.sort_frame.place(relx=0.5, rely=0.1, anchor='center')

        self.sort_all_button = tk.Button(self.sort_frame, text="全て", command=self.on_sort_all_button_click)

        self.sort_confidence_button = tk.Button(self.sort_frame, text="自信あり⚪︎", command=self.on_sort_confidence_button_click)

        self.sort_no_confidence_button = tk.Button(self.sort_frame, text="自信なし×", command=self.on_sort_no_confidence_button_click)

        self.sort_all_button.pack(side = 'left')
        self.sort_confidence_button.pack(side = 'left')
        self.sort_no_confidence_button.pack(side = 'left')

        # "理解度チェック"ボタンを作成
        self.understand_check_button = tk.Button(self, text="理解度チェック", command=lambda w=self.word_list: self.on_understand_check_button_click(w))
        self.understand_check_button.place(relx=0, rely=1, anchor='sw')

        # 単語リストの各単語について、ボタンとチェックボックスを作成
        for word in self.word_list:
            frame = tk.Frame(self)  # 各ボタン/チェックボタンペアの新しいフレームを作成
            frame.pack()  # フレームをx方向に伸ばす

            # 単語ボタンを作成
            tk.Button(frame, text=word[2], command=lambda g = genre, w=word: self.on_word_button_click(g, w)).pack(expand=True, side = 'left')

            # 自信度チェックボックスを作成
            confidence = tk.IntVar()
            confidence.set(word[4])
            handler = self.make_confidence_change_handler(word, confidence)
            confidence.trace('w', handler)
            confidence_button = tk.Checkbutton(frame, variable=confidence,onvalue=1, offvalue=0)
            confidence_button.pack(side = 'left')

        self.update()

    # "＋"ボタンがクリックされた時の処理
    def on_plus_button_click(self):
        print("追加Button clicked!")
        # 単語追加画面に切り替え
        self.switcher.switchTo(AddWordFrame, self.genre)

    # "戻る"ボタンがクリックされた時の処理
    def on_back_button_click(self):
        print("戻るButton clicked!")
        # スタート画面に切り替え
        self.switcher.switchTo(StartFrame)

    # "全て"ボタンがクリックされた時の処理
    def on_sort_all_button_click(self):
        print("全てButton clicked!")
        # ジャンルに属する全ての単語を取得
        self.word_list = self.model.get_words(self.genre[0])
        # 全ての単語を表示する画面に切り替え
        self.switcher.switchTo(WordListFrame, self.genre, self.word_list)

    # "自信あり⚪︎"ボタンがクリックされた時の処理
    def on_sort_confidence_button_click(self):
        print("自信ありButton clicked!")
        # 自信ありの単語のみを取得
        self.word_list = self.model.sort_confidence(self.genre[0])
        # 自信ありの単語を表示する画面に切り替え
        self.switcher.switchTo(WordListFrame, self.genre, self.word_list)

    # "自信なし×"ボタンがクリックされた時の処理
    def on_sort_no_confidence_button_click(self):
        print("自信なしButton clicked!")
        # 自信なしの単語のみを取得
        self.word_list = self.model.sort_no_confidence(self.genre[0])
        # 自信なしの単語を表示する画面に切り替え
        self.switcher.switchTo(WordListFrame, self.genre, self.word_list)

    # 単語ボタンがクリックされた時の処理
    def on_word_button_click(self, genre: list, word: list):
        print("単語Button clicked!")
        # 単語詳細画面に切り替え
        self.switcher.switchTo(WordDetailFrame, genre, word)

    # "理解度チェック"ボタンがクリックされた時の処理
    def on_understand_check_button_click(self, word_list):
        print("理解度チェックButton clicked!")
        # 単語リストをシャッフル
        shuffle_list = self.model.make_shuffle_list(word_list)
        # 理解度チェック画面に切り替え
        self.switcher.switchTo(WordCheckFrame, self.genre, shuffle_list, 0)

    # 自信度チェックボタンがクリックされた時の処理
    def on_confidence_change(self, word, confidence, *args):
        print("自信属性 Button clicked!")
        # データベース内の自信属性を更新
        self.model.update_word_confidence(word[0], confidence.get())

    # 自信度チェックボタンの変更イベントハンドラを作成
    def make_confidence_change_handler(self, word, confidence):
        def handler(*args):
            self.on_confidence_change(word, confidence)
        return handler



# 単語追加フレームを表現するクラス
class AddWordFrame(tk.Frame):
    # 初期化
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list):
        super().__init__(switcher.parent)
        # データベース操作のためのModel、フレームスイッチャー、ジャンルを保存
        self.model = model
        self.genre = genre

        # ウィジェットを中心に配置するためのフレームを作成
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        # "単語名"というラベルを作成
        tk.Label(self.center_frame, text="単語名").grid(row=0, column=0, columnspan=2, pady=5)
        # 単語名を入力するテキストボックスを作成
        self.word_name_entry = tk.Entry(self.center_frame)
        self.word_name_entry.grid(row=1, column=0, columnspan=2, pady=5)

        # "単語の詳細"というラベルを作成
        tk.Label(self.center_frame, text="単語の詳細").grid(row=2, column=0, columnspan=2, pady=5)
        # 単語の詳細を入力するテキストボックスを作成
        self.word_detail_entry = ScrolledText(self.center_frame, font=("", 15), height=10, width=30)
        self.word_detail_entry.grid(row=3, column=0, columnspan=2, pady=5)

        # "完了"ボタンを作成
        self.add_button = tk.Button(self.center_frame, text="完了", command=self.on_add_button_click)
        self.add_button.grid(row=4, column=1, pady=5)

        # "キャンセル"ボタンを作成
        self.cancel_button = tk.Button(self.center_frame, text="キャンセル", command=self.on_cancel_button_click)
        self.cancel_button.grid(row=4, column=0, pady=5)

        self.update()

    # "キャンセル"ボタンがクリックされた時の処理
    def on_cancel_button_click(self):
        print("キャンセルbutton clicked!")
        # ジャンルに属する全ての単語を取得
        word_list = self.model.get_words(self.genre[0])
        # 単語リスト画面に切り替え
        switcher.switchTo(WordListFrame, self.genre, word_list)

    # "完了"ボタンがクリックされた時の処理
    def on_add_button_click(self):
        print("完了button clicked!")
        # 単語名と詳細を取得
        word_name = self.word_name_entry.get()
        word_detail = self.word_detail_entry.get('1.0','end - 1c')
        # 新しい単語をデータベースに追加
        self.model.add_word(self.genre[0], word_name, word_detail)
        # ジャンルに属する全ての単語を取得
        word_list = self.model.get_words(self.genre[0])
        # 単語リスト画面に切り替え
        switcher.switchTo(WordListFrame, self.genre, word_list)



# 単語詳細フレームを表現するクラス
class WordDetailFrame(tk.Frame):
    # 初期化
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list, word: list):
        super().__init__(switcher.parent)
        # データベース操作のためのModel、フレームスイッチャー、ジャンル、単語を保存
        self.model= model
        self.genre = genre
        self.word = word

        # 単語名を表示するためのラベルを作成
        word_name = tk.Label(self, text=word[2], font=("Helvetica",25))
        word_name.place(relx=0.5, rely=0.15, anchor='center')

        # "詳細"というラベルを作成
        tk.Label(self,text="詳細").pack()

        # 単語の詳細を表示するためのフレームを作成
        word_detail_frame = tk.Frame(self)
        word_detail_frame.place(relx=0.5, rely=0.5, anchor='center')

        # 単語の詳細を表示するためのテキストウィジェットを作成
        word_detail = tk.Text(word_detail_frame, font=("Helvetica", 20), wrap='word', height=10, width=30)
        word_detail.insert('1.0', word[3])  # 単語の詳細をテキストウィジェットに挿入
        word_detail.pack(side='left', fill='both', expand=True)

        # テキストウィジェットにスクロールバーを付けるためのスクロールバーを作成
        scrollbar = tk.Scrollbar(word_detail_frame, command=word_detail.yview)
        scrollbar.pack(side='right', fill='y')

        # テキストウィジェットの編集を無効化
        word_detail.config(state='disabled')

        # テキストウィジェットとスクロールバーを連携させる
        word_detail.config(yscrollcommand=scrollbar.set)

        # "単語一覧へ"ボタンを作成
        self.back_button = tk.Button(self, text="単語一覧へ", command=self.on_wordlist_back_button_click)
        self.back_button.place(relx=0.0, rely=0.0, anchor='nw')

        # "編集"ボタンを作成
        self.edit_button = tk.Button(self, text="編集", command=self.on_edit_button_click)
        self.edit_button.place(relx=1.0, rely=0.0, anchor='ne')

        # "次へ"ボタンを作成
        self.next_word = tk.Button(self, text="次へ", command=lambda g = genre, w=word: self.on_next_button_click(g, w))
        self.next_word.place(relx=1.0, rely=1.0, anchor='se')

        # "前へ"ボタンを作成
        self.before_word  = tk.Button(self, text="前へ", command=lambda g = genre, w=word: self.on_before_button_click(g, w))
        self.before_word.place(relx=0.88, rely=1.0, anchor='se')

        self.update()

    # "単語一覧へ"ボタンがクリックされた時の処理
    def on_wordlist_back_button_click(self):
        print("単語一覧button clicked!")
        # ジャンルに属する全ての単語を取得
        word_list = self.model.get_words(self.genre[0])
        # 単語リスト画面に切り替え
        switcher.switchTo(WordListFrame, self.genre, word_list)

    # "編集"ボタンがクリックされた時の処理
    def on_edit_button_click(self):
        print("編集button clicked!")
        # 単語編集画面に切り替え
        switcher.switchTo(WordEditFrame, self.genre, self.word)

    # "次へ"ボタンがクリックされた時の処理
    def on_next_button_click(self, genre:list, word:list):
        print("次へbutton clicked!")
        # ジャンルに属する全ての単語を取得
        search_word_list = model.get_words(genre[0])
        # 現在の単語がリストの中で何番目にあるかを取得
        word_index = search_word_list.index(word)
        # 全ての単語の数を取得
        len_search_word_list = len(search_word_list)
        # 現在の単語が最後の単語だった場合、最初の単語を表示
        if word_index + 1 == len_search_word_list:
            word_index = 0
            # 単語詳細画面に切り替え
            switcher.switchTo(WordDetailFrame, genre, search_word_list[word_index])
        # それ以外の場合、次の単語を表示
        else:
            # 単語詳細画面に切り替え
            switcher.switchTo(WordDetailFrame, genre, search_word_list[word_index+1])

    # "前へ"ボタンがクリックされた時の処理
    def on_before_button_click(self, genre:list, word:list):
        print("前へbutton clicked!")
        # ジャンルに属する全ての単語を取得
        search_word_list = model.get_words(genre[0])
        # 現在の単語がリストの中で何番目にあるかを取得
        word_index = search_word_list.index(word)
        # 全ての単語の数を取得
        len_search_word_list = len(search_word_list)
        # 現在の単語が最初の単語だった場合、最後の単語を表示
        if word_index == 0:
            word_index = len_search_word_list - 1
            # 単語詳細画面に切り替え
            switcher.switchTo(WordDetailFrame, genre, search_word_list[word_index])
        # それ以外の場合、前の単語を表示
        else:
            # 単語詳細画面に切り替え
            switcher.switchTo(WordDetailFrame, genre, search_word_list[word_index-1])

# 単語確認フレームを表現するクラス
class WordCheckFrame(tk.Frame):
    # 初期化
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list, shuffle_list: list, count: int):
        super().__init__(switcher.parent)
        # データベース操作のためのModel、フレームスイッチャー、ジャンル、シャッフルした単語リスト、カウンターを保存
        self.genre = genre
        self.model = model
        self.switcher = switcher
        self.shuffle_list = shuffle_list
        self.count = count

        # "単語一覧へ"ボタンを作成
        self.back_button = tk.Button(self, text="単語一覧へ", command=self.on_back_button_click)
        self.back_button.place(relx=1.0, rely=0.0, anchor='ne')

        # "解答へ"ボタンを作成
        self.answer_button = tk.Button(self, text="解答へ", command=self.on_answer_button_click)
        self.answer_button.place(relx=1.0, rely=1.0, anchor='se')

        # カウンターがシャッフルリストの長さ（つまり、全単語が終了した）と同じなら
        if self.count == len(self.shuffle_list):
            # "終了しました"と表示
            label = tk.Label(self, text="終了しました", font=("Helvetica", 50))
            label.place(relx=0.5, rely=0.5, anchor='center')
            # "解答へ"ボタンを非表示に
            self.answer_button.destroy()
        else:
            # それ以外の場合、シャッフルリストのカウンター番目の単語を表示
            label = tk.Label(self, text=self.shuffle_list[self.count][2], font=("Helvetica", 50))
            label.place(relx=0.5, rely=0.5, anchor='center')

    # "単語一覧へ"ボタンがクリックされた時の処理
    def on_back_button_click(self):
        print("単語一覧Button clicked!")
        # ジャンルに属する全ての単語を取得
        word_list = self.model.get_words(self.genre[0])
        # 単語リスト画面に切り替え
        switcher.switchTo(WordListFrame, self.genre, word_list)

    # "解答へ"ボタンがクリックされた時の処理
    def on_answer_button_click(self):
        print("答えButton clicked!")
        # 単語確認回答フレームに切り替え
        switcher.switchTo(WordCheckAnswerFrame, self.genre, self.shuffle_list, self.count)


# 単語確認回答フレームを表現するクラス
class WordCheckAnswerFrame(tk.Frame):
    # 初期化
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list, shuffle_list: list, count: int):
        super().__init__(switcher.parent)
        # データベース操作のためのModel、フレームスイッチャー、ジャンル、シャッフルした単語リスト、カウンターを保存
        self.genre = genre
        self.model = model
        self.switcher = switcher
        self.shuffle_list = shuffle_list
        self.count = count

        # "単語一覧へ"ボタンを作成
        self.back_button = tk.Button(self, text="単語一覧へ", command=self.on_back_button_click)
        self.back_button.place(relx=1.0, rely=0.0, anchor='ne')

        # "次の単語へ"ボタンを作成
        self.next_word_button = tk.Button(self, text="次の単語へ", command=self.on_next_word_button_click)
        self.next_word_button.place(relx=1.0, rely=1.0, anchor='se')

        # シャッフルリストのカウンター番目の単語を表示
        word_name = tk.Label(self, text=self.shuffle_list[self.count][2], font=("Helvetica", 25))
        word_name.place(relx=0.5, rely=0.2, anchor='center')

        # 単語の詳細をテキストウィジェットを使用して表示
        word_detail_frame = tk.Frame(self)
        word_detail_frame.place(relx=0.5, rely=0.5, anchor='center')

        word_detail = tk.Text(word_detail_frame, font=("Helvetica", 20), wrap='word', height=10, width=30)
        word_detail.insert('1.0', self.shuffle_list[self.count][3])
        word_detail.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(word_detail_frame, command=word_detail.yview)
        scrollbar.pack(side='right', fill='y')

        word_detail.config(yscrollcommand=scrollbar.set)

        # 自信度のチェックボックスを作成
        tk.Label(self, text="自信").place(relx=0.02, rely=0.995, anchor='sw')
        confidence = tk.IntVar()
        confidence.set(self.shuffle_list[self.count][3])
        handler = self.make_confidence_change_handler(self.shuffle_list[self.count], confidence)
        confidence.trace('w', handler)
        confidence_button = tk.Checkbutton(self, variable=confidence,onvalue=1, offvalue=0)
        confidence_button.place(relx=0.08, rely=1.0, anchor='sw')

    # "単語一覧へ"ボタンがクリックされた時の処理
    def on_back_button_click(self):
        print("単語一覧Button clicked!")
        word_list = self.model.get_words(self.genre[0])
        # 単語リスト画面に切り替え
        self.switcher.switchTo(WordListFrame, self.genre, word_list)

    # "次の単語へ"ボタンがクリックされた時の処理
    def on_next_word_button_click(self):
        print("次の単語Button clicked!")
        self.count += 1
        # 理解度チェック画面に切り替え
        self.switcher.switchTo(WordCheckFrame, self.genre, self.shuffle_list, self.count)

    # 自信度のチェックボックスが変更された時の処理
    def on_confidence_change(self, word, confidence, *args):
        print("自信属性 Button clicked!")
        self.model.update_word_confidence(word[0], confidence.get())

    # 自信度のチェックボックスが変更された時のイベントハンドラーを作成
    def make_confidence_change_handler(self, word, confidence):
        def handler(*args):
            self.on_confidence_change(word, confidence)
        return handler



# 単語編集フレームを表現するクラス
class WordEditFrame(tk.Frame):
    # 初期化
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list, word: list):
        super().__init__(switcher.parent)
        # データベース操作のためのModel、フレームスイッチャー、ジャンル、編集対象の単語を保存
        self.model= model
        self.genre = genre
        self.word = word

        # 中心フレームを作成
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        # 単語名と単語詳細の入力欄を作成
        tk.Label(self.center_frame, text="単語名").grid(row=0, column=0, columnspan=2, pady=5)
        self.word_name_entry = tk.Entry(self.center_frame)
        self.word_name_entry.insert(tk.END,word[2])
        self.word_name_entry.grid(row=1, column=0, columnspan=2, pady=5)

        tk.Label(self.center_frame, text="単語の詳細").grid(row=2, column=0, columnspan=2, pady=5)
        self.word_detail_entry = ScrolledText(self.center_frame, font=("", 15), height=10, width=30)
        self.word_detail_entry.insert(tk.END,word[3])
        self.word_detail_entry.grid(row=3, column=0, columnspan=2, pady=5)

        # "完了"ボタンと"キャンセル"ボタンを作成
        self.add_button = tk.Button(self.center_frame, text="完了", command=self.on_edit_button_click)
        self.add_button.grid(row=4, column=1, pady=5)

        self.cancel_button = tk.Button(self.center_frame, text="キャンセル", command=self.on_cancel_button_click)
        self.cancel_button.grid(row=4, column=0, pady=5)

        # "削除"ボタンを作成
        self.delete_button = tk.Button(self, text="削除", command=self.on_delete_button_click)
        self.delete_button.place(relx=1.0, rely=0.0, anchor='ne')

    # "キャンセル"ボタンがクリックされた時の処理
    def on_cancel_button_click(self):
        print("キャンセルbutton clicked!")
        word_list = self.model.get_words(self.genre[0])
        # 単語リスト画面に切り替え
        switcher.switchTo(WordListFrame, self.genre, word_list)

    # "完了"ボタンがクリックされた時の処理
    def on_edit_button_click(self):
        print("edit完了button clicked!")
        word_name = self.word_name_entry.get()
        word_detail = self.word_detail_entry.get('1.0','end - 1c')
        # 単語の編集を行い、その後単語リストフレームに戻る
        self.model.edit_word(self.word[0], word_name, word_detail)
        word_list = self.model.get_words(self.genre[0])
        # 単語リスト画面に切り替え
        switcher.switchTo(WordListFrame, self.genre, word_list)

    # "削除"ボタンがクリックされた時の処理
    def on_delete_button_click(self):
        print("削除button clicked!")
        # ユーザーに削除確認のダイアログを表示
        result = messagebox.askyesno("削除確認", f"本当にこの単語({self.word[2]})を削除しますか？")
        if result:
            # はいを押した場合は、単語を削除し、その後単語リストフレームに戻る
            self.model.delete_word(self.word[0])
            word_list = self.model.get_words(self.genre[0])
            # 単語リスト画面に切り替え
            switcher.switchTo(WordListFrame, self.genre, word_list)



# ジャンル編集フレームを表現するクラス
class GenreEditFrame(tk.Frame):
    # 初期化
    def __init__(self, switcher: FrameSwitcher, model: Model, genre: list):
        super().__init__(switcher.parent)
        # データベース操作のためのModel、フレームスイッチャー、編集対象のジャンルを保存
        self.model = model
        self.genre = genre

        # 中心フレームを作成
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        # ジャンル名の入力欄を作成
        tk.Label(self.center_frame, text="追加するジャンル名").grid(row=0, column=0, columnspan=2, pady=5)
        self.genre_name_entry = tk.Entry(self.center_frame)
        self.genre_name_entry.insert(tk.END, genre[1])
        self.genre_name_entry.grid(row=1, column=0, columnspan=2, pady=5)

        # "完了"ボタンと"キャンセル"ボタンを作成
        self.add_button = tk.Button(self.center_frame, text="完了", command=self.on_add_genre_button_click)
        self.add_button.grid(row=2, column=1, pady=5)

        self.cancel_button = tk.Button(self.center_frame, text="キャンセル", command=self.on_cancel_button_click)
        self.cancel_button.grid(row=2, column=0, pady=5)

        # "削除"ボタンを作成
        self.delete_button = tk.Button(self, text="削除", command=self.on_delete_button_click)
        self.delete_button.place(relx=1.0, rely=0.0, anchor='ne')

    # "キャンセル"ボタンがクリックされた時の処理
    def on_cancel_button_click(self):
        print("キャンセルbutton clicked!")
        # スタート画面に切り替え
        switcher.switchTo(StartFrame)

    # "完了"ボタンがクリックされた時の処理
    def on_add_genre_button_click(self):
        print("完了button clicked!")
        genre_name = self.genre_name_entry.get()
        # ジャンルの編集を行い、その後スタート画面に戻る
        self.model.edit_genre(self.genre[0], genre_name)
        # スタート画面に切り替え
        switcher.switchTo(StartFrame)

    # "削除"ボタンがクリックされた時の処理
    def on_delete_button_click(self):
        print("削除button clicked!")
        # ユーザーに削除確認のダイアログを表示
        if messagebox.askyesno('確認', f'{self.genre[1]}を削除してもよろしいですか？'):
            # はいを押した場合は、ジャンルを削除し、その後スタート画面に戻る
            self.model.delete_genre(self.genre[0])
            # スタート画面に切り替え
            switcher.switchTo(StartFrame)



# メインウィンドウを作成
window = tk.Tk()

# メインウィンドウのタイトルを設定
window.title("My単語帳")

# メインウィンドウの初期サイズを設定
window.geometry("500x500")

# メインウィンドウのサイズ変更を無効
window.resizable(False, False)

# データベースとのやり取りを管理するModelインスタンスを作成
model = Model("test.db")

# フレームを切り替えるためのスイッチャーを作成
switcher = FrameSwitcher(window, model)

# スタート画面切り替え
switcher.switchTo(StartFrame)

# アプリケーションのメインループを開始
window.mainloop()
