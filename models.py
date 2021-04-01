from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, \
    Date, Boolean, create_engine, UniqueConstraint
import os

# for local database:
# database name, username and password are in
# setup.sh file in the same directory \
# run "source setup.sh" in terminal

database_name = os.environ.get('database_name')
database_username = os.environ.get('database_username')
database_user_pw = os.environ.get(
    'database_user_pw') if os.environ.get('database_user_pw') else ''
database_path = "postgresql://{}:{}@{}/{}".format(
    database_username,
    database_user_pw,
    'localhost:5432',
    database_name)

# for Heroku
# database_path = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    identifier = Column(String, nullable=False, unique=True)
    name = Column(String)

    def format(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Baby(db.Model):
    __tablename__ = 'babies'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    birthday = Column(Date)
    public = Column(Boolean, default=False)

    first_spoken_words = db.relationship(
        'FirstSpokenWord',
        backref='baby',
        lazy='joined',
        cascade='all, delete')
    # Baby.words_backref = all rows in FirstSpoken that belong to this Baby.
    # If this Baby is deleted, rows in FirstSpoken corresponding to this Baby
    # will be deleted as well

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'birthday': self.birthday,
            'public': self.public
        }


class UserWord(db.Model):
    __tablename__ = 'user_words'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, db.ForeignKey('users.id'))
    name = Column(String, nullable=False)
    user_word_categories = db.relationship(
        'UserWordCategory',
        backref='word',
        lazy='joined',
        cascade='all, delete')
    first_spoken_words = db.relationship(
        'FirstSpokenWord',
        backref='word',
        lazy='joined',
        cascade='all, delete')

    def format(self):
        return {
            'id': self.id,
            'name': self.name
        }


class UserCategory(db.Model):
    __tablename__ = 'user_categories'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, db.ForeignKey('users.id'))
    name = Column(String, nullable=False)
    user_word_categories = db.relationship(
        'UserWordCategory',
        backref='category',
        lazy='joined',
        cascade='all, delete')
    __table_args__ = (
        UniqueConstraint('user', 'name'),
    )

    def format(self):
        return {
            'id': self.id,
            'name': self.name
        }


class FirstSpokenWord(db.Model):
    __tablename__ = 'first_spoken_words'
    id = Column(Integer, primary_key=True)
    baby_id = Column(Integer, db.ForeignKey('babies.id'), nullable=False)
    user_word = Column(Integer, db.ForeignKey('user_words.id'), nullable=False)
    user = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    details = Column(String)

    def format(self):
        return {
            'id': self.id,
            'word_id': self.user_word,
            'word': self.word.name,
            'baby_id': self.baby_id,
            'baby_name': self.baby.name,
            'date': self.date,
            'details': self.details
        }


class UserWordCategory(db.Model):
    __tablename__ = 'user_word_categories'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, db.ForeignKey('users.id'))
    user_word = Column(Integer, db.ForeignKey('user_words.id'), nullable=False)
    user_category = Column(
        Integer,
        db.ForeignKey('user_categories.id'),
        nullable=False)


class DefaultCategory(db.Model):
    __tablename__ = 'default_categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    default_word_categories = db.relationship(
        'DefaultWordCategory',
        backref='category',
        lazy='joined',
        cascade='all, delete')

    def format(self):
        return {
            'id': self.id,
            'name': self.name
        }


class DefaultWord(db.Model):
    __tablename__ = 'default_words'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    default_word_categories = db.relationship(
        'DefaultWordCategory',
        backref='word',
        lazy='joined',
        cascade='all, delete')

    def format(self):
        return {
            'id': self.id,
            'name': self.name
        }


class DefaultWordCategory(db.Model):
    __tablename__ = 'default_word_categories'
    id = Column(Integer, primary_key=True)
    default_word = Column(
        Integer,
        db.ForeignKey('default_words.id'),
        nullable=False)
    default_category = Column(Integer, db.ForeignKey(
        'default_categories.id'), nullable=False)
    __table_args__ = (
        UniqueConstraint(default_word, default_category),
    )
