import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    """ User class to store logged in facebook users """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), nullable=False)

class Category(Base):
    """ Category class to store the catalog categories """
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'))
    
    # Serialize method to create JSON
    @property
    def serialize(self):
        """ JSON serialize method """
        return {
            'id': self.id,
            'name': self.name,
            'creator_id': self.creator_id
        }

class Item(Base):
    """ Item class to store the catalog items """
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(1000))
    price = Column(String(10))
    category_id = Column(Integer, ForeignKey('categories.id'))
    creator_id = Column(Integer, ForeignKey('users.id'))
    
    # Serialize method to create JSON
    @property
    def serialize(self):
        """ JSON serialize method """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'category_id': self.category_id,
            'creator_id': self.creator_id,
        }

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
