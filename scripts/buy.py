
from flask_restful import Resource
from flask import request
from sites.walmart import Walmart
from utils import *
class Buy(Resource):
    def post(self):
        task_id = request.values.get('task_id')
        status_signal = request.values.get('status_signal')
        image_signal = request.values.get('image_signal')
        product = request.values.get('product')
        profile = request.values.get('profile')
        proxy = request.values.get('proxy')
        monitor_delay = request.values.get('monitor_delay')
        error_delay = request.values.get('error_delay')
        max_price = request.values.get('max_price')
        Walmart(task_id, status_signal, image_signal, product, profile, proxy, monitor_delay, error_delay, max_price)