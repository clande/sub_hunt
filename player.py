from dataclasses import dataclass, field
import random
import uuid


@dataclass
class Player:
    name: str
    id: uuid.UUID
    sub_location: tuple[int, int] = field(
        default_factory=lambda: (random.randrange(50), random.randrange(50))
    )

    def to_dict(self):
        return {
            "name": self.name,
            "id": str(self.id),
            "sub_location": list(self.sub_location),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            id=uuid.UUID(data["id"]),
            sub_location=tuple(data["sub_location"]),
        )
