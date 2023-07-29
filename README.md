# My単語帳

## 環境構築
- Python 3.8.11 以上
### インストール手順
1. このアプリケーションのソースコードをダウンロードまたはクローンします。
2. ターミナルまたはコマンドプロンプトを開き、ダウンロードまたはクローンしたソースコードのディレクトリに移動します。
3. 必要なライブラリをインストールします。本アプリケーションはPythonの標準ライブラリを主に使用しており、追加でインストールが必要なライブラリはありません。
### 起動方法
以下のコマンドをターミナルまたはコマンドプロンプトで実行し、アプリケーションを起動します。
```sh
python app.py
```
これでアプリケーションが正常に起動し、ご利用いただけるはずです。

## 機能

### ジャンルの追加
- スタート画面(`StartFrame`)に表示されるジャンル一覧の上部にある「＋」ボタンをクリックします。
- 新しいジャンルの追加画面(`AddGenreFrame`)が表示されます。
- 追加したいジャンル名を入力して「完了」ボタンをクリックすると、新しいジャンルが作成されます。

### ジャンルの編集と削除
- スタート画面(`StartFrame`)に表示されるジャンル一覧の各ジャンル名を右クリックします。
- ジャンルの編集画面(`GenreEditFrame`)が表示されます。
- 編集画面では、既存のジャンル名を変更することができます。
- 編集画面には「削除」ボタンもあり、ジャンルを削除することができます。

### 単語の追加
- スタート画面(`StartFrame`)に表示されるジャンル一覧の各ジャンル名をクリックします。
- そのジャンルに属する単語一覧画面(`WordListFrame`)が表示されます。
- 単語一覧画面の右上にある「＋」ボタンをクリックします。
- 新しい単語の追加画面(`AddWordFrame`)が表示されます。
- 追加したい単語名と詳細を入力して「完了」ボタンをクリックすると、新しい単語が作成されます。

### 単語の詳細の閲覧、編集と削除
- 単語一覧画面(`WordListFrame`)に表示される単語一覧の各単語名をクリックします。
- その単語の詳細画面(`WordDetailFrame`)が表示されます。
- 単語詳細画面では、単語の詳細情報を表示します。
- 単語詳細画面には「編集」ボタンがあり、これをクリックすると単語の編集画面(`WordEditFrame`)が表示されます。
- 編集画面で単語名や詳細を変更して「完了」ボタンをクリックすると、単語が編集されます。
- 編集画面には「削除」ボタンもあり、単語を削除することができます。

### 単語の理解度チェック
- 単語一覧画面(`WordListFrame`)に表示される単語一覧の下部にある「理解度チェック」ボタンをクリックします。
- 単語の理解度チェック画面(`WordCheckFrame`)が表示されます。
- 理解度チェック画面では、単語の問題が出題されます。自信がある場合は「自信あり」チェックボックスをクリックしてください。
- 問題は順番に表示され、全ての問題に解答したら終了となります。

以上の操作手順により、単語の追加、編集、削除、および単語の理解度チェックが行えます。
