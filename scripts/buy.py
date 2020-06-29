
from flask_restful import Resource
from flask import request
from sites.walmart import Walmart
from utils import *
class Buy(Resource):
    def post(self):
        username =request.values.get('idcard')
        password = request.values.get('cvc')
        print('username: ' + username)
        self.run()
        return username
    def run(self):
        profile,proxy = get_profile(self.profile),get_proxy(self.proxies)
        if profile == None:
            self.status_signal.emit({"msg":"Invalid profile","status":"error"})
            return
        if proxy == None:
            self.status_signal.emit({"msg":"Invalid proxy list","status":"error"})
            return
        Walmart(self.task_id,self.status_signal,self.image_signal,self.product,profile,proxy,self.monitor_delay,self.error_delay,self.max_price)
