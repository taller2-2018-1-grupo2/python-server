import json
import logging
import time

from flask import request, jsonify, make_response
from flask_restful import Resource

from model.friendship_request import FriendshipRequest
from model.user import User
from resources.error_handler import ErrorHandler


class FriendshipResource(Resource):

    def post(self):
        try:
            logging.info("Received SetFriendshipResource POST Request")
            friendship_data = json.loads(request.data)

            User.add_friend(friendship_data["from_username"], friendship_data["to_username"])
            User.add_friend(friendship_data["to_username"], friendship_data["from_username"])

            deleted_friendship_request = FriendshipRequest.delete(friendship_data["from_username"], friendship_data["to_username"])

            if deleted_friendship_request is None:
                logging.debug("Python Server Response: 409 - %s", "No friendship request found for those parameters.")
                return make_response("No friendship request found for those parameters.", 409)
            else:
                logging.debug("Python Server Response: 201 - %s", deleted_friendship_request)
                return make_response(jsonify(deleted_friendship_request), 201)

        except UserNotFoundException:
            error = "Unable to find a User with the parameters given. SetFriendshipResource POST Request"
            logging.error("Python Server Response: 403 - %s", error)
            return ErrorHandler.create_error_response(403, error)
        except ValueError:
            error = "Unable to handle SetFriendshipResource POST Request"
            logging.error("Python Server Response: 500 - %s", error)
            return ErrorHandler.create_error_response(500, error)
        
