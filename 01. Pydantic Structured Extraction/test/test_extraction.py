import pytest

from app.extractor import ExtractionError, extract_person


def test_normal_person_extraction():
    text = """
    John Smith is 28 years old and works at Google
    as a Software Engineer. He has 5 years of experience.
    """

    person = extract_person(text)

    assert person.name == "John Smith"
    assert person.age == 28
    assert person.company == "Google"
    assert person.role == "Software Engineer"
    assert person.experience_years == 5


def test_different_wording():
    text = """
    Sarah is a 32-year-old backend engineer at Microsoft.
    She has been working professionally for 8 years.
    """

    person = extract_person(text)

    assert person.name == "Sarah"
    assert person.age == 32
    assert person.company == "Microsoft"
    assert person.role == "backend engineer"
    assert person.experience_years == 8


def test_missing_information():
    text = """
    Michael works at Amazon as a Data Scientist.
    """

    person = extract_person(text)

    assert person.name == "Michael"
    assert person.company == "Amazon"
    assert person.role == "Data Scientist"
    assert person.age is None
    assert person.experience_years is None


def test_ambiguous_information():
    text = """
    John is an experienced engineer at Google.
    He joined the company when he was 25.
    """

    person = extract_person(text)

    assert person.name == "John"
    assert person.company == "Google"
    assert person.role == "engineer"
    assert person.age is None
    assert person.experience_years is None


def test_invalid_information():
    text = """
    John Smith is -10 years old and works at Google
    as a Software Engineer. He has -5 years of experience.
    """

    with pytest.raises(ExtractionError):
        extract_person(text)


def test_invalid_information_raises_extraction_error():
    text = """
    John Smith is -10 years old and works at Google
    as a Software Engineer. He has -5 years of experience.
    """

    with pytest.raises(ExtractionError) as exc_info:
        extract_person(text)

    assert str(exc_info.value) == (
        "The LLM could not produce valid structured output."
    )


def test_missing_age_only():
    text = """
    Sarah is a backend engineer at Microsoft.
    She has 8 years of professional experience.
    """

    person = extract_person(text)

    assert person.name == "Sarah"
    assert person.company == "Microsoft"
    assert person.role == "backend engineer"
    assert person.age is None
    assert person.experience_years == 8


def test_missing_experience_only():
    text = """
    David is 35 years old and works at Amazon
    as a Data Scientist.
    """

    person = extract_person(text)

    assert person.name == "David"
    assert person.age == 35
    assert person.company == "Amazon"
    assert person.role == "Data Scientist"
    assert person.experience_years is None