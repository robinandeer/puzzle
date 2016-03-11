from puzzle.plugins import GeminiPlugin

def test_get_individuals(gemini_case_obj):
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)
    
    ind_ids = [ind.ind_id for ind in adapter.individual_objs]
    assert set(ind_ids) == set(['NA12877', 'NA12878', 'NA12882'])

def test_get_individuals_one_ind(gemini_case_obj):
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    ind_ids = [ind.ind_id for ind in adapter.individuals('NA12877')]
    assert set(ind_ids) == set(['NA12877'])

def test_get_individuals_two_inds(gemini_case_obj):
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    ind_ids = [ind.ind_id for ind in adapter.individuals('NA12877', 'NA12878')]
    assert set(ind_ids) == set(['NA12877', 'NA12878'])

def test__get_individuals(gemini_case_obj):
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    ind_ids = [ind.ind_id for ind in adapter.individuals()]
    assert set(ind_ids) == set(['NA12877', 'NA12878', 'NA12882'])

def test_cases(gemini_case_obj):
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    case_ids = [case.case_id for case in adapter.cases()]
    assert set(case_ids) == set(['643594'])

def test_case_objs(gemini_case_obj):
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    case_ids = [case.case_id for case in adapter.case_objs]
    assert set(case_ids) == set(['643594'])

def test_case(gemini_case_obj):
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    case_id = '643594'
    assert adapter.case(case_id).case_id == case_id

def test_case_no_id(gemini_case_obj):
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    case_id = '643594'
    assert adapter.case().case_id == case_id

def test_case_wrong_id(gemini_case_obj):
    adapter = GeminiPlugin()
    adapter.add_case(gemini_case_obj)

    case_id = 'hello'
    assert adapter.case(case_id) == None
