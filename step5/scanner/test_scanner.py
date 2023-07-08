from scanner import (
    construct_payloads,
    Payload,
    calc_similarity_between_given_two_values,
)


def test_construct_payloads_response():
    # key_nameが付与されない場合、空のリストが返却されるか
    assert [] == construct_payloads("")

    # key_nameが付与された場合、Payloadを含むリストが返却されるか
    key_name = "dummy key"
    payloads = construct_payloads(key_name)
    assert any(payloads)
    assert any([isinstance(p, Payload) and p.key == key_name for p in payloads])


def test_get_response_with_payload():
    pass


def test_calc_similarity_between_given_two_values():
    # 類似度を計算すると、0以外の値が返却されるか
    assert calc_similarity_between_given_two_values("hoge", "hoge") != 0

    # 異なる文字列のペアに関しては異なる値が返却されるか
    similarity1 = calc_similarity_between_given_two_values("hoge", "fuga")
    similarity2 = calc_similarity_between_given_two_values("hoge", "hoge")
    assert similarity1 != similarity2


def test_output_vulnerabilities():
    pass
