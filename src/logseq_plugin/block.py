from dataclasses import dataclass, field


@dataclass
class Block:
    id: int = 0
    uuid: str = ""
    content: str = ""
    properties: dict = field(default_factory=dict)
    children: list = field(default_factory=list)
    parent: str = ""
