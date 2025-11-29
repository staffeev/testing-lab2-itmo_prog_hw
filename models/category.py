from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relation, validates
from .db_session import SqlAlchemyBase
from random import randint


def get_random_color():
    """Возвращает случайный цвет для категории"""
    return "#%02X%02X%02X" % (randint(0, 255), randint(0, 255), randint(0, 255))


class Category(SqlAlchemyBase):
    """Класс для ORM-модели категории товара"""
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    color = Column(String, nullable=False, default=get_random_color)
    products = relation(
        "Product", back_populates="category", 
        # cascade='all, delete-orphan',
        passive_deletes=True
    )

    @validates("name")
    def validate_name(self, _, value):
        """Проверка допустимых значений для имени"""
        if not value:
            raise ValueError("Name can't be empty")
        if len(value) > 1000:
            raise ValueError("Name length can't be more than 1000 symbols")
        return value
    
    def __repr__(self):
        return f"Category(name={self.name})"
    
    def __str__(self):
        return self.name



    