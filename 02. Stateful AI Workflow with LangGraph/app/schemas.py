from typing import Literal

from pydantic import BaseModel, Field


class ReviewResult(BaseModel):
    decision: Literal["approved", "revise"] = Field(
        description="Whether the plan is approved or needs revision."
    )

    review: str = Field(
        description="Detailed explanation of the plan review."
    )

    suggestions: list[str] = Field(
        default_factory=list,
        description="Specific improvements required if revision is needed."
    )