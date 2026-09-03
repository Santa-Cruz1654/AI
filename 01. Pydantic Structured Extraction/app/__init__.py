from pydantic import BaseModel, Field


class Person(BaseModel):
    name: str = Field(
        description="The person's full name"
    )

    age: int = Field(
        description="The person's age in years"
    )

    company: str = Field(
        description="The company where the person works"
    )

    role: str = Field(
        description="The person's job role"
    )

    experience_years: int = Field(
        description="The person's total years of professional experience"
    )