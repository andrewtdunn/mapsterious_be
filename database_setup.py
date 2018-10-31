import sys
import os

from sqlalchemy import Column, ForeignKey, Integer, String, Float

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'picture': self.picture
        }


class Review(Base):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    review_text = Column(String(500))
    location_id = Column(Integer, ForeignKey('location.id'))
    location = relationship("Location")
    user = relationship(User)
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        """ Return object data in easily serializable format"""
        return {
            'id': self.id,
            'review_text': self.review_text,
            'reviewer_name': self.user.name,
            'reviewer_id': self.user.id,
            'reviewer_pic': self.user.picture,
            'location_name': self.location.label,
            'location_id': self.location.id
        }


class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    label = Column(String(80))
    lat = Column(
        Float(40), nullable=False)
    lng = Column(
        Float(40), nullable=False)
    menuLabel = Column(String(80))
    icon = Column(String(80))
    type = Column(String(80))
    active = Column(String(80))
    reviews = relationship(Review, cascade="all,save-update,delete-orphan")
    user = relationship(User)
    user_id = Column(Integer, ForeignKey('user.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'location',
        'polymorphic_on': type
    }

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'position': {
                'lat': self.lat,
                'lng': self.lng
            },
            'menuLabel': self.menuLabel,
            'label': self.label,
            'icon': self.icon,
            'locationType': self.type,
            'locator_id': self.user_id,
            'location.name': self.user.name,
            'locator_picture': self.user.picture
        }

class Restaurant(Location):
    __tablename__ = 'restaurant'
    id = Column(Integer, ForeignKey('location.id'), primary_key=True)
    yelp_id = Column(String(80))
    __mapper_args__ = {
        'polymorphic_identity': 'food',
    }

    @property
    def serialize(self):
        props = super(Restaurant, self).serialize
        props['yelp_id'] = self.yelp_id
        return props


class Recreation(Location):
    __tablename__ = 'recreation'
    id = Column(Integer, ForeignKey('location.id'), primary_key=True)
    wiki_id = Column(String(80))
    __mapper_args__ = {
        'polymorphic_identity': 'rec',
    }

    @property
    def serialize(self):
        props = super(Recreation, self).serialize
        props['wiki_id'] = self.wiki_id
        return props

class School(Location):
    __tablename__ = 'school'
    id = Column(Integer, ForeignKey('location.id'), primary_key=True)
    wiki_id = Column(String(80))
    __mapper_args__ = {
        'polymorphic_identity': 'school',
    }

    @property
    def serialize(self):
        props = super(School, self).serialize
        props['wiki_id'] = self.wiki_id
        return props


engine = create_engine(os.environ['DB_KEY'])
Base.metadata.create_all(engine)
