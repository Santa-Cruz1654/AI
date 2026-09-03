import pytest
from pydantic import ValidationError

from app.schemas import Person


def test_valid_boundary_values():
    person = Person(
        name="John",
        age=120,
        company="Google",
        role="Engineer",
        experience_years=80,
    )

    assert person.age == 120
    assert person.experience_years == 80


def test_negative_age_is_invalid():
    with pytest.raises(ValidationError):
        Person(
            name="John",
            age=-1,
            company="Google",
            role="Engineer",
            experience_years=5,
        )


def test_age_above_120_is_invalid():
    with pytest.raises(ValidationError):
        Person(
            name="John",
            age=121,
            company="Google",
            role="Engineer",
            experience_years=5,
        )


def test_negative_experience_is_invalid():
    with pytest.raises(ValidationError):
        Person(
            name="John",
            age=30,
            company="Google",
            role="Engineer",
            experience_years=-1,
        )


def test_experience_above_80_is_invalid():
    with pytest.raises(ValidationError):
        Person(
            name="John",
            age=30,
            company="Google",
            role="Engineer",
            experience_years=81,
        )