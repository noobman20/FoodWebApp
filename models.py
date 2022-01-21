import base64
import os

from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash

from flask_login import UserMixin
from app import db
from flask import json


def to_json(inst, cls):
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        d[c.name] = v
    return json.dumps(d)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    pin_key = db.Column(db.String(100), nullable=False)

    # User activity information
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    def __init__(self, email, firstname, lastname, phone, password, role):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = generate_password_hash(password)

        self.role = role
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = None

    def __repr__(self):
        return to_json(self, self.__class__)

    def __str__(self):
        d = dict()
        d["id"] = self.id
        d["email"] = self.email
        d["firstname"] = self.firstname
        d["lastname"] = self.lastname
        d["phone"] = self.phone
        d["role"] = self.role
        return json.dumps(d)


class Foods(db.Model):
    __tablename__ = 'foods'

    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(100), nullable=False)

    def __init__(self, food_name):
        self.food_name = food_name

    def __repr__(self):
        return to_json(self, self.__class__)

    def __str__(self):
        return to_json(self, self.__class__)


class Places(db.Model):
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(100), nullable=False)

    def __init__(self, place_name):
        self.place_name = place_name

    def __repr__(self):
        return to_json(self, self.__class__)

    def __str__(self):
        return to_json(self, self.__class__)


class Posts(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'))
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'))
    user_id = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    post_time = db.Column(db.String(100), nullable=False)

    foods = relationship("Foods", backref="my_food_record")
    places = relationship("Places", backref="my_place_record")

    def __init__(self, food_id, place_id, user_id, amount, post_time):
        self.food_id = food_id
        self.place_id = place_id
        self.user_id = user_id
        self.amount = amount
        self.post_time = post_time

    def __repr__(self):
        return to_json(self, self.__class__)

    def __str__(self):
        return to_json(self, self.__class__)

class Takens(db.Model):
    __tablename__ = 'takens'

    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'))
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'))
    user_id = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    post_time = db.Column(db.String(100), nullable=False)
    post_id = db.Column(db.Integer)
    foods = relationship("Foods", backref="take_food_record")
    places = relationship("Places", backref="take_place_record")

    def __init__(self, food_id, place_id, user_id, amount, post_time, post_id):
        self.food_id = food_id
        self.place_id = place_id
        self.user_id = user_id
        self.amount = amount
        self.post_time = post_time
        self.post_id = post_id

    def __repr__(self):
        return to_json(self, self.__class__)

    def __str__(self):
        return to_json(self, self.__class__)

