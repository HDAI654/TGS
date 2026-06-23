from src.core.entity import Entity


class TestEntity:
    def test_str_entity(self):
        entity = Entity()
        entity.id = "ID:)"
        entity.name = "Marshall"

        assert entity.__str__() == "Entity(id=ID:), name=Marshall)"

    def test_repr_entity(self):
        entity = Entity()
        entity.id = "ID:)"
        entity.name = "Marshall"

        assert entity.__repr__() == "Entity(id=ID:), name=Marshall)"

    def test_eq_entity(self):
        entity = Entity()
        entity.id = "MyID"
        entity2 = Entity()
        entity2.id = "MyID"

        assert entity == entity2

    def test_hash_entity(self):
        entity = Entity()
        entity.id = "MyID"
        entity2 = Entity()
        entity2.id = "MyID"
        entity3 = Entity()
        entity3.id = "MyDifferentID"

        assert hash(entity) == hash(entity2)
        assert hash(entity) != hash(entity3) and hash(entity2) != hash(entity3)
