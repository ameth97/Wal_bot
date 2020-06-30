from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from sites.walmart import Walmart
from my_scripts.transform_tasks import create_tasks
from utils import get_profile, get_proxy, return_data

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/buy', methods = ['POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      filename = secure_filename(f.filename)
      f.save(filename)
      create_tasks(filename)

      tasks_data = return_data("./data/tasks.json")

      for task in tasks_data:
         profile, proxy = get_profile(task["profile"]), get_proxy(task["proxies"])
         Walmart(task["task_id"], None, None, task["product"], profile, proxy, task["monitor_delay"], task["error_delay"], task["max_price"], flask=True, proxies=task["proxies"])


      # Walmart(task_id, status_signal, image_signal, product, profile, proxy, monitor_delay, error_delay, max_price)
      return 'file uploaded successfully qkslkl' + str("request")
		
if __name__ == '__main__':
   app.run(debug = True, port=8880)