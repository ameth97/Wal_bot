import concurrent.futures
from sites.walmart import Walmart
from my_scripts.transform_tasks import create_tasks
from utils import get_profile, get_proxy, return_data
from my_scripts.load_proxies import load_proxies


def get_tasks(profile_name):
      
      create_tasks(profile_name)
      tasks_data = return_data("./data/tasks.json")
      l1 = [task["product"] for task in tasks_data]
      l2 = []
      l3 = []
      for i, product in enumerate(l1):
          if product not in l2:
            l3.append((True,i))
            l2.append(product)
          else:
            l3.append((False,l1.index(product)))
      del l1,l2
      for i, task in enumerate(tasks_data):
          task["monitor"] = l3[i][0]
          task["group"] = l3[i][1]
      return tasks_data

def buy_product(task):

    profile, proxy = get_profile(task["profile"]), get_proxy(task["proxies"])
    Walmart(task["task_id"], None, None, task["product"], profile, proxy, task["monitor_delay"], task["error_delay"], 
            task["max_price"], flask=True, proxies=task["proxies"], is_monitored=task["monitor"], 
            profile_name=task["profile"],monitor_group=task['group'], run_task_group=run_task_group)

    return 'ok'

def run_task_group(profile_name, monitor_group):
    tasks = get_tasks(profile_name)
    group = [task for task in tasks if task['group'] == monitor_group]
    executor = concurrent.futures.ProcessPoolExecutor(50)
    futures = [executor.submit(buy_product, task) for task in group]
    concurrent.futures.wait(futures)


def main(profile_name):

    load_proxies()
    tasks = get_tasks(profile_name)
    executor = concurrent.futures.ProcessPoolExecutor(2)
    futures = [executor.submit(buy_product, task) for task in tasks]
    concurrent.futures.wait(futures)



if __name__ == '__main__':
    
    profile_name = "./profiles.csv"
    main(profile_name)
