from typing import List

from sqlalchemy import (TEXT, VARCHAR, Boolean, Column, ForeignKey, Integer,
                        Table)
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship


class Base(DeclarativeBase):
    pass


favorite_dishes = Table(
    "favorite_dishes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.user_id")),
    Column("dish_id", Integer, ForeignKey("dishes.dish_id"))
)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(128), nullable=True, unique=False)
    premium = Column(Boolean, default=False)
    dishes: Mapped[List["Dish"]] = relationship(back_populates='users', secondary=favorite_dishes,
                                                lazy='selectin')

    def __str__(self):
        return f'User: {self.user_id}'


class Dish(Base):
    __tablename__ = "dishes"

    dish_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(250), nullable=False, unique=True)
    recipe = Column(TEXT, nullable=False)
    users: Mapped[List["User"]] = relationship(back_populates="dishes", secondary=favorite_dishes,
                                               lazy='selectin')

    def __str__(self):
        return self.title


# class FavoriteDishes(Base):
#     __tablename__ = "fovorite_dishes"
#
#     user_id = Column(Integer, ForeignKey("users.user_id"))
#     dish_id - Column(Integer, ForeignKey("dishes.dish_id"))

