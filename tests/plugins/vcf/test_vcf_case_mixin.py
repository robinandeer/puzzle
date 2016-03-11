from puzzle.plugins import VcfPlugin

def test_add_case(case_obj):
    adapter=VcfPlugin()
    adapter.add_case(case_obj)
    assert len(adapter.individual_objs) == 3
    case_obj = adapter.case_objs[0]
    assert case_obj.name == "636808"

def test__add_individual(individual):
    adapter=VcfPlugin()
    adapter._add_individual(individual)
    assert len(adapter.individual_objs) == 1

def test_cases(case_obj):
    adapter=VcfPlugin()
    adapter.add_case(case_obj)
    case_id = "636808"
    case_obj = adapter.cases()[0]
    assert case_obj.name == "636808"

def test_case(case_obj):
    adapter=VcfPlugin()
    adapter.add_case(case_obj)
    case_id = "636808"
    case_obj = adapter.case(case_id)
    assert case_obj.case_id == case_id

def test_individual(case_obj):
    adapter=VcfPlugin()
    adapter.add_case(case_obj)
    
    ind_id = "ADM1059A1"
    ind_obj = adapter.individual(ind_id)
    assert ind_obj.ind_id == ind_id

def test_individuals(case_obj):
    adapter=VcfPlugin()
    adapter.add_case(case_obj)
    
    individuals = [ind for ind in adapter.individuals()]
    assert len(individuals) == 3
