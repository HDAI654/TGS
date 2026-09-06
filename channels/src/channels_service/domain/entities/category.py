from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Category:
    id: int
    name: str

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "name": self.name}
