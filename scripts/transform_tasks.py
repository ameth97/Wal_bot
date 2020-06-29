
#!/usr/bin/env python
import sys
import pandas as pd
import time

class TransformTasks ():

    def _format_data(self):
        pass
    
    def transform_to_json_profile(self, csv_df):

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
        csv_df.to_json(path_or_buf='data/profiles.json', orient='records')

    def create_task(self, csv_path):

        csv_df = pd.read_csv(csv_path, sep=';')

        task_df = csv_df[["store","link"]].copy().rename(columns={'store': 'site', 'link': 'product'})
        task_df["profile"] = task_df.index
        task_df["monitor_delay"] = "5.0"
        task_df["error_delay"] = "5.0"
        task_df["max_price"] = ""
        task_df["proxies"] = "no_auth"
        task_df["site"] = "Walmart"
        task_df["task_id"] = task_df.index
        task_df.fillna('', inplace=True)
        task_df = task_df.astype(str)

        csv_df["profile_name"] = task_df.index
        csv_df["profile_name"] = csv_df["profile_name"].apply(str)

        del csv_df['store'], csv_df['link']


        task_df.to_json(path_or_buf='data/tasks.json', orient='records')

        return self.transform_to_json_profile(csv_df)

t = TransformTasks()
t.create_task('data/profiles.csv')