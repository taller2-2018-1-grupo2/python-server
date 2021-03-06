# Lo siguiente debe inicializarse en setup.py
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
########
import unittest
from config.mongodb import db
from app import app
from mock import patch
import json
import config.firebase_config

test_user = {
    "username": "asd",
    "password": "123",
    "email": "asd@asd.com",
    "name": "Nombre Apellido",
    "profile_pic": "",
    "firebase_token": "fdsfsdfjsdkfhsdjklhjk23h4234"
}

test_second_user = {
    "username": "456",
    "password": "456",
    "email": "asd@asd.com",
    "name": "Nombre Apellido",
    "firebase_token": "fdsfsdfjsdkfhsdjklhjk23h555"
}

test_third_user = {
    "username": "789",
    "password": "789",
    "email": "asd@asd.com",
    "name": "Nombre Apellido",
    "firebase_token": "fdsfsdfjsdkfhsdjklhjk23h777"
}

test_friendship_request = {
    "from_username": "asd",
    "to_username": "456"
}

test_story = {
    "location": "",
    "visibility": "public",
    "title": "un titulo",
    "description": "una descripcion",
    "is_quick_story": "true",
    "timestamp": "2018-06-25 15:44:05"
}

headers = {'content-type': 'application/json', 'Authorization': 'Bearer {}'.format("asd")}


class StoriesResourceTestCase(unittest.TestCase):

    def setUp(self):
        config.firebase_config.FIREBASE_NOTIFICATIONS_ENABLED = False
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        with app.app_context():
            db.stories.delete_many({})
            db.users.delete_many({})
            db.requests_stats.delete_many({})
            db.friendship_requests.delete_many({})

    @patch('requests.post')
    def test_get_all_stories_nonexistent_user(self, mock_post):
        mock_post.return_value.status_code = 200
        response = self.app.get("/api/v1/stories?user_id=sarasa", headers=headers)
        self.assertEqual(response.status_code, 403)

    @patch('resources.user_resource.requests.post')
    def test_get_all_stories_empty(self, mock_post):
        mock_post.return_value.status_code = 200
        response = {
            "token": {
                "expiresAt": "123",
                "token": "asd"
            }
        }
        mock_post.return_value.text = json.dumps(response)

        user = test_user.copy()

        response = self.app.post("/api/v1/users",
                                 data=json.dumps(user),
                                 content_type='application/json')
        user_response = json.loads(response.data)
        user_id = user_response["user"]["user_id"]
        response = self.app.get("/api/v1/stories?user_id={}".format(user_id), headers=headers)
        self.assertEqual(response.status_code, 200)
        stories_response = json.loads(response.data)
        stories = stories_response["stories"]
        self.assertEqual(len(stories), 0)

    @patch('resources.user_resource.requests.post')
    @patch('resources.user_resource.requests.get')
    def test_post_story(self, mock_get, mock_post):
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 200
        response = {
            "token": {
                "expiresAt": "123",
                "token": "asd"
            }
        }
        mock_post.return_value.text = json.dumps(response)

        user = test_user.copy()

        response = self.app.post("/api/v1/users",
                                 data=json.dumps(user),
                                 content_type='application/json')
        user_response = json.loads(response.data)
        user_id = user_response["user"]["user_id"]

        story = test_story.copy()
        story["user_id"] = user_id
        response = self.app.post("/api/v1/stories",
                                 data=json.dumps(story),
                                 headers=headers)
        self.assertEqual(response.status_code, 200)
        response = self.app.get("/api/v1/stories?user_id={}".format(user_id), headers=headers)
        stories_response = json.loads(response.data)
        stories = stories_response["stories"]
        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0]["title"], test_story["title"])
        self.assertEqual(stories[0]["description"], test_story["description"])

    @patch('resources.user_resource.requests.post')
    @patch('resources.user_resource.requests.get')
    def test_post_story_no_data(self, mock_get, mock_post):
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 200
        response = {
            "token": {
                "expiresAt": "123",
                "token": "asd"
            }
        }
        mock_post.return_value.text = json.dumps(response)

        response = self.app.post("/api/v1/stories",
                                 headers=headers)
        self.assertEqual(response.status_code, 500)

    @patch('resources.user_resource.requests.post')
    def test_post_and_delete_story(self, mock_post):
        mock_post.return_value.status_code = 200
        response = {
            "token": {
                "expiresAt": "123",
                "token": "asd"
            }
        }
        mock_post.return_value.text = json.dumps(response)

        user = test_user.copy()

        response = self.app.post("/api/v1/users",
                                 data=json.dumps(user),
                                 content_type='application/json')
        user_response = json.loads(response.data)
        user_id = user_response["user"]["user_id"]

        story = test_story.copy()
        story["user_id"] = user_id
        response = self.app.post("/api/v1/stories",
                                 data=json.dumps(story),
                                 headers=headers)
        response_story = json.loads(response.data)

        response = self.app.delete("/api/v1/stories/{}".format(response_story["id"]), headers=headers)
        self.assertEqual(response.status_code, 201)

    @patch('requests.post')
    def test_delete_nonexistent_story(self, mock_post):
        mock_post.return_value.status_code = 200
        response = self.app.delete("/api/v1/stories/{}".format("sarasa"), headers=headers)
        self.assertEqual(response.status_code, 409)

    @patch('requests.post')
    def test_stories_from_non_existent_user(self, mock_post):
        mock_post.return_value.status_code = 200
        username = "one_username"
        user_id = "one_user_id"
        response = self.app.get("/api/v1/stories/from/{}/{}".format(username, user_id), headers=headers)
        self.assertEqual(response.status_code, 403)

    @patch('requests.post')
    def test_stories_from_user(self, mock_post):
        mock_post.return_value.status_code = 200
        response = {
            "token": {
                "expiresAt": "123",
                "token": "asd"
            }
        }
        mock_post.return_value.text = json.dumps(response)
        user = test_user.copy()
        response = self.app.post("/api/v1/users",
                                 data=json.dumps(user),
                                 content_type='application/json')
        user_response = json.loads(response.data)
        user_id = user_response["user"]["user_id"]
        story = test_story.copy()
        story["user_id"] = user_id
        self.app.post("/api/v1/stories",
                      data=json.dumps(story),
                      headers=headers)
        story = test_story.copy()
        story["user_id"] = user_id + "1"
        self.app.post("/api/v1/stories",
                      data=json.dumps(story),
                      headers=headers)

        username = user["username"]
        response = self.app.get("/api/v1/stories/from/{}/{}".format(username, user_id), headers=headers)
        self.assertEqual(response.status_code, 200)
        stories_response_data = json.loads(response.data)["stories"]
        self.assertEqual(len(stories_response_data), 1)
        self.assertEqual(stories_response_data[0]["username"], username)
        self.assertEqual(stories_response_data[0]["user_id"], user_id)

    @patch('requests.post')
    def test_stories_from_user2(self, mock_post):
        mock_post.return_value.status_code = 200
        response = {
            "token": {
                "expiresAt": "123",
                "token": "asd"
            }
        }
        mock_post.return_value.text = json.dumps(response)
        user = test_user.copy()
        response = self.app.post("/api/v1/users",
                                 data=json.dumps(user),
                                 content_type='application/json')
        user_response = json.loads(response.data)
        first_user_id = user_response["user"]["user_id"]
        first_user_username = user["username"]
        story = test_story.copy()
        story["user_id"] = first_user_id
        story["visibility"] = "private"
        self.app.post("/api/v1/stories",
                      data=json.dumps(story),
                      headers=headers)
        user = test_second_user.copy()
        response = self.app.post("/api/v1/users",
                                 data=json.dumps(user),
                                 content_type='application/json')
        user_response = json.loads(response.data)
        second_user_id = user_response["user"]["user_id"]
        friendship_request = test_friendship_request.copy()
        self.app.post("/api/v1/friendship/request",
                      data=json.dumps(friendship_request),
                      headers=headers)
        self.app.post("/api/v1/friendship",
                      data=json.dumps(friendship_request),
                      headers=headers)
        user = test_third_user.copy()
        response = self.app.post("/api/v1/users",
                                 data=json.dumps(user),
                                 content_type='application/json')
        user_response = json.loads(response.data)
        third_user_id = user_response["user"]["user_id"]
        third_user_username = user["username"]
        story = test_story.copy()
        story["user_id"] = third_user_id
        story["visibility"] = "private"
        self.app.post("/api/v1/stories",
                      data=json.dumps(story),
                      headers=headers)
        story = test_story.copy()
        story["user_id"] = third_user_id
        self.app.post("/api/v1/stories",
                      data=json.dumps(story),
                      headers=headers)

        response = self.app.get("/api/v1/stories/from/{}/{}".format(first_user_username, second_user_id), headers=headers)
        self.assertEqual(response.status_code, 200)
        stories_response_data = json.loads(response.data)["stories"]
        self.assertEqual(len(stories_response_data), 1)
        self.assertEqual(stories_response_data[0]["username"], first_user_username)
        self.assertEqual(stories_response_data[0]["user_id"], first_user_id)

        response = self.app.get("/api/v1/stories/from/{}/{}".format(third_user_username, second_user_id), headers=headers)
        self.assertEqual(response.status_code, 200)
        stories_response_data = json.loads(response.data)["stories"]
        self.assertEqual(len(stories_response_data), 1)
        self.assertEqual(stories_response_data[0]["username"], third_user_username)
        self.assertEqual(stories_response_data[0]["visibility"], "public")
        self.assertEqual(stories_response_data[0]["user_id"], third_user_id)
