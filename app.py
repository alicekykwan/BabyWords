import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, db, User, Baby, UserWord, \
  FirstSpokenWord, UserWordCategory, UserCategory, \
    DefaultWord, DefaultWordCategory, DefaultCategory
import datetime

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    return app

app = create_app()
setup_db(app)

@app.route('/user')
def get_user():
    identifier = 'hello123'
    user = User.query.filter(User.identifier==identifier).one_or_none()
    return jsonify({
             "success": True,
             "user": user.format()
        })

@app.route('/user', methods=['PATCH'])
def edit_user():
    identifier = 'hello123'
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
def get_babies():
    identifier = 'hello123'
    user = User.query.filter(User.identifier==identifier).one_or_none()
    babies = Baby.query.filter_by(user=user.id).all()
    return jsonify({
             "success": True,
             "babies": [baby.format() for baby in babies]
        })

@app.route('/babies', methods=['POST'])
def add_baby():
    identifier = 'hello123'
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
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        abort(422)
    finally:
        db.session.close()

@app.route('/baby/<int:baby_id>', methods=['PATCH'])
def edit_baby(baby_id):
    identifier = 'hello123'
    user = User.query.filter(User.identifier==identifier).one_or_none()
    try:
        body = request.get_json()
        currbaby = Baby.query.filter_by(id=baby_id).one_or_none()
        if not currbaby: abort(404)

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
def show_categories():
    #maybe add a /login_result endpoint that handles user reaction 
    #get payload from requires auth, pull out "sub" as identifier
    identifier = 'hello123'
    user = User.query.filter(User.identifier==identifier).one_or_none()
    if user is None:
        #handle create a new user
        pass
    categories = UserCategory.query.filter_by(user=user.id).all()
    cat_objects = [c.format() for c in categories]
    return jsonify({
        "success": True,
        "categories": cat_objects 
    })

@app.route('/category/<int:category_id>')
def show_category(category_id):
    identifier = 'hello123'
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
def show_category_for_baby(category_id, baby_id):
    identifier = 'hello123'
    user = User.query.filter(User.identifier==identifier).one_or_none()
    category_user = UserCategory.query.filter_by(id=category_id).one_or_none().user
    assert user.id == category_user

    word_cats = UserWordCategory.query.filter_by(user_category=category_id).all()
    words = [wc.word for wc in word_cats]
    babywords = []
    for word in words:
        babyword = FirstSpokenWord.query.filter_by(baby_id=baby_id).filter_by(user_word=word.id).one_or_none()
        babywords.append(babyword.format())
    
    return jsonify({
        "success": True,
        "category":  category_id,
        "babywords": babywords
    })

@app.route('/baby/<baby_id>/timeline')
def display_baby_timeline(baby_id):
    currbaby = Baby.query.filter_by(id=baby_id).one_or_none()
    if not currbaby: abort(404)
    first_spoken_words = FirstSpokenWord.query.filter_by(baby_id=baby_id).order_by(FirstSpokenWord.date).all()
    return jsonify({
        "success": True,
        "first_spoken_words": [w.format() for w in first_spoken_words]
    })


@app.route('/categories', methods=['POST'])
def add_category():
    identifier = 'hello123'
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
        })
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
def add_word():
    identifier = 'hello123'
    user = User.query.filter(User.identifier==identifier).one_or_none()
    try:
        body = request.get_json()
        user = user.id
        name = body.get('name', None)
        newWord = UserWord(user=user, name=name)
        
        db.session.add(newWord)
        db.session.commit()
        
        categories = body.get('categories', None)
        newWordCategoriesIds = []
        if categories:
            for category in categories:
                newWordCategory = UserWordCategory(user=user, user_word=newWord.id, user_category=category)
                db.session.add(newWordCategory)
                db.session.commit()
                newWordCategoriesIds.append(newWordCategory.id)
        
        db.session.commit()
        return jsonify({
             "success": True,
             "created_word_id": newWord.id,
             "created_word_category_ids": newWordCategoriesIds,
        })
        
    except Exception as e:
        app.logger.error(e)
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()

@app.route('/first_spoken_words', methods=['POST'])
def add_first_spoken_word():
    identifier = 'hello123'
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
        })
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
def edit_category(category_id):
    identifier = 'hello123'
    user = User.query.filter(User.identifier==identifier).one_or_none()
    try:
        body = request.get_json()
        currCategory = UserCategory.query.filter_by(id=category_id).one_or_none()
        if not currCategory: abort(404)

        assert user.id == currCategory.user

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
def edit_word(word_id):
    identifier = 'hello123'
    user = User.query.filter(User.identifier==identifier).one_or_none()
    try:
        body = request.get_json()
        currWord = UserWord.query.filter_by(id=word_id).one_or_none()
        if not currWord: abort(404)

        assert user.id == currWord.user

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



@app.route('/category/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    identifier = 'hello123'
    user = User.query.filter(User.identifier==identifier).one_or_none()
    try:
        currCategory = UserCategory.query.filter_by(id=category_id).one_or_none()
        if not currCategory: abort(404)
        assert user.id == currCategory.user
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

@app.route('/word/<int:word_id>', methods=['DELETE'])
def delete_word(word_id):
    identifier = 'hello123'
    user = User.query.filter(User.identifier==identifier).one_or_none()
    try:
        currWord = UserWord.query.filter_by(id=word_id).one_or_none()
        if not currWord: abort(404)
        assert user.id == currWord.user
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






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    