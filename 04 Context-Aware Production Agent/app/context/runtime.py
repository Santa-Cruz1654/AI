from dataclasses import dataclass


@dataclass
class RuntimeContext:
    user_id: str
    account_type: str
    permissions: list[str]
    environment: str
    region: str