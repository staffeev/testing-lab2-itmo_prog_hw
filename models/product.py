from sqlalchemy import Column, Integer, ForeignKey, String, Float, DateTime
from sqlalchemy.orm import relation, validates
from .db_session import SqlAlchemyBase
import datetime


class Product(SqlAlchemyBase):
    """Класс для ORM-модели товара"""
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.datetime.now)
    cost = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id", ondelete='CASCADE'), nullable=False, index=True)
    category = relation("Category", back_populates="products")

    @validates("name")
    def validate_name(self, _, value):
        """Проверка допустимых значений для имени"""
        if len(value) > 1000:
            raise ValueError("Name length can't be more than 1000 symbols")
        return value

    @validates("cost")
    def validate_cost(self, _, value):
        """Проверка допустимых значений для цены"""
        # if value < 0:
        #     raise ValueError("Cost must be positive float")
        if value > 10 ** 9:
            raise ValueError("Cost can't be so enormous")
        return value
    
    def __repr__(self):
        return f"Product(name={self.name}, cost={self.cost}, date={self.date})"
    
    def __str__(self):
        return self.name


