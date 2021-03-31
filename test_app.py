import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, db, User, Baby, UserWord, \
  FirstSpokenWord, UserWordCategory, UserCategory, \
    DefaultWord, DefaultWordCategory, DefaultCategory


class BabyWordsTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "BabyWords_Test"
        
        self.database_username = 'testuser'
        self.database_user_pw = ''
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            self.database_username,
            self.database_user_pw,
            'localhost:5432',
            self.database_name)


        # self.database_path = "postgresql://{}/{}".format(
        #     'localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.newDefaultCategory = {
            'name': 'Toys'}
        self.newDefaultWord = {
            'name': 'Truck',
            'categories': [1]
        }
        self.expiredToken="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNBNFRLWWJXcXdxZXVRMXVHbjE1ZSJ9.eyJpc3MiOiJodHRwczovL2FiZ29nby51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjA2MmM2OGFkODUwZjkwMDcxNTZlYjQzIiwiYXVkIjoiYmFieXdvcmRzIiwiaWF0IjoxNjE3MDg3MDE0LCJleHAiOjE2MTcxNzM0MTQsImF6cCI6InJaTlBoQzZDRTNKblRScTRLUnJQa2p4SjVBQlNIWGxuIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJjcnVkOm93bl9kYXRhIl19.XqC5PwGfL0-53QEfqu5RKRmNHOqz8TvDQdWC-eRmt41NFrFH_qj3zZnZSBxuJlT5DT2C8cQm8UKevldUBC9zcldrUKcE8yPlnxLw9yQq14JA8ZXM3YfCT4KAZqOojr-k0lPitogSBSMaSENPqVXueCYS-OOLw1pMMKEiTsDKD2Gm7UFgwnnECV2-s5sIhABI2C_AXwmFK--GbKjeSbY1KjDfIVUcNB87zA3qbzphkIitMWVE6q1qf-QE65H1YMYWtO8lvu4_gZZtY3s31Sjc7g8CeHhj-SOxZwq_HoMjipSPZpRmS5KuczfjfvS1-Qkn_PXrrwtKaFtlnou8qam7lQ"
        self.userToken="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNBNFRLWWJXcXdxZXVRMXVHbjE1ZSJ9.eyJpc3MiOiJodHRwczovL2FiZ29nby51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjA2MmM3MTk2ZTY1NTAwMDcwN2RkNGY2IiwiYXVkIjoiYmFieXdvcmRzIiwiaWF0IjoxNjE3MTc1NTMwLCJleHAiOjE2MTcyNjE5MzAsImF6cCI6InJaTlBoQzZDRTNKblRScTRLUnJQa2p4SjVBQlNIWGxuIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJjcnVkOm93bl9kYXRhIl19.l4rJxhjTdrkoJWN_PN_wc9n53DtUyqLUIUZ2yjsTQ4JIMc4tYs9u0s-acTt53oOe0Jy4zi3Ort2s8keF-HGJ2jwT2L_HFI7UgCXGUlO1XbK3J_LdjwgmPTfElSd43B9kE-qOksgIEgZ2ftpqoJMVxt8bK4Pl6R7CqoNZXsxm91TTsPKVvTfP_UUKIs2X8lsEC9YLSg77jERlQDMev4kEme6liDdAlulgAQjnSgaxUmdw9qVxEwSneM5Fk8dOYfNhYYjM1eoGQjxBCHPYVJnAwHgZrcbEZoSALLl9PDd4IDxm3i790kIVcZ0BWsqXvHJ6XKEraessRMd5G56FE4aGdA"
        self.badToken="abc"

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_user(self):
        res = self.client().get('/user', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['user'])
    
    def test_401_get_user(self):
        res = self.client().get('/user')
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected.")
        self.assertEqual(res.status_code, 401)
    
    def test_edit_user(self):
        res = self.client().patch(
            '/user', 
            headers={
                "Authorization": f"Bearer {self.userToken}"},
            json={
                "name":"Aileen",
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['user'])

    def test_401_edit_user(self):
        res = self.client().patch('/user')
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected.")
        self.assertEqual(res.status_code, 401)

    def test_get_babies(self):
        res = self.client().get('/babies', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['babies'])

    def test_401_get_babies(self):
        res = self.client().get('/babies', headers={"Authorization": self.badToken})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Authorization header must start with "Bearer".')
        self.assertEqual(res.status_code, 401)

    def test_add_baby(self):
        res = self.client().post('/babies',
            headers={"Authorization": f"Bearer {self.userToken}"},
            json={
                "name":"Elizabeth2",
                "birthday":"2017-6-4"
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['baby_id'])

    def test_401_add_baby(self):
        res = self.client().post('/babies', headers={"Authorization": self.badToken})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Authorization header must start with "Bearer".')
        self.assertEqual(res.status_code, 401)


    # def test_get_public_timeline(self):
    #     res = self.client().get('/baby/3/timeline/public')
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['first_spoken_words'])
    
    # def test_get_private_timeline(self):
    #     res = self.client().get('/baby/3/timeline', headers={"Authorization": f"Bearer {self.userToken}"})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['first_spoken_words'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
