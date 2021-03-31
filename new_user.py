from models import setup_db, db, User, Baby, UserWord, \
  FirstSpokenWord, UserWordCategory, UserCategory, \
    DefaultWord, DefaultWordCategory, DefaultCategory


def populate_defaults(user_id, app):
    try: 
        #populate categories
        catmap = {}
        dCats = DefaultCategory.query.all()
        for dCat in dCats:
            name = dCat.name
            newUserCat = UserCategory(user=user_id, name=name)
            db.session.add(newUserCat)
            db.session.flush()
            catmap[dCat.id] = newUserCat.id
        #app.logger.info('populated categories')

        #populate words
        wordmap = {}
        dWords = DefaultWord.query.all()
        for dWord in dWords:
            name = dWord.name
            newUserWord = UserWord(user=user_id, name=name)
            db.session.add(newUserWord)
            db.session.flush()
            wordmap[dWord.id] = newUserWord.id
        #app.logger.info('populated words')
        
        #populate word-categories
        dWordCats = DefaultWordCategory.query.all()
        for dWC in dWordCats:
            dWord_id = dWC.default_word
            dCat_id = dWC.default_category
            newWordCategory = UserWordCategory(user=user_id, user_word=wordmap[dWord_id], user_category=catmap[dCat_id])
            db.session.add(newWordCategory)
        #app.logger.info('populated wordcats')
        
    except Exception as e:
        raise 'error populating defaults'


