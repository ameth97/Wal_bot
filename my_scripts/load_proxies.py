from utils import return_data, write_data    
    

def load_proxies():
    """
    Function to load proxies from proxies.txt and transform it to json
    """
    try:
        f = open("proxies.txt", "rt")
        proxies = f.read()
        f.close()
        list_name = "news" #I created a default proxy list name, as I though this could evoluate to allow users to use multiple proxy list
        num_proxies = len(proxies.splitlines())
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
            return num_proxies

    except Exception as e:
        print("loading proxies failed...check proxies.txt")
        raise e
 