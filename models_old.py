from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Date, Boolean, create_engine, UniqueConstraint
import os
from dotenv import load_dotenv
load_dotenv()


database_name = "BabyWords"
# username and password to be configured in the .env file in the same
# directory or in a python terminal shell
database_username = os.environ.get('database_username')
database_user_pw = os.environ.get(
    'database_user_pw') if os.environ.get('database_user_pw') else ''
database_path = "postgres://{}:{}@{}/{}".format(
    database_username,
    database_user_pw,
    'localhost:5432',
    database_name)

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
    identifier = Column(String, nullable=False, unique = True)
    name = Column(String)
    birthday = Column(Date)
    public = Column(Boolean)
    categories_backref = db.relationship('Category', backref='user', lazy='joined', cascade='all, delete')

    def format(self):
        return {
            'id': self.id,
            'identifier': self.identifier,
            'name': self.name,
            'birthday': self.birthday,
            'public': self.public
        }

class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'))
    category_name = Column(String)
    words_backref = db.relationship('Word', backref='category', lazy='joined', cascade='all, delete')
    UniqueConstraint('user_id', 'category_name')


class Word(db.Model):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, db.ForeignKey('categories.id'))
    word_name = Column(String)
    first_spoken = Column(Date)
    



class DefaultCategory(db.Model):
    __tablename__ = 'default_categories'

    id = Column(Integer, primary_key=True)
    category_name = Column(String, unique=True)
    default_words_backref = db.relationship('DefaultWord', backref='default_category', lazy='joined', cascade='all, delete')


class DefaultWord(db.Model):
    __tablename__ = 'default_words'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, db.ForeignKey('default_categories.id'))
    word_name = Column(String, unique=True)
    