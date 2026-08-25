from dataclasses import dataclass
import uuid


@dataclass
class Player:
    name: str
    id: uuid.UUID

    def to_dict(self):
        return {"name": self.name, "id": str(self.id)}

    @classmethod
    def from_dict(cls, data):
        return cls(name=data["name"], id=uuid.UUID(data["id"]))
