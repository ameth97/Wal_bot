import concurrent.futures
from sites.walmart import Walmart
from my_scripts.transform_tasks import create_tasks
from utils import get_profile, get_proxy, return_data
from my_scripts.load_proxies import load_proxies


def get_tasks(profile_name):
      
      create_tasks(profile_name)
      tasks_data = return_data("./data/tasks.json")
      return tasks_data

def buy_product(task):

    profile, proxy = get_profile(task["profile"]), get_proxy(task["proxies"])
    Walmart(task["task_id"], None, None, task["product"], profile, proxy, task["monitor_delay"], task["error_delay"], task["max_price"], flask=True, proxies=task["proxies"])

    return 'ok'

if __name__ == '__main__':
    load_proxies()
    profile_name = "./profiles.csv"
    tasks = get_tasks(profile_name)
    executor = concurrent.futures.ProcessPoolExecutor(20)
    futures = [executor.submit(buy_product, task) for task in tasks]
    concurrent.futures.wait(futures)
