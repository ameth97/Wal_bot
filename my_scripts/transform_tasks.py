
#!/usr/bin/env python
import pandas as pd


def transform_to_json_profile(csv_df):

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

    })

    csv_df.fillna('', inplace=True)
    csv_df = csv_df.astype(str)
    csv_df["card_month"] = csv_df['card_month'].str.zfill(2)
    csv_df.to_json(path_or_buf='data/profiles.json', orient='records')

def create_tasks( csv_path):

    csv_df = pd.read_csv(csv_path, dtype=object, sep=',')

    task_df = csv_df[["store", "link"]].copy().rename(
        columns={'store': 'site', 'link': 'product'})
    task_df["profile"] = task_df.index
    task_df["monitor_delay"] = "5.0"
    task_df["error_delay"] = "5.0"
    task_df["max_price"] = ""
    task_df["proxies"] = "news"
    task_df["site"] = "Walmart"
    task_df["task_id"] = task_df.index
    task_df.fillna('', inplace=True)
    task_df = task_df.astype(str)
    

    csv_df["profile_name"] = task_df.index

    del csv_df['store'], csv_df['link']

    task_df.to_json(path_or_buf='data/tasks.json', orient='records')

    return transform_to_json_profile(csv_df)


if __name__ == "__main__":
    create_tasks('./profiles.csv')
