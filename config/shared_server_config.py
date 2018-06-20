import os

SHARED_SERVER_URI = 'https://shared-server-stories.herokuapp.com'
SHARED_SERVER_APPLICATION_OWNER = os.getenv('SHARED_SERVER_NAME', 'newModifiedName')
SHARED_SERVER_TOKEN = os.getenv('SHARED_SERVER_TOKEN')
SHARED_SERVER_TOKEN_VALIDATION_PATH = SHARED_SERVER_URI + '/api/token_check'
SHARED_SERVER_PING_PATH = SHARED_SERVER_URI + '/api/ping'
SHARED_SERVER_USER_PATH = SHARED_SERVER_URI + '/api/user'
SHARED_SERVER_TOKEN_PATH = SHARED_SERVER_URI + '/api/token'
SHARED_SERVER_FILE_UPLOAD_PATH = SHARED_SERVER_URI + '/api/files/upload_multipart'
