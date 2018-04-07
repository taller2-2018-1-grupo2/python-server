from flask import Flask
from flask_restful import Api

from model.mongodb import mongo
from resources.cat_resource import CatResource
from resources.user_resource import UserDetailResource
from resources.user_resource import UserInsertionResource
from resources.user_resource import UsersCountResource
from resources.user_resource import UsersResource
from resources.ping_resource import PingResource
from resources.ping_resource import PingSharedServerResource

app = Flask("python_server")

api = Api(app, prefix="/api/v1")

# connect to another MongoDB database
app.config['MONGO_DBNAME'] = 'python_server'
mongo.init_app(app, config_prefix='MONGO')

api.add_resource(UsersResource, '/users')
api.add_resource(UsersCountResource, '/users/count')
api.add_resource(UserDetailResource, '/users/<string:user_id>')
api.add_resource(UserInsertionResource, '/users/insert')

api.add_resource(PingResource, '/ping')
api.add_resource(PingSharedServerResource, '/pingSharedServer')

api.add_resource(CatResource, '/cats')

@app.route('/')
def hello_world():
    return "Hi, I'm a Python Server!"


if __name__ == '__main__':
    app.run()
