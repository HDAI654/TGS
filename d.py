class Entity:
    def __str__(self):
        return f"{self.__class__.__name__}({', '.join(f'{key}={value}' for key, value in vars(self).items())})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other) -> bool:
        return self.__class__ is other.__class__ and self.id == other.id

    def __hash__(self) -> int:
        return hash((self.__class__, self.id))


class X(Entity):
    def __init__(self, id):
        self.id = id
        super().__init__()


n = {X("0"), X("1")}
print(n)
