# -*- coding: utf-8 -*-


def test_add_resource(test_db):
    ind_obj = test_db.individual('ADM1059A2')
    name = 'test-resource'
    file_path = './tests/fixtures/gene-list.txt'
    new_resource_obj = test_db.add_resource(name, file_path, ind_obj)
    assert isinstance(new_resource_obj.id, int)

    # test getting a resource
    resource_obj = test_db.resource(new_resource_obj.id)
    assert resource_obj == new_resource_obj

    # delete resource
    test_db.delete_resource(resource_obj.id)
    assert test_db.resource(resource_obj.id) is None
