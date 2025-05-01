import os
from replit import db
import config
import requests
import platform
from urllib3 import encode_multipart_formdata


def login():

    test = requests.request("GET", config.urls["tvcoins"])
    #print(test.text)


    
    if test.status_code != 200 and 'username' in os.environ.keys() and 'password' in os.environ.keys():
        print("in")
        username = os.environ['username']
        password = os.environ['password']

        payload = {
            'username': username,
            'password': password,
            'remember': 'on'
        }
        body, contentType = encode_multipart_formdata(payload)
        userAgent = 'TWAPI/3.0 (' + platform.system(
        ) + '; ' + platform.version() + '; ' + platform.release() + ')'
        #print(userAgent)
        login_headers = {
            'origin': 'https://www.tradingview.com',
            'User-Agent': userAgent,
            'Content-Type': contentType,
            'referer': 'https://www.tradingview.com'
        }
        login = requests.post(config.urls["signin"],
                              data=body,
                              headers=login_headers)
        cookies = login.cookies.get_dict()
        #print(cookies)
        sessionid = cookies["sessionid"]
        db["sessionid"] = sessionid
