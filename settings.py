import json

def return_data(path):
    with open(path,"r") as file:
        data = json.load(file)
    file.close()
    return data

data = return_data('data/settings.json')[0]
global webhook
webhook = data["webhook"]
global webhook_on_order
webhook_on_order = data["webhookonfailed"]
global webhook_on_failed
webhook_on_failed = data["webhookonorder"]
