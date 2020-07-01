import pandas as pd
try:
    from Crypto import Random
    from Crypto.Cipher import AES
except:
    from Cryptodome import Random
    from Cryptodome.Cipher import AES
from colorama import init, Fore, Back, Style
from datetime import datetime
import json, platform, darkdetect, random, settings, threading, hashlib, base64

normal_color = Fore.BLUE
e_key = "YnJ1aG1vbWVudA==".encode()
BLOCK_SIZE=16
if platform.system() == "Windows":
    init(convert=True)
else:
    init()
print(normal_color + "Starting....")
class Encryption:

    def encrypt(self,msg):
        IV = Random.new().read(BLOCK_SIZE)
        aes = AES.new(self.trans(e_key), AES.MODE_CFB, IV)
        return base64.b64encode(IV + aes.encrypt(msg.encode("utf-8")))
    
    def decrypt(self,msg):
        msg = base64.b64decode(msg)
        IV = msg[:BLOCK_SIZE]
        aes = AES.new(self.trans(e_key), AES.MODE_CFB, IV)
        return aes.decrypt(msg[BLOCK_SIZE:])
    
    def trans(self,key):
        return hashlib.md5(key).digest()

def return_data(path):
    with open(path,"r") as file:
        data = json.load(file)
    file.close()
    return data

def write_data(path,data):
    with open(path, "w") as file:
        json.dump(data, file)
    file.close()

def get_profile(profile_name):
    profiles = return_data("./data/profiles.json")
    for p in profiles:
        if p["profile_name"] == profile_name:
            try:
                p["card_number"] = (Encryption().decrypt(p["card_number"].encode("utf-8"))).decode("utf-8")
            except ValueError:
                pass
            return p
    return None



def get_proxy(list_name):
    if list_name == "Proxy List" or list_name == "None":
        return False
    proxies = return_data("./data/proxies.json") 
    for proxy_list in proxies:
        if proxy_list["list_name"] == list_name:
            return format_proxy(random.choice(proxy_list["proxies"].splitlines()))
    return None

def format_proxy(proxy):
    try:
        proxy_parts = proxy.split(":")
        ip, port, user, passw = proxy_parts[0], proxy_parts[1], proxy_parts[2], proxy_parts[3]
        return {
            "http": "http://{}:{}@{}:{}".format(user, passw, ip, port),
            "https": "https://{}:{}@{}:{}".format(user, passw, ip, port)
        }
    except IndexError:
        return {"http": "http://" + proxy, "https": "https://" + proxy}

