from pydantic import BaseModel, Field


class Person(BaseModel):
    name: str = Field(
        description="The person's full name."
    )

    age: int | None = Field(
        default=None,
        description=(
            "The person's current age in years. "
            "Only extract the age if the text clearly refers to "
            "the person's current age. Do not use historical ages, "
            "such as the age when the person joined a company."
        ),
        ge=0,
        le=120,
    )

    company: str = Field(
        description="The company where the person works."
    )

    role: str = Field(
        description="The person's job role."
    )

    experience_years: int | None = Field(
        default=None,
        description=(
            "The person's total years of professional experience. "
            "Only extract this when the number of years of experience "
            "is explicitly stated. Do not infer it."
        ),
        ge=0,
        le=80,
    )