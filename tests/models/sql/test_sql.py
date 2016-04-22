from puzzle.models.sql import Case, Individual, BASE

def test_case(session):
    """Test to add a case to the session"""
    # proband = Individual(ind_id="Proband")
    family = Case(case_id="afamily")
    # proband.case = family
    session.add(family)
    session.commit()

    fam = session.query(Case).filter(Case.case_id == "afamily").one()
    assert fam.id == 1

def test_individual(session):
    """Test to add a case to the session"""
    # proband = Individual(ind_id="Proband")
    family = Case(case_id="2")
    proband = Individual(ind_id="Proband")
    proband.cases.append(family)
    session.add(proband)
    session.add(family)
    session.commit()

    fam = session.query(Case).filter(Case.case_id == "2").one()
    assert fam.individuals[0].ind_id == "Proband"
    