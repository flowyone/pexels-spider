# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import urllib
import gevent
from gevent import Greenlet
import socket
import random
import re, pymysql, threading,os,time
from PIL import Image
connect = pymysql.Connect(
    host='localhost',
    port=3306,
    user='python',
    passwd='8eeded',
    db='python',
    charset='utf8'
)
cursor = connect.cursor()
mutex = threading.Lock()
user_agent_list = [ \
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36", \
        "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko", \
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36 QIHU 360SE", \
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36", \
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E)", \
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393", \
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/60.0.1163.0 Safari/536.3"
    ]
def cbk(a, b, c):
    '''''回调函数
    '''
    per = 100.0 * a * b / c
    if per > 100:
        per = 100
    print('%.2f%%' % per)
def photo_download(photo_thread, index_number, photo_number, number):
    while number < 3564:
        try:
            i = 0
            number = number + 1
            url = "https://www.pexels.com/search/"+random.choice(dict)+"?page="+str(index_number)+"&format=js&seed=2018-06-27%2002:36:18%20+0000"
            # print(headers)
            headers = {'User-Agent': random.choice(user_agent_list)}
            r = requests.get(url, headers=headers)
            # 获得目标页面返回信息
            cate = url.split('?')[0].split('/')[4]
            while r.status_code == 404:
                # 判断响应状态码
                i = i + 1
                url = "https://www.pexels.com/search/" + random.choice(dict) + "?page=" + str(index_number) + "&format=js&seed=2018-06-27%2002:36:18%20+0000"
                print(url)
            else:
                for link in re.findall(re.compile(r'alt=\\"(.*?)\\" data-big-src=\\"(.*?)"'),r.text):
                    #https://images.pexels.com/photos/713829/pexels-photo-713829.jpeg?auto=compress&amp;cs=tinysrgb&amp;h=750&amp;w=1260\\
                    #取出入库属性：
                    img_url =  link[1].split("?")[0]
                    img_height = link[1].split("?")[1].split('&amp;')[2].split('=')[1]
                    img_width = link[1].split("?")[1].split('&amp;')[3].split('=')[1].replace('\\','')
                    title=link[0]
                    # 输出图片信息
                    print(img_url,img_height,img_width,title)
                    # 设置超时
                    socket.setdefaulttimeout(3.0)
                    photo_number = photo_number + 1
                    img_save  = time.strftime('%Y%m%d', time.localtime(time.time()))+img_url[-10:]
                    img_thumb = 'thumb_'+time.strftime('%Y%m%d', time.localtime(time.time()))+img_url[-10:]
                    save(img_url)#图片本地化
                    save_db(img_url,img_height,img_width,img_save,title,img_thumb,cate)#图片上传数据库
        except Exception as e:
            # print(e)
            index_number = index_number + 1
        index_number = index_number + 1
def save_db(img_url,img_height, img_width, img_save, title,img_thumb,cate):
        sql = "insert into lcr_cs (`img_url`,`img_height`,`img_width`,`img_save`,`title`,`img_thumb`,`img_cate`) values ('%s','%s','%s','%s','%s','%s','%s')"
        sql = sql % (img_url,img_height, img_width, img_save,title,img_thumb,cate)
        print(sql)
        if mutex.acquire():
            try:
                cursor.execute(sql)
                connect.commit()
            except:
                print(img_url + "：插入失败，记录可能已存在")
            mutex.release()
def save(img_url):
    #生成原图
        res = requests.get(img_url)
        with open(file + img_url[-10:], 'wb') as f:
            f.write(res.content)
            create_thumbnail(os.path.abspath('.')+"\orig\\"+img_url[-10:])
def create_thumbnail(filename):
    # 生成缩略图
    im = Image.open(filename)
    im.thumbnail(SIZE, Image.ANTIALIAS)
    base, fname = os.path.split(filename)
    save_path = os.path.join(base, THUMB_DIRECTORY, 'thumb_'+fname)
    im.save(save_path)
if __name__ == '__main__':
    # 照片分类
    dict = ['face', 'beach', 'family', 'medical', 'young', 'man', 'art', 'healthy', 'kids' ]
    # 线程
    photo_thread = [1, 2]
    SIZE = (400,300)
    THUMB_DIRECTORY = os.path.abspath('.')+"\\thumb\\"
    photo_number = -1
    # 下载图片计数器，最大50
    file =os.path.abspath('.')+"\orig\\"
    # 图片的保存地址
    thread1 = Greenlet.spawn(photo_download, photo_thread[0], 1, photo_number, 0)
    thread2 = gevent.spawn(photo_download, photo_thread[1], 300, photo_number, 0)
    threads = [thread1, thread2]
    # 阻止所有线程完成
    gevent.joinall(threads)
