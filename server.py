import os
from api.restful_api import *
from flask import Flask
from flask_restful import Api

DATABASE = 'api/meetings_data1.db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)

api.add_resource(GetTries, '/staff_api/user/get_tries/<string:user_id>')
api.add_resource(GetCodes, '/staff_api/prize/codes')

api.add_resource(UserLoading, '/staff_api/user/loading/<string:user_id>/<string:username>/<int:tries>')
api.add_resource(UserWin, '/staff_api/user/win/<string:username>/<string:prize>')
api.add_resource(UserSpinUpdate, '/staff_api/user/spin_update/<string:user_id>/<int:tries>')
api.add_resource(PrizeLoading, '/staff_api/prize/loading/<string:prize_id>/<string:name>')
app.config.update(dict(DATABASE=os.path.join(app.root_path, DATABASE)))

if __name__ == "__main__":
    app.run(port=8000, debug=DEBUG)
