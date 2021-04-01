import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, db, User, Baby, UserWord, \
  FirstSpokenWord, UserWordCategory, UserCategory, \
    DefaultWord, DefaultWordCategory, DefaultCategory
import datetime
from auth import AuthError, requires_auth
from new_user import populate_defaults
from reset_db import reset_database

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    setup_db(app)
    
    def db_drop_and_create_all():
        db.drop_all()
        db.create_all()
        reset_database(db)
    '''
    ************ UNCOMMENT AFTER FIRST RUN ************
    This will reset the database and populate it with defaults specified in reset_db.py.
    All user information will be lost.
    '''
    #db_drop_and_create_all()
    '''
    ******************************************************
    '''
    @app.route('/user')
    @requires_auth('crud:own_data')
    def get_user(payload):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        if not user: abort(404)
        return jsonify({
                "success": True,
                "user": user.format()
            })

    @app.route('/user', methods=['PATCH'])
    @requires_auth('crud:own_data')
    def edit_user(payload):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        try:
            body = request.get_json()
            name = body.get('name', None)
            user.name=name
            db.session.commit()
            return jsonify({
                "success": True,
                "user": user.format()
            })
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)
        finally:
            db.session.close()


    @app.route('/babies')
    @requires_auth('crud:own_data')
    def get_babies(payload):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        babies = Baby.query.filter_by(user=user.id).all()
        return jsonify({
                "success": True,
                "babies": [baby.format() for baby in babies]
            })

    @app.route('/babies', methods=['POST'])
    @requires_auth('crud:own_data')
    def add_baby(payload):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        try:
            body = request.get_json()
            name = body.get('name', None)
            birthday = body.get('birthday', None)
            newBaby = Baby(name=name, birthday=birthday, user=user.id)
            db.session.add(newBaby)
            db.session.commit()
            return jsonify({
                "success": True,
                "baby_id": newBaby.id
            }), 201
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)
        finally:
            db.session.close()

    @app.route('/baby/<int:baby_id>', methods=['PATCH'])
    @requires_auth('crud:own_data')
    def edit_baby(payload, baby_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        try:
            body = request.get_json()
            currbaby = Baby.query.filter_by(id=baby_id).one_or_none()
            if not currbaby or currbaby.user != user.id: abort(404)

            name = body.get('name', None)
            if name:
                currbaby.name = name
            birthday = body.get('birthday', None)
            if birthday:
                currbaby.birthday = birthday
            public = body.get('public', None)
            if public is not None:
                currbaby.public = public

            db.session.commit()

            return jsonify({
                "success": True,
                "edited_baby_id": currbaby.id
            })
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)
        finally:
            db.session.close()
        


    @app.route('/categories')
    @requires_auth('crud:own_data')
    def show_categories(payload):
        #maybe add a /login_result endpoint that handles user reaction 
        #get payload from requires auth, pull out "sub" as identifier
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        categories = UserCategory.query.filter_by(user=user.id).all()
        cat_objects = [c.format() for c in categories]
        return jsonify({
            "success": True,
            "categories": cat_objects 
        })

    @app.route('/category/<int:category_id>')
    @requires_auth('crud:own_data')
    def show_category(payload, category_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        category_user = UserCategory.query.filter_by(id=category_id).one_or_none().user
        assert user.id == category_user

        word_cats = UserWordCategory.query.filter_by(user_category=category_id).all()
        words = [wc.word.format() for wc in word_cats]
        
        return jsonify({
            "success": True,
            "category":  category_id,
            "words": words
        })

    @app.route('/category/<int:category_id>/baby/<int:baby_id>')
    @requires_auth('crud:own_data')
    def show_category_for_baby(payload, category_id, baby_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        category_user = UserCategory.query.filter_by(id=category_id).one_or_none().user
        if user.id != category_user:
            # do not return 401 to prevent leaking information
            abort(404)  

        word_cats = UserWordCategory.query.filter_by(user_category=category_id).all()
        words = [wc.word for wc in word_cats]
        babywords = []
        for word in words:
            babyword = FirstSpokenWord.query.filter_by(baby_id=baby_id).filter_by(user_word=word.id).one_or_none()
            if babyword:
                babywords.append(babyword.format())
        
        return jsonify({
            "success": True,
            "category":  category_id,
            "babywords": babywords
        })

    @app.route('/word/<int:word_id>')
    @requires_auth('crud:own_data')
    def show_word(payload, word_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        word = UserWord.query.filter_by(id=word_id).one_or_none()
        if not word or word.user != user.id: abort(404)
        first_spoken = FirstSpokenWord.query.filter_by(user_word=word.id)
        return jsonify({
            "success": True,
            "word": word.format(),
            "first_spoken": [fs.format() for fs in first_spoken]
        })

    @app.route('/baby/<int:baby_id>/timeline')
    @requires_auth('crud:own_data')
    def display_baby_timeline(payload, baby_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        currbaby = Baby.query.filter_by(id=baby_id).one_or_none()
        if not currbaby or currbaby.user != user.id: abort(404)
        first_spoken_words = FirstSpokenWord.query.filter_by(baby_id=baby_id).order_by(FirstSpokenWord.date).all()
        return jsonify({
            "success": True,
            "first_spoken_words": [w.format() for w in first_spoken_words]
        })


    @app.route('/baby/<baby_id>/timeline/public')
    def display_baby_timeline_public(baby_id):
        currbaby = Baby.query.filter_by(id=baby_id).one_or_none()
        if not currbaby or not currbaby.public: abort(404)

        first_spoken_words = FirstSpokenWord.query.filter_by(baby_id=baby_id).order_by(FirstSpokenWord.date).all()
        return jsonify({
            "success": True,
            "first_spoken_words": [w.format() for w in first_spoken_words]
        }), 200


    @app.route('/categories', methods=['POST'])
    @requires_auth('crud:own_data')
    def add_category(payload):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        try:
            body = request.get_json()
            user = user.id
            name = body.get('name', None)
            newCategory = UserCategory(name=name, user=user)
            db.session.add(newCategory)
            db.session.commit()
            return jsonify({
                "success": True,
                "created_category_id": newCategory.id
            }), 201
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

    '''
    curl http://0.0.0.0:8080/first_spoken_words -X POST \
    -H "Content-Type: application/json" \
    -d '{"name":"dragon fruit","categories":[1,2]}'

    ''' 
    @app.route('/words', methods=['POST'])
    @requires_auth('crud:own_data')
    def add_word(payload):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        try:
            body = request.get_json()
            user = user.id
            name = body.get('name', None)
            newWord = UserWord(user=user, name=name)
            
            db.session.add(newWord)
            db.session.flush()
            
            categories = body.get('categories', None)
            newWordCategories = []
            if categories:
                for category in categories:
                    newWordCategory = UserWordCategory(user=user, user_word=newWord.id, user_category=category)
                    db.session.add(newWordCategory)
                    newWordCategories.append(newWordCategory)
            
            db.session.commit()
            return jsonify({
                "success": True,
                "created_word_id": newWord.id,
                "created_word_category_ids": [c.id for c in newWordCategories],
            }), 201
            
        except Exception as e:
            app.logger.error(e)
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

    @app.route('/first_spoken_words', methods=['POST'])
    @requires_auth('crud:own_data')
    def add_first_spoken_word(payload):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        try:
            body = request.get_json()
            baby_id = body.get('baby_id', None)
            word_id = body.get('word_id', None)
            date = body.get('date', None)
            details = body.get('details', None)
            newFirstSpokenWord = FirstSpokenWord(baby_id=baby_id, user_word=word_id, user=user.id, date=date, details=details)
            db.session.add(newFirstSpokenWord)
            db.session.commit()
            return jsonify({
                "success": True,
                "created_first_spoken_word_id": newFirstSpokenWord.id
            }), 201
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()


    '''
    curl http://0.0.0.0:8080/category/2 -X PATCH \
    -H "Content-Type: application/json" \
    -d '{"name":"Spiky Fruits"}'
    '''
    @app.route('/category/<int:category_id>', methods=['PATCH'])
    @requires_auth('crud:own_data')
    def edit_category(payload, category_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        try:
            body = request.get_json()
            currCategory = UserCategory.query.filter_by(id=category_id).one_or_none()
            if not currCategory or currCategory.user != user.id: abort(404)

            name = body.get('name', None)
            if name:
                currCategory.name = name

            db.session.commit()

            return jsonify({
                "success": True,
                "edited_category_id": currCategory.id
            })
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)
        finally:
            db.session.close()



    '''
    curl http://0.0.0.0:8080/word/10 -X PATCH \
    -H "Content-Type: application/json" \
    -d '{"name":"dragonfruit","categories":[2]}'
    '''
    @app.route('/word/<int:word_id>', methods=['PATCH'])
    @requires_auth('crud:own_data')
    def edit_word(payload, word_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        try:
            body = request.get_json()
            currWord = UserWord.query.filter_by(id=word_id).one_or_none()
            if not currWord or currWord.user != user.id: abort(404)

            name = body.get('name', None)
            if name:
                currWord.name = name

            newCategories = body.get('categories', None)
            oldCategories = [wordcat.user_category for wordcat in currWord.user_word_categories]
            if set(newCategories) != set(oldCategories):
                
                #for newCategory that's not in old category, add
                for newCat in newCategories:
                    if newCat not in set(oldCategories):
                        newWordCategory = UserWordCategory(user=user.id, user_word=currWord.id, user_category=newCat)
                        db.session.add(newWordCategory)
                for oldCat in oldCategories:
                    if oldCat not in set(newCategories):
                        oldWordCat = UserWordCategory.query.filter_by(user=user.id, user_word=currWord.id, user_category=oldCat).one_or_none()
                        db.session.delete(oldWordCat)
                
                #for old category that's not in new category, remove

            db.session.commit()
            updatedCategoryIds = [wordcat.user_category for wordcat in currWord.user_word_categories]
            return jsonify({
                "success": True,
                "edited_word_id": currWord.id,
                "edited_category_ids": updatedCategoryIds
            })
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)
        finally:
            db.session.close()


    @app.route('/first_spoken_word/<int:first_spoken_word_id>', methods=['PATCH'])
    @requires_auth('crud:own_data')
    def edit_first_spoken(payload, first_spoken_word_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        currFirstSpoken = FirstSpokenWord.query.filter_by(id=first_spoken_word_id).one_or_none()
        if not currFirstSpoken or currFirstSpoken.user != user.id: abort(404)
        try:
            body = request.get_json()
            #date and baby_id are required field. If left out, do not modify
            #user should delete item instead if they intend to remove the record
            date = body.get('date', None)
            if date:
                currFirstSpoken.date = date
            baby_id = body.get('baby_id', None)
            if baby_id:
                currFirstSpoken.baby_id = baby_id
            
            #"details" is optional. If a user deletes their original details and submits nothing,
            # replace original details with nothing
            details = body.get('details', None)
            currFirstSpoken.details = details

            db.session.commit()
            return jsonify({
                "success": True,
                "edited_first_spoken_word_id": currFirstSpoken.id,
            })
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)
        finally:
            db.session.close()


    @app.route('/category/<int:category_id>', methods=['DELETE'])
    @requires_auth('crud:own_data')
    def delete_category(payload, category_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        currCategory = UserCategory.query.filter_by(id=category_id).one_or_none()
        if not currCategory or currCategory.user != user.id : abort(404)
        try:
            db.session.delete(currCategory)
            db.session.commit()
            return jsonify({
                "success": True,
                "deleted_category_id": category_id
            })
        except Exception as e:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

    @app.route('/word/<int:word_id>', methods=['DELETE'])
    @requires_auth('crud:own_data')
    def delete_word(payload, word_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        currWord = UserWord.query.filter_by(id=word_id).one_or_none()
        if not currWord or currWord.user != user.id: abort(404)
        try:
            db.session.delete(currWord)
            db.session.commit()
            return jsonify({
                "success": True,
                "deleted_word_id": word_id
            })
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)
        finally:
            db.session.close()


    @app.route('/first_spoken_word/<int:first_spoken_word_id>', methods=['DELETE'])
    @requires_auth('crud:own_data')
    def delete_first_spoken_word(payload, first_spoken_word_id):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        currFirstSpoken = FirstSpokenWord.query.filter_by(id=first_spoken_word_id).one_or_none()
        if not currFirstSpoken or currFirstSpoken.user != user.id: abort(404)
        try:
            db.session.delete(currFirstSpoken)
            db.session.commit()
            return jsonify({
                "success": True,
                "deleted_first_spoken_word_id": first_spoken_word_id
            })
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)
        finally:
            db.session.close()


    @app.route('/login_landing')
    @requires_auth('crud:own_data')
    def login_landing(payload):
        identifier = payload['sub']
        user = User.query.filter(User.identifier==identifier).one_or_none()
        if user:
            return jsonify({
                "success": True,
                "redirect": "you are logged in!"
            }), 200
        
        try:
            newUser = User(identifier=identifier)
            db.session.add(newUser)
            db.session.flush()
            populate_defaults(newUser.id, app)
            db.session.commit()
            return jsonify({
                "success": True,
                "created_user_id": newUser.id
            }), 201
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)

        finally:
            db.session.close()


    '''
    ENDPOINTS FOR DEFAULTS
    '''
    @app.route('/view_defaults')
    @requires_auth('crud:default_values')
    def view_defaults(payload):
        cats = DefaultCategory.query.all()
        words_in_cats = {}
        for cat in cats:
            words = []
            wordcats = cat.default_word_categories
            for wordcat in wordcats:
                words.append(wordcat.word.format())
            words_in_cats[cat.name]=words
        return jsonify({
            "success": True,
            "categories": [cat.format() for cat in cats],
            "words": words_in_cats
        })
            



    @app.route('/default_categories', methods=['POST'])
    @requires_auth('crud:default_values')
    def add_default_category(payload):
        try:
            body = request.get_json()
            name = body.get('name', None)
            newCategory = DefaultCategory(name=name)
            db.session.add(newCategory)
            db.session.commit()
            return jsonify({
                "success": True,
                "created_category_id": newCategory.id
            }), 201
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

    '''

    ''' 

    @app.route('/default_words', methods=['POST'])
    @requires_auth('crud:default_values')
    def add_default_word(payload):
        try:
            body = request.get_json()
            name = body.get('name', None)
            newWord = DefaultWord(name=name)
            
            db.session.add(newWord)
            db.session.flush()
            
            categories = body.get('categories', None)
            newWordCategories = []
            if categories:
                for category in categories:
                    newWordCategory = DefaultWordCategory(default_word=newWord.id, default_category=category)
                    db.session.add(newWordCategory)
                    newWordCategories.append(newWordCategory)
            
            db.session.commit()
            return jsonify({
                "success": True,
                "created_word_id": newWord.id,
                "created_word_category_ids": [c.id for c in newWordCategories],
            }), 201
            
        except Exception as e:
            app.logger.error(e)
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()



    @app.route('/default_category/<int:category_id>', methods=['DELETE'])
    @requires_auth('crud:default_values')
    def delete_default_category(payload, category_id):
        currCategory = DefaultCategory.query.filter_by(id=category_id).one_or_none()
        if not currCategory: abort(404)
        try:
            db.session.delete(currCategory)
            db.session.commit()
            return jsonify({
                "success": True,
                "deleted_category_id": category_id
            })
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)
        finally:
            db.session.close()

    @app.route('/default_word/<int:word_id>', methods=['DELETE'])
    @requires_auth('crud:default_values')
    def delete_default_word(payload, word_id):
        currWord = DefaultWord.query.filter_by(id=word_id).one_or_none()
        if not currWord: abort(404)
        try:
            db.session.delete(currWord)
            db.session.commit()
            return jsonify({
                "success": True,
                "deleted_word_id": word_id
            })
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            abort(422)
        finally:
            db.session.close()








    '''
    error handling
    '''
    # e.g. no such baby/user/category/word
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    # unprocessable entity - e.g. cannot add to dababase due to unique constraints, formats
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def server_errors(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server errors"
        }), 500

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.error['code'],
            "message": error.error['description']
        }), error.status_code


    return app

app = create_app()




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    