# -*- coding: utf-8 -*-
from flask import url_for


def test_variants(client):
    res = client.get(url_for('variants.variants',
                     case_id='tests|fixtures|15031.vcf'))
    assert res.status_code == 200

    # test with skip
    res = client.get(url_for('variants.variants',
                     case_id='tests|fixtures|15031.vcf', skip=30))
    assert res.status_code == 200
