
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
    settings["webhook_on_failed"] = bool(settings["webhook_on_failed"])
    settings["webhook_on_order"] = bool(settings["webhook_on_order"])
    return settings

