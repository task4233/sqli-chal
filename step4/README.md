# step4 - sqlmapの実装を読む
## このステップのゴール
- sqlmapの実装を読み、検出ロジックを理解すること

## はじめに

1つ前のステップで、次のようなSQL文を実行することで脆弱性があると検出できていました。この章では、どのようにしてそれを検出しているかを確認していきましょう。

```sql
SELECT * FROM users WHERE name LIKE '%name=-9901' OR 6151=6151-- FfuT%' AND is_admin=0
```

## 手順
順番にコードを読んでいきます。

ソースコードを読む時は次のようなやり方などがあります。

- プログラムのエントリポイントから順番に読む
- プログラムの似ている部分から読む

今回は出力からソースコードを追ってみます。先ほどの結果をまた見てみましょう。

|属性|値|
|:-:|:-:|
|Type|boolean-based blind|
|Title|OR boolean-based blind - WHERE or HAVING clause|
|Payload|`name=-9901' OR 6151=6151-- FfuT`|

今回は特徴的な `OR boolean-based blind - WHERE or HAVING clause` に注目してコード検索してみます。私はVS Codeを利用しますが、宗教戦争を起こしたい訳ではないので、各自好きなエディタを使って検索してください。

すると、`data/xml/payloads/boolean_blind.xml` というファイルに記述が見つかります([ref](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/data/xml/payloads/boolean_blind.xml#L174C1-L188))。このファイルを利用している所を探すと、`PAYLOAD_XML_FILES` という変数を利用している `settings.py` というファイルがあることが分かります([ref](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/core/settings.py#L867))。この変数が利用されている場所は、[payloads.py](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/core/settings.py#L867)です。

これを続けていくと、以下のような順序で読み解くことができます。

- [data/xml/payloads/boolean_blind.xml#L174C1-L188](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/data/xml/payloads/boolean_blind.xml#L174C1-L188)
- [lib/core/settings.py#L867](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/core/settings.py#L867)
- [lib/parse/payloads.py#L110](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/parse/payloads.py#L110)
  - [parseXmlNode(root)](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/parse/payloads.py#L43)内で`conf.tests`を更新していることが分かる
- [lib/core/common.py#L3726](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/core/common.py#L3726)
- [lib/controller/checks.py#L130](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/controller/checks.py#L130)
- [lib/controller/checks.py#L554](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/controller/checks.py#L554)
  - ここでTrue判定をしている
  - Injectableであることを確認
- [lib/controller/checks.py#L731](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/controller/checks.py#L731)
  - injectableがTrueだった時の挙動
- [lib/controller/checks.py#L766-L783](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/controller/checks.py#L766-L783)
  - injectした時の情報を保存


最終的に、以下の検出ロジックに辿り着きます([ref](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/controller/checks.py#L526-L531))。

```python
# Perform the test's True request
# 
trueResult = Request.queryPage(reqPayload, place, raise404=False)
truePage, trueHeaders, trueCode = threadData.lastComparisonPage or "", threadData.lastComparisonHeaders, threadData.lastComparisonCode
trueRawResponse = "%s%s" % (trueHeaders, truePage)

if trueResult and not(truePage == falsePage and not any((kb.nullConnection, conf.code))):
```

このif文がいつ成立するか考えてみます。そのために、`Request.queryPage`の実装を追う必要がありそうです。この実装は、[lib/request/connect.py#L984](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/request/connect.py#L984)にあります。

```python
def queryPage(
  value=None,
  place=None,
  content=False,
  getRatioValue=False,
  silent=False,
  method=None,
  timeBasedCompare=False,
  noteResponseTime=True,
  auxHeaders=None,
  response=False,
  raise404=None,
  removeReflection=True,
  disableTampering=False,
  ignoreSecondOrder=False
):
```

色々見ていくと、最終的にreturnされる値が分かります([ref](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/request/connect.py#L1597-L1603))。

```python
if content or response:
    return page, headers, code
if getRatioValue:
    return comparison(page, headers, code, getRatioValue=False, pageLength=pageLength), comparison(page, headers, code, getRatioValue=True, pageLength=pageLength)
else:
    return comparison(page, headers, code, getRatioValue, pageLength)
```

ここで、`content`、`response`、`getRatioValue`は基本的に`False`が設定されるはずであることが分かります([ref](https://docs.python.org/ja/3.11/reference/expressions.html#boolean-operations))。したがって、`return comparison(page, headers, code, False, pageLength)`が呼ばれるはずです。この`comparison`の実装を追ってみましょう([ref](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/request/comparison.py#L37))。

comparison周りの実装は[lib/request/comparison.py](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/request/comparison.py#L37)にあります。

```python
def comparison(page, headers, code=None, getRatioValue=False, pageLength=None):
    _ = _adjust(_comparison(page, headers, code, getRatioValue, pageLength), getRatioValue)
    return _

def _adjust(condition, getRatioValue):
    if not any((conf.string, conf.notString, conf.regexp, conf.code)):
        # Negative logic approach is used in raw page comparison scheme as that what is "different" than original
        # PAYLOAD.WHERE.NEGATIVE response is considered as True; in switch based approach negative logic is not
        # applied as that what is by user considered as True is that what is returned by the comparison mechanism
        # itself
        retVal = not condition if kb.negativeLogic and condition is not None and not getRatioValue else condition
    else:
        retVal = condition if not getRatioValue else (MAX_RATIO if condition else MIN_RATIO)

    return retVal

def _comparison(page, headers, code, getRatioValue, pageLength):
    # 略
    # If it has been requested to return the ratio and not a comparison
    # response
    if getRatioValue:
        return ratio

    elif ratio > UPPER_RATIO_BOUND:
        return True

    elif ratio < LOWER_RATIO_BOUND:
        return False

    elif kb.matchRatio is None:
        return None

    else:
        return (ratio - kb.matchRatio) > DIFF_TOLERANCE
```

このratioの計算には`difflib`を利用しており、単純にdiffの割合を出力しています。初期化は[ここ]()で、ratioの計算は[この辺り](https://github.com/sqlmapproject/sqlmap/blob/df388b2150fe00b045185d1f32d4d714cd567597/lib/request/comparison.py#L160-L166)で実施されています。

```python
seqMatcher.set_seq1(seq1)
seqMatcher.set_seq2(seq2)

if key in kb.cache.comparison:
    ratio = kb.cache.comparison[key]
else:
    ratio = round(seqMatcher.quick_ratio() if not kb.heavilyDynamic else seqMatcher.ratio(), 3)
```

この `seq1`には通常のページ状態が、`seq2`には引数に指定された`page`の値が指定されるため、この`comparison`ロジックはデフォルトのページ状態と渡されたページロジックの違いの指標として類似度を算出し、類似度が低い場合はinjectできたと判断するロジックになっていることがわかりました。

次の[step5 - sqlmapの実装を参考に簡易的なスキャナを実装する](../step5/)では、このロジックを参考に簡易的なスキャナを(穴埋めで)実装してみましょう。

