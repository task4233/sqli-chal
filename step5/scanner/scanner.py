# 実装方針
# 1. ペイロードを構築する
# 2. ペイロードをリクエストして、レスポンスを取得する
# 3. 通常のレスポンスとリクエストした結果を比較して大きな差があれば脆弱性があると判断する
# 4. 検出結果を出力する

from typing import List, TextIO
import argparse
import sys
import requests

MIN_THRESHOLD = 0.05
MAX_THRESHOLD = 0.95


class Payload:
    """
    Payload manages information to occur SQL Injection.

    Payload はSQL Injectionを引き起こす情報を管理します。
    """

    def __init__(self, key: str, value: str) -> None:
        self.key = key
        self.value = value


class Response:
    """
    Response manages information returned from a target.

    Response はターゲットから返却された情報を管理します。
    """

    def __init__(self, text: str) -> None:
        self.text = text


class Vulnerability:
    """
    Vulnerability は脆弱性を管理します。
    """

    def __init__(self, resp: str) -> None:
        self.resp = resp


def construct_payloads(key_name: str) -> List[Payload]:
    """
    construct_payloads returns constructed payload list to occur SQL Injection.

    construct_payloads はSQL Injectionを引き起こすために構築されたペイロードリストを返却します。
    """

    # キー名が空の時は設定できないので、空のリストを返却する。
    if key_name == "":
        return []

    payload_list = [
        # TODO-1: ここに構築したペイロードを追加してください
    ]
    return [Payload(key_name, payload) for payload in payload_list]


def get_response_with_payload(
    target_url: str, method: str = "GET", payload: Payload = None
) -> Response:
    """
    get_response_with_payload returns response by sending a request with given payload.

    get_response_with_payload は渡されたペイロードと共にリクエストを送ることによるレスポンスを返却します。

    """
    params = None
    if payload is not None:
        params = {payload.key: payload.value}

    # TODO-2: HTTPリクエストを送って、結果を取得する部分を書いてください
    return Response()


def calc_similarity_between_given_two_values(val1: str, val2: str) -> float:
    """
    calc_similarity_between_given_two_values returns similarity of given two values.

    calc_similarity_between_given_two_values は渡された2つの値の類似度を返却します。
    """

    # TODO-3: similarityを算出する部分を書いてください
    return 0.0


def output_vulnerabilities(results: List[Vulnerability], out: TextIO = sys.stdout):
    """
    output_vulnerabilities output given vulnerabilities to specified output resource.
    out parameter is optional value, if not given, out is set as sys.stdout.
    """

    # TODO-4: 結果を出力する部分を書いてください
    pass


def parse_args() -> tuple[str, str]:
    parser = argparse.ArgumentParser("SQL Injection用の脆弱性スキャナの実装デモ")
    parser.add_argument("-u", type=str, required=True, help="対象リソースのuriを指定します")
    parser.add_argument("-p", type=str, required=True, help="インジェクトできるパラメータ名を指定します")

    args = parser.parse_args()
    return args.u, args.p


def main():
    # 2. コマンドライン引数をパースします。
    # 例えば、python3 scanner.py -u http://localhost:31555 -p nameで実行されたとき、
    # target_urlにはhttp://localhost:31555が、key_nameにはnameが格納されます。
    target_url, key_name = parse_args()
    vulnerabilities = []

    # 3. 正常系のHTTPレスポンスを保持します。
    normal_response = get_response_with_payload(target_url)

    # 4. SQL Injectionを引き起こすためのペイロードをpayloadsに格納します。
    payloads = construct_payloads(key_name)

    # 5. forループでそれぞれのペイロードを検証します。
    for payload in payloads:
        # 5-1. SQL Injectionを引き起こすためのペイロードを用いた場合のHTTPレスポンスを受け取ります。
        response = get_response_with_payload(
            target_url=target_url,
            payload=payload,
        )
        if response is None:
            continue

        # 5-2. 正常系のHTTPレスポンスとSQL Injectionを引き起こすためのペイロードを用いた場合のHTTPレスポンス
        # との類似度を算出します。
        similarity = calc_similarity_between_given_two_values(
            normal_response.text, response.text
        )
        # 5-3. もし、類似度がMIN_THRESHOLD <= 類似度 < MAX_THRESHOLDの範囲に含まれていない場合に、
        # 脆弱性のあるレスポンスとして検出します。
        if not (MIN_THRESHOLD <= similarity and similarity < MAX_THRESHOLD):
            vulnerabilities.append(Vulnerability(response.text))

    # 6. 発見された結果を出力します。
    output_vulnerabilities(vulnerabilities)


if __name__ == "__main__":
    # 1. main関数が実行されます。
    main()
