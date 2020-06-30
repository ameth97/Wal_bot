import requests


def get_cookies():

    url = 'http://localhost:8880/buy'


    headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36"
        }

    file = {'file': open('data/profiles.csv','rb')}
    session = requests.Session()
    r = session.post(url, headers=headers, files=file)
    print(r.content,r)
    # r = session.get(url=url)

  


print(get_cookies())
