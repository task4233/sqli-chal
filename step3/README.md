# step3 - sqlmapを触る
## このステップのゴール
- sqlmapを実行して、結果を得ることができる。

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

これらのオプションを適切に設定して、実行してみましょう。

### 3. sqlmapの実行

sqlmapを実行すると、次のような結果が得られると思います。

```plaintext
Parameter: name (GET)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: name=-9901' OR 6151=6151-- FfuT

    Type: UNION query
    Title: Generic UNION query (NULL) - 4 columns
    Payload: name=test' UNION ALL SELECT NULL,NULL,NULL,CHAR(113,120,112,122,113)||CHAR(81,73,101,97,75,99,82,98,77,115,115,120,117,118,122,120,99,121,89,66,99,80,105,86,90,88,69,98,105,107,119,102,88,102,102,70,77,122,119,77)||CHAR(113,118,107,120,113)-- EqlQ
```

この結果のうち、boolean-basedの方に注目してみましょう。表にすると以下のような形になります。

|属性|値|
|:-:|:-:|
|Type|boolean-based blind|
|Title|OR boolean-based blind - WHERE or HAVING clause|
|Payload|`name=-9901' OR 6151=6151-- FfuT`|

この結果から、`OR boolean-based blind`という攻撃の `WHERE` もしくは `HAVING` 句を利用した攻撃であることが分かります。そして、実際のペイロードは、`name=-9901' OR 6151=6151-- FfuT`です。実際に埋め込んで考えてみると良いです。

```sql
SELECT * FROM users WHERE name LIKE '%name=-9901' OR 6151=6151-- FfuT%' AND is_admin=0
```

このクエリを見ると、step2で確認したクエリとよく似ていることがわかります。OR条件で必ず成立するものを入れて、最後の条件を無視するようにしていることがわかります。

念の為、step2と同様に機能することを確認しましょう。`$ docker compose up`でコンテナを起動し、[http://127.0.0.1:31555/](http://127.0.0.1:31555/)にブラウザでアクセスしてください。その後、`name=-9901' OR 6151=6151-- FfuT`で検索してみます。すると、結果が出力されることが分かります。

しかし、ブラウザのアドレスバーを見ると、`http://localhost:31555/?name=name%3D-9901%27+OR+6151%3D6151--+FfuT`のように`name`が重複していることが分かります。したがって、`http://localhost:31555/?`の後に`name%3D-9901%27+OR+6151%3D6151--+FfuT`
を付与すれば良いことが分かります。この`?`以降に書く記法については、[MDNのドキュメント](https://developer.mozilla.org/ja/docs/Web/HTTP/Basics_of_HTTP/Identifying_resources_on_the_Web#%E3%82%AF%E3%82%A8%E3%83%AA)をご覧ください。

では、次の[step4 - sqlmapの実装を読む](../step4/)では、このクエリをどのように検出しているか確認していきましょう。
