class UserVO:

    def __init__(self, user_id, username, email, name, profile_pic, friends_usernames, firebase_token):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.name = name
        self.profile_pic = profile_pic
        self.friends_usernames = friends_usernames
        self.firebase_token = firebase_token
