from utils import return_data, write_data    
    
def load_proxies():
    print("loading proxies...")
    try:
        f = open("my_proxies.txt", "rt")
        proxies = f.read()
        f.close()
        list_name = "news"
        if proxies != "" and list_name != "":
            for item in proxies.splitlines():
                if ":" not in item or item == "":
                    print("Incorrect Proxies")
                    return
            proxies_data = {
                "list_name": list_name,
                "proxies": proxies
            }
            proxies = return_data("./data/proxies.json")
            for p in proxies:
                if p["list_name"] == list_name:
                    proxies.remove(p)
                    break
            proxies.append(proxies_data)
            write_data("./data/proxies.json",proxies)

            print("Loaded Proxies")
    except Exception as e:
        print("loading proxies failed...check myproxies.txt")
        raise e
 