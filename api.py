# -*- coding:utf-8 -*-                             #中文编码
import sys

reload(sys)  # 不加这部分好像处理中文还是会出问题
sys.setdefaultencoding('utf-8')

import time
from flask import Flask, request, make_response
import hashlib
import json
import xml.etree.ElementTree as ET

from dispatcher import *


app = Flask(__name__)
app.debug = True


@app.route('/')  # 网址
def index():
    return 'Index Page'


@app.route('/wx', methods=['GET', 'POST'])
def wechat_auth():  # 处理微信请求的处理函数，get方法用于认证，post方法取得微信转发的数据
    if request.method == 'GET':
        token = 'hello2017'
        data = request.args
        signature = data.get('signature', '')
        timestamp = data.get('timestamp', '')
        nonce = data.get('nonce', '')
        echostr = data.get('echostr', '')
        s = [timestamp, nonce, token]
        s.sort()
        s = ''.join(s)
        if (hashlib.sha1(s).hexdigest() == signature):
            return make_response(echostr)
    else:
        rec = request.stream.read()  # 接收消息
        dispatcher = MsgDispatcher(rec)
        data = dispatcher.dispatch()
        with open("./debug.log", "a") as file:
            file.write(data)
            file.close()
        response = make_response(data)
        response.content_type = 'application/xml'
        return response


def message_del(content):  # 次数是自定义的消息处理函数，自由发挥
    if "baidu" in content:
        message = "www.baidu.com"
    elif "金牛" in content:
        message = "贪财好色小心眼"
    else:
        message = "我不知道！"
    return message


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
