# -*- coding: utf-8 -*-
from flask import url_for


def test_index(client):
    res = client.get(url_for('public.index'))
    assert res.status_code == 200
    assert b'hapmap.vcf' in res.data
