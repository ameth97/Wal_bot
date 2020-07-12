import pandas as pd
try:
    from Crypto import Random
    from Crypto.Cipher import AES
except:
    from Cryptodome import Random
    from Cryptodome.Cipher import AES
from colorama import init, Fore, Back, Style
from datetime import datetime
import json, platform, darkdetect, random, threading, hashlib, base64
from webhook import DiscordWebhook, DiscordEmbed
from settings import get_settings

# this is for coloring
normal_color = Fore.BLUE
e_key = "YnJ1aG1vbWVudA==".encode()
BLOCK_SIZE=16
if platform.system() == "Windows":
    init(convert=True)
else:
    init()

class EventLogger:
    def ts(self):
        return str(datetime.now())[:-7]
    def normal(self,task_id,msg):
        print(normal_color + "[{}][TASK {}] {}".format(self.ts(),task_id,msg))
    def alt(self,task_id,msg):
        print(Fore.MAGENTA + "[{}][TASK {}] {}".format(self.ts(),task_id,msg))
    def error(self,task_id,msg):
        print(Fore.RED + "[{}][TASK {}] {}".format(self.ts(),task_id,msg))
    def success(self,task_id,msg):
        print(Fore.GREEN + "[{}][TASK {}] {}".format(self.ts(),task_id,msg))
    def present(self, msg):
        print(Fore.WHITE + "[{}] {}".format(self.ts(), msg))

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

def send_webhook(webhook_type, site, profile, task_id, image_url, price, email, product):
    settings = get_settings()
    if settings["webhook"]!="":
        webhook = DiscordWebhook(url=settings["webhook"], username="walmart Bot", avatar_url="https://i.imgur.com/tdp2hPi.jpg")
        if webhook_type == "OP":
            if not settings["webhook_on_order"]:
                return
            embed = DiscordEmbed(title="Order Placed",color=0x34c693)

        elif webhook_type == "PF":
            if not settings["webhook_on_failed"]:
                return
            embed = DiscordEmbed(title="Payment Failed", color=0xfc5151)
        embed.set_footer(text="Via walmart Bot",icon_url="https://i.imgur.com/tdp2hPi.jpg")
        embed.add_embed_field(name="Site", value=site, inline=False)
        embed.add_embed_field(name="Profile", value=profile)
        embed.add_embed_field(name="Quantity", value="1")
        embed.add_embed_field(name="Price", value=str(price))
        embed.add_embed_field(name="email", value=email, inline=False)
        embed.add_embed_field(name="Product", value=product, inline=False)
        embed.set_thumbnail(url=image_url)
        embed.set_timestamp()
        webhook.add_embed(embed)
        try:
            webhook.execute()
        except:
            pass
