from puzzle.plugins import GeminiPlugin

def test_get_individuals(gemini_path):
    adapter = GeminiPlugin(db=gemini_path)
    
    ind_ids = [ind.ind_id for ind in adapter.get_individuals()]
    assert set(ind_ids) == set(['NA12877', 'NA12878', 'NA12882'])

def test_get_individuals_one_ind(gemini_path):
    adapter = GeminiPlugin(db=gemini_path)
    
    ind_ids = [ind.ind_id for ind in adapter.get_individuals('NA12877')]
    assert set(ind_ids) == set(['NA12877'])

def test_get_individuals_two_inds(gemini_path):
    adapter = GeminiPlugin(db=gemini_path)
    
    ind_ids = [ind.ind_id for ind in adapter.get_individuals('NA12877', 'NA12878')]
    assert set(ind_ids) == set(['NA12877', 'NA12878'])

def test__get_individuals(gemini_path):
    adapter = GeminiPlugin(db=gemini_path)
    
    ind_ids = [ind.ind_id for ind in adapter._get_individuals()]
    assert set(ind_ids) == set(['NA12877', 'NA12878', 'NA12882'])

def test__get_cases(gemini_path):
    adapter = GeminiPlugin(db=gemini_path)
    
    individuals = adapter._get_individuals()
    case_ids = [case.case_id for case in adapter._get_cases(individuals)]
    assert set(case_ids) == set(['643594'])

def test_cases(gemini_path):
    adapter = GeminiPlugin(db=gemini_path)
    
    case_ids = [case.case_id for case in adapter.cases()]
    assert set(case_ids) == set(['643594'])

def test_case(gemini_path):
    adapter = GeminiPlugin(db=gemini_path)
    
    case_id = '643594'
    assert adapter.case(case_id).case_id == case_id

def test_case_no_id(gemini_path):
    adapter = GeminiPlugin(db=gemini_path)
    
    case_id = '643594'
    assert adapter.case().case_id == case_id

def test_case_wrong_id(gemini_path):
    adapter = GeminiPlugin(db=gemini_path)
    
    case_id = 'hello'
    assert adapter.case(case_id) == None
