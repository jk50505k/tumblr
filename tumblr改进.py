import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import hashlib
import shutil
from tqdm import tqdm
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
DIR1='video6'#目录1
DIR2='picture5'#目录2
picList=[]#图片链接列表
vidList=[]#视频链接列表
pic_num=0#图片起始数
video_num=0#视频起始数
user_name=''#账号
password=''#密码
missed_file=0#丢包数
same_file=0
pic_file_list = []#图片md5列表
vid_file_list=[]#视频md5列表
depth=30#爬取的页数
page=0#当前页数
url='https://www.tumblr.com/dashboard/'#主页url
user=''#用户名
url_user='https://'+user+'.tumblr.com/page/'#用户页url


def getHTMLText(url):
    try:
        r=requests.get(url,headers=headers,cookies=cookies1)
        r.encoding=r.apparent_encoding
        return r.content
    except:
        return 'error'

def calcMD5(filepath):
    with open(filepath,'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash

def removeSamePicture(file_download,file_num):
    global same_file
    if file_num==0:
        pic_file_list.append(calcMD5(file_download))
    else:
        if calcMD5(file_download) in pic_file_list:
            os.remove(file_download)
            print('This file and No.%d  are same picture'%file_num)
            same_file+=1
        else:
            pic_file_list.append(calcMD5(file_download))

def removeSameVideo(file_download,file_num):
    global same_file
    if file_num==0:
        vid_file_list.append(calcMD5(file_download))
    if file_num > 0:
        if calcMD5(file_download) in vid_file_list:
            os.remove(file_download)
            print('This file and No.%d  are same video'%file_num)
            same_file += 1
        else:
            vid_file_list.append(calcMD5(file_download))

def getCookies():
    global cookies,cookies1

    options = webdriver.ChromeOptions()
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"')
    driver = webdriver.Chrome(executable_path='',chrome_options=options)#填入自己driver的地址，也可以换成别的浏览器
    driver.get('https://www.tumblr.com/dashboard/')

    elem_id=driver.find_element_by_id('signup_determine_email')
    elem_id.send_keys(user_name)
    elem_next1=driver.find_element_by_xpath("//span[@class='signup_determine_btn active']")
    elem_next1.click()
    time.sleep(2)
    elem_next2=driver.find_element_by_id('signup_magiclink').find_element_by_xpath("//div[@class='magiclink_password_container chrome']")
    elem_next2.click()
    elem_pw=driver.find_element_by_id('signup_password')
    elem_pw.send_keys(password)
    try:
        elem_signup=driver.find_element_by_xpath("//span[@class='signup_login_btn active']").click()
    except:
        elem_signup=driver.find_element_by_id("signup_forms_submit").click()

    time.sleep(10)
    cookies=driver.get_cookies()
    jsonCookies=json.dumps(cookies)
    with open('tumblr_cookies.json','w') as fd:
        fd.write(jsonCookies)
    driver.quit()
    with open('tumblr_cookies.json', 'r',encoding='utf-8') as fd:
        listCookies=json.loads(fd.read())
    cookie=[item['name']+'='+item['value'] for item in listCookies]
    cookies=';'.join(item for item in cookie)
    cookies1={'Cookie':cookies}
    return cookies1

def getLocalLog():
    # 读取本地的md5
    f_pic = open('pic_md5.txt', 'r')
    f_vid = open('vid_md5.txt', 'r')
    pic_file_list1 = f_pic.readlines()
    vid_file_list1 = f_vid.readlines()
    # 去除文件中换行符
    for line in pic_file_list1:
        pic_file_list.append(line.strip('\n'))

    for line in vid_file_list1:
        vid_file_list.append(line.strip('\n'))

def getPicture():
    global pic_num,missed_file,page
    picture = soup.select('a > img ')  # 图片
    for i in picture:
        links=i.get('src')
        if 'pnj' in links:
            continue
        picList.append(links)
        #print('Downloading:',links)


def getVideo():
    video = soup.select('source')  # 视频
    for i in video:
        video_links=i.get('src')
        #print('Downloading:', video_links)
        vidList.append(video_links)

def downloadVid(filenum,video_links):
    global missed_file ,video_num
    filename=str(filenum)+'.mp4'
    mp4 = getHTMLText(video_links)
    try:
        with open(os.path.join(DIR1, filename), "wb") as fd:
            fd.write(mp4)
    except:
        print('error')
        missed_file = missed_file + 1
    removeSameVideo(os.path.join(DIR1, filename), video_num)
    video_num+=1

def downloadPic(filenum,links):
    global missed_file,pic_num
    filename = str(filenum) + '.jpg'
    image = getHTMLText(links)
    try:
        with open(os.path.join(DIR2, filename), "wb") as fd:
            fd.write(image)
            # print('Download successfully')
    except:
        print('error')
        missed_file = missed_file + 1
    removeSamePicture(os.path.join(DIR2, filename), pic_num)
    pic_num = pic_num + 1
def saveLog():
    # 将md5存入本地
    with open('pic_md5.txt', 'w') as fd:
        for md5 in pic_file_list:
            fd.write(md5 + '\n')

    with open('vid_md5.txt', 'w') as fd:
        for md5 in vid_file_list:
            fd.write(md5 + '\n')


if __name__ == '__main__':

    getCookies()#获取cookie
    getLocalLog()#获取本地日志
    if not os.path.exists(DIR1):
        os.makedirs(DIR1)

    if not os.path.exists(DIR2):
        os.makedirs(DIR2)

    start=time.clock()
    print('getting downloaded links ')
    for i in tqdm(range(1,depth+1)):

        html = getHTMLText(url+str(i))
        soup=BeautifulSoup(html,'html.parser')
        getVideo()
        getPicture()

    for i in tqdm(vidList):
        downloadVid(video_num,i)

    for i in tqdm(picList):
        downloadPic(pic_num,i)

    print('For now\n loss:%d\n download: %d \n samefile: %d' % (missed_file, pic_num + video_num, same_file))

    saveLog()#保存日志
    end=time.clock()
    print('There are %d files missing during the downloading'%missed_file)
    print('There are %d same files in total'%same_file)
    print('Running time: %f seconds'%(end-start))
