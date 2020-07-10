
#!/usr/bin/env python
import pandas as pd


def transform_to_json_profile(csv_df):
    
    """
    read user profile from the csv dataframe and transform it to data/profile.json

    Args:
        csv_df (pandas dataframe): csv returned by create_tasks
    """
    
    csv_df = csv_df.rename(columns={

        "firstname": "shipping_fname",
        "lastname": "shipping_lname",
        "shipping email": "shipping_email",
        "shipping phone": "shipping_phone",
        "shipping adress 1": "shipping_a1",
        "shipping address 2": "shipping_a2",
        "shipping city": "shipping_city",
        "shipping zipcode": "shipping_zipcode",
        "shipping state": "shipping_state",

    }) #rename_column to match data posted by walmart

    csv_df.fillna('', inplace=True)
    csv_df = csv_df.astype(str)
    csv_df["card_month"] = csv_df['card_month'].str.zfill(2)
    csv_df.to_json(path_or_buf='data/profiles.json', orient='records')

def create_tasks(csv_path):
    """
    create tasks as json file with task_id, link and profile_id associated (take a look at data/tasks.json)
    this allows to use 1 profile for multiple tasks important for evolution
    the user could have 1 profile and associate it to multiples tasks rather than having 1 profile for 1 task
    Args:
        csv_path (string): path of the profiles.csv file

    Returns:
        [pandas dataframe]: csv containing only profile infos
    """

    csv_df = pd.read_csv(csv_path, dtype=object, sep=',')
    
    task_df = csv_df[["store", "link"]].copy().rename(
        columns={'store': 'site', 'link': 'product'})
    task_df["profile"] = task_df.index
    task_df["monitor_delay"] = "5.0" #delay to send request for monitorinf
    task_df["error_delay"] = "5.0" #delay to retry when there is error
    task_df["max_price"] = "" #not user for now, but permits to not buy if the price is below this
    task_df["proxies"] = "news" #proxy list name
    task_df["site"] = "Walmart" # site name
    task_df["task_id"] = task_df.index 
    task_df.fillna('', inplace=True)
    task_df = task_df.astype(str)
    

    csv_df["profile_name"] = task_df.index

    del csv_df['store'], csv_df['link']

    task_df.to_json(path_or_buf='data/tasks.json', orient='records')

    return transform_to_json_profile(csv_df)


if __name__ == "__main__":
    create_tasks('./profiles.csv')
