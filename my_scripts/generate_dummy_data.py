import os.path
import pandas as pd


dummy_profile = """store,link,firstname,lastname,shipping email,shipping phone,shipping adress 1,shipping address 2,shipping city,shipping zipcode,shipping state,shipping_country,billing_fname,billing_lname,billing_email,billing_phone,billing_a1,billing_a2,billing_city,billing_zipcode,billing_state,billing_country,card_number,card_month,card_year,card_type,card_cvv
walmart,https://www.walmart.com/ip/Clemson-Tigers-Colosseum-Wordmark-Arch-Team-Logo-Full-Zip-Hoodie-Orange/363332481,Billo,Part,test@gmail.com,2023250121,tweet,colto,San Bruno,04066,CA,United States,Billo,Part,test@gmail.com,2023250120,topoi,lo,San Bruno,04066,CA,United States,5104098076542470,11,2021,MASTERCARD,653
walmart,https://www.walmart.com/ip/Wilson-Hex-Stinger-Soccer-Ball-Size-3/631216105,Billo,Part,test@gmail.com,2023250121,aksdk,mail,San Bruno,94066,CA,United States,Billo,Part,test@gmail.com,2023250120,kol,oo,San Bruno,94066,CA,United States,5104098076542470,11,2021,MASTERCARD,653
walmart,https://www.walmart.com/ip/Wilson-Hex-Stinger-Soccer-Ball-Size-3/631216105,Billo,Part,test@gmail.com,2023250121,aksdk,mail,San Bruno,94066,CA,United States,Billo,Part,test@gmail.com,2023250120,kol,oo,San Bruno,94066,CA,United States,5104098076542470,11,2021,MASTERCARD,653
walmart,https://www.walmart.com/ip/Clemson-Tigers-Colosseum-Wordmark-Arch-Team-Logo-Full-Zip-Hoodie-Orange/363332481,Billo,Part,test@gmail.com,2023250121,tweet,colto,San Bruno,04066,CA,United States,Billo,Part,test@gmail.com,2023250120,topoi,lo,San Bruno,04066,CA,United States,5104098076542470,11,2021,MASTERCARD,653
"""

dummy_proxies = """zproxy.lum-superproxy.io:22225:lum-customer-hl_6c936c5b-zone-footdev-ip-104.227.165.3:9wrn77wwkv75
zproxy.lum-superproxy.io:22225:lum-customer-hl_6c936c5b-zone-footdev-ip-67.227.83.169:9wrn77wwkv75"""

dummy_proxies_json = """[{"list_name": "news", "proxies": ""}]"""

dummy_settings = """webhook:https://discord.com/api/webhooks/730885837255868467/f5HbIOX0J8Wd0KuNyrgdpRH47qTOZs1URIYEn_whTAJzlZHS5qI3tsAH3T2banskCR5L
webhook_on_order:True
webhook_on_failed:True
monitor_delay:5.0
error_delay:5.0
"""

def generate_dummy_data():

    if not os.path.exists("./data"):
        os.mkdir("data")
        
    for filename, dummy_data in [("settings.txt", dummy_settings), ("tasks.csv", dummy_profile),
                                ("proxies.txt", dummy_proxies), ("data/proxies.json", dummy_proxies_json)]:
        if not os.path.isfile(filename):
            print("generating dummy " + filename + "...")
            f=open(filename,"wb")
            f.write(dummy_data.encode())
            f.close()




