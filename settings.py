
def read_settings(path):
    settings = {}
    with open(path,"r") as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
        for line in lines:
            key, val = line.split(":", 1)
            settings[key] = val
    file.close()
    return settings

def get_settings():
    settings = read_settings('settings.txt')
    settings["webhookonfailed"] = bool(settings["webhookonfailed"])
    settings["webhookonorder"] = bool(settings["webhookonorder"])
    return settings

