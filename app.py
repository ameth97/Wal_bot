from flask import Flask
from flask_restful import Api
from scripts.buy import Buy
app = Flask(__name__)
api = Api(app)

@app.route('/')
def hello():
    return "Hello World!"
api.add_resource(Buy,'/buy')
if __name__ == '__main__':
    app.run(debug=True)