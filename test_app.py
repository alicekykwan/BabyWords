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

        #test database needs to have 
        #defults populated
        #one user
        #one baby
        #baby spoken 1 word

        self.expiredToken="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNBNFRLWWJXcXdxZXVRMXVHbjE1ZSJ9.eyJpc3MiOiJodHRwczovL2FiZ29nby51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjA2MmM2OGFkODUwZjkwMDcxNTZlYjQzIiwiYXVkIjoiYmFieXdvcmRzIiwiaWF0IjoxNjE3MDg3MDE0LCJleHAiOjE2MTcxNzM0MTQsImF6cCI6InJaTlBoQzZDRTNKblRScTRLUnJQa2p4SjVBQlNIWGxuIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJjcnVkOm93bl9kYXRhIl19.XqC5PwGfL0-53QEfqu5RKRmNHOqz8TvDQdWC-eRmt41NFrFH_qj3zZnZSBxuJlT5DT2C8cQm8UKevldUBC9zcldrUKcE8yPlnxLw9yQq14JA8ZXM3YfCT4KAZqOojr-k0lPitogSBSMaSENPqVXueCYS-OOLw1pMMKEiTsDKD2Gm7UFgwnnECV2-s5sIhABI2C_AXwmFK--GbKjeSbY1KjDfIVUcNB87zA3qbzphkIitMWVE6q1qf-QE65H1YMYWtO8lvu4_gZZtY3s31Sjc7g8CeHhj-SOxZwq_HoMjipSPZpRmS5KuczfjfvS1-Qkn_PXrrwtKaFtlnou8qam7lQ"
        self.userToken="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNBNFRLWWJXcXdxZXVRMXVHbjE1ZSJ9.eyJpc3MiOiJodHRwczovL2FiZ29nby51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjA2MmM3MTk2ZTY1NTAwMDcwN2RkNGY2IiwiYXVkIjoiYmFieXdvcmRzIiwiaWF0IjoxNjE3MTc1NTMwLCJleHAiOjE2MTcyNjE5MzAsImF6cCI6InJaTlBoQzZDRTNKblRScTRLUnJQa2p4SjVBQlNIWGxuIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJjcnVkOm93bl9kYXRhIl19.l4rJxhjTdrkoJWN_PN_wc9n53DtUyqLUIUZ2yjsTQ4JIMc4tYs9u0s-acTt53oOe0Jy4zi3Ort2s8keF-HGJ2jwT2L_HFI7UgCXGUlO1XbK3J_LdjwgmPTfElSd43B9kE-qOksgIEgZ2ftpqoJMVxt8bK4Pl6R7CqoNZXsxm91TTsPKVvTfP_UUKIs2X8lsEC9YLSg77jERlQDMev4kEme6liDdAlulgAQjnSgaxUmdw9qVxEwSneM5Fk8dOYfNhYYjM1eoGQjxBCHPYVJnAwHgZrcbEZoSALLl9PDd4IDxm3i790kIVcZ0BWsqXvHJ6XKEraessRMd5G56FE4aGdA"
        self.adminToken="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNBNFRLWWJXcXdxZXVRMXVHbjE1ZSJ9.eyJpc3MiOiJodHRwczovL2FiZ29nby51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjA2MmM3MTk2ZTY1NTAwMDcwN2RkNGY2IiwiYXVkIjoiYmFieXdvcmRzIiwiaWF0IjoxNjE3MTQ1Nzk0LCJleHAiOjE2MTcyMzIxOTQsImF6cCI6InJaTlBoQzZDRTNKblRScTRLUnJQa2p4SjVBQlNIWGxuIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJjcnVkOmRlZmF1bHRfdmFsdWVzIl19.UDxUOG6YziiqhFSJNOhXN5FO88RiZfFylERy3DbWoXbmUUXm3vgJiTQo1-0aRz9vLnkwMFot7_PNqe--k-Vzm5xDnpOBSH_N0_rz226LPQNkJOP-v6EqzjOa4VK356NbOnY40biPeFuglmQyX6P04S7cUV6JJvVYN8NZzmHQf7mEf2cx-rPpnzJ-TEG8jrgm-5eQf_krMZxqJ5eCd9ICcNZlvgVv07z7bVi-dYQHyehAo2T-FVLatXVqH935Xf2EPdZeDgS2vYWs0N4pXhwiBI5pHaGdiENRs6S3dsyVyjKi69hT60_nXxbdKab0lllVBrazosiRVggDPHtUsjJkUQ"
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

    # def test_add_baby(self):
    #     res = self.client().post('/babies',
    #         headers={"Authorization": f"Bearer {self.userToken}"},
    #         json={
    #             "name":"Elizabeth2",
    #             "birthday":"2017-6-4"
    #         })
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 201)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['baby_id'])

    def test_401_add_baby(self):
        res = self.client().post('/babies', headers={"Authorization": self.badToken})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Authorization header must start with "Bearer".')
        self.assertEqual(res.status_code, 401)

    def test_edit_baby(self):
        res = self.client().patch('/baby/1',
            headers={"Authorization": f"Bearer {self.userToken}"},
            json={
                "name": "Benjamin",
                "public": True
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['edited_baby_id'])

    def test_401_edit_baby(self):
        res = self.client().patch('/baby/1', headers={"Authorization": self.badToken})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Authorization header must start with "Bearer".')
        self.assertEqual(res.status_code, 401)
    
    def test_show_categories(self):
        res = self.client().get('/categories', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    
    def test_401_show_categories(self):
        res = self.client().get('/categories', headers={"Authorization": self.badToken})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Authorization header must start with "Bearer".')
        self.assertEqual(res.status_code, 401)

    def test_show_category(self):
        res = self.client().get('/category/1', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['category'])
        self.assertTrue(data['words'])
    
    def test_403_show_category(self):
        res = self.client().get('/category/1', headers={"Authorization": f"Bearer {self.adminToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')
        self.assertEqual(res.status_code, 403)

    def test_show_category_for_baby(self):
        res = self.client().get('/category/1/baby/1', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['category'])
        #ok for there to be no spoken words in a category:
        #self.assertTrue(data['babywords'])
    
    def test_403_show_category_for_baby(self):
        res = self.client().get('/category/1/baby/1', headers={"Authorization": f"Bearer {self.adminToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')
        self.assertEqual(res.status_code, 403)
    
    def test_show_word(self):
        res = self.client().get('/word/1', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['word'])
        self.assertTrue(data['first_spoken'])

    def test_403_show_word(self):
        res = self.client().get('/word/1', headers={"Authorization": f"Bearer {self.adminToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')
        self.assertEqual(res.status_code, 403)

    def test_get_private_timeline(self):
        res = self.client().get('/baby/1/timeline', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['first_spoken_words'])
    
    def test_403_get_private_timeline(self):
        res = self.client().get('/baby/1/timeline', headers={"Authorization": f"Bearer {self.adminToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')
        self.assertEqual(res.status_code, 403)

    def test_get_public_timeline(self):
        res = self.client().get('/baby/1/timeline/public')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['first_spoken_words'])
    
    def test_404_get_public_timeline(self):
        res = self.client().get('/baby/100000/timeline/public')
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)
    
    # def test_add_category(self):
    #     res = self.client().post('/categories',
    #         headers={"Authorization": f"Bearer {self.userToken}"},
    #         json={
    #             "name":"Family"
    #         })
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 201)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['created_category_id'])

    def test_401_add_category(self):
        res = self.client().post('/categories', headers={"Authorization": self.badToken})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Authorization header must start with "Bearer".')
        self.assertEqual(res.status_code, 401)
    
    # def test_add_word(self):
    #     res = self.client().post('/words',
    #         headers={"Authorization": f"Bearer {self.userToken}"},
    #         json={
    #             "name":"Mommy",
    #             "categories": [5]
    #         })
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 201)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['created_word_id'])
    #     self.assertTrue(data['created_word_category_ids'])

    def test_401_add_word(self):
        res = self.client().post('/words', headers={"Authorization": self.badToken})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Authorization header must start with "Bearer".')
        self.assertEqual(res.status_code, 401)

    # def test_add_first_spoken_word(self):
    #     res = self.client().post('/first_spoken_words',
    #         headers={"Authorization": f"Bearer {self.userToken}"},
    #         json={
    #             "baby_id": 1,
    #             "word_id": 3,
    #             "date": "2021-03-28",
    #             "details": "used sign too!"
    #         })
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 201)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['created_first_spoken_word_id'])
    
    def test_422_add_first_spoken_word(self):
        res = self.client().post('/first_spoken_words', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        self.assertEqual(res.status_code, 422)

    def test_edit_category(self):
        res = self.client().patch('/category/1',
            headers={"Authorization": f"Bearer {self.userToken}"},
            json={
                "name": "Yummies!",
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['edited_category_id'])
    
    def test_401_edit_category(self):
        res = self.client().patch('/category/1')
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected.")
        self.assertEqual(res.status_code, 401)
    
    def test_edit_word(self):
        res = self.client().patch('/word/1',
            headers={"Authorization": f"Bearer {self.userToken}"},
            json={
                "name": "Milku",
                "categories": [5]
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['edited_word_id'])
        self.assertTrue(data['edited_category_ids'])

    def test_401_edit_word(self):
        res = self.client().patch('/word/1')
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected.")
        self.assertEqual(res.status_code, 401)

    def test_edit_first_spoken(self):
        res = self.client().patch('/first_spoken_word/1',
            headers={"Authorization": f"Bearer {self.userToken}"},
            json={
                "date": "2020-12-25",
                "baby_id": 1,
                "details": "what he calls mom!!"
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['edited_first_spoken_word_id'])

    def test_401_edit_first_spoken(self):
        res = self.client().patch('/first_spoken_word/1')
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected.")
        self.assertEqual(res.status_code, 401)

    # def test_delete_category(self):
    #     res = self.client().delete('/category/3', headers={"Authorization": f"Bearer {self.userToken}"})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['deleted_category_id'])
    
    def test_404_delete_category(self):
        res = self.client().delete('/category/1000000', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)

    # def test_delete_word(self):
    #     res = self.client().delete('/word/5', headers={"Authorization": f"Bearer {self.userToken}"})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['deleted_word_id'])
    
    def test_404_delete_word(self):
        res = self.client().delete('/word/1000000', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)    
    
    # def test_delete_first_spoken_word(self):
    #     res = self.client().delete('/first_spoken_word/2', headers={"Authorization": f"Bearer {self.userToken}"})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['deleted_first_spoken_word_id'])
    
    def test_404_delete_first_spoken_word(self):
        res = self.client().delete('/first_spoken_word/1000000', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)    
    
    def test_login_landing(self):
        res = self.client().get('/login_landing', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 301)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['redirect'])
    
    def test_401_login_landing(self):
        res = self.client().get('login_landing')
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected.")
        self.assertEqual(res.status_code, 401)

    '''
    TESTS FOR DEFAULTS
    '''
    def test_view_defaults(self):
        res = self.client().get('/view_defaults', headers={"Authorization": f"Bearer {self.adminToken}"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['words'])
    
    def test_403_view_defaults(self):
        res = self.client().get('/view_defaults', headers={"Authorization": f"Bearer {self.userToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')
        self.assertEqual(res.status_code, 403)

    # def test_add_default_category(self):
    #     res = self.client().post('/default_categories',
    #         headers={"Authorization": f"Bearer {self.adminToken}"},
    #         json={
    #             "name":"Family"
    #         })
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 201)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['created_category_id'])

    def test_401_add_default_category(self):
        res = self.client().post('/default_categories', headers={"Authorization": self.badToken})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Authorization header must start with "Bearer".')
        self.assertEqual(res.status_code, 401)
    
    # def test_add_default_word(self):
    #     res = self.client().post('/default_words',
    #         headers={"Authorization": f"Bearer {self.adminToken}"},
    #         json={
    #             "name":"Mommy",
    #             "categories": [5]
    #         })
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 201)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['created_word_id'])
    #     self.assertTrue(data['created_word_category_ids'])

    def test_401_add_default_word(self):
        res = self.client().post('/default_words', headers={"Authorization": self.badToken})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Authorization header must start with "Bearer".')
        self.assertEqual(res.status_code, 401)

    # def test_delete_default_category(self):
    #     res = self.client().delete('/default_category/5', headers={"Authorization": f"Bearer {self.adminToken}"})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['deleted_category_id'])
    
    def test_404_delete_default_category(self):
        res = self.client().delete('/default_category/1000000', headers={"Authorization": f"Bearer {self.adminToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)

    # def test_delete_default_word(self):
    #     res = self.client().delete('/default_word/5', headers={"Authorization": f"Bearer {self.adminToken}"})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['deleted_word_id'])
    
    def test_404_delete_default_word(self):
        res = self.client().delete('/default_word/1000000', headers={"Authorization": f"Bearer {self.adminToken}"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
