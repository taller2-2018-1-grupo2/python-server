# Lo siguiente debe inicializarse en setup.py
import os
import sys

from mock import patch

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
########
from config.mongodb import db
from app import app
import unittest
import json
import config.firebase_config

test_direct_message = {
    "from_username": "123",
    "to_username": "456",
    "message": "Hello!"
}

test_first_user = {
    "username": "123",
    "password": "123",
    "email": "asd@asd.com",
    "name": "Nombre Apellido",
    "firebase_token": "fdsfsdfjsdkfhsdjklhjk23h4234"
}

test_second_user = {
    "username": "456",
    "password": "456",
    "email": "asd@asd.com",
    "name": "Nombre Apellido",
    "firebase_token": "fdsfsdfjsdkfhsdjklhjk23h555"
}

test_otro_user = {
    "username": "otro",
    "password": "456",
    "email": "asd@asd.com",
    "name": "Nombre Apellido",
    "firebase_token": "fdsfsdfjsdkfhsdjklhjk23h888"
}

headers = {'content-type': 'application/json', 'Authorization': 'Bearer {}'.format("asd")}


class DirectMessageResourceTestCase(unittest.TestCase):

    @patch('resources.user_resource.requests.post')
    def setUp(self, mock_post):
        mock_post.return_value.status_code = 200
        config.firebase_config.FIREBASE_NOTIFICATIONS_ENABLED = False
        self.app = app.test_client()
        self.app.testing = True

        user1 = test_first_user.copy()
        user2 = test_second_user.copy()
        user3 = test_otro_user.copy()

        self.app.post("/api/v1/users",
                      data=json.dumps(user1),
                      content_type='application/json')

        self.app.post("/api/v1/users",
                      data=json.dumps(user2),
                      content_type='application/json')

        self.app.post("/api/v1/users",
                      data=json.dumps(user3),
                      content_type='application/json')

    def tearDown(self):
        with app.app_context():
            db.direct_messages.delete_many({})
            db.requests_stats.delete_many({})

    @patch('resources.token_validation_decorator.requests.post')
    def test_create_direct_message(self, mock_post):
        mock_post.return_value.status_code = 200
        direct_message = test_direct_message.copy()

        response = self.app.post("/api/v1/direct_message",
                                 data=json.dumps(direct_message),
                                 headers=headers)
        self.assertEqual(response.status_code, 201)
        direct_message_response = json.loads(response.data)
        direct_message_response["direct_message"].pop("_id")
        direct_message_response["direct_message"].pop("timestamp")
        self.assertEqual(direct_message, direct_message_response["direct_message"])

    @patch('resources.token_validation_decorator.requests.post')
    def test_no_data(self, mock_post):
        mock_post.return_value.status_code = 200

        response = self.app.post("/api/v1/direct_message",
                                 headers=headers)
        self.assertEqual(response.status_code, 500)

    @patch('resources.token_validation_decorator.requests.post')
    def test_received_messages(self, mock_post):
        mock_post.return_value.status_code = 200
        direct_message = test_direct_message.copy()

        self.app.post("/api/v1/direct_message",
                      data=json.dumps(direct_message),
                      headers=headers)
        uri = "/api/v1/direct_message/received/" + direct_message["to_username"]
        response = self.app.get(uri, headers=headers)
        self.assertEqual(response.status_code, 200)
        direct_message_response = json.loads(response.data)
        self.assertEqual(len(direct_message_response["direct_messages"]), 1)
        self.assertEqual(direct_message_response["direct_messages"][0]["to_username"],
                         direct_message["to_username"])

    @patch('resources.token_validation_decorator.requests.post')
    def test_message_to_non_existent_user(self, mock_post):
        mock_post.return_value.status_code = 200
        direct_message = test_direct_message.copy()
        direct_message["to_username"] = direct_message["to_username"] + "1"

        response = self.app.post("/api/v1/direct_message",
                                 data=json.dumps(direct_message),
                                 headers=headers)
        self.assertEqual(response.status_code, 403)

    @patch('resources.token_validation_decorator.requests.post')
    def test_user_messages_count(self, mock_post):
        mock_post.return_value.status_code = 200
        direct_message = test_direct_message.copy()
        self.app.post("/api/v1/direct_message",
                      data=json.dumps(direct_message),
                      headers=headers)

        other_test_direct_message = {
            "from_username": direct_message["to_username"],
            "to_username": direct_message["from_username"],
            "message": "Hi! How are you?"
        }
        self.app.post("/api/v1/direct_message",
                      data=json.dumps(other_test_direct_message),
                      headers=headers)

        uri = "/api/v1/direct_message/" + direct_message["to_username"]
        response = self.app.get(uri, headers=headers)
        direct_message_response = json.loads(response.data)
        self.assertEqual(len(direct_message_response["direct_messages"]), 1)

    @patch('resources.user_resource.requests.post')
    @patch('model.firebase_manager.messaging.send')
    def test_send_firebase_notification(self, mock_messaging, mock_post):
        config.firebase_config.FIREBASE_NOTIFICATIONS_ENABLED = True
        mock_messaging.return_value.status_code = 200
        with app.app_context():
            db.users.delete_many({})
        mock_post.return_value.status_code = 200
        response = {
            "token": {
                "expiresAt": "123",
                "token": "asd"
            }
        }
        mock_post.return_value.text = json.dumps(response)

        user1 = test_first_user.copy()
        self.app.post("/api/v1/users", data=json.dumps(user1), content_type='application/json')

        direct_message = test_direct_message.copy()
        user = {
            "username": direct_message["to_username"],
            "password": "123",
            "email": "asd@asd.com",
            "name": "Nombre Apellido",
            "profile_pic": "",
            "firebase_token": "fdsfsdfjsdkfhsdjklhjk23h4234",
        }

        self.app.post("/api/v1/users", data=json.dumps(user), content_type='application/json')

        self.app.post("/api/v1/direct_message",
                      data=json.dumps(direct_message),
                      headers=headers)

        mock_messaging.call_args_list[0][0][0].notification = direct_message["message"]
        mock_messaging.call_args_list[0][0][0].title = user1["name"]
        mock_messaging.assert_called()

    @patch('resources.token_validation_decorator.requests.post')
    def test_user_messages(self, mock_post):
        mock_post.return_value.status_code = 200
        direct_message = test_direct_message.copy()
        self.app.post("/api/v1/direct_message",
                      data=json.dumps(direct_message),
                      headers=headers)

        other_test_direct_message = {
            "from_username": direct_message["to_username"],
            "to_username": "otro",
            "message": "Hi! How are you?"
        }
        self.app.post("/api/v1/direct_message",
                      data=json.dumps(other_test_direct_message),
                      headers=headers)

        uri = "/api/v1/direct_message/" + direct_message["to_username"]
        response = self.app.get(uri, headers=headers)
        direct_message_response = json.loads(response.data)
        self.assertEqual(len(direct_message_response["direct_messages"]), 2)
        self.assertLessEqual(direct_message_response["direct_messages"][0]["timestamp"],
                             direct_message_response["direct_messages"][1]["timestamp"])

    @patch('resources.token_validation_decorator.requests.post')
    def test_conversation_messages(self, mock_post):
        mock_post.return_value.status_code = 200
        direct_message = test_direct_message.copy()
        self.app.post("/api/v1/direct_message",
                      data=json.dumps(direct_message), headers=headers)

        other_test_direct_message = {
            "from_username": direct_message["to_username"],
            "to_username": direct_message["from_username"],
            "message": "Hi! How are you?"
        }
        self.app.post("/api/v1/direct_message",
                      data=json.dumps(other_test_direct_message),
                      headers=headers)

        other_test_direct_message = {
            "from_username": direct_message["to_username"],
            "to_username": "otro",
            "message": "Hi! How are you?"
        }
        self.app.post("/api/v1/direct_message",
                      data=json.dumps(other_test_direct_message),
                      headers=headers)

        uri = "/api/v1/direct_message/conversation/" + direct_message["from_username"] + "/" + direct_message[
            "to_username"]
        response = self.app.get(uri, headers=headers)
        self.assertEqual(response.status_code, 200)
        direct_message_response = json.loads(response.data)
        self.assertEqual(len(direct_message_response["direct_messages"]), 2)
        users = [direct_message["from_username"], direct_message["to_username"]]
        self.assertIn(direct_message_response["direct_messages"][0]["from_username"], users)
        self.assertIn(direct_message_response["direct_messages"][0]["to_username"], users)
        self.assertIn(direct_message_response["direct_messages"][1]["from_username"], users)
        self.assertIn(direct_message_response["direct_messages"][1]["to_username"], users)
        self.assertLessEqual(direct_message_response["direct_messages"][0]["timestamp"],
                             direct_message_response["direct_messages"][1]["timestamp"])
    #        messaging.send.assert_called_once_with(direct_message["from_username"], direct_message["to_username"],
    #                                               direct_message["message"])

    @patch('resources.token_validation_decorator.requests.post')
    def test_conversation_messages_non_existent_friend(self, mock_post):
        mock_post.return_value.status_code = 200
        direct_message = test_direct_message.copy()
        self.app.post("/api/v1/direct_message",
                      data=json.dumps(direct_message), headers=headers)

        other_test_direct_message = {
            "from_username": direct_message["to_username"],
            "to_username": direct_message["from_username"],
            "message": "Hi! How are you?"
        }
        self.app.post("/api/v1/direct_message",
                      data=json.dumps(other_test_direct_message),
                      headers=headers)

        other_test_direct_message = {
            "from_username": direct_message["to_username"],
            "to_username": "otro",
            "message": "Hi! How are you?"
        }
        self.app.post("/api/v1/direct_message",
                      data=json.dumps(other_test_direct_message),
                      headers=headers)

        uri = "/api/v1/direct_message/conversation/" + direct_message["from_username"] + "/" + direct_message[
            "to_username"] + "1"
        response = self.app.get(uri, headers=headers)
        self.assertEqual(response.status_code, 403)
