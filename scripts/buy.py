
from flask_restful import Resource
from flask import request
from sites.walmart import Walmart
from utils import *
class Buy(Resource):
    def post(self):
        username =request.values.get('idcard')
        password = request.values.get('cvc')
        print('username: ' + username)
        #run() Walmart class