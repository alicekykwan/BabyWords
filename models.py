from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Date, Boolean, create_engine, UniqueConstraint
import os
# from dotenv import load_dotenv
# load_dotenv()


database_name = "BabyWords"
# username and password to be configured in the .env file in the same
# directory or in a python terminal shell
database_username = os.environ.get('database_username')
database_username = 'testuser'
database_user_pw = os.environ.get(
    'database_user_pw') if os.environ.get('database_user_pw') else ''
database_path = "postgresql://{}:{}@{}/{}".format(
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



#INSERT INTO users (identifier, name) VALUES ('hello123', 'Alice');
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    identifier = Column(String, nullable=False, unique = True)
    name = Column(String)

    def format(self):
        return {
            'id': self.id,
            'identifier': self.identifier,
            'name': self.name
        }

#INSERT INTO babies ("user", name) VALUES (1, 'Liddy');
class Baby(db.Model):
    __tablename__ = 'babies'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, db.ForeignKey('users.id'))
    name = Column(String)
    birthday = Column(Date)
    public = Column(Boolean, default=False)

    first_spoken_words = db.relationship('FirstSpokenWord', backref='baby', lazy='joined', cascade='all, delete')
    #Baby.words_backref = all rows in FirstSpoken that belong to this Baby.
    #If this Baby is deleted, rows in FirstSpoken corresponding to this Baby will be deleted as well

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'birthday': self.birthday,
            'public': self.public
        }

#INSERT INTO user_words ("user", name) VALUES (1, 'Banana');
#INSERT INTO user_words ("user", name) VALUES (1, 'Apple');
class UserWord(db.Model):
    __tablename__ = 'user_words'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, db.ForeignKey('users.id'))
    name = Column(String, nullable=False)
    user_word_categories = db.relationship('UserWordCategory', backref='word', lazy='joined', cascade='all, delete')
    first_spoken_words = db.relationship('FirstSpokenWord', backref='word', lazy='joined', cascade='all, delete')
    
    def format(self):
        return {
            'id': self.id,
            'name': self.name
        }

#INSERT INTO user_categories ("user", name) VALUES (1, 'Fruits');
class UserCategory(db.Model):
    __tablename__ = 'user_categories'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, db.ForeignKey('users.id'))
    name = Column(String, nullable=False)
    user_word_categories = db.relationship('UserWordCategory', backref='category', lazy='joined', cascade='all, delete')
    UniqueConstraint('user', 'name')
    
    def format(self):
        return {
            'id': self.id,
            'name': self.name
        }

#INSERT INTO first_spoken_words (baby_id, user_word, "user", date) VALUES (2, 1, 1, '2020-03-01');
#INSERT INTO first_spoken_words (baby_id, user_word, "user", date) VALUES (2, 2, 1, '2020-03-01');
class FirstSpokenWord(db.Model):
    __tablename__ = 'first_spoken_words'
    id = Column(Integer, primary_key=True)
    baby_id = Column(Integer, db.ForeignKey('babies.id'))
    user_word = Column(Integer, db.ForeignKey('user_words.id'))
    user = Column(Integer, db.ForeignKey('users.id'))
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

#INSERT INTO user_word_categories ("user", user_word, user_category) VALUES (1, 1, 1);
class UserWordCategory(db.Model):
    __tablename__ = 'user_word_categories'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, db.ForeignKey('users.id'))
    user_word = Column(Integer, db.ForeignKey('user_words.id'), nullable=False)
    user_category = Column(Integer, db.ForeignKey('user_categories.id'), nullable=False)

class DefaultCategory(db.Model):
    __tablename__ = 'default_categories'
    id = Column(Integer, primary_key=True)
    category_name = Column(String, unique=True, nullable=False)
    default_word_categories = db.relationship('DefaultWordCategory', backref='category', lazy='joined', cascade='all, delete')

class DefaultWord(db.Model):
    __tablename__ = 'default_words'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    default_word_categories = db.relationship('DefaultWordCategory', backref='word', lazy='joined', cascade='all, delete')
    
class DefaultWordCategory(db.Model):
    __tablename__ = 'default_word_categories'
    id = Column(Integer, primary_key=True)
    default_word = Column(Integer, db.ForeignKey('default_words.id'))
    default_category = Column(Integer, db.ForeignKey('default_categories.id'))

