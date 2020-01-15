# -*- coding: utf-8 -*-
# """
# Created on Wed Jan  8 07:21:34 2020

# @author: howard
# """

import requests
import time
import json
from threading import Thread
from queue import Queue
from bs4 import BeautifulSoup
import json
import pandas
from flask import Flask, request, jsonify
#from flask_restful import Api
#from flask_restful import Resource

#import pytest
#from app import app

app = Flask(__name__)
#api = Api(app)
name = ''
s = ''

def run_time(func):         #使用run_time封裝這個方法 依序列出各執行序的執行時間
    #*args: positional arguments #**kw: keyword arguments
    def wrapper(*args, **kw):  # (*args:可以輸入任意長度list, #**kw: 輸入項會變成字典的儲存格式)
        start = time.time() #開始時間(年月日)
        func(*args, **kw)
        end = time.time()   #結束時間
        # print('running', end - start, 's')
    return wrapper


class makeProp:
    def __init__(self, name, img, href, store, price):
        self.name = list()
        self.img = list()
        self.href = list()
        self.store = list()
        self.price = list()

class Spider():
    def __init__(self):
        self.qurl = Queue()
        self.data = {}
        self.page_num = 10
        self.thread_num = 10
        self.name = ""
        self.proName = list()
        self.img = list()
        self.href = list() 
        self.store =list()
        self.price = list()

    def produce_url(self, name):
        baseurl = "https://feebee.com.tw/product/" + name + "/?a=1&page={}"
        for i in range(1, self.page_num + 1):
            url = baseurl.format(i)
            self.qurl.put(url)  # 生成url 並加入Queue中等待

    def get_info(self):
        while not self.qurl.empty():  # 當全部的url都完成工作後結束
            url = self.qurl.get()  # 從Queue中提取 url
            # print(url)
            # print('crawling', url)
            headers = {
                'user-agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
            }
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            selaa = soup.select("ul#product_list > li.mod_table > a.img_container")
            selab = soup.select("li.mod_table > a.product_link > div > img.imgd4")

            for n in selaa:
                    self.proName.append(n.get('title'))
                    self.price.append(n.get('data-price'))
                    self.href.append(n.get('href'))
                    self.store.append(n.get('data-store'))
            for n in selab:
                    self.img.append(n.get('src'))

            # print('pro:',len(self.proName),'\n')
            # print('price:', len(self.price), '\n')
            # print('href', len(self.href), '\n')
            # print('store', len(self.store), '\n')
            # print('img', len(self.img), '\n')
            self.data = {"productName": self.proName, "price": self.price, "href":self.href, "store": self.store , "Img": self.img }

    @run_time
    def run(self, name):
        self.produce_url(name)
        ths = []
        for _ in range(self.thread_num): #迴圈執行"執行緒總數"的循環次數
            th = Thread(target=self.get_info)  # 把執行每個url後爬蟲後的工作，分派給每個執行緒
            th.start()
            ths.append(th)
        for th in ths:
            th.join()  # Wait until the thread terminates.
            try: #執行緒任務結束後 就不要他了 如檢查後還沒結束就報錯
                # if the thread is still alive, the join() call timed out.
                th.is_alive() == False
            except:
                RuntimeError
        for n in self.data:
            output = n
            table = pandas.DataFrame(self.data)
            # print(table)
            global s
            s = table.to_json(orient='records', force_ascii=False)
            json.loads(s)


@app.route('/', methods=['POST'])
def test():
    data = request.get_json()
    # print(data)
    global name
    name = data['name']
    Spider().run(name)
    return s

@app.route('/', methods=['GET'])
def getDisplay():
    return "Please Use Post Method ====>  Format: {\"name\": \"YourSearchItem\"}"

@app.errorhandler(404)
def notFound(error):
    return '404'


if __name__ == '__main__':
    app.run()
