from utils import return_data, write_data    
    

def load_proxies():
    """
    Function to load proxies from my_proxies.txt and transform it to json
    """
    print("loading proxies...")
    try:
        f = open("my_proxies.txt", "rt")
        proxies = f.read()
        f.close()
        list_name = "news" #I created a default proxy list name, as I though this could evoluate to allow users to use multiple proxy list
        if proxies != "" and list_name != "":
            for item in proxies.splitlines():
                if ":" not in item or item == "":
                    print("Incorrect Proxies")
                    return
            proxies_data = { #the json format saved in data/proxies.json
                "list_name": list_name,
                "proxies": proxies
            }
            proxies = return_data("./data/proxies.json") #read json as dict
            for p in proxies:
                if p["list_name"] == list_name: 
                    proxies.remove(p) #remove previous news proxy list 
                    break
            proxies.append(proxies_data)
            write_data("./data/proxies.json",proxies)

            print("Loaded Proxies")
    except Exception as e:
        print("loading proxies failed...check myproxies.txt")
        raise e
 