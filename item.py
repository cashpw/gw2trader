from dataclasses import dataclass

@dataclass
class Item():
    """Represents a Guild Wars 2 item."""

    id: int
    name: str
