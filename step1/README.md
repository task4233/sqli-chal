# step1 - 環境構築
## このステップのゴール
- 環境構築が完了し、Flagが得られていること

## 手順
### 0. (Windowsの方のみ): WSL2の環境構築
本演習ではWSL2の利用を強く推奨します。
[WSL を使用して Windows に Linux をインストールする](https://learn.microsoft.com/ja-jp/windows/wsl/install)を参考に、WSL環境の構築をお願いします。OSはUbuntuが最もポピュラーで良いと思います。もちろん、他の仮想化ソフトウェアとしてVirtualBoxやVMwareを使っても構いません。

インストール終了後に、Ubuntuにログインして`uname`を実行し、`Linux`と表示されることを確認してください。

目的はサポートをしやすくすることなので、自分で問題解決できる方はWindowsで課題に取り組んでも構いません。

### 1. ツールのインストール
今後の作業で必要になるツールをインストールしてください。

- [Git](https://git-scm.com/book/ja/v2/%E4%BD%BF%E3%81%84%E5%A7%8B%E3%82%81%E3%82%8B-Git%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB)
- [Docker(Docker Compose)](https://www.docker.com/products/docker-desktop/)
- SQLiteクライアント
- Python

以下のコマンドを実行して、各ツールのバージョンと`git ok`、`docker ok`、`docker compose ok`、`sqlite3 ok`、`python3 ok`が全て表示されることを確認したら次の手順へ進んでください。

```bash
git version && echo "git ok"
docker --version && echo "docker ok"
docker compose version && echo "docker compose ok"
sqlite3 --version && echo "sqlite3 ok"
python3 --version && echo "python3 ok"
```

実行例

```bash
> git version && echo "git ok"
docker --version && echo "docker ok"
docker compose version && echo "docker compose ok"
sqlite3 --version && echo "sqlite3 ok"
python3 --version && echo "python3 ok"

git version 2.41.0
git ok
Docker version 24.0.2, build cb74dfc
docker ok
Docker Compose version v2.18.1
docker compose ok
3.39.4 2022-09-07 20:51:41 6bf7a2712125fdc4d559618e3fa3b4944f5a0d8f8a4ae21165610e153f77aapl
sqlite3 ok
Python 3.11.4
python3 ok
```

### 2. リポジトリのフォークとクローン
リポジトリをフォークして、あなたのローカル環境にクローンしてください。

```bash
git clone https://github.com/<あなたのGitHub ID>/sqli-chall
cd sqli-chall/step1
```

### 3. SQLite3の利用
`sqli-chall/step1`ディレクトリ内にいることを確認してください。
その後、SQLite3クライアントを利用してデータベースにアクセスし、キーとなる文字列が得られることを確認してください。

```bash
sqlite3 app/step1.db
sqlite> select * from secrets;
```

SQLite3のコンソールを終了する時は `Ctrl+D` を押してください。

### 4. Flaskアプリケーションへのアクセス
`sqli-chall/step1`ディレクトリ内にいることを確認してください。
その後、以下コマンドを実行してアプリケーションを起動してください。

```bash
docker compose up
```

`step1-nginx-1  | /docker-entrypoint.sh: Configuration complete; ready for start up` というログがコンソールに表示されたら、[http://127.0.0.1:31555/](http://127.0.0.1:31555/)にブラウザでアクセスしてください。

その後、`3. SQLite3の利用`で取得したキーとなる文字列を入力してください。
`mini{...}`という文字列が得られましたか？

この形式の文字列をFlagと呼びます。今後のstepではこの文字列を得ることを目的とします。

得られたらアプリケーションを終了してください。
`docker compose up`を実行したディレクトリで`Ctrl+C`を実行した後に、`docker compose down`を実行してください。
