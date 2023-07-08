## sqli-chal
### 講義タイトル
『脆弱性スキャナ開発を通して脆弱性の理解を深めよう！』

### 想定対象者
基礎知識の如何にかかわらず、情報セキュリティについて学びたいという意欲を持った方

### はじめに
脆弱性スキャナの実装を通して**脆弱性に対する理解を深めることを目的とした講義**です。扱う脆弱性は、応募課題のうち全体の4分の1を占めていたSQL Injectionとします。

<details>
<summary>応募課題で選択された脆弱性の種類と件数</summary>

脆弱性でないものはその他に分類しました。

|脆弱性の種類|件数|
|:-:|:-:|
|SQL Injection|4|
|XSS|3|
|CSRF|1|
|SSRF|1|
|Prototype Pollution|1|
|Directory Traversal(Path Traversal)|1|
|Information Disclosure|1|
|その他|N/A|

</details>

### 本講義のゴール
1. 脆弱性スキャナの仕組みを知ること
2. 脆弱性を悪用するペイロードを構築すること
3. (Optional) 簡易的な脆弱性スキャナを実装して脆弱性を検出すること

これらを満たすために、本講義ではstep0からstep5(+1)までの6(+1)つのステップを通して、段階的に理解を深めていただきます。最後まで到達できるかは分かりませんが、可能な限りサポートはします。一緒に頑張りましょう！

### Steps
- [ ] [step0 - 調べ方と質問の仕方](./step0)
- [ ] [step1 - 環境構築](./step1)
- [ ] [step2 - SQL Injectionを試す](./step2)
- [ ] [step3 - sqlmapを使う](./step3)
- [ ] [step4 - sqlmapの実装を読む](./step4)
- [ ] [step5 - sqlmapのコードを参考に簡易的なスキャナを実装する](./step5)
- [ ] step6(Optional) - 自力でで簡易的なスキャナのコードを実装する
- [ ] appendix(./appendix)
