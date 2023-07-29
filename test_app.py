import unittest
import os
from app import Model

class TestModel(unittest.TestCase):
    def setUp(self):
        # テスト用のデータベースを作成し、モデルを初期化する
        self.db_name = "test.db"
        self.model = Model(self.db_name)
        self.model.add_genre("Test Genre")
        self.model.add_word(1, "Test Word", "Test Details", False)


    def tearDown(self):
        # テスト後にデータベースを削除する
        self.model.connection.close()
        os.remove(self.db_name)


    def test_add_genre(self):
        # ジャンルを追加して、データベースにジャンルが存在することを確認するテスト
        genre_name = "Test Genre"
        self.model.add_genre(genre_name)


        # データベースからジャンルを取得し、追加したジャンルが存在するか確認
        genres = self.model.get_genres()
        genre_names = [genre[1] for genre in genres]
        self.assertIn(genre_name, genre_names)


    def test_add_word(self):
        # 単語を追加して、データベースに単語が存在し、理解度がFalseであることを確認するテスト
        genre_name = "Test Genre"
        self.model.add_genre(genre_name)


        # ジャンルを取得
        genres = self.model.get_genres()
        genre_id = genres[0][0]


        word = "Test Word"
        details = "This is a test word."
        self.model.add_word(genre_id, word, details)


        # データベースから単語を取得し、追加した単語が存在するか確認
        words = self.model.get_words(genre_id)
        word_names = [w[2] for w in words]
        self.assertIn(word, word_names)


        # 理解度がFalseであることを確認
        for w in words:
            if w[2] == word:
                self.assertFalse(w[4])


    def test_sort_confidence(self):
        # 自信ありの単語をソートして、ソート結果に自信ありの単語が含まれているかテスト
        genre_name = "Test Genre"
        self.model.add_genre(genre_name)


        # ジャンルを取得
        genres = self.model.get_genres()
        genre_id = genres[0][0]


        word1 = "Word 1"
        details1 = "This is Word 1."
        self.model.add_word(genre_id, word1, details1, confidence=True)


        word2 = "Word 2"
        details2 = "This is Word 2."
        self.model.add_word(genre_id, word2, details2, confidence=False)


        word3 = "Word 3"
        details3 = "This is Word 3."
        self.model.add_word(genre_id, word3, details3, confidence=True)


        # 自信ありの単語をソート
        sorted_words = self.model.sort_confidence(genre_id)


        # ソート結果に自信ありの単語が含まれているか確認
        sorted_word_names = [w[2] for w in sorted_words]
        self.assertIn(word1, sorted_word_names)
        self.assertIn(word3, sorted_word_names)
        self.assertNotIn(word2, sorted_word_names)




    if __name__ == "__main__":
        unittest.main()
