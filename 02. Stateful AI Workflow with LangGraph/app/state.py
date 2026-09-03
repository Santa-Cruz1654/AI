from typing_extensions import TypedDict


class State(TypedDict):
    request: str
    analysis: str
    plan: str
    review: str
    suggestions: list[str]
    approval: bool
    revision_count: int
    final_response: str
    error: str