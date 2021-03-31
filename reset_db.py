from models import User, Baby, UserWord, \
  FirstSpokenWord, UserWordCategory, UserCategory, \
    DefaultWord, DefaultWordCategory, DefaultCategory

DEFAULT_CATEGORIES = [
  'Food',
  'Colors',
  'Animals',
  'Bathtime'
]

DEFAULT_WORDS = {
  'Milk': ['Food'],
  'More': ['Food'],
  'Eat': ['Food'],
  'Water': ['Food'],
  'Cracker': ['Food'],
  'Cheese': ['Food'],
  'Cereal': ['Food'],
  'Cheerios': ['Food'],
  'Yogurt': ['Food'],
  'Bread': ['Food'],
  'Meat': ['Food'],
  'Pizza': ['Food'],
  'Avocado': ['Food'],
  'Egg': ['Food'],
  'Macaroni': ['Food'],
  'Red': ['Colors'],
  'Orange': ['Colors'],
  'Green': ['Colors'],
  'Blue': ['Colors'],
  'Yellow': ['Colors'],
  'Purple': ['Colors'],
  'Black': ['Colors'],
  'White': ['Colors'],
  'Brown': ['Colors'],
  'Grey': ['Colors'],
  'Pink': ['Colors'],
  'Gold': ['Colors'],
  'Silver': ['Colors'],
  'Bird': ['Animals'],
  'Cat': ['Animals'],
  'Chicken': ['Animals'],
  'Cow': ['Animals'],
  'Dog': ['Animals'],
  'Donkey': ['Animals'],
  'Duck': ['Animals'],
  'Goat': ['Animals'],
  'Horse': ['Animals'],
  'Pig': ['Animals'],
  'Sheep': ['Animals'],
  'Rooster': ['Animals'],
  'Turkey': ['Animals'],
  'Bath': ['Bathtime'],
  'Brush': ['Bathtime'],
  'Bubbles': ['Bathtime'],
  'Clean': ['Bathtime'],
  'Comb': ['Bathtime'],
  'Dirty': ['Bathtime'],
  'Hair Dryer': ['Bathtime'],
  'Naked': ['Bathtime'],
  'Shampoo': ['Bathtime'],
  'Shower': ['Bathtime'],
  'Soap': ['Bathtime'],
  'Toothbrush': ['Bathtime'],
  'Towel': ['Bathtime'],
  'Wash': ['Bathtime'],
  'Wash Hands': ['Bathtime'],
  'Hot': ['Bathtime'],
  'Cold': ['Bathtime'],
  'Warm': ['Bathtime'],
  'Poop': ['Bathtime'],
  'Potty': ['Bathtime']
}

def add_default_category(db, default_category):
    newCategory = DefaultCategory(name=default_category)
    db.session.add(newCategory)


def add_default_word(db, default_word, categories, catmap):
    newWord = DefaultWord(name=default_word)
    db.session.add(newWord)
    db.session.flush()
    for cat_name in categories:
        cat_id = catmap[cat_name]
        newWordCategory = DefaultWordCategory(default_word=newWord.id, default_category=cat_id)
        db.session.add(newWordCategory)

def reset_database(db):
    def db_drop_and_create_all(db):
        db.drop_all()
        db.create_all()
    for default_category in DEFAULT_CATEGORIES:
        add_default_category(db, default_category)
    db.session.flush()
    catmap = {cat.name: cat.id for cat in DefaultCategory.query.all()}
    for default_word, categories in DEFAULT_WORDS.items():
        add_default_word(db, default_word, categories, catmap)
    db.session.commit()

