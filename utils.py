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


# this is for coloring
normal_color = Fore.BLUE
e_key = "YnJ1aG1vbWVudA==".encode()
BLOCK_SIZE=16
if platform.system() == "Windows":
    init(convert=True)
else:
    init()
print(normal_color + "Starting....")


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
    for profile in profiles:
        if profile["profile_name"]  == profile_name:
            return profile
    return None


def get_proxy(list_name):
    """Given a list proxy name return one randomly choosen proxy

    Args:
        list_name (string): list of the proxy name

    Returns:
        [dict]: [a proxy formatted for request.session]
    """    
    if list_name == "Proxy List" or list_name == "None":
        return False
    proxies = return_data("./data/proxies.json") 
    for proxy_list in proxies:
        if proxy_list["list_name"] == list_name:
            return format_proxy(random.choice(proxy_list["proxies"].splitlines()))
    return None

def format_proxy(proxy):
    """format the proxie from host:port:user:pass to the dict below
    to match requests.session of python

    Args:
        proxy (string): proxy in format host:port:user:pass

    Returns:
        [dict]: proxy dict
    """

    try:
        proxy_parts = proxy.split(":")
        ip, port, user, passw = proxy_parts[0], proxy_parts[1], proxy_parts[2], proxy_parts[3]
        return {
            "http": "http://{}:{}@{}:{}".format(user, passw, ip, port),
            "https": "https://{}:{}@{}:{}".format(user, passw, ip, port)
        }
    except IndexError:
        return {"http": "http://" + proxy, "https": "https://" + proxy}

