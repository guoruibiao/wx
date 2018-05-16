#! /usr/bin python
# coding: utf8
import sys

reload(sys)
sys.setdefaultencoding("utf8")
import time
import json
import xml.etree.ElementTree as ET
from robot import *
from random import randint

class MsgParser(object):
    """
    用于解析从微信公众平台传递过来的参数，并进行解析
    """

    def __init__(self, data):
        self.data = data

    def parse(self):
        self.et = ET.fromstring(self.data)
        self.user = self.et.find("FromUserName").text
        self.master = self.et.find("ToUserName").text
        self.msgtype = self.et.find("MsgType").text
        # 纯文字信息字段
        self.content = self.et.find("Content").text if self.et.find("Content") is not None else ""
        # 语音信息字段
        self.recognition = self.et.find("Recognition").text if self.et.find("Recognition") is not None else ""
        self.format = self.et.find("Format").text if self.et.find("Format") is not None else ""
        self.msgid = self.et.find("MsgId").text if self.et.find("MsgId") is not None else ""
        # 图片
        self.picurl = self.et.find("PicUrl").text if self.et.find("PicUrl") is not None else ""
        self.mediaid = self.et.find("MediaId").text if self.et.find("MediaId") is not None else ""
        # 事件
        self.event = self.et.find("Event").text if self.et.find("Event") is not None else ""

        return self


class MsgDispatcher(object):
    """
    根据消息的类型，获取不同的处理返回值
    """

    def __init__(self, data):
        parser = MsgParser(data).parse()
        self.msg = parser
        self.handler = MsgHandler(parser)

    def dispatch(self):
        self.result = ""  # 统一的公众号出口数据
        if self.msg.msgtype == "text":
            self.result = self.handler.textHandle()
        elif self.msg.msgtype == "voice":
            self.result = self.handler.voiceHandle()
        elif self.msg.msgtype == 'image':
            self.result = self.handler.imageHandle()
        elif self.msg.msgtype == 'video':
            self.result = self.handler.videoHandle()
        elif self.msg.msgtype == 'shortvideo':
            self.result = self.handler.shortVideoHandle()
        elif self.msg.msgtype == 'location':
            self.result = self.handler.locationHandle()
        elif self.msg.msgtype == 'link':
            self.result = self.handler.linkHandle()
        elif self.msg.msgtype == 'event':
            self.result = self.handler.eventHandle()
        return self.result


class MsgHandler(object):
    """
    针对type不同，转交给不同的处理函数。直接处理即可
    """

    def __init__(self, msg):
        self.msg = msg
        self.time = int(time.time())

    def textHandle(self, user='', master='', time='', content=''):
        template = """
        <xml>
             <ToUserName><![CDATA[{}]]></ToUserName>
             <FromUserName><![CDATA[{}]]></FromUserName>
             <CreateTime>{}</CreateTime>
             <MsgType><![CDATA[text]]></MsgType>
             <Content><![CDATA[{}]]></Content>
         </xml>
        """
        # 对用户发过来的数据进行解析，并执行不同的路径
        try:
            response = get_response_by_keyword(self.msg.content)
            if response['type'] == "image":
                result = self.imageHandle(self.msg.user, self.msg.master, self.time, response['content'])
            elif response['type'] == "music":
                data = response['content']
                result = self.musicHandle(data['title'], data['description'], data['url'], data['hqurl'])
            elif response['type'] == "news":
                items = response['content']
                result = self.newsHandle(items)
            # 这里还可以添加更多的拓展内容
            else:
                #response = get_turing_response(self.msg.content)
                sex = "woman" if randint(1,9)%2==0 else "man"
                response = getpicurl(sex, self.msg.content)
                result = template.format(self.msg.user, self.msg.master, self.time, response)
            #with open("./debug.log", 'a') as f:
            #   f.write(response['content'] + '~~' + result)
            #    f.close()
        except Exception as e:
            with open("./debug.log", 'a') as f:
               f.write("text handler:"+str(e.message))
               f.close()
        return result

    def musicHandle(self, title='', description='', url='', hqurl=''):
        template = """
        <xml>
             <ToUserName><![CDATA[{}]]></ToUserName>
             <FromUserName><![CDATA[{}]]></FromUserName>
             <CreateTime>{}</CreateTime>
             <MsgType><![CDATA[music]]></MsgType>
             <Music>
             <Title><![CDATA[{}]]></Title>
             <Description><![CDATA[{}]]></Description>
             <MusicUrl><![CDATA[{}]]></MusicUrl>
             <HQMusicUrl><![CDATA[{}]]></HQMusicUrl>
             </Music>
             <FuncFlag>0</FuncFlag>
        </xml>
        """
        response = template.format(self.msg.user, self.msg.master, self.time, title, description, url, hqurl)
        return response

    def voiceHandle(self):
        response = get_turing_response(self.msg.recognition)
        result = self.textHandle(self.msg.user, self.msg.master, self.time, response)
        return result

    def imageHandle(self, user='', master='', time='', mediaid=''):
        template = """
        <xml>
             <ToUserName><![CDATA[{}]]></ToUserName>
             <FromUserName><![CDATA[{}]]></FromUserName>
             <CreateTime>{}</CreateTime>
             <MsgType><![CDATA[image]]></MsgType>
             <Image>
             <MediaId><![CDATA[{}]]></MediaId>
             </Image>
         </xml>
        """
        if mediaid == '':
            response = self.msg.mediaid
        else:
            response = mediaid
        result = template.format(self.msg.user, self.msg.master, self.time, response)
        return result

    def videoHandle(self):
        return 'video'

    def shortVideoHandle(self):
        return 'shortvideo'

    def locationHandle(self):
        return 'location'

    def linkHandle(self):
        return 'link'

    def eventHandle(self):
        return 'event'

    def newsHandle(self, items):
        # 图文消息这块真的好多坑，尤其是<![CDATA[]]>中间不可以有空格，可怕极了
        articlestr = """
        <item>
            <Title><![CDATA[{}]]></Title>
            <Description><![CDATA[{}]]></Description>
            <PicUrl><![CDATA[{}]]></PicUrl>
            <Url><![CDATA[{}]]></Url>
        </item>
        """
        itemstr = ""
        for item in items:
            itemstr += str(articlestr.format(item['title'], item['description'], item['picurl'], item['url']))

        template = """
        <xml>
            <ToUserName><![CDATA[{}]]></ToUserName>
            <FromUserName><![CDATA[{}]]></FromUserName>
            <CreateTime>{}</CreateTime>
            <MsgType><![CDATA[news]]></MsgType>
            <ArticleCount>{}</ArticleCount>
            <Articles>{}</Articles>
        </xml>
        """
        result = template.format(self.msg.user, self.msg.master, self.time, len(items), itemstr)
        return result


if __name__ == '__main__':
    string = """
    <xml>
<ToUserName><![CDATA[公众号]]></ToUserName>
 <FromUserName><![CDATA[粉丝号]]></FromUserName>
 <CreateTime>1460537339</CreateTime>
 <MsgType><![CDATA[text]]></MsgType>
 <Content><![CDATA[欢迎开启公众号开发者模式]]></Content>
 <MsgId>6272960105994287618</MsgId>
 </xml>

    """
    sd = MsgDispatcher(string)
    result = sd.dispatch()
    print result
