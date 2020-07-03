import concurrent.futures
from sites.walmart import Walmart
from my_scripts.transform_tasks import create_tasks
from utils import get_profile, get_proxy, return_data
from my_scripts.load_proxies import load_proxies


def get_tasks(profile_name):
    """retrun the task data

    Args:
        profile_name (string): profile id

    Returns:
        dict: tasks data
    """      
    create_tasks(profile_name)
    tasks_data = return_data("./data/tasks.json")

    #here we give the same groupid for the task with the same product link as monitoring group
    #monitor is true for only one element of the group
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
    """given a task this call walmart class for buying

    Args:
        task (dict): task

    Returns:
        [string]: [description]
    """    
    profile, proxy = get_profile(task["profile"]), get_proxy(task["proxies"])
    # print(profile)
    Walmart(task["task_id"], None, None, task["product"], profile, proxy, task["monitor_delay"], task["error_delay"], 
            task["max_price"], flask=True, proxies=task["proxies"], is_monitored=task["monitor"], 
            profile_name=task["profile"],monitor_group=task['group'], run_task_group=run_task_group)

    return 'ok'

def run_task_group(profile_name, monitor_group):
    # this run tasks of one group when the restock is complete
    tasks = get_tasks(profile_name)
    group = [task for task in tasks if task['group'] == monitor_group]
    executor = concurrent.futures.ProcessPoolExecutor(20)
    futures = [executor.submit(buy_product, task) for task in group]
    concurrent.futures.wait(futures)


def main(profile_name):
    # here we multiprocess the tasks in tasks dict by 20 at a time
    load_proxies()
    tasks = get_tasks(profile_name)
    # print(tasks)
    executor = concurrent.futures.ProcessPoolExecutor(4)
    futures = [executor.submit(buy_product, task) for task in tasks]
    concurrent.futures.wait(futures)



if __name__ == '__main__':
    
    profile_name = "./profiles.csv"
    main(profile_name)
