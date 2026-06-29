import pytest
from shared.domain.value_objects.category import Category
from src.core.exceptions import InvalidCategoryError


class TestCategory:
    def test_not_str_category(self):
        with pytest.raises(InvalidCategoryError):
            Category(25)
            Category(None)

    def test_empty_str_category(self):
        with pytest.raises(InvalidCategoryError):
            Category("")
            Category(" ")
            Category("  ")

    def test_category_strip(self):
        str_category = "        Category  "
        category = Category(str_category)

        assert category.value == str_category.strip()

    def test_long_category(self):
        with pytest.raises(InvalidCategoryError):
            Category("Mycategory" + "ABC" * 100)

    def test_title_and_lower_category(self):
        str_category = "mYcAteGoRy"
        category = Category(str_category)

        assert category.value == str_category.lower().title()
