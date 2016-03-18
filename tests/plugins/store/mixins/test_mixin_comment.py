# -*- coding: utf-8 -*-
from puzzle.models.sql import Comment

def test_add_comment_case(test_db):
    text = 'test-comment'
    case_obj = test_db.cases().first()
    comment_obj = test_db.add_comment(case_obj, text)
    assert isinstance(comment_obj, Comment)
    assert comment_obj.text == text

def test_add_comment_variant(test_db, variant):
    text = 'variant-comment'
    case_obj = test_db.cases().first()
    comment_obj = test_db.add_comment(case_obj, text, variant.md5)

    assert isinstance(comment_obj, Comment)
    assert comment_obj.text == text
    assert comment_obj.variant_id == variant.md5

def test_get_comments_variant(test_db, variant):
    text = 'variant-comment'
    case_obj = test_db.cases().first()
    test_db.add_comment(case_obj, text, variant.md5)

    query = test_db.comments(variant_id=variant.md5)
    for comment in query:
        assert comment.case_id == case_obj.id
        assert comment.variant_id == variant.md5

    assert query.count() == 1
    comment_obj = query.first()

    assert isinstance(comment_obj, Comment)
    assert comment_obj.text == text

def test_get_comments(test_db):
    text = 'test-comment'
    case_obj = test_db.cases().first()
    test_db.add_comment(case_obj, text)
    comments = []
    for comment in test_db.comments(case_obj.id):
        assert comment.case_id == case_obj.id
        comments.append(comment)
    assert len(comments) == 1
    comment_obj = comments[0]
    assert comment_obj.text == text


def test_get_comment(test_db):
    text = 'test-comment'
    case_obj = test_db.cases().first()
    comment_obj = test_db.add_comment(case_obj, text)
    new_comment_obj = test_db.comment(comment_obj.id)
    assert new_comment_obj.text == text

def test_delete_comment(test_db):
    text = 'test-comment'
    case_obj = test_db.cases().first()
    comment_obj = test_db.add_comment(case_obj, text)

    test_db.delete_comment(comment_obj.id)

    comments = []
    for comment in test_db.comments(case_obj.id):
        comments.append(comment)
    assert len(comments) == 0


def test_update_synopsis(test_db):
    text = '# header'
    case_obj = test_db.cases().first()
    test_db.update_synopsis(case_obj, text)

    updated_case_obj = test_db.cases().first()
    assert updated_case_obj.synopsis == text
