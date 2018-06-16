from config.mongodb import db
from pymongo import ReturnDocument
from model.db.storyVO import StoryVO
import uuid


class StoryNotFoundException(Exception):
    pass


from .user import User

class Story:

    @staticmethod
    def get_all():
        db_response = list(db.stories.find())
        response = {
            "stories": []
        }

        for story in db_response:
            response["stories"].append(Story._decode(story))

        return response

    @staticmethod
    def get_by_user(userId):

        # Get all public stories
        publicStories = list(db.stories.find({ "visibility": "public" }))

        # Get all private stories
        privateStories = list(db.stories.find({ "visibility": "private" }))

        # Filter out private stories, keeping only
        # 1) Private stories of the user
        # 2) Private stories of the user's friends
        user = db.users.find_one({ "user_id": userId })
        userFriendsIds = list()

        for friends_username in user["friends_usernames"]:
            friend = db.users.find_one({ "username": friends_username })
            userFriendsIds.append(friend["user_id"])

        validUserIds = userFriendsIds + [userId]
        visiblePrivateStories = list()

        for privateStory in privateStories:
            if privateStory["user_id"] in validUserIds:
                visiblePrivateStories.append(privateStory)

        # Merge all stories
        result = publicStories + visiblePrivateStories

        response = {
            "stories": []
        }

        for story in result:
            response["stories"].append(Story._decode(story))

        return response

    @staticmethod
    def create(user_id, location, visibility, title, description, is_quick_story, timestamp):
        id = str(uuid.uuid4())
        new_story = StoryVO(id, user_id, location, visibility, title, description, is_quick_story, timestamp)
        encoded_story = Story._encode(new_story)
        db.stories.insert_one(encoded_story)
        response = Story._decode(encoded_story)
        return response

    @staticmethod
    def update(story_id, file_url):
        updated_fields = {
            "file_url": file_url
        }
        result = db.stories.find_one_and_update({"id": story_id}, {'$set': updated_fields},
                                                return_document=ReturnDocument.AFTER)
        if result is None:
            raise StoryNotFoundException("There is no story with that ID!")
        response = Story._decode(result)
        return response

    @staticmethod
    def _encode(item):
        return {
            "_type": "story",
            "id": item.id,
            "user_id": item.user_id,
            "location": item.location,
            "visibility": item.visibility,
            "title": item.title,
            "description": item.description,
            "file_url": item.file_url,
            "is_quick_story": item.is_quick_story,
            "timestamp": item.timestamp
        }

    @staticmethod
    def _decode(document):
        assert document["_type"] == "story"
        story = {
            "id": document["id"],
            "user_id": document["user_id"],
            "location": document["location"],
            "visibility": document["visibility"],
            "title": document["title"],
            "description": document["description"],
            "file_url": document["file_url"],
            "is_quick_story": document["is_quick_story"],
            "timestamp": document["timestamp"]
        }
        return story
