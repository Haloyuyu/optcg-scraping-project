from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Card:
    """Card data model."""
    card_name: str
    card_id: Optional[str] = None
    set_name: Optional[str] = None
    rarity: Optional[str] = None
    color: Optional[str] = None
    card_type: Optional[str] = None
    cost: Optional[str] = None
    life: Optional[str] = None
    power: Optional[str] = None
    attribute: Optional[str] = None
    counter: Optional[str] = None
    effect: Optional[str] = None
    feature: Optional[str] = None
    block: Optional[str] = None
    image_url: Optional[str] = None

    def to_dict(self):
        return asdict(self)