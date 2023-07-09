# step5 - sqlmapの実装を参考に簡易的なスキャナを実装する
## このステップのゴール
- sqlmapの実装を参考に簡易的なスキャナを実装すること

## はじめに

このステップでは1つ前で調査したsqlmapの実装を参考に、簡易的なスキャナを実装することを目的とします。

フルスクラッチで実装できる人は、ここから先は読まずに実装してみてください。実装言語はお好みのものを使ってください。  
もしフルスクラッチで実装することが不安という方がいれば、[私が用意したサンプルファイル](./scanner/scanner.py)を穴埋めするなり編集するなりして実装してみてください。

実装できたら、(可能なら)Pull Requestを作っても良いです。その場合、レビューします。

### ロジックを考える
まず、実装をする前にロジックを考えることが肝要です。行き当たりばったりで実装をしてしまい、まとまりのないコードを書いてしまうことはよくあることです。今回は簡単のためにロジックを以下の4パーツに分けました。

1. ペイロードを構築する
2. ペイロードをリクエストして、レスポンスを取得する
3. 通常のレスポンスとリクエストした結果を比較して大きな差があれば脆弱性があると判断する
4. 検出結果を出力する

スキャナと言えど、簡単なスクリプトで構成されています。

上記のロジックを参考に実装してみてください。

### scanner.pyの全体像を理解する
ロジックの肝は、**正常なリクエストを送った時に得られるHTTPレスポンスと、異常なペイロードを含むリクエストを送った時に得られるHTTPレスポンスに大きな違いがあればSQL Injectionの脆弱性があると判断する** ことです。その上で、[scanner.py](./scanner/scanner.py)に書かれている、`1.`から`6.`までの処理手順のコメントを確認してみましょう。

1. main関数が実行されます。
2. コマンドライン引数をパースします。  
2-1. 例えば、`$ python3 scanner.py -u http://localhost:31555 -p name`というコマンドが実行されたとき、`target_url`には`http://localhost:31555`が、`key_name`には`name`が格納されます。
3. 正常系のHTTPレスポンスを保持します。
4. SQL Injectionを引き起こすためのペイロードをpayloadsに格納します。
5. forループでそれぞれのペイロードを検証します。  
5-1. SQL Injectionを引き起こすためのペイロードを用いた場合のHTTPレスポンスを受け取ります。  
5-2. 正常系のHTTPレスポンスとSQL Injectionを引き起こすためのペイロードを用いた場合のHTTPレスポンスとの類似度を算出します。  
5-3. もし、類似度が`MIN_THRESHOLD <= 類似度 < MAX_THRESHOLD`の範囲に含まれていない場合に、脆弱性のあるレスポンスとして検出します。
6. 発見された結果を出力します。

以上の流れでプログラムが実行されます。

### 1. ペイロードを構築する
scanner.pyにおける`# TODO-1`とコメントされている部分に注目してください。

```python
payload_list = [
    # TODO-1: ここに構築したペイロードを追加してください
]
```

という部分がありますね。ここに、あなたが構築したペイロードを追加してください。

<details>
<summary>参考実装(ここをクリックすると表示されます)</summary>

例えば、

```python
payload_list = [
    # TODO-1: ここに構築したペイロードを追加してください
    "\' OR 1=1 -- ",
]
```

のようなものです。ペイロードリストはググれば出てくるので、好きなものを使ってください。動的に生成させても構いません。

</details>

### 2. ペイロードをリクエストして、レスポンスを取得する。
scanner.pyにおける`# TODO-2`とコメントされている部分に注目してください。

```python
params = None
if payload is not None:
    params = {payload.key: payload.value}

# TODO-2: HTTPリクエストを送って、結果を取得する部分を書いてください
return Response()
```

こちらにHTTPリクエストを送ってHTTPレスポンスを取得する処理を書いてみましょう。HTTPリクエストを送れるライブラリはいくつかありますね。

<details>
<summary>参考実装(ここをクリックすると表示されます)</summary>

今回提示する例では[requests](https://requests.readthedocs.io/en/latest/)を利用します。実装すると以下のようになります。

```python
s = Session()
req = Request(method, target_url, params=params)
prep = s.prepare_request(req)
resp = s.send(prep)
return Response(resp.text)
```

単純に`res = request.get(target_url, params=params)`のように書いても良いです。ただ、今後の拡張性を考えたときに任意のHTTPメソッドに対応したいので、このような書き方を提示しました。最初は動くことを目標としているので、どのような書き方でも良いです。

</details>

### 3. 通常のレスポンスとリクエストした結果を比較して大きな差があれば脆弱性があると判断する

scanner.pyにおける`# TODO-3`とコメントされている部分に注目してください。

```python
# TODO-3: similarityを算出する部分を書いてください
return 0.0
```

ここに類似度を算出する実装を書いてください。[sqlmapではdifflibを利用している](https://github.com/sqlmapproject/sqlmap/blob/bb48dd037f04d60d5d2804657f44444eefa07f93/lib/core/threads.py#L10)ので、difflibを用いた実装が一番楽かもしれません。

<details>
<summary>参考実装(ここをクリックすると表示されます)</summary>

今回は[sqlmapで利用されているSequenceMatcher](https://github.com/sqlmapproject/sqlmap/blob/bb48dd037f04d60d5d2804657f44444eefa07f93/lib/core/threads.py#L66)を利用する例を提示します。

```python
# TODO-3: similarityを算出する部分を書いてください
matcher = difflib.SequenceMatcher()
matcher.set_seq1(val1)
matcher.set_seq2(val2)
return matcher.quick_ratio()
```

</details>

### 4. 検出結果を出力する

scanner.pyにおける`# TODO-4`とコメントされている部分に注目してください。

```python
# TODO-4: 結果を出力する部分を書いてください
pass
```

ここに実装を書いてください。関数の引数で、outと呼ばれる`TextIO`が渡されているので、そちらも利用できると良さそうです。

<details>
<summary>参考実装(ここをクリックすると表示されます)</summary>

[builtin関数の`print()`](https://docs.python.org/3/library/functions.html#print)を使うことで以下のように実装できます。


```python
# TODO: 結果を出力する部分を書いてください
for result in results:
    print(result.resp, file=out)
```

個の出力方法だと分かりづらいので、正常系との差分を出力するコードを以下のように実装しても良いです。

```python
diffs = difflib.unified_diff(val1.split(), val2.split())
for d in diffs:
    print(d, file=out)
```

</details>

### 最終的な参考実装
参考実装は[step5/scanner/sample_scanner.py](./scanner/sample_scanner.py)にあります。どうしても分からない場合は参照してください。

