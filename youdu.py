# coding: utf8

import requests
from random import randint

def getpicurl(sex, username):
    headers = {
        "Referer": "https://servicewechat.com/wx4ce0fb3f71ec3d5b/1/page-frame.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
        "Host": "www.likejiujisong.net",
        "Connection": "Keep-Alive",
        "Upgrade-Insecure-Requests": "1",
    }
    # picid 有毒，它只是一个模板罢了
    geturl = "https://www.likejiujisong.net/youduo/tomake.php?picid={}&sex={}&name={}&audit=youduov1.0".format(randint(1, 300), sex, username)
    response = requests.get(url=geturl, headers=headers, verify=False)
    data = response.json()['data']
    picurl = "https://www.likejiujisong.net/youduo/{}".format(data)
    return picurl

